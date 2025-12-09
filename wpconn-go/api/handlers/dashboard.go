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
	_ = database.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM tenants WHERE is_active = true").Scan(&activeTenants)

	// 2. Messages (Last 24h)
	var messages24h int
	_ = database.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM messages WHERE created_at > NOW() - INTERVAL '24 hours'").Scan(&messages24h)

	// 3. Webhook Queue (Pending Messages)
	var pendingMessages int
	_ = database.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM messages WHERE status = 'pending'").Scan(&pendingMessages)

    // TODO: Implement real queries for these
    // For now, return empty/default data to prevent frontend crash
    kpis := fiber.Map{
        "pending_webhooks": pendingMessages,
        "error_rate_24h":   0.0, // Need to implement error tracking
        "daily_messages":   messages24h,
        "active_tenants":   activeTenants,
    }

	return c.JSON(fiber.Map{
		"kpis":                kpis,
		"hourly_traffic":      []fiber.Map{}, // Return empty array
		"status_distribution": []fiber.Map{}, // Return empty array
		"event_health":        []fiber.Map{}, // Return empty array
        "recent_errors":       []fiber.Map{}, // Return empty array
	})
}
