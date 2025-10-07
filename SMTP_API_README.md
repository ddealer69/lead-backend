# SMTP Credentials Management System - API Documentation

Complete CRUD operations for managing SMTP email configurations with encrypted password storage and verification system.

## 🏗️ **System Architecture**

```
Account (Root)
    ├── SMTP Credential 1 (Gmail)
    ├── SMTP Credential 2 (Outlook)  
    ├── SMTP Credential 3 (Custom SMTP)
    └── SMTP Credential N...
```

## 📊 **Database Relationships**

```sql
accounts (1) ←→ (N) smtp_credentials
users (1) ←→ (N) smtp_credentials (created_by)
```

- **accounts.id** → **smtp_credentials.account_id** (Foreign Key)
- **users.id** → **smtp_credentials.created_by** (Foreign Key, Optional)

## 🚀 **Quick Start**

### **Prerequisites**
- Flask authentication system already running
- Valid account_id from accounts table
- Supabase credentials configured in `.env`

### **Base URL**: `http://localhost:5000`

---

## 📚 **SMTP Credentials Management API**

### **1. Create SMTP Credentials**
Create new SMTP email configuration for an account.

**Endpoint**: `POST /smtp-credentials`

**Request Body**:
```json
{
  "account_id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "Gmail - Sales Team",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "sales@company.com",
  "password": "app_password_here",
  "auth_type": "app_password",
  "rate_limit_per_hour": 100,
  "metadata": {
    "provider": "gmail",
    "department": "sales",
    "tls": true
  },
  "created_by": "user-uuid-here"
}
```

**Required Fields**:
- `account_id`: UUID of the parent account
- `display_name`: Friendly name for the SMTP configuration
- `smtp_host`: SMTP server hostname
- `smtp_port`: SMTP server port (1-65535)
- `username`: SMTP username (usually email address)
- `password`: SMTP password (will be encrypted)

**Optional Fields**:
- `auth_type`: Authentication type (`plain`, `oauth2`, `app_password`) - defaults to `plain`
- `rate_limit_per_hour`: Max emails per hour - for throttling
- `metadata`: JSON object for additional configuration
- `created_by`: UUID of user creating the credentials

**Success Response (201)**:
```json
{
  "success": true,
  "message": "SMTP credentials created successfully",
  "smtp_credentials": {
    "id": "smtp-uuid-here",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_by": "user-uuid-here",
    "display_name": "Gmail - Sales Team",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "sales@company.com",
    "auth_type": "app_password",
    "verified": false,
    "last_verified_at": "2025-10-06T10:30:00Z",
    "rate_limit_per_hour": 100,
    "metadata": {
      "provider": "gmail",
      "department": "sales",
      "tls": true
    },
    "created_at": "2025-10-06T10:30:00Z",
    "updated_at": "2025-10-06T10:30:00Z"
  }
}
```

**Note**: The password is encrypted and never returned in responses.

**Error Responses**:
```json
// Account not found (400)
{
  "success": false,
  "message": "Account not found or inactive",
  "smtp_credentials": null
}

// Duplicate display name (400)
{
  "success": false,
  "message": "SMTP credentials with this display name already exists for this account",
  "smtp_credentials": null
}

// Invalid auth type (400)
{
  "success": false,
  "message": "Invalid auth_type. Must be: plain, oauth2, or app_password",
  "smtp_credentials": null
}

// Invalid port (400)
{
  "success": false,
  "message": "Invalid SMTP port. Must be between 1 and 65535",
  "smtp_credentials": null
}
```

### **2. Get SMTP Credentials**
Retrieve SMTP credentials by ID (password excluded for security).

