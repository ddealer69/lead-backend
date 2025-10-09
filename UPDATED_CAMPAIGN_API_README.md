# Updated Campaign Management API

This API provides comprehensive email campaign management with support for campaign leads, bulk operations, detailed statistics, and email delivery logging.

## Features

- Create and manage email campaigns with templates and scheduling
- Campaign lead management with automatic personalization from leads table
- Bulk operations for efficient campaign lead creation
- Real-time campaign statistics and analytics
- Email delivery event tracking and logging
- Integration with existing leads and user management systems
- Support for multiple campaign types and SMTP configurations
- Enhanced campaign lead retrieval by company and campaign

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
Stores individual campaign lead information with **automatic personalization**:
- `id`: Campaign lead UUID (auto-generated)
- `campaign_id`: Associated campaign UUID
- `query_id`: Associated lead UUID (references leads.id)
- `status`: queued | sent | failed | bounced | opened | clicked | scheduled
- `send_attempts`: Number of send attempts
- `last_sent_at`: Timestamp of last send attempt
- `scheduled_at`: Scheduled send time
- `personalization_vars`: **Auto-populated JSON** from leads table (source_link, full_name, source_name, title, company_name)
- `error`: Error message if failed

### email_delivery_logs
Tracks email delivery events and provider responses:
- `id`: Log entry UUID (auto-generated)
- `campaign_lead_id`: Associated campaign lead UUID
- `campaign_id`: Associated campaign UUID
- `smtp_credential_id`: SMTP configuration used
- `recipient`: Email recipient address
- `event_type`: delivered | bounced | open | click | complaint
- `provider_event`: JSON response from email provider
- `occurred_at`: Event timestamp

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
    "body_template": "Hello {{full_name}}, we're excited to announce...",
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
    "company_banner_id": "d70b795e-7041-495d-bc4c-2408bfdb7b48",
    "smtp_credential_id": "d4daf7f7-1374-4857-afc0-99d50259e444",
    "subject_template": "Exciting news about our new product!",
    "body_template": "Hello {{full_name}}, we are excited to announce our latest innovation...",
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
        "body_template": "Hello {{full_name}}, we are excited to announce our latest innovation...",
        "send_rate_per_hour": 50,
        "max_retries": 3,
        "status": "draft",
        "created_at": "2025-10-09T14:30:00Z",
        "updated_at": "2025-10-09T14:30:00Z"
    }
}
```

#### Get Campaign
```http
GET /api/campaigns/{campaign_id}
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

#### Delete Campaign
```http
DELETE /api/campaigns/{campaign_id}
```

#### Get Campaigns by Company
```http
GET /api/campaigns/companies/{company_id}
GET /api/campaigns/companies/{company_id}?status=running
```

#### Get Campaigns by Account
```http
GET /api/campaigns/accounts/{account_id}
GET /api/campaigns/accounts/{account_id}?status=draft
```

### Campaign Lead Management

#### Create Campaign Lead (with Auto-Personalization)
**NEW**: Automatically fetches personalization variables from leads table based on `query_id`.

```http
POST /api/campaign-leads
Content-Type: application/json

{
    "campaign_id": "uuid",
    "query_id": "uuid",  // Must exist in leads table
    "status": "queued",
    "send_attempts": 0,
    "scheduled_at": "2025-10-09T15:00:00Z"
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
    "scheduled_at": "2025-10-09T15:00:00Z"
  }'
```

**Success Response (with Auto-Personalization):**
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
        "scheduled_at": "2025-10-09T15:00:00Z",
        "personalization_vars": {
            "source_link": "https://linkedin.com/in/johndoe",
            "full_name": "John Doe",
            "source_name": "johndoe",
            "title": "Senior Software Engineer",
            "company_name": "Tech Corp"
        },
        "created_at": "2025-10-09T14:30:00Z"
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
    "last_sent_at": "2025-10-09T15:00:00Z"
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

#### **NEW**: Get Campaign Leads by Company
```http
GET /api/campaign-leads/companies/{company_id}
GET /api/campaign-leads/companies/{company_id}?status=queued
```

**Example Request:**
```bash
curl http://localhost:3000/api/campaign-leads/companies/9302e04a-d558-4e9c-b4ae-548c8146082a
curl http://localhost:3000/api/campaign-leads/companies/9302e04a-d558-4e9c-b4ae-548c8146082a?status=sent
```

#### Get Campaign Leads by Query/Lead
```http
GET /api/campaign-leads/queries/{query_id}
```

### Bulk Operations

#### Bulk Create Campaign Leads (with Auto-Personalization)
Create multiple campaign leads for a campaign in a single request. **NEW**: Automatically personalizes each lead.

