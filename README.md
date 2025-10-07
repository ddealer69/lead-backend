# Flask Authentication System with Supabase

A complete user authentication and management system built with Flask and Supabase, featuring multi-tenant account management, secure password handling, and RESTful API endpoints.

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│   Flask API     │───▶│   Supabase DB   │
│ (Web/Mobile/CLI)│    │   (main.py)     │    │  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   db_utils.py   │
                       │ (Database Layer)│
                       └─────────────────┘
```

## 📁 **Project Structure**

```
/teamspace/studios/this_studio/
├── .env                    # Environment variables (Supabase credentials)
├── .gitignore             # Git ignore patterns
├── main.py                # Flask API server with endpoints
├── db_utils.py            # Database utilities and operations
├── requirements.txt       # Python dependencies
├── database_schema.sql    # Complete database schema
└── README.md             # This documentation
```

## 🗄️ **Database Schema**

### **Accounts Table**
```sql
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
```

### **Users Table**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id),
    email CITEXT NOT NULL,
    full_name TEXT NULL,
    password_hash TEXT NULL,
    role VARCHAR(32) DEFAULT 'member',
    last_login TIMESTAMPTZ NULL,
    is_active BOOLEAN DEFAULT TRUE,
    prefs JSONB NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## 🚀 **Quick Start Guide**

### **1. Environment Setup**

Create `.env` file with your Supabase credentials:
```env
SUPABASE_URL=https://abwlrumylqkervfaadhl.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PORT=5000
```

### **2. Install Dependencies**

```bash
# Install Python packages
pip install -r requirements.txt

# Or install individually
pip install flask flask-cors supabase python-dotenv
```

### **3. Run the Server**

```bash
# Start the Flask development server
python main.py

# Server will run on: http://localhost:5000
```

### **4. Verify Setup**

```bash
# Test health endpoint
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "message": "Authentication API is running"
}
```

## 📚 **API Documentation**

### **Base URL**: `http://localhost:5000`

---

## 🔐 **Authentication Endpoints**

### **1. User Signup**
Create a new user account with associated company/account.

**Endpoint**: `POST /auth/signup`

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "account_name": "Acme Corporation",
  "role": "member"
}
```

**Required Fields**:
- `email`: Valid email address (will be converted to lowercase)
- `password`: Minimum 6 characters
- `full_name`: User's display name
- `account_name`: Company/organization name (auto-creates account if needed)

**Optional Fields**:
- `role`: User role (`owner`, `admin`, `member`) - defaults to `member`

**Success Response (201)**:
```json
{
  "success": true,
  "message": "User created successfully.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "account_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "member",
    "is_active": true,
    "created_at": "2025-10-06T10:30:00Z"
  }
}
```

**Error Responses**:
```json
// Missing fields (400)
{
  "success": false,
  "message": "Email, password, full_name, and account_name are required"
}

// Weak password (400)
{
  "success": false,
  "message": "Password must be at least 6 characters long"
}

// User exists (400)
{
  "success": false,
  "message": "User with this email already exists."
}
```

### **2. User Login**
Authenticate existing user with email and password.

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Authentication successful.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "account_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "member",
    "last_login": "2025-10-06T10:35:00Z",
    "is_active": true
  }
}
```

**Error Responses**:
```json
// Email not found (401)
{
  "success": false,
  "message": "Email not found. Please create a new account.",
  "user": null
}

// Wrong password (401)
{
  "success": false,
  "message": "Password does not match.",
  "user": null
}
```

### **3. Delete Account**
Permanently deactivate user account (soft delete).

**Endpoint**: `DELETE /auth/delete-account`

**Request Body**:
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Success Response (200)**:
```json
{
  "success": true,
  "message": "User account deleted successfully."
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "message": "Password does not match."
}
```

---

## 👤 **User Management Endpoints**

### **4. Get User Profile**
Retrieve user details by email address.

**Endpoint**: `GET /user/profile?email=john@example.com`

**Query Parameters**:
- `email`: User's email address (required)

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "account_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "member",
    "last_login": "2025-10-06T10:35:00Z",
    "prefs": {"theme": "dark", "notifications": true},
    "created_at": "2025-10-06T10:30:00Z",
    "updated_at": "2025-10-06T10:35:00Z"
  }
}
```

**Error Response (404)**:
```json
{
  "success": false,
  "message": "User not found"
}
```

### **5. Update User Profile**
Update user information (except email and password).

**Endpoint**: `PUT /user/update-profile`

**Request Body**:
```json
{
  "email": "john@example.com",
  "full_name": "John Smith",
  "role": "admin",
  "prefs": {
    "theme": "dark",
    "notifications": true,
    "language": "en"
  }
}
```

**Updatable Fields**:
- `full_name`: Display name
- `role`: User role (`owner`, `admin`, `member`)
- `prefs`: JSON object with user preferences

**Success Response (200)**:
```json
{
  "success": true,
  "message": "Profile updated successfully.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "account_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "email": "john@example.com",
    "full_name": "John Smith",
    "role": "admin",
    "prefs": {"theme": "dark", "notifications": true, "language": "en"},
    "updated_at": "2025-10-06T10:40:00Z"
  }
}
```

---

## 🧪 **Complete Testing Workflow**

### **Step 1: Create a New User**
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@techcorp.com",
    "password": "securepassword123",
    "full_name": "Alice Johnson",
    "account_name": "TechCorp Solutions",
    "role": "admin"
  }'
```

### **Step 2: Login with New User**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@techcorp.com",
    "password": "securepassword123"
  }'
