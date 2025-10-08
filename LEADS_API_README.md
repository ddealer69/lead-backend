# Leads Management API

This API provides comprehensive LinkedIn lead management with profile enrichment using Apify API integration.

## Features

- Create and manage LinkedIn leads from Google search results
- Automatic profile enrichment using Apify LinkedIn scraper
- Batch processing capabilities for multiple leads
- Integration with search query results
- Real-time enrichment with comprehensive profile data
- Support for custom lead IDs and metadata

## Environment Variables Required

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
APIFY_API_TOKEN=your_apify_api_token
```

## Database Tables

### leads
Stores lead information and enrichment status with the following key fields:
- `id`: Lead UUID (auto-generated if not provided)
- `account_id`: Associated account UUID
- `company_id`: Associated company UUID
- `company_banner_id`: Optional company banner reference
- `source_query_id`: Optional search query reference
- `google_result_id`: Google search result reference
- `source_link`: LinkedIn profile URL
- `full_name`: Contact's full name
- `title`: Job title/headline
- `company_name`: Current company
- `enrichment_status`: pending | in_progress | enriched | failed
- `enrichment_payload`: Full JSON response from Apify

## API Endpoints

### Lead Management

#### Create Lead
```http
POST /api/leads
Content-Type: application/json

{
    "account_id": "uuid",
    "company_id": "uuid",
    "created_by": "uuid",
    "profile_url": "https://linkedin.com/in/johndoe",
    "source_query_id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "title": "Software Engineer",
    "company_name": "Tech Corp",
    "location": "San Francisco, CA",
    "notes": "Potential candidate for senior role"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Lead created successfully",
    "lead": {
        "id": "uuid",
        "account_id": "uuid",
        "company_id": "uuid",
        "profile_url": "https://linkedin.com/in/johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "title": "Software Engineer",
        "enrichment_status": "pending",
        "is_enriched": false,
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

#### Get Lead
```http
GET /api/leads/{lead_id}
```

#### Update Lead
```http
PUT /api/leads/{lead_id}
Content-Type: application/json

{
    "title": "Senior Software Engineer",
    "notes": "Updated role information"
}
```

#### Delete Lead
```http
DELETE /api/leads/{lead_id}
```

#### Get Leads by Account
```http
GET /api/leads/accounts/{account_id}
GET /api/leads/accounts/{account_id}?enriched_only=true
```

#### Get Leads by Company
```http
GET /api/leads/companies/{company_id}
GET /api/leads/companies/{company_id}?enriched_only=true
```

#### Get Leads by Query
```http
GET /api/leads/queries/{query_id}
```

### Lead Enrichment

#### Enrich Single Lead
Enriches a lead's profile using Apify LinkedIn scraper. Uses `google_result_id` to fetch LinkedIn URL from Google search results.

```http
POST /api/leads/{any_lead_id}/enrich
Content-Type: application/json

{
    "account_id": "uuid",
    "company_id": "uuid", 
    "created_by": "uuid",
    "company_banner_id": "uuid",     // Optional
    "source_query_id": "uuid",       // Optional
    "google_result_id": "uuid"       // Required - ID from google_search_results table
}
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/leads/new-lead-123/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
    "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
    "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
    "company_banner_id": "d70b795e-7041-495d-bc4c-2408bfdb7b48",
    "source_query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
    "google_result_id": "906a61d4-9e9b-44df-81a2-0d4b3d685d70"
  }'
```

**Success Response:**
```json
{
    "success": true,
    "message": "Lead created and enriched successfully",
    "lead": {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
        "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
        "company_banner_id": "d70b795e-7041-495d-bc4c-2408bfdb7b48",
        "source_query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
        "google_result_id": "906a61d4-9e9b-44df-81a2-0d4b3d685d70",
        "source_link": "https://linkedin.com/in/sarptecimer",
        "source_username": "sarptecimer",
        "full_name": "Sarp Tecimer",
        "title": "Cybersecurity Consultant, Advisor, Vendor and Channel Management Professional",
        "company_name": "Kafein Technology Solutions",
        "email": null,
        "location": "Istanbul, Türkiye",
        "enrichment_status": "enriched",
        "enrichment_payload": {
            "basic_info": {
                "fullname": "Sarp Tecimer",
                "headline": "Cybersecurity Consultant, Advisor, Vendor and Channel Management Professional",
                "current_company": "Kafein Technology Solutions",
                "location": {"full": "Istanbul, Türkiye"},
                "about": "Cyber security consultant...",
                "profile_url": "https://linkedin.com/in/sarptecimer"
            },
            "experience": [...],
            "education": [...],
            "skills": [...],
            "certifications": [...]
        },
        "last_enriched_at": "2025-10-08T12:31:11.376701+00:00",
        "created_at": "2025-10-08T12:31:11.77729+00:00"
    }
}
```

**Error Responses:**

Missing required fields:
```json
{
    "success": false,
    "message": "For non-existing leads, account_id, company_id, created_by, and google_result_id are required",
    "lead": null
}
```

Google result not found:
```json
{
    "success": false,
    "message": "No search result found for this google_result_id",
    "lead": null
}
```

Invalid LinkedIn URL:
```json
{
    "success": false,
    "message": "Search result does not contain a LinkedIn profile URL",
    "lead": null
}
```

Apify enrichment failed:
```json
{
    "success": false,
    "message": "Failed to run enrichment: [error details]",
    "lead": null
}
```

#### Bulk Enrich Leads
Enriches multiple leads in a single batch operation using multiple Google search result IDs.

```http
POST /api/leads/bulk-enrich
Content-Type: application/json

{
    "account_id": "uuid",
    "company_id": "uuid",
    "created_by": "uuid",
    "company_banner_id": "uuid",           // Optional
    "source_query_id": "uuid",             // Optional
    "google_result_ids": ["uuid1", "uuid2", "uuid3"]  // Required - Array of IDs
}
```

**Example Request:**
```bash
curl -X POST http://localhost:3000/api/leads/bulk-enrich \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
    "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
    "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
    "company_banner_id": "d70b795e-7041-495d-bc4c-2408bfdb7b48",
    "source_query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
    "google_result_ids": [
      "906a61d4-9e9b-44df-81a2-0d4b3d685d70",
      "123e4567-e89b-12d3-a456-426614174000",
      "987fcdeb-51a2-43d1-9c45-123456789abc"
    ]
  }'
```

**Success Response:**
```json
{
    "success": true,
    "message": "Bulk enrichment completed successfully. 3 leads processed, 2 successful, 1 failed",
    "leads_processed": 3,
    "leads_successful": 2,
    "leads_failed": 1,
    "leads": [
        {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "full_name": "John Doe",
            "title": "Software Engineer",
            "enrichment_status": "enriched",
            "google_result_id": "906a61d4-9e9b-44df-81a2-0d4b3d685d70"
        },
        {
            "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
            "full_name": "Jane Smith",
            "title": "Product Manager",
            "enrichment_status": "enriched",
            "google_result_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    ],
    "failed_results": [
        {
            "google_result_id": "987fcdeb-51a2-43d1-9c45-123456789abc",
            "error": "No search result found for this google_result_id"
        }
    ]
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "No google_result_ids provided",
    "leads_processed": 0,
    "leads_successful": 0,
    "leads_failed": 0,
    "leads": [],
    "failed_results": []
}
```

### Search Integration

#### Create Leads from Search Results
Automatically creates leads from Google search results containing LinkedIn profiles.

```http
POST /api/leads/from-search/{query_id}
Content-Type: application/json

{
    "account_id": "uuid",
    "company_id": "uuid", 
    "created_by": "uuid"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Created 15 leads from search results",
    "leads_created": 15,
    "leads": [
        {
            "id": "uuid",
            "profile_url": "https://linkedin.com/in/johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "source_query_id": "uuid"
        }
    ]
}
```

## Field Descriptions

### Request Fields
- `account_id`: UUID of the account (required)
- `company_id`: UUID of the company (required)
- `created_by`: UUID of the user creating the lead (required)
- `company_banner_id`: UUID of company banner (optional)
- `source_query_id`: UUID of originating search query (optional)
- `google_result_id`: UUID from google_search_results table (required for single enrichment)
- `google_result_ids`: Array of UUIDs from google_search_results table (required for bulk enrichment)

### Response Lead Fields
- `id`: Auto-generated UUID for the lead
- `source_link`: LinkedIn profile URL from Google search results
- `source_username`: LinkedIn username/public identifier
- `full_name`: Contact's full name from LinkedIn
- `title`: Current job title/headline from LinkedIn
- `company_name`: Current company from LinkedIn
- `email`: Email address (if public on LinkedIn)
- `location`: Geographic location from LinkedIn
- `enrichment_status`: Current enrichment status
- `enrichment_payload`: Complete JSON response from Apify
- `last_enriched_at`: Timestamp of last enrichment
- `created_at`: Lead creation timestamp

### Enrichment Status Values
- `pending`: Not yet enriched
- `in_progress`: Currently being enriched
- `enriched`: Successfully enriched
- `failed`: Enrichment failed

## Enriched Data Structure

The `enrichment_payload` field contains comprehensive LinkedIn profile information from Apify:

```json
{
    "basic_info": {
        "fullname": "Sarp Tecimer",
        "first_name": "Sarp",
        "last_name": "Tecimer",
        "headline": "Cybersecurity Consultant, Advisor, Vendor and Channel Management Professional",
        "public_identifier": "sarptecimer",
        "profile_url": "https://linkedin.com/in/sarptecimer",
        "profile_picture_url": "https://media.licdn.com/dms/image/...",
        "about": "Cyber security consultant with a base of business administration...",
        "location": {
            "country": "Türkiye",
            "city": "Istanbul", 
            "full": "Istanbul, Türkiye",
            "country_code": "TR"
        },
        "current_company": "Kafein Technology Solutions",
        "current_company_url": "https://www.linkedin.com/company/kafein-technology-solutions",
        "follower_count": 2018,
        "connection_count": 2010,
        "email": null,
        "is_premium": false,
        "is_creator": true,
        "creator_hashtags": ["compliance", "datasecurity", "itmanagement"]
    },
    "experience": [
        {
            "title": "Senior Product Owner",
            "company": "Kafein Technology Solutions",
            "location": "Istanbul, Türkiye",
            "description": "Building and managing product roadmaps...",
            "duration": "Jun 2024 - Oct 2025 · 1 yr 5 mos",
            "start_date": {"year": 2024, "month": "Jun"},
            "end_date": {"year": 2025, "month": "Oct"},
            "is_current": false,
            "employment_type": "Full-time",
            "location_type": "Hybrid",
            "company_linkedin_url": "https://www.linkedin.com/company/642741/",
            "company_logo_url": "https://media.licdn.com/dms/image/..."
        }
    ],
    "education": [
        {
            "school": "Bahcesehir University",
            "degree": "MBA., Yonetim Bilisim Sistemleri (MIS)",
            "degree_name": "MBA.",
            "field_of_study": "Yonetim Bilisim Sistemleri (MIS)",
            "duration": "2007 - 2008",
            "start_date": {"year": 2007},
            "end_date": {"year": 2008},
            "school_linkedin_url": "https://www.linkedin.com/company/31394/",
            "school_logo_url": "https://media.licdn.com/dms/image/..."
        }
    ],
    "skills": [
        "Relationship management",
        "security architecture", 
        "compliance",
        "training",
        "building new channels",
        "partner onboarding",
        "business development",
        "channel management"
    ],
    "certifications": [
        {
            "name": "BCNE",
            "issuer": "Brocade"
        },
        {
            "name": "Blue Coat Accredited Sales Professional",
            "issuer": "Blue Coat"
        }
    ],
    "languages": [
        {
            "language": "English",
            "proficiency": "Full professional proficiency"
        },
        {
            "language": "German", 
            "proficiency": "Elementary proficiency"
        }
    ],
    "projects": [
        {
            "name": "Bulutt Belbil",
            "description": "Modern city information system...",
            "associated_with": "Turk Telekom",
            "is_current": false
        }
    ]
}
```

## Error Responses

```json
{
    "success": false,
    "message": "Error description",
    "lead": null
}
```

## Technical Details

### Apify Integration
- Uses **apimaestro~linkedin-profile-detail** actor via synchronous API
- Endpoint: `https://api.apify.com/v2/acts/apimaestro~linkedin-profile-detail/run-sync-get-dataset-items`
- Real-time enrichment (no polling required)
- Comprehensive profile data extraction
- Automatic error handling and validation

### Processing Times
- Single lead enrichment: 10-30 seconds (synchronous)
- Bulk enrichment: 1-5 minutes (depending on batch size)
- No timeout issues - completes when ready

### Data Flow
1. **Input**: `google_result_id` from request payload
2. **Lookup**: Query `google_search_results` table for LinkedIn URL
3. **Validation**: Ensure URL is a valid LinkedIn profile
4. **Enrichment**: Send to Apify for profile scraping
5. **Storage**: Create lead record with enriched data
6. **Response**: Return complete lead object

## Complete Usage Examples

### Single Lead Enrichment Workflow

```bash
# Step 1: Enrich a single lead from Google search result
curl -X POST http://localhost:3000/api/leads/my-custom-lead-id/enrich \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
    "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a", 
    "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
    "company_banner_id": "d70b795e-7041-495d-bc4c-2408bfdb7b48",
    "source_query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
    "google_result_id": "906a61d4-9e9b-44df-81a2-0d4b3d685d70"
  }'

# Step 2: Get the enriched lead data
curl http://localhost:3000/api/leads/{returned_lead_uuid}
```

### Bulk Lead Enrichment Workflow

```bash
# Enrich multiple leads from Google search results
curl -X POST http://localhost:3000/api/leads/bulk-enrich \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "0cba4319-1bac-4399-a616-caf4367790fd",
    "company_id": "9302e04a-d558-4e9c-b4ae-548c8146082a",
    "created_by": "406f34af-9d1e-44d2-82c3-d910afe7fb5b",
    "company_banner_id": "d70b795e-7041-495d-bc4c-2408bfdb7b48",
    "source_query_id": "26b49b5a-4036-43f4-85a7-fdace10e3b0f",
    "google_result_ids": [
      "906a61d4-9e9b-44df-81a2-0d4b3d685d70",
      "123e4567-e89b-12d3-a456-426614174000",
      "987fcdeb-51a2-43d1-9c45-123456789abc",
      "456f7890-e12b-34c5-d678-901234567890"
    ]
  }'
```

### Query Existing Leads

```bash
# Get all leads for an account
curl http://localhost:3000/api/leads/accounts/0cba4319-1bac-4399-a616-caf4367790fd

# Get enriched leads only
curl http://localhost:3000/api/leads/accounts/0cba4319-1bac-4399-a616-caf4367790fd?enriched_only=true

# Get leads by company
curl http://localhost:3000/api/leads/companies/9302e04a-d558-4e9c-b4ae-548c8146082a

# Get specific lead
curl http://localhost:3000/api/leads/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

## Common Error Scenarios

### Invalid Google Result ID
```bash
curl -X POST http://localhost:3000/api/leads/test-lead/enrich \
  -H "Content-Type: application/json" \
  -d '{"account_id": "...", "google_result_id": "invalid-uuid"}'

# Response:
{
  "success": false,
  "message": "No search result found for this google_result_id",
  "lead": null
}
```

### Missing Required Fields
```bash
curl -X POST http://localhost:3000/api/leads/test-lead/enrich \
  -H "Content-Type: application/json" \
  -d '{"account_id": "..."}'

# Response:
{
  "success": false,
  "message": "For non-existing leads, account_id, company_id, created_by, and google_result_id are required",
  "lead": null
}
```

### Non-LinkedIn URL in Search Results
```bash
# If google_result_id points to non-LinkedIn URL
{
  "success": false,
  "message": "Search result does not contain a LinkedIn profile URL",
  "lead": null
}
```

## Integration Notes

- **Lead IDs**: Can be any string - system generates UUID if needed
- **Google Search Results**: Must exist in `google_search_results` table
- **Batch Processing**: Recommended for processing multiple leads efficiently
- **Error Handling**: Partial success supported in bulk operations
- **Data Persistence**: All enriched data stored in `enrichment_payload` field
- **Real-time**: Synchronous API provides immediate results