# Search Query Management API

This API provides comprehensive search query management with Google Custom Search API integration for LinkedIn profile discovery.

## Features

- Create and manage search queries
- Google Custom Search API integration
- Automatic result storage and processing
- Progress tracking and status management
- Deduplication support
- Batch processing capabilities

## Environment Variables Required

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_google_custom_search_engine_id
```

## Database Tables

### queries
Stores search query information and execution status.

### google_search_results  
Stores individual search results from Google Custom Search API.

## API Endpoints

### Search Query Management

#### Create Search Query
```http
POST /api/search/queries
Content-Type: application/json

{
    "account_id": "uuid",
    "company_id": "uuid", 
    "created_by": "uuid",
    "query_string": "site:linkedin.com/in/ software engineer",
    "name": "Software Engineers Search",
    "company_banner_id": "uuid",
    "pages_requested": 5,
    "dedupe_mode": "per_company",
    "notes": "Search for senior software engineers"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Search query created successfully",
    "query": {
        "id": "uuid",
        "account_id": "uuid",
        "company_id": "uuid",
        "name": "Software Engineers Search",
        "query_string": "site:linkedin.com/in/ software engineer",
        "pages_requested": 5,
        "pages_fetched": 0,
        "status": "pending",
        "created_at": "2024-01-01T12:00:00Z"
    }
}
```

#### Get Search Query
```http
GET /api/search/queries/{query_id}
```

#### Update Search Query
```http
PUT /api/search/queries/{query_id}
Content-Type: application/json

{
    "name": "Updated Search Name",
    "pages_requested": 10,
    "status": "paused"
}
```

#### Delete Search Query
```http
DELETE /api/search/queries/{query_id}
```

#### Get Queries by Account
```http
GET /api/search/accounts/{account_id}/queries
```

#### Get Queries by Company
```http
GET /api/search/companies/{company_id}/queries
```

### Search Execution

#### Process Search Query
Executes Google searches and stores results.

```http
POST /api/search/queries/{query_id}/process
```

**Response:**
```json
{
    "success": true,
    "message": "Query processed successfully. Saved 47 results across 5 pages",
    "query": {
        "id": "uuid",
        "status": "completed",
        "pages_fetched": 5,
        "finished_at": "2024-01-01T12:05:00Z"
    },
    "total_results_saved": 47
}
```

### Search Results Management

#### Get Search Results
```http
GET /api/search/queries/{query_id}/results
GET /api/search/queries/{query_id}/results?processed_only=true
```

**Response:**
```json
{
    "success": true,
    "message": "Retrieved 47 search results",
    "results": [
        {
            "id": "uuid",
            "query_id": "uuid",
            "page_number": 1,
            "position": 1,
            "title": "John Doe - Software Engineer at Tech Corp | LinkedIn",
            "link": "https://linkedin.com/in/johndoe",
            "snippet": "Experienced software engineer with 5+ years...",
            "is_processed": false,
            "created_at": "2024-01-01T12:01:00Z"
        }
    ]
}
```

#### Delete Search Results
```http
DELETE /api/search/queries/{query_id}/results
```

#### Mark Results as Processed
```http
POST /api/search/queries/{query_id}/results/mark-processed
```

## Query Parameters

### Dedupe Modes
- `per_query`: Deduplicate within single query only
- `per_company`: Deduplicate across all queries for a company  
- `per_account`: Deduplicate across all queries for an account

### Status Values
- `pending`: Query created but not yet executed
- `running`: Currently executing Google searches
- `paused`: Execution paused (can be resumed)
- `completed`: All requested pages processed successfully
- `failed`: Execution failed due to error

## Error Responses

```json
{
    "success": false,
    "message": "Error description",
    "query": null
}
```

## Rate Limiting

The Google Custom Search API has the following limits:
- 100 queries per day (free tier)
- 10,000 queries per day (paid tier)
- Maximum 10 results per query
- 1 second delay between requests to respect API limits

## Example Usage Flow

1. **Create Query**: Create a search query for LinkedIn profiles
2. **Process Query**: Execute the search and store results
3. **Get Results**: Retrieve stored search results
4. **Mark Processed**: Mark results as processed after use

```bash
# 1. Create search query
curl -X POST http://localhost:5000/api/search/queries \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "123e4567-e89b-12d3-a456-426614174000",
    "company_id": "987fcdeb-51a2-43d1-9c45-123456789abc", 
    "created_by": "456e7890-e89b-12d3-a456-426614174111",
    "query_string": "site:linkedin.com/in/ \"software engineer\" San Francisco",
    "name": "SF Software Engineers",
    "pages_requested": 3
  }'

# 2. Process the query (using returned query ID)
curl -X POST http://localhost:5000/api/search/queries/query-uuid/process

# 3. Get results
curl http://localhost:5000/api/search/queries/query-uuid/results

# 4. Mark as processed
curl -X POST http://localhost:5000/api/search/queries/query-uuid/results/mark-processed
```