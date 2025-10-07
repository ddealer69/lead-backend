-- Multi-tenant Lead Management System Database Schema
-- Postgres-flavored SQL with UUID PKs, jsonb fields, and proper indexing
-- Generated from comprehensive schema specification

-- Enable UUID and case-insensitive text extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- 1. ACCOUNTS - Multi-tenant root table
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    plan VARCHAR(32) DEFAULT 'free',
    billing_info JSONB NULL,
    settings JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for accounts
CREATE UNIQUE INDEX idx_accounts_name ON accounts(name) WHERE is_active = TRUE;

-- 2. USERS - Account members and authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    email CITEXT NOT NULL,
    full_name TEXT,
    password_hash TEXT NULL,
    role VARCHAR(32) DEFAULT 'member',
    last_login TIMESTAMPTZ NULL,
    is_active BOOLEAN DEFAULT TRUE,
    prefs JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX idx_users_account_id ON users(account_id);
CREATE UNIQUE INDEX idx_users_account_email ON users(account_id, email) WHERE is_active = TRUE;

-- 3. COMPANIES - Companies/clients under an account
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    domain TEXT NULL,
    notes TEXT NULL,
    metadata JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for companies
CREATE INDEX idx_companies_account_id ON companies(account_id);
CREATE UNIQUE INDEX idx_companies_account_name ON companies(account_id, name) WHERE is_active = TRUE;

-- 4. COMPANY_BANNERS - Brand variants under a company
CREATE TABLE company_banners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    logo_url TEXT NULL,
    signature TEXT NULL,
    metadata JSONB NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for company_banners
CREATE INDEX idx_company_banners_company_id ON company_banners(company_id);
CREATE INDEX idx_company_banners_created_by ON company_banners(created_by);

-- 5. API_KEYS - Encrypted API keys storage
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    type VARCHAR(32) NOT NULL,
    display_name TEXT NULL,
    encrypted_key_ciphertext TEXT NOT NULL,
    scopes JSONB NULL,
    last_validated_at TIMESTAMPTZ NULL,
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for api_keys
CREATE INDEX idx_api_keys_account_type ON api_keys(account_id, type);
CREATE INDEX idx_api_keys_created_by ON api_keys(created_by);

-- 6. SMTP_CREDENTIALS - Email sender credentials
CREATE TABLE smtp_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    created_by UUID REFERENCES users(id),
    display_name TEXT NOT NULL,
    smtp_host TEXT NOT NULL,
    smtp_port INTEGER NOT NULL,
    username TEXT NOT NULL,
    encrypted_password_ciphertext TEXT NOT NULL,
    auth_type VARCHAR(16) DEFAULT 'plain',
    verified BOOLEAN DEFAULT FALSE,
    last_verified_at TIMESTAMPTZ NULL,
    rate_limit_per_hour INTEGER NULL,
    metadata JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for smtp_credentials
CREATE INDEX idx_smtp_credentials_account_id ON smtp_credentials(account_id);
CREATE INDEX idx_smtp_credentials_created_by ON smtp_credentials(created_by);

-- 7. QUERIES - LeadQuery runs (resumable)
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    company_banner_id UUID REFERENCES company_banners(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    name TEXT NULL,
    query_string TEXT NOT NULL,
    pages_requested INTEGER NOT NULL DEFAULT 1,
    pages_fetched INTEGER NOT NULL DEFAULT 0,
    next_page_start TEXT NULL,
    status VARCHAR(32) DEFAULT 'pending',
    locked_by TEXT NULL,
    locked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_run_at TIMESTAMPTZ NULL,
    finished_at TIMESTAMPTZ NULL,
    notes TEXT NULL,
    dedupe_mode VARCHAR(16) DEFAULT 'per_company',
    CONSTRAINT chk_queries_pages CHECK (pages_fetched >= 0 AND pages_fetched <= pages_requested)
);

-- Create indexes for queries
CREATE INDEX idx_queries_account_company_user ON queries(account_id, company_id, created_by);
CREATE INDEX idx_queries_status ON queries(status);
CREATE INDEX idx_queries_company_banner ON queries(company_banner_id);

