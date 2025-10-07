# Company Management System - API Documentation

Complete CRUD operations for managing companies and company banners within the multi-tenant lead management system.

## 🏗️ **System Architecture**

```
Account (Root)
    ├── Companies (Multiple per account)
    │   ├── Company Banner 1
    │   ├── Company Banner 2
    │   └── Company Banner N
    └── Other Companies...
```

## 📊 **Database Relationships**

```sql
accounts (1) ←→ (N) companies (1) ←→ (N) company_banners
```

- **accounts.id** → **companies.account_id** (Foreign Key)
- **companies.id** → **company_banners.company_id** (Foreign Key)
- **users.id** → **company_banners.created_by** (Foreign Key, Optional)

## 🚀 **Quick Start**

### **Prerequisites**
- Flask authentication system already running
- Valid account_id from accounts table
- Supabase credentials configured in `.env`

### **Base URL**: `http://localhost:5000`

---

## 📚 **Company Management API**

### **1. Create Company**
Create a new company under an existing account.

**Endpoint**: `POST /companies`

**Request Body**:
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Tech Solutions Inc",
  "domain": "techsolutions.com",
  "notes": "Main technology company",
  "metadata": {
    "industry": "Technology",
    "size": "Medium",
    "location": "San Francisco"
  }
}
```

**Required Fields**:
- `account_id`: UUID of the parent account
- `name`: Company name (must be unique per account)

**Optional Fields**:
- `domain`: Company website domain
- `notes`: Free text notes
- `metadata`: JSON object for additional data

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Company created successfully",
  "company": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Tech Solutions Inc",
    "domain": "techsolutions.com",
    "notes": "Main technology company",
    "metadata": {
      "industry": "Technology",
      "size": "Medium",
      "location": "San Francisco"
    },
    "is_active": true,
    "created_at": "2025-10-06T10:30:00Z",
    "updated_at": "2025-10-06T10:30:00Z"
  }
}
```

**Error Responses**:
```json
// Account not found (400)
{
  "success": false,
  "message": "Account not found or inactive",
  "company": null
}

// Duplicate company name (400)
{
  "success": false,
  "message": "Company with this name already exists for this account",
  "company": null
}
```

### **2. Get Company**
Retrieve company details by company ID.

**Endpoint**: `GET /companies/{company_id}`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Company retrieved successfully",
  "company": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Tech Solutions Inc",
    "domain": "techsolutions.com",
    "notes": "Main technology company",
    "metadata": {...},
    "is_active": true,
    "created_at": "2025-10-06T10:30:00Z",
    "updated_at": "2025-10-06T10:30:00Z"
  }
}
```

### **3. Update Company**
Update company information.

**Endpoint**: `PUT /companies/{company_id}`

**Request Body**:
```json
{
  "name": "Tech Solutions Corp",
  "domain": "techsolutionscorp.com",
  "notes": "Updated company description",
  "metadata": {
    "industry": "Technology & Consulting",
    "size": "Large"
  }
}
```

**Note**: All fields are optional. Only provided fields will be updated.

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Company updated successfully",
  "company": {
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "name": "Tech Solutions Corp",
    "domain": "techsolutionscorp.com",
    "notes": "Updated company description",
    "metadata": {
      "industry": "Technology & Consulting",
      "size": "Large"
    },
    "updated_at": "2025-10-06T11:00:00Z"
  }
}
```

### **4. Delete Company**
Soft delete a company (sets is_active = false).

**Endpoint**: `DELETE /companies/{company_id}`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Company and associated banners deleted successfully"
}
```

**Note**: This operation also soft-deletes all associated company banners.

### **5. Get All Companies by Account**
Retrieve all active companies for an account.

**Endpoint**: `GET /accounts/{account_id}/companies`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 3 companies",
  "companies": [
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "account_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Tech Solutions Inc",
      "domain": "techsolutions.com",
      "notes": "Main technology company",
      "metadata": {...},
      "is_active": true,
      "created_at": "2025-10-06T10:30:00Z",
      "updated_at": "2025-10-06T10:30:00Z"
    }
  ]
}
```

---

## 🎨 **Company Banner Management API**

### **1. Create Company Banner**
Create a new banner for an existing company.

**Endpoint**: `POST /company-banners`

**Request Body**:
```json
{
  "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "name": "Tech Solutions - Sales Banner",
  "logo_url": "https://example.com/logo.png",
  "signature": "Best regards,\nTech Solutions Sales Team\nwww.techsolutions.com",
  "metadata": {
    "purpose": "Sales campaigns",
    "department": "Sales"
  },
  "created_by": "user-uuid-here"
}
```

