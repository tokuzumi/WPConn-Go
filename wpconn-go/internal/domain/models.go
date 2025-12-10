package domain

import (
	"time"
)

// Tenant represents a client using the API.
type Tenant struct {
	ID            string    `json:"id" db:"id"`
	Alias         string    `json:"alias" db:"alias"`
	WabaID        string    `json:"waba_id" db:"waba_id"`
	PhoneNumberID string    `json:"phone_number_id" db:"phone_number_id"`
	Token         string    `json:"token" db:"token"`
	APIKey        string    `json:"api_key" db:"api_key"`
	WebhookURL    string    `json:"webhook_url" db:"webhook_url"`
	IsActive      bool      `json:"is_active" db:"is_active"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// Message represents a WhatsApp message (inbound or outbound).
type Message struct {
	ID           string    `json:"id" db:"id"`
	TenantID     string    `json:"tenant_id" db:"tenant_id"`        // Deprecated
	TenantWabaID string    `json:"waba_id" db:"waba_id"`            // New WABA Linkage
	TenantAlias  string    `json:"tenant_alias" db:"-"`             // Joined field for display
	Wamid        string    `json:"wamid" db:"wamid"`
	Type         string    `json:"type" db:"type"`         // text, image, video, etc.
	Direction    string    `json:"direction" db:"direction"` // inbound, outbound
	Status       string    `json:"status" db:"status"`       // sent, delivered, read, failed
	Content      string    `json:"content" db:"content"`
	MediaURL     string    `json:"media_url" db:"media_url"`
	MetaMediaID  string    `json:"meta_media_id" db:"meta_media_id"`
	ReplyToWamid string    `json:"reply_to_wamid" db:"reply_to_wamid"`
	SenderPhone  string    `json:"sender_phone" db:"sender_phone"`
	BusinessPhoneID string `json:"business_phone_id" db:"-"` // Still needed for Signal (if multiple phones per WABA)
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
}

// AuditLog tracks important system actions.
type AuditLog struct {
	ID        string    `json:"id" db:"id"`
	TenantID  *string   `json:"tenant_id" db:"tenant_id"` // Nullable
	Action    string    `json:"action" db:"action"`
	Details   string    `json:"details" db:"details"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// User represents a dashboard user.
type User struct {
	ID           string    `json:"id" db:"id"`
	Email        string    `json:"email" db:"email"`
	PasswordHash string    `json:"-" db:"password_hash"`
	Name         string    `json:"name" db:"name"`
	Role         string    `json:"role" db:"role"` // admin, user
	IsActive     bool      `json:"is_active" db:"is_active"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
}
