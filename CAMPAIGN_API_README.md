# Campaign Management API

This API provides comprehensive email campaign management with support for campaign leads, bulk operations, and detailed statistics.

## Features

- Create and manage email campaigns with templates and scheduling
- Campaign lead management with status tracking
- Bulk operations for efficient campaign lead creation
- Real-time campaign statistics and analytics
- Integration with existing query and user management systems
- Support for multiple campaign types and SMTP configurations

## Environment Variables Required

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

## Database Tables

### campaigns
Stores campaign information with the following key fields:
- `id`: Campaign UUID (auto-generated)
- `account_id`: Associated account UUID
- `company_id`: Associated company UUID
- `company_banner_id`: Optional company banner reference
- `name`: Campaign name
- `campaign_type`: email | linkedin_extension | other
- `created_by`: Creator user UUID
- `smtp_credential_id`: SMTP configuration reference
- `subject_template`: Email subject template
- `body_template`: Email body template
- `send_rate_per_hour`: Sending rate limit
- `max_retries`: Maximum retry attempts
- `status`: draft | running | paused | completed | cancelled

### campaign_leads
Stores individual campaign lead information:
- `id`: Campaign lead UUID (auto-generated)
- `campaign_id`: Associated campaign UUID
- `query_id`: Associated query UUID
- `status`: queued | sent | failed | bounced | opened | clicked | scheduled
- `send_attempts`: Number of send attempts
- `last_sent_at`: Timestamp of last send attempt
- `scheduled_at`: Scheduled send time
- `personalization_vars`: JSON variables for personalization
- `error`: Error message if failed

## API Endpoints

### Campaign Management

#### Create Campaign
```http
POST /api/campaigns
Content-Type: application/json

{
    "account_id": "uuid",
    "company_id": "uuid",
    "name": "Q4 Product Launch Campaign",
    "campaign_type": "email",
    "created_by": "uuid",
    "company_banner_id": "uuid",
    "smtp_credential_id": "uuid",
    "subject_template": "Exciting news about {{product_name}}!",
    "body_template": "Hello {{first_name}}, we're excited to announce...",
    "send_rate_per_hour": 100,
    "max_retries": 3,
    "status": "draft"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
    "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
    "name": "Q4 Product Launch Campaign",
    "campaign_type": "email",
    "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
    "subject_template": "Exciting news about our new product!",
    "body_template": "Hello {{first_name}}, we are excited to announce our latest innovation...",
    "send_rate_per_hour": 50,
    "max_retries": 3,
    "status": "draft"
  }'
```

**Success Response:**
```json
{
    "success": true,
    "message": "Campaign created successfully",
    "campaign": {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
        "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
        "name": "Q4 Product Launch Campaign",
        "campaign_type": "email",
        "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
        "subject_template": "Exciting news about our new product!",
        "body_template": "Hello {{first_name}}, we are excited to announce our latest innovation...",
        "send_rate_per_hour": 50,
        "max_retries": 3,
        "status": "draft",
        "created_at": "2025-10-08T14:30:00Z",
        "updated_at": "2025-10-08T14:30:00Z"
    }
}
```

#### Get Campaign
```http
GET /api/campaigns/{campaign_id}
```

**Example Request:**
```bash
curl http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

#### Update Campaign
```http
PUT /api/campaigns/{campaign_id}
Content-Type: application/json

{
    "name": "Updated Campaign Name",
    "status": "running",
    "send_rate_per_hour": 75
}
```

**Example Request:**
```bash
curl -X PUT http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "running",
    "send_rate_per_hour": 75
  }'
```

#### Delete Campaign
```http
DELETE /api/campaigns/{campaign_id}
```

**Example Request:**
```bash
curl -X DELETE http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

#### Get Campaigns by Company
```http
GET /api/campaigns/companies/{company_id}
GET /api/campaigns/companies/{company_id}?status=running
```

**Example Request:**
```bash
curl http://localhost:3000/api/campaigns/companies/9302e04a-d558-4e9c-b4ae-548c8146082a
curl http://localhost:3000/api/campaigns/companies/9302e04a-d558-4e9c-b4ae-548c8146082a?status=running
```

