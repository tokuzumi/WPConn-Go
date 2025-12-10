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

	// Assuming global view for now as requested (or admin view)
	// We join with tenants to get the Alias based on waba_id matching tenants.waba_id
	query := `
		SELECT 
			m.id, 
			COALESCE(m.waba_id, ''), 
			COALESCE(t.alias, t.name, 'Desconhecido'),
			m.wamid, 
			m.type, 
			m.direction, 
			m.status, 
			COALESCE(m.content, ''), 
			COALESCE(m.media_url, ''), 
			COALESCE(m.sender_phone, ''), 
			m.created_at 
		FROM messages m
		LEFT JOIN tenants t ON m.waba_id = t.waba_id
		ORDER BY m.created_at DESC 
		LIMIT $1 OFFSET $2
	`
	rows, err = database.Pool.Query(ctx, query, limit, offset)

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to fetch messages"})
	}
	defer rows.Close()

	messages := []domain.Message{}
	for rows.Next() {
		var m domain.Message
		// We map waba_id to TenantWabaID and alias to TenantAlias
		if err := rows.Scan(&m.ID, &m.TenantWabaID, &m.TenantAlias, &m.Wamid, &m.Type, &m.Direction, &m.Status, &m.Content, &m.MediaURL, &m.SenderPhone, &m.CreatedAt); err != nil {
			return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to scan message"})
		}
		messages = append(messages, m)
	}

	return c.JSON(messages)
}
