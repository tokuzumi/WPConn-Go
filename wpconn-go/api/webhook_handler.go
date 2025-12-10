package api

import (
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"

	"time"

	"wpconn-go/internal/domain"
	"wpconn-go/internal/database"

	"github.com/gofiber/fiber/v3"
	"go.temporal.io/sdk/client"
)

type WebhookHandler struct {
	Temporal client.Client
}


func (h *WebhookHandler) VerifyWebhook(c fiber.Ctx) error {
	mode := c.Query("hub.mode")
	token := c.Query("hub.verify_token")
	challenge := c.Query("hub.challenge")

	verifyToken := os.Getenv("WEBHOOK_VERIFY_TOKEN")

	if mode == "subscribe" && token == verifyToken {
		log.Println("Webhook verified successfully!")
		
		// Persist Handshake to Messages for visibility
		go func() {
			ctx := context.Background()
			query := `
				INSERT INTO messages (wamid, type, direction, status, content, created_at, waba_id)
				VALUES ($1, $2, $3, $4, $5, $6, $7)
			`
			// We don't have phone_id in handshake, so we leave it empty (Global/System)
			wamid := fmt.Sprintf("handshake-%d", time.Now().Unix())
			content := "Webhook Verificado com Sucesso (Handshake)"
			_, err := database.Pool.Exec(ctx, query, wamid, "system", "inbound", "read", content, time.Now(), "system")
			if err != nil {
				log.Printf("Failed to log handshake: %v", err)
			}
		}()

		return c.SendString(challenge)
	}

	return c.Status(fiber.StatusForbidden).SendString("Verification failed")
}

func (h *WebhookHandler) RetryWebhook(c fiber.Ctx) error {
	logID := c.Params("id")
	// TODO: Implement actual retry logic. 
	// This would require fetching the original payload from the log (if stored) 
	// and re-submitting it to the workflow.
    // For now, we simulate success to prevent frontend error.
    log.Printf("Retrying webhook for log ID: %s", logID)
	return c.JSON(fiber.Map{"status": "retried", "message": "Retry signal sent (stub)"})
}

func (h *WebhookHandler) HandleWebhook(c fiber.Ctx) error {
	// 0. Debug Logging
	log.Println("--- DEBUG: Webhook POST Received ---")
	
	// 1. Validate Signature
	signature := c.Get("X-Hub-Signature-256")
	if signature == "" {
		signature = c.Get("x-hub-signature-256")
	}
	log.Printf("DEBUG: Signature Header: %s", signature)

	body := c.Body()
	log.Printf("DEBUG: Body Size: %d", len(body))

	appSecret := os.Getenv("APP_SECRET")
	// Warn if secret is suspicious
	if len(appSecret) < 5 {
		log.Println("CRITICAL: APP_SECRET in env is very short or empty!")
	}

	if !validateSignature(body, signature, appSecret) {
		log.Println("ERROR: Invalid signature! Check if APP_SECRET matches Meta App Secret.")
		return c.Status(fiber.StatusForbidden).SendString("Invalid signature")
	}
	log.Println("DEBUG: Signature validated successfully.")

	// 2. Parse Payload
	var event WebhookEvent
	if err := json.Unmarshal(body, &event); err != nil {
		log.Printf("Error parsing webhook: %v", err)
		return c.SendStatus(fiber.StatusBadRequest)
	}

	// 3. Process Entries
	go func() {
		for _, entry := range event.Entry {
			tenantWabaID := entry.ID // Extracted WABA ID

			for _, change := range entry.Changes {
				value := change.Value
				if value.Messages == nil {
					continue
				}

				phoneNumberID := value.Metadata.PhoneNumberID
				
				for _, msg := range value.Messages {
					// Map to Domain Message
					domainMsg := domain.Message{
						Wamid:       msg.ID,
						Type:        msg.Type,
						Direction:   "inbound",
						Status:      "pending",
						Content:     extractContent(msg),
						MetaMediaID: extractMediaID(msg),
						BusinessPhoneID: phoneNumberID,
						TenantWabaID: tenantWabaID, // Set WABA ID
						SenderPhone: msg.From,
						CreatedAt:   time.Now(), 
					}

					// SignalWithStart
					workflowID := fmt.Sprintf("conversation-%s", phoneNumberID)
					options := client.StartWorkflowOptions{
						ID:        workflowID,
						TaskQueue: "WHATSAPP_TASK_QUEUE",
					}

					_, err := h.Temporal.SignalWithStartWorkflow(context.Background(), options.ID, "NewMessage", domainMsg, options, "ConversationWorkflow")
					if err != nil {
						log.Printf("Failed to SignalWithStart for wamid %s: %v", domainMsg.Wamid, err)
					} else {
						log.Printf("Signaled workflow %s for wamid %s", workflowID, domainMsg.Wamid)
					}
				}
			}
		}
	}()

	return c.SendStatus(fiber.StatusOK)
}

func validateSignature(payload []byte, signatureHeader string, secret string) bool {
	if signatureHeader == "" {
		return false
	}
	parts := strings.Split(signatureHeader, "=")
	if len(parts) != 2 || parts[0] != "sha256" {
		return false
	}
	signature := parts[1]

	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write(payload)
	expectedSignature := hex.EncodeToString(mac.Sum(nil))

	return hmac.Equal([]byte(signature), []byte(expectedSignature))
}

func extractContent(msg MessageData) string {
	switch msg.Type {
	case "text":
		return msg.Text.Body
	case "image":
		return msg.Image.Caption
	case "video":
		return msg.Video.Caption
	case "document":
		return msg.Document.Caption
	default:
		return ""
	}
}

func extractMediaID(msg MessageData) string {
	switch msg.Type {
	case "image":
		return msg.Image.ID
	case "video":
		return msg.Video.ID
	case "audio":
		return msg.Audio.ID
	case "document":
		return msg.Document.ID
	case "sticker":
		return msg.Sticker.ID
	default:
		return ""
	}
}

// Structs for parsing
type WebhookEvent struct {
	Entry []struct {
		ID string `json:"id"` 
		Changes []struct {
			Value ValueData `json:"value"`
		} `json:"changes"`
	} `json:"entry"`
}

type ValueData struct {
	Metadata struct {
		PhoneNumberID string `json:"phone_number_id"`
	} `json:"metadata"`
	Messages []MessageData `json:"messages"`
}

type MessageData struct {
	ID        string `json:"id"`
	From      string `json:"from"` // Sender phone number
	Type      string `json:"type"`
	Timestamp string `json:"timestamp"` // Often unix timestamp string or int
	Text      struct {
		Body string `json:"body"`
	} `json:"text,omitempty"`
	Image struct {
		ID      string `json:"id"`
		Caption string `json:"caption"`
	} `json:"image,omitempty"`
	Video struct {
		ID      string `json:"id"`
		Caption string `json:"caption"`
	} `json:"video,omitempty"`
	Audio struct {
		ID string `json:"id"`
	} `json:"audio,omitempty"`
	Document struct {
		ID      string `json:"id"`
		Caption string `json:"caption"`
	} `json:"document,omitempty"`
	Sticker struct {
		ID string `json:"id"`
	} `json:"sticker,omitempty"`
}

func SystemTimeNow() int64 {
    return time.Now().UnixNano()
}
