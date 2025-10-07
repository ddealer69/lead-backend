# Leads Management API

This API provides comprehensive LinkedIn lead management with profile enrichment using Apify API integration.

## Features

- Create and manage LinkedIn leads
- Automatic profile enrichment using Apify
- Batch processing capabilities
- Integration with search query results
- Status tracking and progress monitoring
- Rich profile data extraction

## Environment Variables Required

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
APIFY_API_TOKEN=your_apify_api_token
```

## Database Tables

### leads
Stores lead information and enrichment status.

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
Enriches a lead's profile using Apify LinkedIn scraper.

```http
POST /api/leads/{lead_id}/enrich
```

**Response:**
```json
{
    "success": true,
    "message": "Lead enriched successfully",
    "lead": {
        "id": "uuid",
        "first_name": "John",
        "last_name": "Doe",
        "title": "Senior Software Engineer",
        "company_name": "Tech Corp",
        "location": "San Francisco Bay Area",
        "enrichment_status": "completed",
        "is_enriched": true,
        "enriched_data": {
            "firstName": "John",
            "lastName": "Doe",
            "headline": "Senior Software Engineer at Tech Corp",
            "company": "Tech Corp",
            "location": "San Francisco Bay Area",
            "summary": "Experienced software engineer...",
            "experience": [...],
            "education": [...],
            "skills": [...]
        },
        "last_enriched_at": "2024-01-01T12:05:00Z"
    }
}
```

#### Bulk Enrich Leads
Enriches multiple leads in a single batch operation.

```http
POST /api/leads/bulk-enrich
Content-Type: application/json

{
    "lead_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Batch enrichment completed for 3 leads",
    "results": [
        {
            "id": "uuid1",
            "enrichment_status": "completed",
            "is_enriched": true
        }
    ]
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

### Lead Fields
- `profile_url`: LinkedIn profile URL (required)
- `first_name`: Lead's first name
- `last_name`: Lead's last name  
- `title`: Current job title/headline
- `company_name`: Current company
- `location`: Geographic location
- `notes`: Additional notes or context
- `enrichment_status`: Current enrichment status
- `is_enriched`: Boolean indicating if profile is enriched
- `enriched_data`: Full enriched profile data from Apify
- `apify_actor_run_id`: Apify run ID for tracking

### Enrichment Status Values
- `pending`: Not yet enriched
- `running`: Currently being enriched
- `completed`: Successfully enriched
- `failed`: Enrichment failed

## Enriched Data Structure

The `enriched_data` field contains comprehensive LinkedIn profile information:

```json
{
    "firstName": "John",
    "lastName": "Doe", 
    "headline": "Senior Software Engineer at Tech Corp",
    "company": "Tech Corp",
    "location": "San Francisco Bay Area",
    "summary": "Experienced software engineer with 8+ years...",
    "experience": [
        {
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "startDate": "2020-01",
            "endDate": "Present",
            "description": "Lead development of..."
        }
    ],
    "education": [
        {
            "school": "University of California, Berkeley",
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "startYear": 2012,
            "endYear": 2016
        }
    ],
    "skills": ["JavaScript", "Python", "React", "Node.js"],
    "certifications": [...],
    "languages": [...],
    "volunteerExperience": [...]
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

## Rate Limiting & Processing

### Apify Integration
- Uses Apify LinkedIn Profile Scraper actor
- Supports batch processing of multiple profiles
- Automatic retry logic for failed enrichments
- Respects Apify API rate limits

### Processing Times
- Single lead enrichment: 30-60 seconds
- Batch enrichment: 2-10 minutes (depending on size)
- Maximum wait time: 5 minutes (single), 10 minutes (batch)

## Example Usage Flow

1. **Create Lead**: Add a LinkedIn profile to track
2. **Enrich Profile**: Get detailed profile information
3. **Review Data**: Access enriched profile data
4. **Bulk Operations**: Process multiple leads efficiently

```bash
# 1. Create a lead
curl -X POST http://localhost:5000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "123e4567-e89b-12d3-a456-426614174000",
    "company_id": "987fcdeb-51a2-43d1-9c45-123456789abc",
    "created_by": "456e7890-e89b-12d3-a456-426614174111", 
    "profile_url": "https://linkedin.com/in/johndoe",
    "notes": "Potential senior engineer candidate"
  }'

# 2. Enrich the lead (using returned lead ID)
curl -X POST http://localhost:5000/api/leads/lead-uuid/enrich

# 3. Get enriched lead data
curl http://localhost:5000/api/leads/lead-uuid

# 4. Create leads from search results
curl -X POST http://localhost:5000/api/leads/from-search/query-uuid \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "123e4567-e89b-12d3-a456-426614174000",
    "company_id": "987fcdeb-51a2-43d1-9c45-123456789abc",
    "created_by": "456e7890-e89b-12d3-a456-426614174111"
  }'

# 5. Bulk enrich multiple leads
curl -X POST http://localhost:5000/api/leads/bulk-enrich \
  -H "Content-Type: application/json" \
  -d '{
    "lead_ids": ["uuid1", "uuid2", "uuid3"]
  }'
```