-- 8. GOOGLE_SEARCH_RESULTS - Raw Google CSE results
CREATE TABLE google_search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    position INTEGER NOT NULL,
    title TEXT NULL,
    link TEXT NOT NULL,
    snippet TEXT NULL,
    raw_response JSONB NULL,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_processed BOOLEAN DEFAULT FALSE,
    unique_hash TEXT NULL
);

-- Create indexes for google_search_results
CREATE UNIQUE INDEX idx_google_results_query_page_pos ON google_search_results(query_id, page_number, position);
CREATE INDEX idx_google_results_processed ON google_search_results(is_processed);
CREATE INDEX idx_google_results_hash ON google_search_results(unique_hash);

-- 9. LEADS - Canonical enriched lead records
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    company_banner_id UUID REFERENCES company_banners(id) ON DELETE SET NULL,
    source_query_id UUID REFERENCES queries(id) ON DELETE SET NULL,
    google_result_id UUID REFERENCES google_search_results(id) ON DELETE SET NULL,
    source_link TEXT NOT NULL,
    source_username TEXT NULL,
    full_name TEXT NULL,
    title TEXT NULL,
    company_name TEXT NULL,
    email CITEXT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    location TEXT NULL,
    phone TEXT NULL,
    enrichment_status VARCHAR(32) DEFAULT 'pending',
    enrichment_payload JSONB NULL,
    enrichment_attempts INTEGER DEFAULT 0,
    last_enriched_at TIMESTAMPTZ NULL,
    lead_score NUMERIC(5,2) NULL,
    tags TEXT[] NULL,
    normalized_contact_hash TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_archived BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ NULL
);

-- Create indexes for leads
CREATE INDEX idx_leads_account_company_hash ON leads(account_id, company_id, normalized_contact_hash);
CREATE INDEX idx_leads_company_enrichment ON leads(company_id, enrichment_status);
CREATE INDEX idx_leads_source_query ON leads(source_query_id);
CREATE INDEX idx_leads_google_result ON leads(google_result_id);
CREATE INDEX idx_leads_email ON leads(email) WHERE email IS NOT NULL;
CREATE INDEX idx_leads_deleted ON leads(deleted_at) WHERE deleted_at IS NOT NULL;
-- Optional unique constraint for deduplication
CREATE UNIQUE INDEX idx_leads_company_dedupe ON leads(company_id, normalized_contact_hash) WHERE normalized_contact_hash IS NOT NULL AND deleted_at IS NULL;

-- 10. CAMPAIGNS - Email/LinkedIn/extension campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    company_banner_id UUID REFERENCES company_banners(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    campaign_type VARCHAR(32) DEFAULT 'email',
    created_by UUID REFERENCES users(id),
    smtp_credential_id UUID REFERENCES smtp_credentials(id) ON DELETE SET NULL,
    subject_template TEXT NULL,
    body_template TEXT NULL,
    send_rate_per_hour INTEGER NULL,
    max_retries INTEGER DEFAULT 3,
    status VARCHAR(32) DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ NULL,
    finished_at TIMESTAMPTZ NULL
);

-- Create indexes for campaigns
CREATE INDEX idx_campaigns_account_company_status ON campaigns(account_id, company_id, status);
CREATE INDEX idx_campaigns_smtp_credential ON campaigns(smtp_credential_id);
CREATE INDEX idx_campaigns_created_by ON campaigns(created_by);

-- 11. CAMPAIGN_LEADS - Junction table for campaigns and leads
CREATE TABLE campaign_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    status VARCHAR(32) DEFAULT 'queued',
    send_attempts INTEGER DEFAULT 0,
    last_sent_at TIMESTAMPTZ NULL,
    scheduled_at TIMESTAMPTZ NULL,
    personalization_vars JSONB NULL,
    error TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for campaign_leads
CREATE INDEX idx_campaign_leads_campaign ON campaign_leads(campaign_id);
CREATE INDEX idx_campaign_leads_lead ON campaign_leads(lead_id);
CREATE INDEX idx_campaign_leads_status ON campaign_leads(status);
CREATE UNIQUE INDEX idx_campaign_leads_unique ON campaign_leads(campaign_id, lead_id);