**Required Fields**:
- `company_id`: UUID of the parent company
- `name`: Banner name

**Optional Fields**:
- `logo_url`: URL to company logo
- `signature`: Email signature template
- `metadata`: JSON object for additional data
- `created_by`: UUID of the user creating the banner

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Company banner created successfully",
  "banner": {
    "id": "banner-uuid-here",
    "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "name": "Tech Solutions - Sales Banner",
    "logo_url": "https://example.com/logo.png",
    "signature": "Best regards,\nTech Solutions Sales Team\nwww.techsolutions.com",
    "metadata": {
      "purpose": "Sales campaigns",
      "department": "Sales"
    },
    "created_by": "user-uuid-here",
    "is_active": true,
    "created_at": "2025-10-06T10:35:00Z",
    "updated_at": "2025-10-06T10:35:00Z"
  }
}
```

### **2. Get Company Banner**
Retrieve banner details by banner ID.

**Endpoint**: `GET /company-banners/{banner_id}`

### **3. Update Company Banner**
Update banner information.

**Endpoint**: `PUT /company-banners/{banner_id}`

**Request Body**:
```json
{
  "name": "Updated Banner Name",
  "logo_url": "https://example.com/new-logo.png",
  "signature": "Updated signature",
  "metadata": {
    "updated_field": "new_value"
  }
}
```

### **4. Delete Company Banner**
Soft delete a banner.

**Endpoint**: `DELETE /company-banners/{banner_id}`

### **5. Get All Banners by Company**
Retrieve all active banners for a company.

**Endpoint**: `GET /companies/{company_id}/banners`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 2 banners",
  "banners": [
    {
      "id": "banner-uuid-1",
      "company_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "name": "Sales Banner",
      "logo_url": "https://example.com/logo.png",
      "signature": "Sales signature",
      "metadata": {...},
      "created_by": "user-uuid",
      "is_active": true,
      "created_at": "2025-10-06T10:35:00Z",
      "updated_at": "2025-10-06T10:35:00Z"
    }
  ]
}
```

---

## 🔄 **Combined Operations**

### **1. Get Account Companies with Banners**
Retrieve all companies and their banners for an account in one request.

**Endpoint**: `GET /accounts/{account_id}/companies-with-banners`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 2 companies with their banners",
  "data": {
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "companies": [
      {
        "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
        "name": "Tech Solutions Inc",
        "domain": "techsolutions.com",
        "notes": "Main technology company",
        "metadata": {...},
        "is_active": true,
        "created_at": "2025-10-06T10:30:00Z",
        "updated_at": "2025-10-06T10:30:00Z",
        "banners": [
          {
            "id": "banner-uuid-1",
            "name": "Sales Banner",
            "logo_url": "https://example.com/logo.png",
            "signature": "Sales signature",
            "metadata": {...},
            "created_by": "user-uuid",
            "is_active": true,
            "created_at": "2025-10-06T10:35:00Z"
          }
        ]
      }
    ],
    "total_companies": 2,
    "total_banners": 3
  }
}
```

### **2. Create Company with Banner**
Create a company and its first banner in one operation.

**Endpoint**: `POST /companies-with-banner`

**Request Body**:
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "company_name": "New Tech Company",
  "company_domain": "newtech.com",
  "company_notes": "Innovative tech startup",
  "company_metadata": {
    "industry": "AI/ML"
  },
  "banner_name": "Default Banner",
  "logo_url": "https://newtech.com/logo.png",
  "signature": "Best regards,\nNew Tech Team",
  "banner_metadata": {
    "type": "default"
  },
  "created_by": "user-uuid"
}
```

**Required Fields**:
- `account_id`: Parent account UUID
- `company_name`: Company name

**Optional Fields**:
- All company fields (domain, notes, metadata)
- All banner fields (banner_name defaults to company_name if not provided)

**Success Response (201)**:
```json
{
  "success": true,
  "message": "Company and banner created successfully",
  "company": {
    "id": "new-company-uuid",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "New Tech Company",
    "domain": "newtech.com",
    "notes": "Innovative tech startup",
    "metadata": {"industry": "AI/ML"},
    "is_active": true,
    "created_at": "2025-10-06T11:00:00Z"
  },
  "banner": {
    "id": "new-banner-uuid",
    "company_id": "new-company-uuid",
    "name": "Default Banner",
    "logo_url": "https://newtech.com/logo.png",
    "signature": "Best regards,\nNew Tech Team",
    "metadata": {"type": "default"},
    "created_by": "user-uuid",
    "is_active": true,
    "created_at": "2025-10-06T11:00:00Z"
  }
}
```