```http
POST /api/campaign-leads/bulk
Content-Type: application/json

{
    "campaign_id": "uuid",
    "query_ids": ["uuid1", "uuid2", "uuid3"],  // Must exist in leads table
    "status": "queued",
    "scheduled_at": "2025-10-09T15:00:00Z"
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
    "scheduled_at": "2025-10-09T15:00:00Z"
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
            "status": "scheduled",
            "personalization_vars": {
                "source_link": "https://linkedin.com/in/johndoe",
                "full_name": "John Doe",
                "source_name": "johndoe",
                "title": "Senior Software Engineer",
                "company_name": "Tech Corp"
            }
        }
    ]
}
```

### Campaign Statistics

#### Get Campaign Statistics
```http
GET /api/campaigns/{campaign_id}/stats
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

### **NEW**: Email Delivery Logs Management

#### Create Email Delivery Log
```http
POST /api/email-delivery-logs
Content-Type: application/json

{
    "campaign_lead_id": "uuid",
    "campaign_id": "uuid",
    "smtp_credential_id": "uuid",
    "recipient": "john.doe@example.com",
    "event_type": "delivered",
    "provider_event": {
        "message_id": "msg_123",
        "status": "delivered",
        "timestamp": "2025-10-09T15:30:00Z"
    }
}
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/email-delivery-logs \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_lead_id": "b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6",
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "smtp_credential_id": "d4daf7f7-1374-4857-afc0-99d50259e444",
    "recipient": "john.doe@example.com",
    "event_type": "delivered",
    "provider_event": {
        "message_id": "msg_abc123",
        "status": "delivered",
        "delivery_time": "2025-10-09T15:30:00Z"
    }
  }'
```

#### Get Email Delivery Log
```http
GET /api/email-delivery-logs/{log_id}
```

#### Update Email Delivery Log
```http
PUT /api/email-delivery-logs/{log_id}
Content-Type: application/json

{
    "event_type": "open",
    "provider_event": {
        "opened_at": "2025-10-09T16:00:00Z",
        "user_agent": "Mozilla/5.0..."
    }
}
```

#### Delete Email Delivery Log
```http
DELETE /api/email-delivery-logs/{log_id}
```

#### Get Email Delivery Logs by Campaign
```http
GET /api/email-delivery-logs/campaigns/{campaign_id}
GET /api/email-delivery-logs/campaigns/{campaign_id}?event_type=delivered
```

#### Get Email Delivery Logs by Campaign Lead
```http
GET /api/email-delivery-logs/campaign-leads/{campaign_lead_id}
```

### **NEW**: Campaign Email Sending

#### Send Campaign Emails
Sends emails to all queued leads in a campaign using the configured SMTP credentials and templates.

```http
POST /api/campaigns/{campaign_id}/send-emails
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479/send-emails \
  -H "Content-Type: application/json"
```

**Success Response:**
```json
{
    "success": true,
    "message": "Campaign emails processed. 5 sent, 1 failed",
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "campaign_name": "Q4 Product Launch Campaign",
    "emails_sent": 5,
    "emails_failed": 1,
    "total_processed": 6,
    "results": [
        {
            "lead_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
            "email": "john.doe@example.com",
            "status": "sent",
            "subject": "John Doe, exciting news from Tech Corp"
        },
        {
            "lead_id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "jane.smith@example.com",
            "status": "sent",
            "subject": "Jane Smith, exciting news from Startup Inc"
        },
        {
            "lead_id": "987fcdeb-51a2-43d1-9c45-123456789abc",
            "email": null,
            "status": "failed",
            "error": "No email address available"
        }
    ]
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Campaign not found",
    "emails_sent": 0,
    "emails_failed": 0,
    "results": []
}
```

**Process Overview:**
1. **Campaign Validation**: Verifies campaign exists and is in sendable state (draft/running)
2. **SMTP Retrieval**: Fetches SMTP credentials and decrypts password
3. **Lead Processing**: Gets all queued campaign leads with their email details
4. **Email Validation**: Skips leads without valid email addresses (null, empty, or whitespace-only)
5. **Template Rendering**: Renders subject and body templates with personalization variables
6. **Email Sending**: Sends emails via SMTP and updates lead status to 'sent' or 'failed'
7. **Logging**: Creates email delivery logs for tracking
8. **Status Updates**: Updates campaign lead statuses automatically

## **NEW**: Enhanced Personalization System

### Automatic Personalization Variables

When creating campaign leads, the system automatically fetches and populates personalization variables from the leads table:

- `source_link`: LinkedIn profile URL
- `full_name`: Contact's full name
- `source_name`: LinkedIn username
- `title`: Job title/headline
- `company_name`: Current company

### Template Variable Usage

Use these variables in your campaign templates:

**Subject Template:**
```
"{{full_name}}, exciting opportunity at {{company_name}}"
```

**Body Template:**
```html
"Hello {{full_name}},