```

### **Step 3: Get User Profile**
```bash
curl "http://localhost:5000/user/profile?email=alice@techcorp.com"
```

### **Step 4: Update User Profile**
```bash
curl -X PUT http://localhost:5000/user/update-profile \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@techcorp.com",
    "full_name": "Alice Johnson-Smith",
    "prefs": {"theme": "dark", "notifications": false}
  }'
```

### **Step 5: Test Wrong Password**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@techcorp.com",
    "password": "wrongpassword"
  }'
```

### **Step 6: Test Non-existent User**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "anypassword"
  }'
```

### **Step 7: Delete Account**
```bash
curl -X DELETE http://localhost:5000/auth/delete-account \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@techcorp.com",
    "password": "securepassword123"
  }'
```

---

## 🔧 **Integration Examples**

### **JavaScript/Frontend Integration**
```javascript
class AuthService {
  constructor(baseURL = 'http://localhost:5000') {
    this.baseURL = baseURL;
  }

  async signup(userData) {
    const response = await fetch(`${this.baseURL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    return await response.json();
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return await response.json();
  }

  async getProfile(email) {
    const response = await fetch(`${this.baseURL}/user/profile?email=${email}`);
    return await response.json();
  }
}

// Usage
const auth = new AuthService();

// Sign up
const signupResult = await auth.signup({
  email: 'user@example.com',
  password: 'password123',
  full_name: 'Test User',
  account_name: 'Test Company'
});

// Login
const loginResult = await auth.login('user@example.com', 'password123');
```

### **Python Client Integration**
```python
import requests
import json

class AuthClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def signup(self, email, password, full_name, account_name, role='member'):
        data = {
            'email': email,
            'password': password,
            'full_name': full_name,
            'account_name': account_name,
            'role': role
        }
        response = requests.post(f'{self.base_url}/auth/signup', json=data)
        return response.json()

    def login(self, email, password):
        data = {'email': email, 'password': password}
        response = requests.post(f'{self.base_url}/auth/login', json=data)
        return response.json()

    def get_profile(self, email):
        response = requests.get(f'{self.base_url}/user/profile', 
                              params={'email': email})
        return response.json()

# Usage
client = AuthClient()

# Sign up
result = client.signup(
    email='test@example.com',
    password='password123',
    full_name='Test User',
    account_name='Test Company'
)
print(result)
```

---

## 🛡️ **Security Features**

### **Password Security**
- ✅ **SHA-256 Hashing**: Passwords are never stored in plaintext
- ✅ **Minimum Length**: 6 character minimum requirement
- ✅ **Secure Verification**: Constant-time password comparison

### **Data Protection**
- ✅ **Service Role Bypass**: Uses Supabase service key to bypass RLS
- ✅ **Input Sanitization**: All inputs are cleaned and validated
- ✅ **SQL Injection Protection**: Supabase client handles parameterization
- ✅ **Soft Deletes**: User data preserved for audit trails

### **Multi-tenant Isolation**
- ✅ **Account Separation**: Users belong to specific accounts/companies
- ✅ **Automatic Account Creation**: New accounts created as needed
- ✅ **Referential Integrity**: Proper foreign key relationships

---

## 🔍 **Troubleshooting**

### **Common Issues**

**1. "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY"**
```bash
# Solution: Check your .env file
cat .env
# Ensure both variables are set correctly
```

**2. "Connection refused" or "Server not responding"**
```bash
# Solution: Verify server is running
python main.py
# Check if port 5000 is available
netstat -an | grep 5000
```

**3. "User with this email already exists"**
```bash
# Solution: Use a different email or delete existing user
curl -X DELETE http://localhost:5000/auth/delete-account \
  -H "Content-Type: application/json" \
  -d '{"email": "existing@example.com", "password": "password"}'
```

**4. "Email not found. Please create a new account."**
```bash
# Solution: Sign up first, then login
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "new@example.com", "password": "password123", ...}'
```

### **Debug Mode**
Enable detailed logging by running with debug flag:
```bash
FLASK_ENV=development python main.py
```

### **Database Verification**
Check your Supabase dashboard to verify:
1. Tables exist: `accounts`, `users`
2. RLS policies are configured
3. Service role has proper permissions

---

## 🚀 **Production Deployment**

### **Environment Variables**
```env
# Production settings
FLASK_ENV=production
SUPABASE_URL=your-production-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-production-service-key
PORT=8080
```

### **Security Considerations**
- Use HTTPS in production
- Implement rate limiting
- Add request logging and monitoring
- Use proper secret management (not .env files)
- Enable CORS only for trusted origins

### **Scaling Options**
- Use Gunicorn or uWSGI for production WSGI server
- Implement Redis for session management
- Add database connection pooling
- Consider containerization with Docker

---

## 📝 **API Response Formats**

### **Standard Success Response**
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "user": { /* user object */ }
}
```

### **Standard Error Response**
```json
{
  "success": false,
  "message": "Descriptive error message",
  "user": null
}
```

### **HTTP Status Codes**
- `200` - OK (successful operation)
- `201` - Created (user created successfully)
- `400` - Bad Request (validation errors, missing fields)
- `401` - Unauthorized (authentication failed)
- `404` - Not Found (user/resource not found)
- `405` - Method Not Allowed (wrong HTTP method)
- `500` - Internal Server Error (system error)

---

## 🤝 **Contributing**

1. Ensure all endpoints follow the established pattern
2. Add proper error handling and validation
3. Update this README for any new features
4. Test all endpoints before deployment

---

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Supabase configuration
3. Test with the provided curl examples
4. Check server logs for detailed error messages

---

**Last Updated**: October 6, 2025
**Version**: 1.0.0