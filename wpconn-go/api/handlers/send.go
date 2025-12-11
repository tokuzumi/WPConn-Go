package handlers

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"wpconn-go/internal/database"
	"wpconn-go/internal/domain"

	"github.com/gofiber/fiber/v3"
)

type SendMessageRequest struct {
	Phone    string `json:"phone"`
	Type     string `json:"type"` // text, image, video, document, audio, sticker
	Content  string `json:"content"`
	MediaURL string `json:"media_url,omitempty"`
}

// Meta API Payloads
type MetaMessageRequest struct {
	MessagingProduct string      `json:"messaging_product"`
	To               string      `json:"to"`
	Type             string      `json:"type"`
	Text             *MetaText   `json:"text,omitempty"`
	Image            *MetaMedia  `json:"image,omitempty"`
	Video            *MetaMedia  `json:"video,omitempty"`
	Audio            *MetaMedia  `json:"audio,omitempty"`
	Document         *MetaMedia  `json:"document,omitempty"`
	Sticker          *MetaMedia  `json:"sticker,omitempty"`
}

type MetaText struct {
	Body string `json:"body"`
}

type MetaMedia struct {
	Link    string `json:"link"`
	Caption string `json:"caption,omitempty"`
}

type MetaResponse struct {
	Contacts []struct {
		Input string `json:"input"`
		WaID  string `json:"wa_id"`
	} `json:"contacts"`
	Messages []struct {
		ID string `json:"id"`
	} `json:"messages"`
}

func SendMessage(c fiber.Ctx) error {
	ctx := context.Background()
	var req SendMessageRequest

	// 1. Parse Body
	if err := c.Bind().Body(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request body"})
	}

	if req.Phone == "" || req.Type == "" {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "phone and type are required"})
	}

	// 2. Get Tenant Context (from Middleware)
	tenantID, ok := c.Locals("tenant_id").(string)
	if !ok || tenantID == "" {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Unauthorized: No Tenant Context"})
	}

	// 3. Fetch Tenant/WABA Credentials
	// We need WABA details to send message FROM the correct number
	// Assuming 1 phone number per tenant for now, or using the primary one.
	var t domain.Tenant
	query := `SELECT waba_id, phone_number_id, token, alias FROM tenants WHERE id = $1 LIMIT 1`
	err := database.Pool.QueryRow(ctx, query, tenantID).Scan(&t.WabaID, &t.PhoneNumberID, &t.Token, &t.Alias)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to fetch tenant credentials"})
	}

	// 4. Construct Meta Payload
	metaReq := MetaMessageRequest{
		MessagingProduct: "whatsapp",
		To:               req.Phone,
		Type:             req.Type,
	}

	switch req.Type {
	case "text":
		if req.Content == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "content is required for text messages"})
		}
		metaReq.Text = &MetaText{Body: req.Content}
	case "image":
		if req.MediaURL == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "media_url is required for image messages"})
		}
		metaReq.Image = &MetaMedia{Link: req.MediaURL, Caption: req.Content}
	case "video":
		if req.MediaURL == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "media_url is required for video messages"})
		}
		metaReq.Video = &MetaMedia{Link: req.MediaURL, Caption: req.Content}
	case "audio":
		if req.MediaURL == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "media_url is required for audio messages"})
		}
		metaReq.Audio = &MetaMedia{Link: req.MediaURL}
	case "document":
		if req.MediaURL == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "media_url is required for document messages"})
		}
		metaReq.Document = &MetaMedia{Link: req.MediaURL, Caption: req.Content}
	case "sticker":
		if req.MediaURL == "" {
			return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "media_url is required for sticker messages"})
		}
		metaReq.Sticker = &MetaMedia{Link: req.MediaURL}
	default:
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Unsupported message type"})
	}

	// 5. Send to Meta
	payloadBytes, err := json.Marshal(metaReq)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to encode payload"})
	}

	url := fmt.Sprintf("https://graph.facebook.com/v17.0/%s/messages", t.PhoneNumberID)
	reqMeta, err := http.NewRequest("POST", url, bytes.NewBuffer(payloadBytes))
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create request"})
	}

	reqMeta.Header.Set("Authorization", "Bearer "+t.Token)
	reqMeta.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(reqMeta)
	if err != nil {
		return c.Status(fiber.StatusBadGateway).JSON(fiber.Map{"error": "Failed to call Meta API: " + err.Error()})
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return c.Status(resp.StatusCode).JSON(fiber.Map{
			"error": "Meta API Error",
			"details": string(bodyBytes),
		})
	}

	// 6. Parse Success Response
	var metaResp MetaResponse
	if err := json.Unmarshal(bodyBytes, &metaResp); err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to parse Meta response"})
	}

	if len(metaResp.Messages) == 0 {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "No message ID returned from Meta"})
	}

	wamid := metaResp.Messages[0].ID

	// 7. Store in Database
	// We store it as 'sent'. The webhook will eventually update it to 'delivered'/'read', 
	// or we might get a transient 'sent' webhook.
	insertQuery := `
		INSERT INTO messages (
			wamid, 
			waba_id, 
			sender_phone, 
			direction, 
			type, 
			status, 
			content, 
			media_url, 
			created_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
	`
	
	// Determine sender phone (our phone) and recipient phone (req.Phone) logic?
	// Actually database schema 'sender_phone' usually means who sent it. 
	// For outbound, we can store the recipient in a 'recipient_phone' column OR 
	// overload 'sender_phone' to be 'our phone' and rely on context.
	// Looking at existing schema/usage:
	// Inbound: SenderPhone = Client Phone.
	// Outbound: We need to know who we sent it TO.
	// The current 'messages' table seems to have 'sender_phone'.
	// Inspecting previous `messages.go`: `m.SenderPhone` is used.
	// Let's check `activities.go`: inbound stores `msg.From` (Client) in `sender_phone`.
	// For outbound, to keep conversation view consistent, we usually want to know who is the "other party".
	// If the dashboard view keys off 'sender_phone' for "Who is this chat with?", 
	// then for outbound messages, we probably want 'sender_phone' to be the RECIPIENT, 
	// OR we need a separate 'recipient_phone' column.
	//
	// Given the constraint of not changing schema in this step if possible, 
	// usually apps use 'remote_jid' or similar. 
	// Let's assume 'sender_phone' acts as "The Contact's Phone" regardless of direction 
	// (so conversation grouping works).
	// If direction=inbound, sender=Client.
	// If direction=outbound, we still want to group by Client.
	// So we will store 'req.Phone' in 'sender_phone' (representing the Contact).
	
	_, err = database.Pool.Exec(ctx, insertQuery, 
		wamid, 
		t.WabaID, 
		req.Phone,   // Storing Contact Phone here for grouping
		"outbound", 
		req.Type, 
		"sent", 
		req.Content, 
		req.MediaURL, 
		time.Now(),
	)

	if err != nil {
		// Log error but don't fail the HTTP request as Meta already accepted it
		// In a real system we might have a background job to retry storage or alert
		fmt.Printf("Error saving outbound message: %v\n", err)
	}

	return c.Status(fiber.StatusCreated).JSON(fiber.Map{
		"status": "success",
		"wamid": wamid,
		"meta_response": metaResp,
	})
}