---

## 🧪 **Complete Testing Workflow**

### **Prerequisites Setup**
First, ensure you have a valid account ID. If not, create a user account to get one:

```bash
# Create user (this also creates an account)
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "full_name": "Test User",
    "account_name": "Test Organization"
  }'

# Note the account_id from the response for use in following tests
```

### **Step 1: Create a Company**
```bash
curl -X POST http://localhost:5000/companies \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID_HERE",
    "name": "Acme Corporation",
    "domain": "acme.com",
    "notes": "Leading provider of innovative solutions",
    "metadata": {
      "industry": "Technology",
      "employees": 150,
      "founded": "2020"
    }
  }'
```

### **Step 2: Get Company Details**
```bash
curl http://localhost:5000/companies/COMPANY_ID_FROM_STEP_1
```

### **Step 3: Create Company Banner**
```bash
curl -X POST http://localhost:5000/company-banners \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "COMPANY_ID_FROM_STEP_1",
    "name": "Acme - Sales Team",
    "logo_url": "https://acme.com/logo.png",
    "signature": "Best regards,\nAcme Sales Team\nPhone: (555) 123-4567\nwww.acme.com",
    "metadata": {
      "department": "Sales",
      "template_type": "formal"
    }
  }'
```

### **Step 4: Create Another Banner**
```bash
curl -X POST http://localhost:5000/company-banners \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "COMPANY_ID_FROM_STEP_1",
    "name": "Acme - Support Team",
    "logo_url": "https://acme.com/support-logo.png",
    "signature": "Best regards,\nAcme Support Team\nSupport: support@acme.com\n24/7 Help Available",
    "metadata": {
      "department": "Support",
      "priority": "high"
    }
  }'
```

### **Step 5: Get All Companies for Account**
```bash
curl http://localhost:5000/accounts/YOUR_ACCOUNT_ID/companies
```

### **Step 6: Get All Banners for Company**
```bash
curl http://localhost:5000/companies/COMPANY_ID_FROM_STEP_1/banners
```

### **Step 7: Get Complete Account Overview**
```bash
curl http://localhost:5000/accounts/YOUR_ACCOUNT_ID/companies-with-banners
```

### **Step 8: Update Company**
```bash
curl -X PUT http://localhost:5000/companies/COMPANY_ID_FROM_STEP_1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation Ltd",
    "domain": "acme-corp.com",
    "notes": "Updated: Now a limited liability company",
    "metadata": {
      "industry": "Technology & Consulting",
      "employees": 200,
      "founded": "2020",
      "legal_status": "LLC"
    }
  }'
```

### **Step 9: Update Banner**
```bash
curl -X PUT http://localhost:5000/company-banners/BANNER_ID \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp - Sales Team",
    "logo_url": "https://acme-corp.com/new-logo.png",
    "signature": "Best regards,\nAcme Corp Sales Team\nPhone: (555) 123-4567\nwww.acme-corp.com"
  }'
```

### **Step 10: Create Company with Banner (One Operation)**
```bash
curl -X POST http://localhost:5000/companies-with-banner \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "company_name": "Innovation Labs",
    "company_domain": "innovationlabs.com",
    "company_notes": "R&D focused company",
    "company_metadata": {
      "type": "Research",
      "focus": "AI/ML"
    },
    "banner_name": "Innovation Labs - Default",
    "logo_url": "https://innovationlabs.com/logo.png",
    "signature": "Best regards,\nInnovation Labs Team\ninnovationlabs.com"
  }'
```

### **Step 11: Test Error Cases**
```bash
# Try to create company with invalid account_id
curl -X POST http://localhost:5000/companies \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "invalid-uuid",
    "name": "Test Company"
  }'

# Try to create duplicate company name
curl -X POST http://localhost:5000/companies \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "name": "Acme Corporation Ltd"
  }'
```

### **Step 12: Clean Up (Delete Resources)**
```bash
# Delete banner
curl -X DELETE http://localhost:5000/company-banners/BANNER_ID

# Delete company (also deletes associated banners)
curl -X DELETE http://localhost:5000/companies/COMPANY_ID
```

---

## 🔧 **Integration Examples**