-- 12. LINKEDIN_EXTENSION_CAMPAIGNS - LinkedIn-specific campaign data
CREATE TABLE linkedin_extension_campaigns (
    campaign_id UUID PRIMARY KEY REFERENCES campaigns(id) ON DELETE CASCADE,
    extension_settings JSONB NULL,
    chrome_extension_id TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 13. SOCIAL_GENERATIONS - AI content generation requests/results
CREATE TABLE social_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    company_banner_id UUID REFERENCES company_banners(id) ON DELETE SET NULL,
    requested_by UUID REFERENCES users(id),
    platform VARCHAR(16) NOT NULL,
    query TEXT NOT NULL,
    include_past BOOLEAN DEFAULT FALSE,
    request_payload JSONB NULL,
    generated_posts JSONB NULL,
    status VARCHAR(32) DEFAULT 'pending',
    error TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL
);

-- Create indexes for social_generations
CREATE INDEX idx_social_generations_account_platform_status ON social_generations(account_id, platform, status);
CREATE INDEX idx_social_generations_company ON social_generations(company_id);
CREATE INDEX idx_social_generations_requested_by ON social_generations(requested_by);

-- 14. TASK_QUEUE - Background job queue
CREATE TABLE task_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE CASCADE,
    type VARCHAR(32) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(16) DEFAULT 'pending',
    priority INTEGER DEFAULT 10,
    attempts INTEGER DEFAULT 0,
    run_after TIMESTAMPTZ DEFAULT NOW(),
    locked_by TEXT NULL,
    locked_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ NULL
);

-- Create indexes for task_queue
CREATE INDEX idx_task_queue_status_run_after ON task_queue(status, run_after);
CREATE INDEX idx_task_queue_type ON task_queue(type);
CREATE INDEX idx_task_queue_locked ON task_queue(locked_by, locked_at);

-- 15. ACTIVITY_LOGS - Audit trail
CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type VARCHAR(32) NULL,
    resource_id UUID NULL,
    ip INET NULL,
    user_agent TEXT NULL,
    payload JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for activity_logs
CREATE INDEX idx_activity_logs_account ON activity_logs(account_id);
CREATE INDEX idx_activity_logs_user ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_resource ON activity_logs(resource_type, resource_id);
CREATE INDEX idx_activity_logs_created_at ON activity_logs(created_at);

-- 16. EMAIL_DELIVERY_LOGS - Email event tracking
CREATE TABLE email_delivery_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_lead_id UUID REFERENCES campaign_leads(id) ON DELETE SET NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    smtp_credential_id UUID REFERENCES smtp_credentials(id) ON DELETE SET NULL,
    recipient TEXT NULL,
    event_type VARCHAR(32) NOT NULL,
    provider_event JSONB NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for email_delivery_logs
CREATE INDEX idx_email_delivery_logs_campaign ON email_delivery_logs(campaign_id);
CREATE INDEX idx_email_delivery_logs_campaign_lead ON email_delivery_logs(campaign_lead_id);
CREATE INDEX idx_email_delivery_logs_event_type ON email_delivery_logs(event_type);
CREATE INDEX idx_email_delivery_logs_occurred_at ON email_delivery_logs(occurred_at);

-- 17. WEBHOOKS - User-registered webhooks
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    event_types TEXT[] NOT NULL,
    callback_url TEXT NOT NULL,
    encrypted_secret_ciphertext TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for webhooks
CREATE INDEX idx_webhooks_account ON webhooks(account_id);
CREATE INDEX idx_webhooks_active ON webhooks(is_active);

-- 18. TAGS - User-defined tags for leads
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for tags
CREATE INDEX idx_tags_account ON tags(account_id);
CREATE UNIQUE INDEX idx_tags_account_name ON tags(account_id, name);

-- 19. LEAD_TAGS - Junction table for leads and tags
CREATE TABLE lead_tags (
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (lead_id, tag_id)
);

-- Create indexes for lead_tags
CREATE INDEX idx_lead_tags_tag ON lead_tags(tag_id);

-- 20. DEDUPE_RULES - Deduplication strategies
CREATE TABLE dedupe_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    scope VARCHAR(16) NOT NULL DEFAULT 'per_company',
    fields TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for dedupe_rules
CREATE INDEX idx_dedupe_rules_account ON dedupe_rules(account_id);

-- Performance improvements: GIN indexes for JSONB and array columns
CREATE INDEX idx_api_keys_scopes_gin ON api_keys USING GIN (scopes);
CREATE INDEX idx_leads_enrichment_payload_gin ON leads USING GIN (enrichment_payload);
CREATE INDEX idx_social_generated_posts_gin ON social_generations USING GIN (generated_posts);
CREATE INDEX idx_leads_tags_gin ON leads USING GIN (tags);
CREATE INDEX idx_task_queue_payload_gin ON task_queue USING GIN (payload);