**Endpoint**: `GET /smtp-credentials/{smtp_id}`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "SMTP credentials retrieved successfully",
  "smtp_credentials": {
    "id": "smtp-uuid-here",
    "account_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_by": "user-uuid-here",
    "display_name": "Gmail - Sales Team",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "sales@company.com",
    "auth_type": "app_password",
    "verified": true,
    "last_verified_at": "2025-10-06T11:00:00Z",
    "rate_limit_per_hour": 100,
    "metadata": {
      "provider": "gmail",
      "department": "sales"
    },
    "created_at": "2025-10-06T10:30:00Z",
    "updated_at": "2025-10-06T11:00:00Z"
  }
}
```

### **3. Update SMTP Credentials**
Update SMTP configuration (all fields optional).

**Endpoint**: `PUT /smtp-credentials/{smtp_id}`

**Request Body**:
```json
{
  "display_name": "Gmail - Updated Sales Team",
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 465,
  "username": "newsales@company.com",
  "password": "new_app_password",
  "auth_type": "oauth2",
  "rate_limit_per_hour": 200,
  "metadata": {
    "provider": "gmail",
    "department": "sales",
    "ssl": true,
    "updated": "2025-10-06"
  }
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "SMTP credentials updated successfully",
  "smtp_credentials": {
    "id": "smtp-uuid-here",
    "display_name": "Gmail - Updated Sales Team",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 465,
    "username": "newsales@company.com",
    "auth_type": "oauth2",
    "verified": false,
    "last_verified_at": "2025-10-06T11:30:00Z",
    "rate_limit_per_hour": 200,
    "updated_at": "2025-10-06T11:30:00Z"
  }
}
```

**Note**: When password is updated, `verified` is reset to `false` and `last_verified_at` is updated.

### **4. Delete SMTP Credentials**
Hard delete SMTP credentials (for security - no soft delete for sensitive data).

**Endpoint**: `DELETE /smtp-credentials/{smtp_id}`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "SMTP credentials deleted successfully"
}
```

### **5. Get All SMTP Credentials by Account**
Retrieve all SMTP configurations for an account.

**Endpoint**: `GET /accounts/{account_id}/smtp-credentials`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 3 SMTP credentials",
  "smtp_credentials": [
    {
      "id": "smtp-uuid-1",
      "account_id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "Gmail - Sales Team",
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "sales@company.com",
      "auth_type": "app_password",
      "verified": true,
      "last_verified_at": "2025-10-06T11:00:00Z",
      "rate_limit_per_hour": 100,
      "metadata": {"provider": "gmail"},
      "created_at": "2025-10-06T10:30:00Z"
    },
    {
      "id": "smtp-uuid-2",
      "account_id": "550e8400-e29b-41d4-a716-446655440000",
      "display_name": "Outlook - Support Team",
      "smtp_host": "smtp-mail.outlook.com",
      "smtp_port": 587,
      "username": "support@company.com",
      "auth_type": "oauth2",
      "verified": false,
      "rate_limit_per_hour": 50,
      "metadata": {"provider": "outlook"},
      "created_at": "2025-10-06T10:45:00Z"
    }
  ]
}
```

### **6. Verify SMTP Credentials**
Mark SMTP credentials as verified and update verification timestamp.

**Endpoint**: `POST /smtp-credentials/{smtp_id}/verify`

**Request Body** (Optional):
```json
{
  "test_connection": true
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "SMTP credentials verified successfully",
  "verified": true
}
```

**Note**: In production, this would test the actual SMTP connection. Currently simulates verification.

### **7. Get Verified SMTP Credentials**
Retrieve only verified SMTP credentials for an account.

**Endpoint**: `GET /accounts/{account_id}/smtp-credentials/verified`

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Retrieved 2 verified SMTP credentials",
  "smtp_credentials": [
    {
      "id": "smtp-uuid-1",
      "display_name": "Gmail - Sales Team",
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "sales@company.com",
      "verified": true,
      "last_verified_at": "2025-10-06T11:00:00Z",
      "rate_limit_per_hour": 100
    }
  ]
}
```

---

## 🧪 **Complete Testing Workflow**

### **Prerequisites Setup**
Get a valid account ID by creating a user account:

