package handlers

import (
	"context"
	"fmt"
	"wpconn-go/internal/database"
	"wpconn-go/internal/domain"

	"github.com/gofiber/fiber/v3"
)

// GetLogs retrieves audit logs with filters
func GetLogs(c fiber.Ctx) error {
	limit := c.QueryInt("limit", 50)
	offset := c.QueryInt("offset", 0)
	event := c.Query("event")

	ctx := context.Background()
	query := "SELECT id, tenant_id, action, details, created_at FROM audit_logs WHERE 1=1"
	args := []interface{}{}
	argCount := 1

	if event != "" {
		query += fmt.Sprintf(" AND action = $%d", argCount)
		args = append(args, event)
		argCount++
	}

	query += fmt.Sprintf(" ORDER BY created_at DESC LIMIT $%d OFFSET $%d", argCount, argCount+1)
	args = append(args, limit, offset)

	rows, err := database.Pool.Query(ctx, query, args...)
	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{"error": "Failed to fetch logs"})
	}
	defer rows.Close()

	// Frontend expects: {id, event, detail, tenant_id, created_at}
	// Backend model AuditLog: {ID, Action, Details...}
	// We map them here.

	type LogResponse struct {
		ID        string `json:"id"`
		TenantID  string `json:"tenant_id,omitempty"`
		Event     string `json:"event"`
		Detail    string `json:"detail"`
		CreatedAt string `json:"created_at"`
	}

	var logs []LogResponse
	for rows.Next() {
		var l domain.AuditLog
		if err := rows.Scan(&l.ID, &l.TenantID, &l.Action, &l.Details, &l.CreatedAt); err != nil {
			continue
		}
		
		tid := ""
		if l.TenantID != nil {
			tid = *l.TenantID
		}

		logs = append(logs, LogResponse{
			ID:        l.ID,
			TenantID:  tid,
			Event:     l.Action,
			Detail:    l.Details,
			CreatedAt: l.CreatedAt.Format("2006-01-02T15:04:05Z"),
		})
	}

	if logs == nil {
		logs = []LogResponse{}
	}
	return c.JSON(logs)
}
