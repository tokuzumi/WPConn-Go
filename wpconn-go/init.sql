-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tenants Table (Must be created first)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    waba_id VARCHAR(255) NOT NULL,
    phone_number_id VARCHAR(255) UNIQUE NOT NULL,
    token TEXT NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    webhook_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    wamid VARCHAR(255) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    direction VARCHAR(20) NOT NULL, -- inbound, outbound
    status VARCHAR(50) DEFAULT 'pending',
    content TEXT,
    media_url TEXT,
    meta_media_id VARCHAR(255),
    sender_phone VARCHAR(50),
    reply_to_wamid VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id),
    action VARCHAR(255) NOT NULL,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users Table (Dashboard)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_messages_wamid ON messages(wamid);
CREATE INDEX IF NOT EXISTS idx_messages_tenant_id ON messages(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tenants_phone_number_id ON tenants(phone_number_id);
CREATE INDEX IF NOT EXISTS idx_tenants_api_key ON tenants(api_key);
