package middleware

import (
	"context"
	"os"

	"wpconn-go/internal/database"

	"github.com/gofiber/fiber/v3"
)

func AuthMiddleware(c fiber.Ctx) error {
	apiKey := c.Get("x-api-key")
	if apiKey == "" {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Missing API Key"})
	}

	// 1. Admin Check
	appSecret := os.Getenv("APP_SECRET")
	if appSecret != "" && apiKey == appSecret {
		c.Locals("role", "admin")
		return c.Next()
	}

	// 2. Tenant Check
	var tenantID string
	query := `SELECT id FROM tenants WHERE api_key = $1 LIMIT 1`
	err := database.Pool.QueryRow(context.Background(), query, apiKey).Scan(&tenantID)
	if err != nil {
		return c.Status(fiber.StatusUnauthorized).JSON(fiber.Map{"error": "Invalid API Key"})
	}

	c.Locals("role", "tenant")
	c.Locals("tenant_id", tenantID)
	return c.Next()
}