### **JavaScript Frontend Integration**
```javascript
class CompanyService {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async createCompany(accountId, companyData) {
    const response = await fetch(`${this.baseURL}/companies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        account_id: accountId,
        ...companyData
      })
    });
    return await response.json();
  }

  async getAccountCompaniesWithBanners(accountId) {
    const response = await fetch(`${this.baseURL}/accounts/${accountId}/companies-with-banners`);
    return await response.json();
  }

  async createCompanyWithBanner(data) {
    const response = await fetch(`${this.baseURL}/companies-with-banner`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await response.json();
  }

  async updateCompany(companyId, updates) {
    const response = await fetch(`${this.baseURL}/companies/${companyId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return await response.json();
  }
}

// Usage Example
const companyService = new CompanyService();

// Create company with banner
const result = await companyService.createCompanyWithBanner({
  account_id: 'account-uuid',
  company_name: 'My Company',
  company_domain: 'mycompany.com',
  logo_url: 'https://mycompany.com/logo.png'
});

// Get all companies and banners
const overview = await companyService.getAccountCompaniesWithBanners('account-uuid');
console.log(`Total companies: ${overview.data.total_companies}`);
console.log(`Total banners: ${overview.data.total_banners}`);
```

### **Python Client Integration**
```python
import requests
import json

class CompanyClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def create_company(self, account_id, name, domain=None, notes=None, metadata=None):
        data = {
            'account_id': account_id,
            'name': name,
            'domain': domain,
            'notes': notes,
            'metadata': metadata or {}
        }
        response = requests.post(f'{self.base_url}/companies', json=data)
        return response.json()

    def create_banner(self, company_id, name, logo_url=None, signature=None, metadata=None):
        data = {
            'company_id': company_id,
            'name': name,
            'logo_url': logo_url,
            'signature': signature,
            'metadata': metadata or {}
        }
        response = requests.post(f'{self.base_url}/company-banners', json=data)
        return response.json()

    def get_account_overview(self, account_id):
        response = requests.get(f'{self.base_url}/accounts/{account_id}/companies-with-banners')
        return response.json()

    def create_company_with_banner(self, **kwargs):
        response = requests.post(f'{self.base_url}/companies-with-banner', json=kwargs)
        return response.json()

# Usage Example
client = CompanyClient()

# Create company
company_result = client.create_company(
    account_id='account-uuid',
    name='Python Test Company',
    domain='pythontest.com',
    notes='Created via Python client',
    metadata={'language': 'Python', 'framework': 'Flask'}
)

if company_result['success']:
    company_id = company_result['company']['id']
    
    # Create banner
    banner_result = client.create_banner(
        company_id=company_id,
        name='Python Company Banner',
        logo_url='https://pythontest.com/logo.png',
        signature='Best regards,\nPython Test Team'
    )
    
    print(f"Company: {company_result['company']['name']}")
    print(f"Banner: {banner_result['banner']['name']}")
```

---

## 🔒 **Security & Validation**

### **Data Validation**
- **UUID Validation**: All IDs are validated as proper UUIDs
- **Required Fields**: account_id and name are mandatory for companies
- **Unique Constraints**: Company names must be unique per account
- **Soft Deletes**: All deletes are soft deletes (is_active = false)
- **Referential Integrity**: Foreign key constraints prevent orphaned records

### **Error Handling**
- **400 Bad Request**: Missing required fields, validation errors
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: System errors

### **Best Practices**
- Always verify account existence before creating companies
- Use the combined operations for efficiency when creating related resources
- Implement proper error handling in client applications
- Use soft deletes to maintain data integrity and audit trails

---

## 🚀 **Production Considerations**

### **Performance**
- Database indexes are automatically created for foreign keys
- Consider adding pagination for large result sets
- Use the combined endpoint to reduce API calls

### **Monitoring**
- All operations are logged with appropriate log levels
- Include request IDs for tracing in production
- Monitor API response times and error rates

### **Scaling**
- Consider implementing caching for frequently accessed data
- Use database connection pooling for high-concurrency scenarios
- Implement rate limiting to prevent API abuse

---

## 📝 **API Summary**

### **Company Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/companies` | Create company |
| GET | `/companies/{id}` | Get company by ID |
| PUT | `/companies/{id}` | Update company |
| DELETE | `/companies/{id}` | Delete company |
| GET | `/accounts/{id}/companies` | Get all companies for account |

### **Banner Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/company-banners` | Create banner |
| GET | `/company-banners/{id}` | Get banner by ID |
| PUT | `/company-banners/{id}` | Update banner |
| DELETE | `/company-banners/{id}` | Delete banner |
| GET | `/companies/{id}/banners` | Get all banners for company |

### **Combined Operations**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/accounts/{id}/companies-with-banners` | Get complete account overview |
| POST | `/companies-with-banner` | Create company and banner together |

---

**Last Updated**: October 6, 2025  
**Version**: 1.0.0