I noticed your work as {{title}} at {{company_name}} and wanted to reach out.

Your LinkedIn profile ({{source_link}}) shows impressive experience.

Best regards,
Sales Team"
```

### **NEW**: Email Sending Process

When you call the `/api/campaigns/{campaign_id}/send-emails` endpoint, the system:

1. **Validates Campaign**: Ensures campaign exists and is in 'draft' or 'running' status
2. **Retrieves SMTP Config**: Gets SMTP credentials and decrypts the password securely
3. **Fetches Queued Leads**: Gets all campaign leads with status 'queued'
4. **Email Validation**: Automatically skips leads with missing, null, empty, or whitespace-only email addresses
5. **Renders Templates**: Replaces template variables with actual lead data:
   - `{{full_name}}` or `{{name}}` → Lead's full name
   - `{{company_name}}` → Lead's company name
   - `{{email}}` → Lead's email address
   - Plus any custom personalization variables
6. **Sends Emails**: Uses SMTP to send personalized emails to valid email addresses only
7. **Updates Status**: Changes campaign lead status from 'queued' to 'sent' or 'failed'
8. **Creates Logs**: Generates email delivery logs for tracking

**Template Example:**
```html
<html>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>Hello {{full_name}}!</h2>
    <p>I noticed your role at {{company_name}} and wanted to connect.</p>
    <p>Your experience as {{title}} is impressive.</p>
    <p>Best regards,<br>Sales Team</p>
  </body>
</html>
```

**Rendered Output:**
```html
<html>
  <body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2>Hello John Doe!</h2>
    <p>I noticed your role at Tech Corp and wanted to connect.</p>
    <p>Your experience as Senior Software Engineer is impressive.</p>
    <p>Best regards,<br>Sales Team</p>
  </body>
</html>
```

## **NEW**: Email Delivery Event Tracking

### Supported Event Types

- `delivered`: Email successfully delivered to recipient
- `bounced`: Email bounced back (hard/soft bounce)
- `open`: Recipient opened the email
- `click`: Recipient clicked a link in the email
- `complaint`: Recipient marked email as spam

### Provider Event Data

The `provider_event` field stores the complete JSON response from your email service provider (SendGrid, Mailgun, etc.):

```json
{
    "message_id": "msg_abc123",
    "status": "delivered",
    "timestamp": "2025-10-09T15:30:00Z",
    "smtp_response": "250 OK",
    "delivery_delay": 1250,
    "bounce_reason": null
}
```

## Field Descriptions

### Campaign Lead Fields (Updated)
- `campaign_id`: UUID of the associated campaign (required)
- `query_id`: UUID of the associated lead from leads table (required)
- `status`: Lead status - queued, sent, failed, bounced, opened, clicked, scheduled
- `send_attempts`: Number of send attempts made
- `last_sent_at`: Timestamp of last send attempt
- `scheduled_at`: Scheduled send time
- `personalization_vars`: **Auto-populated** JSON object with lead details
- `error`: Error message if send failed

### Email Delivery Log Fields
- `campaign_lead_id`: UUID of the associated campaign lead
- `campaign_id`: UUID of the associated campaign
- `smtp_credential_id`: UUID of SMTP configuration used
- `recipient`: Email recipient address
- `event_type`: Type of delivery event
- `provider_event`: Complete JSON response from email provider
- `occurred_at`: When the event occurred

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

### Email Delivery Event Types
- `delivered`: Successfully delivered
- `bounced`: Delivery failed (bounced)
- `open`: Email was opened
- `click`: Link was clicked
- `complaint`: Marked as spam

## Error Responses

### Common Error Format:
```json
{
    "success": false,
    "message": "Error description",
    "data": null
}
```

### Lead Not Found Error:
```json
{
    "success": false,
    "message": "Lead not found for query_id",
    "campaign_lead": null
}
```

### Invalid Event Type Error:
```json
{
    "success": false,
    "message": "Invalid event_type. Must be one of: delivered, bounced, open, click, complaint",
    "email_delivery_log": null
}
```

## Complete Usage Examples

### Enhanced Campaign Creation and Management Workflow

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
    "smtp_credential_id": "d4daf7f7-1374-4857-afc0-99d50259e444",
    "subject_template": "{{full_name}}, exciting news from {{company_name}}",
    "body_template": "Hi {{full_name}}, your experience as {{title}} caught our attention...",
    "send_rate_per_hour": 50,
    "status": "draft"
  }'

# Step 2: Add leads to the campaign (auto-personalized)
curl -X POST http://localhost:3000/api/campaign-leads/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "query_ids": [
        "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
        "123e4567-e89b-12d3-a456-426614174000"
    ],
    "status": "queued"
  }'

# Step 3: Start the campaign
curl -X PUT http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479 \
  -H "Content-Type: application/json" \
  -d '{"status": "running"}'

# Step 4: Send emails to all queued leads (NEW!)
curl -X POST http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479/send-emails \
  -H "Content-Type: application/json"

# Step 5: Monitor campaign progress
curl http://localhost:3000/api/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479/stats

# Step 6: View campaign leads by company
curl http://localhost:3000/api/campaign-leads/companies/9302e04a-d558-4e9c-b4ae-548c8146082a

# Step 7: Check email delivery logs
curl http://localhost:3000/api/email-delivery-logs/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

### Email Delivery Tracking Workflow

```bash
# Track email delivery events
curl -X POST http://localhost:3000/api/email-delivery-logs \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_lead_id": "b1d2c3e4-f5g6-7h8i-9j0k-l1m2n3o4p5q6",
    "campaign_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "smtp_credential_id": "d4daf7f7-1374-4857-afc0-99d50259e444",
    "recipient": "john.doe@example.com",
    "event_type": "open",
    "provider_event": {
        "opened_at": "2025-10-09T16:00:00Z",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
  }'

