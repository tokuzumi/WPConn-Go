package api

import (
	"wpconn-go/api/handlers"
	"wpconn-go/api/middleware"

	"github.com/gofiber/fiber/v3"
	"go.temporal.io/sdk/client"
)

func SetupRoutes(app *fiber.App, temporal client.Client) {
	// Webhook Handler Instance
	webhookHandler := &WebhookHandler{Temporal: temporal}

	// Public Routes (Webhooks)
	webhooks := app.Group("/api/v1/webhooks")
	webhooks.Get("/", webhookHandler.VerifyWebhook)
	webhooks.Post("/", webhookHandler.HandleWebhook)

	// Health Check (Public)
	app.Get("/health", func(c fiber.Ctx) error {
		return c.Status(fiber.StatusOK).JSON(fiber.Map{"status": "ok"})
	})

	// Protected Routes (Dashboard API)
	v1 := app.Group("/api/v1", middleware.AuthMiddleware)

	// Dashboard
	v1.Get("/dashboard/stats", handlers.GetDashboardStats)

	// Tenants
	v1.Get("/tenants", handlers.GetTenants)
	v1.Post("/tenants", handlers.CreateTenant)

	// Messages
	v1.Get("/messages", handlers.GetMessages)
}
