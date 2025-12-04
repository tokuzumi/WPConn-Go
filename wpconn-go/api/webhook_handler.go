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

	"github.com/gofiber/fiber/v3"
	"go.temporal.io/sdk/client"
)

type WebhookHandler struct {
	Temporal client.Client
}

func SetupRoutes(app *fiber.App, temporal client.Client) {
	handler := &WebhookHandler{Temporal: temporal}
	
	// Meta Webhook Verification (GET)
	app.Get("/api/v1/webhooks", handler.VerifyWebhook)
	
	// Meta Webhook Event (POST)
	app.Post("/api/v1/webhooks", handler.HandleWebhook)
}

func (h *WebhookHandler) VerifyWebhook(c fiber.Ctx) error {
	mode := c.Query("hub.mode")
	token := c.Query("hub.verify_token")
	challenge := c.Query("hub.challenge")

	verifyToken := os.Getenv("WEBHOOK_VERIFY_TOKEN")

	if mode == "subscribe" && token == verifyToken {
		log.Println("Webhook verified successfully!")
		return c.SendString(challenge)
	}

	return c.Status(fiber.StatusForbidden).SendString("Verification failed")
}

func (h *WebhookHandler) HandleWebhook(c fiber.Ctx) error {
	// 1. Validate Signature
	signature := c.Get("X-Hub-Signature-256")
	if signature == "" {
		signature = c.Get("x-hub-signature-256")
	}
	
	body := c.Body()
	appSecret := os.Getenv("APP_SECRET")

	if !validateSignature(body, signature, appSecret) {
		log.Println("Invalid signature")
		return c.Status(fiber.StatusForbidden).SendString("Invalid signature")
	}

	// 2. Parse Payload
	var event WebhookEvent
	if err := json.Unmarshal(body, &event); err != nil {
		log.Printf("Error parsing webhook: %v", err)
		return c.SendStatus(fiber.StatusBadRequest)
	}

	// 3. Process Entries
	go func() {
		for _, entry := range event.Entry {
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
						CreatedAt:   time.Now(), // Or use msg.Timestamp if available
						// TenantID: We need to resolve this from PhoneNumberID usually.
						// For now, we leave it empty or pass PhoneNumberID to workflow to resolve.
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
