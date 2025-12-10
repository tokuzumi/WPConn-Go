package handlers

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"time"

	"wpconn-go/internal/database"
	"wpconn-go/internal/domain"

	"github.com/gofiber/fiber/v3"
	"github.com/jackc/pgx/v5"
)

func generateAPIKey() string {
	bytes := make([]byte, 16)
	if _, err := rand.Read(bytes); err != nil {
		return fmt.Sprintf("key-%d", time.Now().UnixNano())
	}
	return hex.EncodeToString(bytes)
}

func GetTenants(c fiber.Ctx) error {
	role := c.Locals("role").(string)
	ctx := context.Background()

	var rows pgx.Rows
	var err error

	if role == "admin" {
		rows, err = database.Pool.Query(ctx, "SELECT id, name, phone_number_id, is_active, created_at, api_key FROM tenants")
	} else {
		tenantID := c.Locals("tenant_id").(string)
		rows, err = database.Pool.Query(ctx, "SELECT id, name, phone_number_id, is_active, created_at, api_key FROM tenants WHERE id = $1", tenantID)
	}

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to fetch tenants"})
	}
	defer rows.Close()

	tenants := []domain.Tenant{}
	for rows.Next() {
		var t domain.Tenant
		// We only scan fields selected in query
		if err := rows.Scan(&t.ID, &t.Name, &t.PhoneNumberID, &t.IsActive, &t.CreatedAt, &t.APIKey); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to scan tenant"})
		}
		tenants = append(tenants, t)
	}

	return c.JSON(tenants)
}

func CreateTenant(c fiber.Ctx) error {
	var req domain.Tenant
	if err := c.Bind().Body(&req); err != nil {
		return c.Status(fiber.StatusBadRequest).JSON(fiber.Map{"error": "Invalid request"})
	}

	if req.APIKey == "" {
		req.APIKey = generateAPIKey()
	}

	query := `
		INSERT INTO tenants (name, waba_id, phone_number_id, token, api_key, is_active)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING id, created_at
	`
	err := database.Pool.QueryRow(context.Background(), query, req.Name, req.WabaID, req.PhoneNumberID, req.Token, req.APIKey, true).Scan(&req.ID, &req.CreatedAt)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to create tenant: " + err.Error()})
	}

	return c.Status(fiber.StatusCreated).JSON(req)
}
