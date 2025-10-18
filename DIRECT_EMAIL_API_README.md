# Direct Email Sending API

This document describes the direct email sending endpoints that allow users to send emails to multiple recipients using their own SMTP credentials.

## Endpoints

### 1. Send Direct Emails

Send emails directly to multiple recipients using provided SMTP credentials.

**Endpoint:** `POST /api/email/send-direct`

**Request Body:**
```json
{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "sender@gmail.com",
    "smtp_password": "your_app_password_here",
    "recipients": [
        "recipient1@example.com",
        "recipient2@example.com",
        "recipient3@example.com"
    ],
    "full_names": [
        "John Doe",
        "Jane Smith",
        "Mike Johnson"
    ],
    "subject": "Hello {{full_name}}, welcome to our service!",
    "body": "<h1>Welcome {{full_name}}!</h1><p>This is personalized content for you. HTML is supported.</p>",
    "sender_name": "Company Name"
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `smtp_host` | string | Yes | SMTP server hostname (e.g., smtp.gmail.com) |
| `smtp_port` | integer | Yes | SMTP server port (587 for TLS, 465 for SSL, 25 for plain) |
| `smtp_email` | string | Yes | Sender email address |
| `smtp_password` | string | Yes | Email password or app password |
| `recipients` | array | Yes | Array of recipient email addresses |
| `full_names` | array | No | Array of recipient names (same order as recipients). Used for {{full_name}} personalization |
| `subject` | string | Yes | Email subject line (supports {{full_name}} placeholder) |
| `body` | string | Yes | Email body content (HTML supported, supports {{full_name}} placeholder) |
| `sender_name` | string | No | Display name for sender (defaults to smtp_email) |

**Personalization:**
- Use `{{full_name}}` placeholder in subject and body to personalize emails
- If `full_names` array is provided, it must match the length of `recipients` array
- Names are matched by index position (recipients[0] gets full_names[0], etc.)
- If no name is provided for a recipient, "there" is used as default

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/email/send-direct \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "your.email@gmail.com",
    "smtp_password": "your_app_password",
    "recipients": [
      "client1@example.com",
      "client2@example.com"
    ],
    "full_names": [
      "John Client",
      "Jane Customer"
    ],
    "subject": "Important Update for {{full_name}}",
    "body": "<h2>Hello {{full_name}}!</h2><p>This is an important personalized update for you.</p><p>Best regards,<br>Your Team</p>",
    "sender_name": "Your Company"
  }'
```

**Success Response (All Emails Sent):**
```json
{
    "success": true,
    "message": "Email sending completed. Sent: 2, Failed: 0",
    "emails_sent": 2,
    "emails_failed": 0,
    "total_recipients": 2,
    "results": [
        {
            "recipient": "client1@example.com",
            "full_name": "John Client",
            "status": "sent",
            "message": "Email sent successfully"
        },
        {
            "recipient": "client2@example.com",
            "full_name": "Jane Customer", 
            "status": "sent",
            "message": "Email sent successfully"
        }
    ]
}
```

**Partial Success Response (Some Failed):**
```json
{
    "success": true,
    "message": "Email sending completed. Sent: 1, Failed: 1",
    "emails_sent": 1,
    "emails_failed": 1,
    "total_recipients": 2,
    "results": [
        {
            "recipient": "client1@example.com",
            "full_name": "John Client",
            "status": "sent",
            "message": "Email sent successfully"
        },
        {
            "recipient": "invalid@nonexistent.com",
            "full_name": "Invalid User",
            "status": "failed",
            "message": "SMTP error: Recipient address rejected"
        }
    ]
}
```

### 2. Test SMTP Connection

Test SMTP connection without sending any emails.

**Endpoint:** `POST /api/email/test-smtp`

**Request Body:**
```json
{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "your.email@gmail.com",
    "smtp_password": "your_app_password"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/email/test-smtp \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "your.email@gmail.com",
    "smtp_password": "your_app_password"
  }'
```

**Success Response:**
```json
{
    "success": true,
    "message": "SMTP connection successful using TLS connection",
    "connection_details": {
        "host": "smtp.gmail.com",
        "port": 587,
        "email": "your.email@gmail.com",
        "connection_type": "TLS"
    }
}
```

## Error Responses

### Common Error Format:
```json
{
    "success": false,
    "message": "Error description",
    "results": []
}
```

### Validation Errors:

**Missing required fields:**
```json
{
    "success": false,
    "message": "smtp_host, smtp_port, smtp_email, smtp_password, recipients, subject, and body are required",
    "results": []
}
```

**Invalid email format:**
```json
{
    "success": false,
    "message": "Invalid recipient email format: invalid-email, another-invalid",
    "results": []
}
```

**SMTP authentication error:**
```json
{
    "success": false,
    "message": "SMTP authentication failed. Please check your email and password/app password."
}
```

## HTTP Status Codes

- `200` - All emails sent successfully
- `207` - Partial success (some emails sent, some failed)
- `400` - All emails failed or validation error
- `401` - Authentication failed
- `500` - Internal server error

## Common SMTP Providers

### Gmail
- **Host**: smtp.gmail.com
- **Port**: 587 (TLS) or 465 (SSL)
- **Authentication**: Use App Passwords (not regular password)
- **Setup**: Enable 2FA and generate app password in Google Account settings

### Outlook/Hotmail
- **Host**: smtp-mail.outlook.com
- **Port**: 587
- **Authentication**: Regular password or app password

### Yahoo
- **Host**: smtp.mail.yahoo.com
- **Port**: 587 or 465
- **Authentication**: Use App Passwords

## Security Notes

1. **Use App Passwords** - For Gmail and other providers, use app-specific passwords
2. **Secure Credentials** - Never log or expose SMTP passwords
3. **Input Validation** - Always validate email addresses before sending
4. **Connection Security** - Use TLS/SSL connections when possible

## Frontend Integration Example

```javascript
// Frontend JavaScript example
async function sendDirectEmails(emailData) {
    try {
        const response = await fetch('/api/email/send-direct', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(emailData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`Successfully sent ${result.emails_sent} emails`);
            if (result.emails_failed > 0) {
                console.warn(`${result.emails_failed} emails failed to send`);
            }
        } else {
            console.error('Email sending failed:', result.message);
        }
        
        return result;
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
}

// Usage example
const emailData = {
    smtp_host: "smtp.gmail.com",
    smtp_port: 587,
    smtp_email: "your.email@gmail.com",
    smtp_password: "your_app_password",
    recipients: ["client@example.com"],
    subject: "Test Email",
    body: "<h1>Hello!</h1><p>This is a test email.</p>",
    sender_name: "Your Name"
};

sendDirectEmails(emailData);
```

This API provides a flexible and robust solution for sending emails directly from your application using any SMTP provider.