```bash
# Create user account (also creates account)
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "password123",
    "full_name": "Test User",
    "account_name": "Test Organization"
  }'

# Note the account_id from response for following tests
```

### **Step 1: Create Gmail SMTP Credentials**
```bash
curl -X POST http://localhost:5000/smtp-credentials \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID_HERE",
    "display_name": "Gmail - Primary",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "auth_type": "app_password",
    "rate_limit_per_hour": 100,
    "metadata": {
      "provider": "gmail",
      "tls": true,
      "description": "Primary Gmail account for outbound emails"
    }
  }'
```

### **Step 2: Create Outlook SMTP Credentials**
```bash
curl -X POST http://localhost:5000/smtp-credentials \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "display_name": "Outlook - Support",
    "smtp_host": "smtp-mail.outlook.com",
    "smtp_port": 587,
    "username": "support@yourcompany.com",
    "password": "outlook-password",
    "auth_type": "plain",
    "rate_limit_per_hour": 50,
    "metadata": {
      "provider": "outlook",
      "department": "support"
    }
  }'
```

### **Step 3: Create Custom SMTP Server**
```bash
curl -X POST http://localhost:5000/smtp-credentials \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "display_name": "Custom SMTP - Marketing",
    "smtp_host": "mail.yourcompany.com",
    "smtp_port": 465,
    "username": "marketing@yourcompany.com",
    "password": "secure-password",
    "auth_type": "plain",
    "rate_limit_per_hour": 300,
    "metadata": {
      "provider": "custom",
      "ssl": true,
      "department": "marketing"
    }
  }'
```

### **Step 4: Get All SMTP Credentials**
```bash
curl http://localhost:5000/accounts/YOUR_ACCOUNT_ID/smtp-credentials
```

### **Step 5: Get Specific SMTP Credentials**
```bash
curl http://localhost:5000/smtp-credentials/SMTP_ID_FROM_STEP_1
```

### **Step 6: Verify SMTP Credentials**
```bash
curl -X POST http://localhost:5000/smtp-credentials/SMTP_ID_FROM_STEP_1/verify \
  -H "Content-Type: application/json" \
  -d '{
    "test_connection": false
  }'
```

### **Step 7: Update SMTP Credentials**
```bash
curl -X PUT http://localhost:5000/smtp-credentials/SMTP_ID_FROM_STEP_1 \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Gmail - Updated Primary",
    "rate_limit_per_hour": 150,
    "metadata": {
      "provider": "gmail",
      "tls": true,
      "updated": "2025-10-06",
      "description": "Updated primary Gmail with higher rate limit"
    }
  }'
```

### **Step 8: Update Password (Resets Verification)**
```bash
curl -X PUT http://localhost:5000/smtp-credentials/SMTP_ID_FROM_STEP_2 \
  -H "Content-Type: application/json" \
  -d '{
    "password": "new-secure-password"
  }'
```

### **Step 9: Get Only Verified Credentials**
```bash
curl http://localhost:5000/accounts/YOUR_ACCOUNT_ID/smtp-credentials/verified
```

### **Step 10: Test Error Cases**
```bash
# Invalid account ID
curl -X POST http://localhost:5000/smtp-credentials \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "invalid-uuid",
    "display_name": "Test",
    "smtp_host": "smtp.test.com",
    "smtp_port": 587,
    "username": "test@test.com",
    "password": "password"
  }'

# Duplicate display name
curl -X POST http://localhost:5000/smtp-credentials \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "display_name": "Gmail - Primary",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "another@gmail.com",
    "password": "password"
  }'

# Invalid SMTP port
curl -X POST http://localhost:5000/smtp-credentials \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "display_name": "Invalid Port Test",
    "smtp_host": "smtp.test.com",
    "smtp_port": 99999,
    "username": "test@test.com",
    "password": "password"
  }'
```