-- Additional composite indexes for common query patterns
CREATE INDEX idx_queries_user_status_pages ON queries(created_by, status, pages_fetched);
CREATE INDEX idx_queries_locked ON queries(locked_by, locked_at) WHERE locked_by IS NOT NULL;

-- Add update triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers to relevant tables
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_company_banners_updated_at BEFORE UPDATE ON company_banners FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_smtp_credentials_updated_at BEFORE UPDATE ON smtp_credentials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON queries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaign_leads_updated_at BEFORE UPDATE ON campaign_leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_linkedin_extension_campaigns_updated_at BEFORE UPDATE ON linkedin_extension_campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_task_queue_updated_at BEFORE UPDATE ON task_queue FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_webhooks_updated_at BEFORE UPDATE ON webhooks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add check constraints for enum-like values
ALTER TABLE accounts ADD CONSTRAINT chk_accounts_plan CHECK (plan IN ('free', 'pro', 'enterprise'));
ALTER TABLE users ADD CONSTRAINT chk_users_role CHECK (role IN ('owner', 'admin', 'member'));
ALTER TABLE api_keys ADD CONSTRAINT chk_api_keys_type CHECK (type IN ('google_cse', 'apify', 'gemini', 'linkedin_extension'));
ALTER TABLE smtp_credentials ADD CONSTRAINT chk_smtp_auth_type CHECK (auth_type IN ('plain', 'oauth2', 'app_password'));
ALTER TABLE queries ADD CONSTRAINT chk_queries_status CHECK (status IN ('pending', 'running', 'paused', 'completed', 'failed'));
ALTER TABLE queries ADD CONSTRAINT chk_queries_dedupe_mode CHECK (dedupe_mode IN ('per_query', 'per_company', 'per_account'));
ALTER TABLE leads ADD CONSTRAINT chk_leads_enrichment_status CHECK (enrichment_status IN ('pending', 'in_progress', 'enriched', 'failed'));
ALTER TABLE campaigns ADD CONSTRAINT chk_campaigns_type CHECK (campaign_type IN ('email', 'linkedin_extension', 'other'));
ALTER TABLE campaigns ADD CONSTRAINT chk_campaigns_status CHECK (status IN ('draft', 'running', 'paused', 'completed', 'cancelled'));
ALTER TABLE campaign_leads ADD CONSTRAINT chk_campaign_leads_status CHECK (status IN ('queued', 'sent', 'failed', 'bounced', 'opened', 'clicked', 'scheduled'));
ALTER TABLE social_generations ADD CONSTRAINT chk_social_platform CHECK (platform IN ('instagram', 'facebook', 'youtube', 'blog', 'linkedin'));
ALTER TABLE social_generations ADD CONSTRAINT chk_social_status CHECK (status IN ('pending', 'completed', 'failed'));
ALTER TABLE task_queue ADD CONSTRAINT chk_task_type CHECK (type IN ('fetch_google_page', 'apify_enrich', 'send_email', 'generate_social'));
ALTER TABLE task_queue ADD CONSTRAINT chk_task_status CHECK (status IN ('pending', 'running', 'failed', 'completed'));
ALTER TABLE email_delivery_logs ADD CONSTRAINT chk_email_event_type CHECK (event_type IN ('delivered', 'bounced', 'open', 'click', 'complaint'));
ALTER TABLE dedupe_rules ADD CONSTRAINT chk_dedupe_scope CHECK (scope IN ('per_query', 'per_company', 'per_account'));

