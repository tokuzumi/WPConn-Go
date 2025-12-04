package handlers

import (
	"context"
	"strconv"

	"wpconn-go/internal/database"
	"wpconn-go/internal/domain"

	"github.com/gofiber/fiber/v3"
	"github.com/jackc/pgx/v5"
)

func GetMessages(c fiber.Ctx) error {
	role := c.Locals("role").(string)
	ctx := context.Background()

	limit := 50
	offset := 0
	if l := c.Query("limit"); l != "" {
		if val, err := strconv.Atoi(l); err == nil {
			limit = val
		}
	}
	if o := c.Query("offset"); o != "" {
		if val, err := strconv.Atoi(o); err == nil {
			offset = val
		}
	}

	var rows pgx.Rows
	var err error

	if role == "admin" {
		query := `SELECT id, tenant_id, wamid, type, direction, status, content, media_url, created_at FROM messages ORDER BY created_at DESC LIMIT $1 OFFSET $2`
		rows, err = database.Pool.Query(ctx, query, limit, offset)
	} else {
		tenantID := c.Locals("tenant_id").(string)
		query := `SELECT id, tenant_id, wamid, type, direction, status, content, media_url, created_at FROM messages WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3`
		rows, err = database.Pool.Query(ctx, query, tenantID, limit, offset)
	}

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to fetch messages"})
	}
	defer rows.Close()

	var messages []domain.Message
	for rows.Next() {
		var m domain.Message
		if err := rows.Scan(&m.ID, &m.TenantID, &m.Wamid, &m.Type, &m.Direction, &m.Status, &m.Content, &m.MediaURL, &m.CreatedAt); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to scan message"})
		}
		messages = append(messages, m)
	}

	return c.JSON(messages)
}