### **Step 11: Delete SMTP Credentials**
```bash
# Delete specific SMTP credentials
curl -X DELETE http://localhost:5000/smtp-credentials/SMTP_ID_FROM_STEP_3
```

---

## 🔧 **Integration Examples**

### **JavaScript Frontend Integration**
```javascript
class SMTPService {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async createSMTPCredentials(smtpData) {
    const response = await fetch(`${this.baseURL}/smtp-credentials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(smtpData)
    });
    return await response.json();
  }

  async getSMTPCredentials(accountId) {
    const response = await fetch(`${this.baseURL}/accounts/${accountId}/smtp-credentials`);
    return await response.json();
  }

  async getVerifiedSMTPCredentials(accountId) {
    const response = await fetch(`${this.baseURL}/accounts/${accountId}/smtp-credentials/verified`);
    return await response.json();
  }

  async updateSMTPCredentials(smtpId, updates) {
    const response = await fetch(`${this.baseURL}/smtp-credentials/${smtpId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    return await response.json();
  }

  async verifySMTPCredentials(smtpId, testConnection = false) {
    const response = await fetch(`${this.baseURL}/smtp-credentials/${smtpId}/verify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_connection: testConnection })
    });
    return await response.json();
  }

  async deleteSMTPCredentials(smtpId) {
    const response = await fetch(`${this.baseURL}/smtp-credentials/${smtpId}`, {
      method: 'DELETE'
    });
    return await response.json();
  }
}

// Usage Example
const smtpService = new SMTPService();

// Create Gmail SMTP credentials
const gmailCredentials = await smtpService.createSMTPCredentials({
  account_id: 'account-uuid',
  display_name: 'Gmail - Marketing',
  smtp_host: 'smtp.gmail.com',
  smtp_port: 587,
  username: 'marketing@company.com',
  password: 'app-password',
  auth_type: 'app_password',
  rate_limit_per_hour: 200,
  metadata: {
    provider: 'gmail',
    department: 'marketing'
  }
});

// Get all SMTP credentials for account
const allCredentials = await smtpService.getSMTPCredentials('account-uuid');
console.log(`Total SMTP configs: ${allCredentials.smtp_credentials.length}`);

// Get only verified credentials
const verifiedCredentials = await smtpService.getVerifiedSMTPCredentials('account-uuid');
console.log(`Verified configs: ${verifiedCredentials.smtp_credentials.length}`);
```

### **Python Client Integration**
```python
import requests
import json

class SMTPClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def create_smtp_credentials(self, **kwargs):
        """Create SMTP credentials"""
        response = requests.post(f'{self.base_url}/smtp-credentials', json=kwargs)
        return response.json()

    def get_smtp_credentials(self, account_id):
        """Get all SMTP credentials for account"""
        response = requests.get(f'{self.base_url}/accounts/{account_id}/smtp-credentials')
        return response.json()

    def get_verified_smtp_credentials(self, account_id):
        """Get only verified SMTP credentials"""
        response = requests.get(f'{self.base_url}/accounts/{account_id}/smtp-credentials/verified')
        return response.json()

    def update_smtp_credentials(self, smtp_id, **updates):
        """Update SMTP credentials"""
        response = requests.put(f'{self.base_url}/smtp-credentials/{smtp_id}', json=updates)
        return response.json()

    def verify_smtp_credentials(self, smtp_id, test_connection=False):
        """Verify SMTP credentials"""
        data = {'test_connection': test_connection}
        response = requests.post(f'{self.base_url}/smtp-credentials/{smtp_id}/verify', json=data)
        return response.json()

    def delete_smtp_credentials(self, smtp_id):
        """Delete SMTP credentials"""
        response = requests.delete(f'{self.base_url}/smtp-credentials/{smtp_id}')
        return response.json()

# Usage Example
client = SMTPClient()