-- Add comments for documentation
COMMENT ON TABLE accounts IS 'Multi-tenant root table - all business data belongs to an account';
COMMENT ON TABLE users IS 'Account members with authentication and role-based access';
COMMENT ON TABLE companies IS 'Companies/clients managed under an account';
COMMENT ON TABLE company_banners IS 'Brand variants for each company (logos, signatures, etc.)';
COMMENT ON TABLE api_keys IS 'Encrypted storage for external API keys (Google, Apify, Gemini, etc.)';
COMMENT ON TABLE smtp_credentials IS 'Email sending credentials with rate limiting and verification';
COMMENT ON TABLE queries IS 'Lead query runs with resumable pagination support';
COMMENT ON TABLE google_search_results IS 'Raw Google Custom Search results for each query page';
COMMENT ON TABLE leads IS 'Enriched lead records with deduplication and scoring';
COMMENT ON TABLE campaigns IS 'Email and LinkedIn outreach campaigns';
COMMENT ON TABLE campaign_leads IS 'Junction table tracking campaign delivery to specific leads';
COMMENT ON TABLE linkedin_extension_campaigns IS 'Additional configuration for LinkedIn extension campaigns';
COMMENT ON TABLE social_generations IS 'AI-generated social media content requests and results';
COMMENT ON TABLE task_queue IS 'Background job queue for async operations (fetch, enrich, send)';
COMMENT ON TABLE activity_logs IS 'Audit trail for compliance and debugging';
COMMENT ON TABLE email_delivery_logs IS 'Email delivery events from webhook providers';
COMMENT ON TABLE webhooks IS 'User-configured webhooks for real-time notifications';
COMMENT ON TABLE tags IS 'User-defined tags for lead organization';
COMMENT ON TABLE lead_tags IS 'Many-to-many relationship between leads and tags';
COMMENT ON TABLE dedupe_rules IS 'Configurable deduplication strategies per account';

-- Security notes: All sensitive fields are stored as ciphertext
COMMENT ON COLUMN api_keys.encrypted_key_ciphertext IS 'Ciphertext from KMS encryption - decrypt only when needed';
COMMENT ON COLUMN smtp_credentials.encrypted_password_ciphertext IS 'Ciphertext from KMS encryption - decrypt only when needed';
COMMENT ON COLUMN webhooks.encrypted_secret_ciphertext IS 'Ciphertext for HMAC verification - decrypt with KMS';
COMMENT ON TABLE queries IS 'Lead query runs with atomic locking via locked_by/locked_at pattern';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES FOR MULTI-TENANT ISOLATION
-- ============================================================================

-- Enable RLS on all business tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_banners ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE smtp_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE google_search_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE dedupe_rules ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for account isolation
-- Set app.current_account_id in your application connection before queries

CREATE POLICY users_account_isolation ON users
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY companies_account_isolation ON companies
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY company_banners_account_isolation ON company_banners
  USING (company_id IN (
    SELECT id FROM companies WHERE account_id = current_setting('app.current_account_id', true)::uuid
  ));

CREATE POLICY api_keys_account_isolation ON api_keys
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY smtp_credentials_account_isolation ON smtp_credentials
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY queries_account_isolation ON queries
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY google_search_results_account_isolation ON google_search_results
  USING (query_id IN (
    SELECT id FROM queries WHERE account_id = current_setting('app.current_account_id', true)::uuid
  ));

CREATE POLICY leads_account_isolation ON leads
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY campaigns_account_isolation ON campaigns
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY campaign_leads_account_isolation ON campaign_leads
  USING (campaign_id IN (
    SELECT id FROM campaigns WHERE account_id = current_setting('app.current_account_id', true)::uuid
  ));

CREATE POLICY social_generations_account_isolation ON social_generations
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY task_queue_account_isolation ON task_queue
  USING (account_id = current_setting('app.current_account_id', true)::uuid OR account_id IS NULL);

CREATE POLICY webhooks_account_isolation ON webhooks
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY tags_account_isolation ON tags
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

CREATE POLICY lead_tags_account_isolation ON lead_tags
  USING (lead_id IN (
    SELECT id FROM leads WHERE account_id = current_setting('app.current_account_id', true)::uuid
  ));

CREATE POLICY dedupe_rules_account_isolation ON dedupe_rules
  USING (account_id = current_setting('app.current_account_id', true)::uuid);

-- ============================================================================
-- HELPER FUNCTIONS FOR SAFE CONCURRENCY AND OPERATIONS
-- ============================================================================