#### Get Campaigns by Account
```http
GET /api/campaigns/accounts/{account_id}
GET /api/campaigns/accounts/{account_id}?status=draft
```

### Campaign Lead Management

#### Create Campaign Lead
```http
POST /api/campaign-leads
Content-Type: application/json

{
    "campaign_id": "uuid",
    "query_id": "uuid",
    "status": "queued",
    "send_attempts": 0,
    "scheduled_at": "2025-10-08T15:00:00Z",
    "personalization_vars": {
        "first_name": "John",
        "company_name": "Tech Corp",
        "product_name": "AI Assistant"
    }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/campaign-leads \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
    "status": "scheduled",
    "scheduled_at": "2025-10-08T15:00:00Z",
    "personalization_vars": {
        "first_name": "John",
        "company_name": "Tech Corp",
        "product_name": "AI Assistant"
    }
  }'
```

**Success Response:**
```json
{
    "success": true,
    "message": "Campaign lead created successfully",
    "campaign_lead": {
        "id": "b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6",
        "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
        "status": "scheduled",
        "send_attempts": 0,
        "scheduled_at": "2025-10-08T15:00:00Z",
        "personalization_vars": {
            "first_name": "John",
            "company_name": "Tech Corp",
            "product_name": "AI Assistant"
        },
        "created_at": "2025-10-08T14:30:00Z"
    }
}
```

#### Get Campaign Lead
```http
GET /api/campaign-leads/{campaign_lead_id}
```

#### Update Campaign Lead
```http
PUT /api/campaign-leads/{campaign_lead_id}
Content-Type: application/json

{
    "status": "sent",
    "send_attempts": 1,
    "last_sent_at": "2025-10-08T15:00:00Z"
}
```

#### Delete Campaign Lead
```http
DELETE /api/campaign-leads/{campaign_lead_id}
```

#### Get Campaign Leads by Campaign
```http
GET /api/campaign-leads/campaigns/{campaign_id}
GET /api/campaign-leads/campaigns/{campaign_id}?status=sent
```

**Example Request:**
```bash
curl http://localhost:3000/api/campaign-leads/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479
curl http://localhost:3000/api/campaign-leads/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479?status=queued
```

**Success Response:**
```json
{
    "success": true,
    "message": "Retrieved 25 campaign leads",
    "campaign_leads": [
        {
            "id": "b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6",
            "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
            "status": "sent",
            "send_attempts": 1,
            "last_sent_at": "2025-10-08T15:00:00Z",
            "personalization_vars": {
                "first_name": "John",
                "company_name": "Tech Corp"
            },
            "created_at": "2025-10-08T14:30:00Z"
        }
    ]
}
```

#### Get Campaign Leads by Query
```http
GET /api/campaign-leads/queries/{query_id}
```

### Bulk Operations

#### Bulk Create Campaign Leads
Create multiple campaign leads for a campaign in a single request.

```http
POST /api/campaign-leads/bulk
Content-Type: application/json

{
    "campaign_id": "uuid",
    "query_ids": ["uuid1", "uuid2", "uuid3"],
    "status": "queued",
    "scheduled_at": "2025-10-08T15:00:00Z"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/campaign-leads/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "query_ids": [
        "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
        "123e4567-e89b-12d3-a456-426614174000",
        "987fcdeb-51a2-43d1-9c45-123456789abc"
    ],
    "status": "scheduled",
    "scheduled_at": "2025-10-08T15:00:00Z"
  }'
```

**Success Response:**
```json
{
    "success": true,
    "message": "Bulk creation completed. 3 successful, 0 failed",
    "total_processed": 3,
    "successful": 3,
    "failed": 0,
    "results": [
        {
            "id": "b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6",
            "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
            "status": "scheduled"
        },
        {
            "id": "c2e3d4f5-g6h7-8i9j-0k1l-m2n3o4p5q6r7",
            "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "query_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "scheduled"
        },
        {
            "id": "d3f4e5g6-h7i8-9j0k-1l2m-n3o4p5q6r7s8",
            "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "query_id": "987fcdeb-51a2-43d1-9c45-123456789abc",
            "status": "scheduled"
        }
    ]
}
```