# Get all delivery logs for a campaign
curl http://localhost:3000/api/email-delivery-logs/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479

# Get specific event types
curl http://localhost:3000/api/email-delivery-logs/campaigns/f47ac10b-58cc-4372-a567-0e02b2c3d479?event_type=open
```

## **NEW**: Key Improvements

1. **Auto-Personalization**: Campaign leads automatically fetch personalization data from leads table
2. **Enhanced Retrieval**: Get campaign leads by company ID for better organization
3. **Email Delivery Tracking**: Comprehensive logging of email delivery events
4. **Automated Email Sending**: Single endpoint to send all queued campaign emails with template rendering
5. **SMTP Integration**: Secure password decryption and multi-protocol SMTP support
6. **Template Rendering**: Dynamic variable replacement in subject and body templates
7. **Status Management**: Automatic campaign lead status updates after email sending
8. **Better Integration**: Seamless connection between leads, campaigns, and delivery tracking
9. **Improved Error Handling**: More descriptive error messages and validation
10. **Performance Optimizations**: Indexed queries and efficient bulk operations

## Integration Notes

- **Automatic Personalization**: No need to manually provide personalization variables
- **Lead Integration**: Campaign leads reference actual leads from the leads table
- **Email Tracking**: Complete delivery event lifecycle tracking
- **Bulk Operations**: Efficient handling of large campaign lead datasets
- **Company-Level Queries**: Easy retrieval of campaign leads by company
- **Real-time Statistics**: Live campaign performance metrics
- **Provider Integration**: Support for any email service provider webhook data
- **SMTP Security**: Encrypted password storage with secure decryption
- **Template Engine**: Dynamic variable replacement with fallback values
- **Email Sending**: Automatic SMTP protocol detection (SSL/TLS/Plain)
- **Email Validation**: Automatic skipping of leads without valid email addresses
- **Status Tracking**: Real-time campaign lead status updates
- **Error Handling**: Comprehensive error logging and status management

## Technical Details

### Database Relationships (Updated)
- Campaigns belong to accounts and companies
- Campaign leads link campaigns to leads table (not queries)
- Email delivery logs track events for campaign leads
- SMTP credentials store encrypted authentication data
- Foreign key constraints ensure data integrity
- Cascade deletes maintain consistency

### Performance Optimizations
- Indexed on frequently queried fields
- Bulk operations minimize database round trips
- Efficient personalization variable fetching
- Optimized campaign lead retrieval by company
- Batch email processing with status updates

### Security Features
- Account and company validation before operations
- Lead existence verification for campaign leads
- Input validation for all status fields and enums
- Encrypted SMTP password storage
- Secure password decryption for email sending
- Comprehensive error handling and logging

### Email Sending Features
- **Multi-Protocol SMTP**: Supports SSL (port 465), TLS (port 587), and plain (port 25)
- **Template Rendering**: Dynamic variable replacement with {{variable}} syntax
- **Email Validation**: Automatic skipping of leads with null, empty, or invalid email addresses
- **Error Recovery**: Individual lead error handling without stopping batch process
- **Status Management**: Automatic campaign lead status updates (queued → sent/failed)
- **Delivery Logging**: Comprehensive email delivery event tracking
- **Password Security**: Encrypted SMTP password storage with secure decryption