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
		// Try lowercase just in case
		signature = c.Get("x-hub-signature-256")
	}
	
	body := c.Body()
	appSecret := os.Getenv("APP_SECRET")

	if !validateSignature(body, signature, appSecret) {
		log.Println("Invalid signature")
		return c.Status(fiber.StatusForbidden).SendString("Invalid signature")
	}

	// 2. Parse Payload (Minimal parsing to extract media)
	// We want to respond FAST (< 5ms).
	// So we might just push the raw body to Temporal.
	// But the requirement says "Extract media_id and type".
	// Let's do a quick parse.
	
	// We'll launch the workflow asynchronously.
	go func(payload []byte) {
		// TODO: Define the Workflow struct/name in a shared package or string
		workflowOptions := client.StartWorkflowOptions{
			ID:        "webhook-" + fmt.Sprintf("%d", time.Now().UnixNano()), // Unique ID strategy needed
			TaskQueue: "WHATSAPP_TASK_QUEUE",
		}
		
		// We pass the raw payload to the workflow to handle parsing logic if complex,
		// OR we parse here if strictly required by "Extract media_id".
		// Requirement: "3. Extrai media_id e tipo. 5. Inicia Workflow... passando apenas os IDs brutos."
		// So we MUST parse here.
		
		var event GenericWebhookEvent
		if err := json.Unmarshal(payload, &event); err != nil {
			log.Printf("Error parsing webhook: %v", err)
			return
		}

		// Iterate over entries and changes to find messages with media
		for _, entry := range event.Entry {
			for _, change := range entry.Changes {
				if change.Value.Messages != nil {
					for _, msg := range change.Value.Messages {
						if msg.Type == "image" || msg.Type == "video" || msg.Type == "audio" || msg.Type == "document" || msg.Type == "sticker" {
							// Found media!
							mediaID := ""
							switch msg.Type {
							case "image": mediaID = msg.Image.ID
							case "video": mediaID = msg.Video.ID
							case "audio": mediaID = msg.Audio.ID
							case "document": mediaID = msg.Document.ID
							case "sticker": mediaID = msg.Sticker.ID
							}

							if mediaID != "" {
								// Start Workflow
								// We use a generated ID for the workflow to ensure uniqueness per message
								workflowID := "media-" + msg.ID
								workflowOptions.ID = workflowID
								
								_, err := h.Temporal.ExecuteWorkflow(context.Background(), workflowOptions, "ProcessMediaWorkflow", mediaID, msg.Type)
								if err != nil {
									log.Printf("Failed to start workflow for media %s: %v", mediaID, err)
								} else {
									log.Printf("Started workflow %s for media %s", workflowID, mediaID)
								}
							}
						}
					}
				}
			}
		}

	}(body)

	// 3. Return 200 OK immediately
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

// Helper structs for minimal parsing
type GenericWebhookEvent struct {
	Entry []struct {
		Changes []struct {
			Value struct {
				Messages []struct {
					ID    string `json:"id"`
					Type  string `json:"type"`
					Image struct {
						ID string `json:"id"`
					} `json:"image,omitempty"`
					Video struct {
						ID string `json:"id"`
					} `json:"video,omitempty"`
					Audio struct {
						ID string `json:"id"`
					} `json:"audio,omitempty"`
					Document struct {
						ID string `json:"id"`
					} `json:"document,omitempty"`
					Sticker struct {
						ID string `json:"id"`
					} `json:"sticker,omitempty"`
				} `json:"messages,omitempty"`
			} `json:"value"`
		} `json:"changes"`
	} `json:"entry"`
}

func SystemTimeNow() int64 {
    return time.Now().UnixNano()
}