### Campaign Statistics

#### Get Campaign Statistics
```http
GET /api/campaigns/{campaign_id}/stats
```

**Example Request:**
```bash
curl http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479/stats
```

**Success Response:**
```json
{
    "success": true,
    "message": "Campaign statistics retrieved successfully",
    "stats": {
        "total_leads": 100,
        "queued": 25,
        "sent": 60,
        "failed": 5,
        "bounced": 3,
        "opened": 45,
        "clicked": 12,
        "scheduled": 7,
        "success_rate": 60.0,
        "failure_rate": 5.0,
        "bounce_rate": 3.0,
        "open_rate": 75.0,
        "click_rate": 20.0
    }
}
```

## Field Descriptions

### Campaign Fields
- `account_id`: UUID of the account (required)
- `company_id`: UUID of the company (required)
- `name`: Campaign name (required)
- `campaign_type`: Type of campaign - email, linkedin_extension, or other
- `created_by`: UUID of the user creating the campaign
- `company_banner_id`: UUID of company banner (optional)
- `smtp_credential_id`: UUID of SMTP configuration (optional)
- `subject_template`: Email subject template with variables
- `body_template`: Email body template with variables
- `send_rate_per_hour`: Maximum emails to send per hour
- `max_retries`: Maximum retry attempts for failed sends
- `status`: Campaign status - draft, running, paused, completed, cancelled

### Campaign Lead Fields
- `campaign_id`: UUID of the associated campaign (required)
- `query_id`: UUID of the associated query (required)
- `status`: Lead status - queued, sent, failed, bounced, opened, clicked, scheduled
- `send_attempts`: Number of send attempts made
- `last_sent_at`: Timestamp of last send attempt
- `scheduled_at`: Scheduled send time
- `personalization_vars`: JSON object with personalization variables
- `error`: Error message if send failed

## Status Values

### Campaign Status
- `draft`: Campaign is being created/edited
- `running`: Campaign is actively sending emails
- `paused`: Campaign is temporarily stopped
- `completed`: Campaign has finished sending all emails
- `cancelled`: Campaign was cancelled before completion

### Campaign Lead Status
- `queued`: Lead is waiting to be sent
- `sent`: Email was successfully sent
- `failed`: Email send failed
- `bounced`: Email bounced back
- `opened`: Recipient opened the email
- `clicked`: Recipient clicked a link in the email
- `scheduled`: Email is scheduled for future sending

## Template Variables

Campaign templates support variable substitution using `{{variable_name}}` syntax:

### Subject Template Example:
```
"Welcome to {{company_name}}, {{first_name}}!"
```

### Body Template Example:
```html
"Hello {{first_name}},

We're excited to welcome you to {{company_name}}! 

Our {{product_name}} can help you achieve {{goal}}.

Best regards,
{{sender_name}}"
```

### Personalization Variables:
```json
{
    "first_name": "John",
    "company_name": "Tech Corp",
    "product_name": "AI Assistant",
    "goal": "increased productivity",
    "sender_name": "Sarah Johnson"
}
```

## Error Responses

### Common Error Format:
```json
{
    "success": false,
    "message": "Error description",
    "campaign": null
}
```

### Validation Errors:

**Missing required fields:**
```json
{
    "success": false,
    "message": "Campaign name is required",
    "campaign": null
}
```

**Invalid campaign type:**
```json
{
    "success": false,
    "message": "Invalid campaign_type. Must be one of: email, linkedin_extension, other",
    "campaign": null
}
```

**Invalid status:**
```json
{
    "success": false,
    "message": "Invalid status. Must be one of: draft, running, paused, completed, cancelled",
    "campaign": null
}
```

**Resource not found:**
```json
{
    "success": false,
    "message": "Campaign not found",
    "campaign": null
}
```

**Duplicate campaign lead:**
```json
{
    "success": false,
    "message": "Campaign lead already exists for this campaign and query combination",
    "campaign_lead": null
}
```

