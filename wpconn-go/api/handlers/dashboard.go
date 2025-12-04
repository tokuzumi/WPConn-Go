package handlers

import (
	"context"

	"wpconn-go/internal/database"

	"github.com/gofiber/fiber/v3"
)

func GetDashboardStats(c fiber.Ctx) error {
	ctx := context.Background()

	// 1. Active Tenants
	var activeTenants int
	err := database.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM tenants WHERE is_active = true").Scan(&activeTenants)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to count tenants"})
	}

	// 2. Messages (Last 24h)
	var messages24h int
	err = database.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM messages WHERE created_at > NOW() - INTERVAL '24 hours'").Scan(&messages24h)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to count messages"})
	}

	// 3. Webhook Queue (Pending Messages)
	var pendingMessages int
	err = database.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM messages WHERE status = 'pending'").Scan(&pendingMessages)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to count pending messages"})
	}

	return c.JSON(fiber.Map{
		"active_tenants":  activeTenants,
		"messages_24h":    messages24h,
		"webhook_queue":   pendingMessages,
	})
}
