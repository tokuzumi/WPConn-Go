package activities

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"wpconn-go/internal/database"
	"wpconn-go/internal/domain"
)

type Activities struct{}

func (a *Activities) SaveMessage(ctx context.Context, msg domain.Message) error {
	log.Printf("Saving message: %s", msg.Wamid)
	
	query := `
		INSERT INTO messages (id, tenant_id, wamid, type, direction, status, content, media_url, meta_media_id, reply_to_wamid, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
		ON CONFLICT (wamid) DO NOTHING
	`
	
	// Ensure ID is generated if empty (though usually DB handles it or we generate before)
	// For now assuming ID might be empty and DB generates it, but we are passing $1.
	// Let's generate a UUID if empty or let Postgres handle it if we pass DEFAULT.
	// But pgx requires matching args.
	// Better: Let's assume the Workflow or Handler assigns a UUID, OR we let DB handle it.
	// If we let DB handle it, we shouldn't pass $1 for ID unless we generated it.
	// Let's generate one here if missing, or use "DEFAULT" in query.
	// Simpler: Use named args or just generate one.
	// Since domain.Message has ID string, let's assume it's set. If not, we generate.
	
	// Actually, for idempotency, it's better if the ID is deterministic or we rely on WAMID.
	// Let's use WAMID as the key for logic, but ID for DB.
	// We'll use a placeholder UUID if empty, or better, let's change query to use DEFAULT for ID if empty.
	// But standard SQL doesn't support "value or default" easily in VALUES.
	// Let's just generate a random UUID here if needed.
	
	if msg.ID == "" {
		// We need a UUID generator. For simplicity in this migration, let's rely on DB default
		// by modifying the query to exclude ID if we can, or just passing nil/default?
		// Postgres driver might not like empty string for UUID.
		// Let's use a raw query without ID and let DB generate it.
		query = `
			INSERT INTO messages (tenant_id, wamid, type, direction, status, content, media_url, meta_media_id, reply_to_wamid, created_at)
			VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
			ON CONFLICT (wamid) DO UPDATE SET status = EXCLUDED.status
			RETURNING id
		`
		var newID string
		err := database.Pool.QueryRow(ctx, query, 
			nil, // TenantID (nullable/placeholder for now if we don't have it yet)
			msg.Wamid, msg.Type, msg.Direction, msg.Status, msg.Content, msg.MediaURL, msg.MetaMediaID, msg.ReplyToWamid, time.Now(),
		).Scan(&newID)
		if err != nil {
			return fmt.Errorf("failed to insert message: %w", err)
		}
		// We might want to return the ID?
	} else {
		// If ID is provided
		_, err := database.Pool.Exec(ctx, query, msg.ID, msg.TenantID, msg.Wamid, msg.Type, msg.Direction, msg.Status, msg.Content, msg.MediaURL, msg.MetaMediaID, msg.ReplyToWamid, msg.CreatedAt)
		if err != nil {
			return fmt.Errorf("failed to save message: %w", err)
		}
	}

	return nil
}

func (a *Activities) ResolveMediaUrl(ctx context.Context, mediaID string, businessPhoneID string) (string, error) {
	log.Printf("Resolving media URL for ID: %s (Phone: %s)", mediaID, businessPhoneID)
	
	// Lookup Token from DB
	var metaToken string
	query := `SELECT token FROM tenants WHERE phone_number_id = $1 LIMIT 1`
	err := database.Pool.QueryRow(ctx, query, businessPhoneID).Scan(&metaToken)
	if err != nil {
		return "", fmt.Errorf("failed to get tenant token for phone %s: %w", businessPhoneID, err)
	}

	url := fmt.Sprintf("https://graph.facebook.com/v17.0/%s", mediaID)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+metaToken)

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("meta api error: %s - %s", resp.Status, string(body))
	}

	var result struct {
		URL string `json:"url"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	return result.URL, nil
}

func (a *Activities) UpdateMessage(ctx context.Context, wamid string, mediaURL string, status string) error {
	log.Printf("Updating message %s: status=%s", wamid, status)
	
	query := `
		UPDATE messages 
		SET media_url = $1, status = $2, updated_at = NOW()
		WHERE wamid = $3
	`
	_, err := database.Pool.Exec(ctx, query, mediaURL, status, wamid)
	if err != nil {
		return fmt.Errorf("failed to update message: %w", err)
	}
	return nil
}