-- Function to atomically claim a query for processing
CREATE OR REPLACE FUNCTION claim_query_for_processing(
  p_query_id UUID,
  p_worker_id TEXT
) RETURNS BOOLEAN AS $$
BEGIN
  UPDATE queries 
  SET locked_by = p_worker_id,
      locked_at = NOW(),
      updated_at = NOW()
  WHERE id = p_query_id 
    AND (locked_by IS NULL OR locked_at < NOW() - INTERVAL '1 hour')
    AND status IN ('pending', 'running');
    
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to release query lock
CREATE OR REPLACE FUNCTION release_query_lock(
  p_query_id UUID,
  p_worker_id TEXT
) RETURNS BOOLEAN AS $$
BEGIN
  UPDATE queries 
  SET locked_by = NULL,
      locked_at = NULL,
      updated_at = NOW()
  WHERE id = p_query_id AND locked_by = p_worker_id;
  
  RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to generate normalized contact hash for deduplication
CREATE OR REPLACE FUNCTION generate_contact_hash(
  p_email TEXT,
  p_source_link TEXT,
  p_full_name TEXT DEFAULT NULL
) RETURNS TEXT AS $$
BEGIN
  RETURN encode(
    digest(
      COALESCE(lower(trim(p_email)), '') || '|' ||
      COALESCE(lower(trim(p_source_link)), '') || '|' ||
      COALESCE(lower(trim(p_full_name)), ''),
      'sha256'
    ),
    'hex'
  );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- PARTITIONING SETUP FOR LARGE TABLES (Optional - uncomment if needed)
-- ============================================================================

-- Uncomment below if you expect very large datasets (millions of leads per company)

/*
-- Partition leads by account_id for better performance at scale
ALTER TABLE leads RENAME TO leads_template;

CREATE TABLE leads (LIKE leads_template INCLUDING ALL) PARTITION BY HASH (account_id);

-- Create initial partitions (adjust number based on expected accounts)
CREATE TABLE leads_p0 PARTITION OF leads FOR VALUES WITH (modulus 4, remainder 0);
CREATE TABLE leads_p1 PARTITION OF leads FOR VALUES WITH (modulus 4, remainder 1);  
CREATE TABLE leads_p2 PARTITION OF leads FOR VALUES WITH (modulus 4, remainder 2);
CREATE TABLE leads_p3 PARTITION OF leads FOR VALUES WITH (modulus 4, remainder 3);

DROP TABLE leads_template;
*/

-- ============================================================================
-- USAGE EXAMPLES AND SECURITY SETUP
-- ============================================================================

-- Example: How to set account context in your application
-- Execute this before running queries in your app:
-- SELECT set_config('app.current_account_id', 'your-account-uuid-here', false);

-- Example: Atomic query claim for worker
-- SELECT claim_query_for_processing('query-uuid', 'worker-instance-123');

-- Example: Generate contact hash for deduplication
-- SELECT generate_contact_hash('john@example.com', 'https://linkedin.com/in/john', 'John Doe');

-- ============================================================================
-- PERFORMANCE MONITORING VIEWS (Optional but recommended)
-- ============================================================================

CREATE VIEW query_performance_stats AS
SELECT 
  q.account_id,
  q.company_id,
  q.status,
  COUNT(*) as query_count,
  AVG(q.pages_fetched) as avg_pages_fetched,
  AVG(EXTRACT(EPOCH FROM (q.finished_at - q.created_at))/60) as avg_duration_minutes,
  COUNT(l.id) as total_leads_found
FROM queries q
LEFT JOIN leads l ON l.source_query_id = q.id
WHERE q.created_at >= NOW() - INTERVAL '30 days'
GROUP BY q.account_id, q.company_id, q.status;

CREATE VIEW email_campaign_metrics AS
SELECT 
  c.account_id,
  c.company_id,
  c.id as campaign_id,
  c.name as campaign_name,
  COUNT(cl.id) as total_recipients,
  COUNT(CASE WHEN cl.status = 'sent' THEN 1 END) as sent_count,
  COUNT(CASE WHEN cl.status = 'failed' THEN 1 END) as failed_count,
  COUNT(edl.id) FILTER (WHERE edl.event_type = 'open') as opens,
  COUNT(edl.id) FILTER (WHERE edl.event_type = 'click') as clicks
FROM campaigns c
LEFT JOIN campaign_leads cl ON cl.campaign_id = c.id
LEFT JOIN email_delivery_logs edl ON edl.campaign_lead_id = cl.id
WHERE c.created_at >= NOW() - INTERVAL '90 days'
GROUP BY c.account_id, c.company_id, c.id, c.name;

-- Grant appropriate permissions to application role
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_role;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_role;