## Complete Usage Examples

### Campaign Creation and Management Workflow

```bash
# Step 1: Create a new campaign
curl -X POST http://localhost:3000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
    "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
    "name": "Product Launch Campaign",
    "campaign_type": "email",
    "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
    "subject_template": "Introducing {{product_name}} - Perfect for {{company_name}}",
    "body_template": "Dear {{first_name}}, we are excited to introduce our latest product...",
    "send_rate_per_hour": 50,
    "status": "draft"
  }'

# Step 2: Add leads to the campaign (bulk operation)
curl -X POST http://localhost:3000/api/campaign-leads/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "query_ids": [
        "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
        "123e4567-e89b-12d3-a456-426614174000",
        "987fcdeb-51a2-43d1-9c45-123456789abc"
    ],
    "status": "queued"
  }'

# Step 3: Start the campaign
curl -X PUT http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "running"
  }'

# Step 4: Monitor campaign progress
curl http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479/stats

# Step 5: View campaign leads
curl http://localhost:3000/api/campaign-leads/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479

# Step 6: Update individual lead status (e.g., after email is sent)
curl -X PUT http://localhost:3000/api/campaign-leads/b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "sent",
    "send_attempts": 1,
    "last_sent_at": "2025-10-08T15:30:00Z"
  }'
```

### Query Campaign Performance

```bash
# Get all campaigns for a company
curl http://localhost:3000/api/campaigns/companies/9302e04a-d558-4e9c-b4ae-548c8146082a

# Get only running campaigns
curl http://localhost:3000/api/campaigns/companies/9302e04a-d558-4e9c-b4ae-548c8146082a?status=running

# Get detailed campaign statistics
curl http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479/stats

# Get campaign leads by status
curl http://localhost:3000/api/campaign-leads/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479?status=sent
curl http://localhost:3000/api/campaign-leads/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479?status=failed
```

### Campaign Lead Management

```bash
# Create individual campaign lead with personalization
curl -X POST http://localhost:3000/api/campaign-leads \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "query_id": "new-query-uuid",
    "status": "scheduled",
    "scheduled_at": "2025-10-08T16:00:00Z",
    "personalization_vars": {
        "first_name": "Jane",
        "company_name": "Startup Inc",
        "product_name": "Growth Platform",
        "sender_name": "Mike Wilson"
    }
  }'

# Update lead after email interaction
curl -X PUT http://localhost:3000/api/campaign-leads/b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "opened",
    "personalization_vars": {
        "first_name": "Jane",
        "company_name": "Startup Inc",
        "last_interaction": "email_opened"
    }
  }'

# Handle failed email
curl -X PUT http://localhost:3000/api/campaign-leads/c2e3d4f5-g6h7-8i9j-0k1l-m2n3o4p5q6r7 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "failed",
    "send_attempts": 3,
    "error": "SMTP connection timeout after 3 retries"
  }'
```

## Integration Notes

- **Campaign Types**: Support for email campaigns with future extensibility for LinkedIn and other platforms
- **Template System**: Flexible variable substitution for personalized messaging
- **Rate Limiting**: Built-in support for send rate limiting to respect SMTP provider limits
- **Retry Logic**: Configurable retry attempts for failed email sends
- **Statistics**: Real-time campaign performance metrics and analytics
- **Bulk Operations**: Efficient handling of large campaign lead datasets
- **Status Tracking**: Comprehensive status tracking from queued to delivered and beyond
- **Error Handling**: Detailed error reporting for troubleshooting failed sends

## Technical Details

### Database Relationships
- Campaigns belong to accounts and companies
- Campaign leads link campaigns to queries with a unique constraint
- Foreign key constraints ensure data integrity
- Cascade deletes maintain consistency

### Performance Optimizations
- Indexed on frequently queried fields (account_id, company_id, status)
- Bulk operations minimize database round trips
- Efficient querying with status filters

### Security Features
- Account and company validation before operations
- User existence verification for created_by fields
- Input validation for all status fields and enums