# Create Gmail SMTP credentials
gmail_result = client.create_smtp_credentials(
    account_id='account-uuid',
    display_name='Gmail - Python Client',
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    username='python@company.com',
    password='app-password',
    auth_type='app_password',
    rate_limit_per_hour=100,
    metadata={'created_by': 'python_client', 'provider': 'gmail'}
)

if gmail_result['success']:
    smtp_id = gmail_result['smtp_credentials']['id']
    print(f"Created SMTP credentials: {smtp_id}")
    
    # Verify the credentials
    verify_result = client.verify_smtp_credentials(smtp_id)
    print(f"Verification: {verify_result['verified']}")
    
    # Get all credentials for account
    all_creds = client.get_smtp_credentials('account-uuid')
    print(f"Total SMTP configs: {len(all_creds['smtp_credentials'])}")
```

---

## 🔒 **Security Features**

### **Password Encryption**
- ✅ **SHA-256 Hashing**: Passwords encrypted before storage
- ✅ **Never Returned**: Encrypted passwords never included in API responses
- ✅ **Verification Reset**: Password changes reset verification status
- ✅ **Hard Delete**: SMTP credentials are hard deleted (no soft delete for sensitive data)

### **Data Validation**
- ✅ **UUID Validation**: All IDs validated as proper UUIDs
- ✅ **Port Validation**: SMTP ports must be between 1-65535
- ✅ **Auth Type Validation**: Only allowed auth types accepted
- ✅ **Unique Constraints**: Display names must be unique per account
- ✅ **Required Fields**: Mandatory field validation

### **Access Control**
- ✅ **Account Isolation**: SMTP credentials scoped to accounts
- ✅ **User Association**: Optional created_by tracking
- ✅ **Verification System**: Track verified vs unverified credentials

---

## 📋 **Common SMTP Configurations**

### **Gmail**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "auth_type": "app_password",
  "metadata": {
    "provider": "gmail",
    "tls": true,
    "requires_app_password": true
  }
}
```

### **Outlook/Hotmail**
```json
{
  "smtp_host": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "auth_type": "plain",
  "metadata": {
    "provider": "outlook",
    "tls": true
  }
}
```

### **Yahoo Mail**
```json
{
  "smtp_host": "smtp.mail.yahoo.com",
  "smtp_port": 587,
  "auth_type": "app_password",
  "metadata": {
    "provider": "yahoo",
    "tls": true,
    "requires_app_password": true
  }
}
```

### **Custom SMTP Server**
```json
{
  "smtp_host": "mail.yourdomain.com",
  "smtp_port": 465,
  "auth_type": "plain",
  "metadata": {
    "provider": "custom",
    "ssl": true,
    "server_type": "postfix"
  }
}
```

---

## 🚀 **Production Considerations**

### **Security Enhancements**
- Use proper encryption (AES) instead of SHA-256 hashing for passwords
- Implement actual SMTP connection testing in verification
- Add rate limiting for SMTP operations
- Use proper secret management (AWS KMS, HashiCorp Vault)

### **Performance**
- Add caching for frequently accessed SMTP credentials
- Implement connection pooling for SMTP testing
- Consider async operations for SMTP verification

### **Monitoring**
- Log all SMTP operations with proper security filtering
- Monitor verification success/failure rates
- Track SMTP usage patterns and rate limit violations

---

## 📝 **API Summary**

### **SMTP Credentials Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/smtp-credentials` | Create SMTP credentials |
| GET | `/smtp-credentials/{id}` | Get SMTP credentials by ID |
| PUT | `/smtp-credentials/{id}` | Update SMTP credentials |
| DELETE | `/smtp-credentials/{id}` | Delete SMTP credentials |
| GET | `/accounts/{id}/smtp-credentials` | Get all SMTP credentials for account |
| POST | `/smtp-credentials/{id}/verify` | Verify SMTP credentials |
| GET | `/accounts/{id}/smtp-credentials/verified` | Get only verified credentials |

---

**Last Updated**: October 6, 2025  
**Version**: 1.0.0