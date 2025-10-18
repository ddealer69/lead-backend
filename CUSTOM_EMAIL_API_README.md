# Custom Email Sending API Documentation

## Overview

The Custom Email Sending API allows you to send personalized emails to a custom list of recipients using existing campaign templates and SMTP configurations. This endpoint is perfect for one-off email campaigns or testing campaign templates with specific recipients.

## Endpoint

```
POST /api/campaigns/{campaign_id}/send-custom-emails
```

## Description

This endpoint sends personalized emails to a custom list of recipients using:
- Campaign templates (subject and body) from the specified campaign
- SMTP configuration associated with the campaign
- Personalization variables for each recipient

## Parameters

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `campaign_id` | string (UUID) | Yes | The ID of the campaign containing the email templates and SMTP configuration |

### Request Body

The request body should be a JSON object with the following structure:

```json
{
  "recipients": [
    {
      "email": "recipient@example.com",
      "full_name": "Recipient Name"
    }
  ]
}
```

#### Recipients Array

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Valid email address of the recipient |
| `full_name` | string | Yes | Full name of the recipient for personalization |

## Prerequisites

Before using this endpoint, ensure the following:

1. **Campaign exists** with the specified `campaign_id`
2. **SMTP credentials** are configured and associated with the campaign
3. **Email templates** are set up in the campaign:
   - `subject_template`: Subject line template
   - `body_template`: Email body template
4. **SMTP credentials are verified** and working

## Template Personalization

The email templates support the following personalization variables:

- `{full_name}`: Recipient's full name
- `{email}`: Recipient's email address

### Example Templates

**Subject Template:**
```
Hello {full_name}, let's connect!
```

**Body Template:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Personal Message</title>
</head>
<body>
    <h1>Hi {full_name}!</h1>
    <p>I hope this email finds you well. I wanted to reach out to you personally at {email}.</p>
    <p>Best regards,<br>
    The Team</p>
</body>
</html>
```

## Request Examples

### Basic Request

```bash
curl -X POST "http://localhost:5000/api/campaigns/123e4567-e89b-12d3-a456-426614174000/send-custom-emails" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {
        "email": "john.doe@example.com",
        "full_name": "John Doe"
      },
      {
        "email": "jane.smith@example.com",
        "full_name": "Jane Smith"
      }
    ]
  }'
```

### JavaScript/Fetch Example

```javascript
const campaignId = '123e4567-e89b-12d3-a456-426614174000';
const recipients = [
  {
    email: 'john.doe@example.com',
    full_name: 'John Doe'
  },
  {
    email: 'jane.smith@example.com',
    full_name: 'Jane Smith'
  }
];

const response = await fetch(`/api/campaigns/${campaignId}/send-custom-emails`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    recipients: recipients
  })
});

const result = await response.json();
console.log(result);
```

### Python Example

```python
import requests
import json

campaign_id = '123e4567-e89b-12d3-a456-426614174000'
url = f'http://localhost:5000/api/campaigns/{campaign_id}/send-custom-emails'

data = {
    'recipients': [
        {
            'email': 'john.doe@example.com',
            'full_name': 'John Doe'
        },
        {
            'email': 'jane.smith@example.com',
            'full_name': 'Jane Smith'
        }
    ]
}

response = requests.post(url, json=data)
result = response.json()
print(result)
```

## Response Format

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Custom emails sent successfully",
  "emails_sent": 2,
  "emails_failed": 0,
  "total_recipients": 2,
  "results": [
    {
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "status": "sent",
      "subject": "Hello John Doe, let's connect!",
      "message": "Email sent successfully"
    },
    {
      "email": "jane.smith@example.com",
      "full_name": "Jane Smith",
      "status": "sent",
      "subject": "Hello Jane Smith, let's connect!",
      "message": "Email sent successfully"
    }
  ]
}
```

### Partial Success Response (200 OK)

When some emails succeed and others fail:

```json
{
  "success": true,
  "message": "Custom emails sent with some failures",
  "emails_sent": 1,
  "emails_failed": 1,
  "total_recipients": 2,
  "results": [
    {
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "status": "sent",
      "subject": "Hello John Doe, let's connect!",
      "message": "Email sent successfully"
    },
    {
      "email": "invalid-email",
      "full_name": "Invalid User",
      "status": "failed",
      "subject": "Hello Invalid User, let's connect!",
      "error": "Invalid email address format"
    }
  ]
}
```

## Error Responses

### 400 Bad Request - Missing Recipients

```json
{
  "success": false,
  "message": "Recipients list is required and must be a non-empty array"
}
```

### 400 Bad Request - Invalid Recipient Format

```json
{
  "success": false,
  "message": "Each recipient must have 'email' and 'full_name' fields"
}
```

### 404 Not Found - Campaign Not Found

```json
{
  "success": false,
  "message": "Campaign not found"
}
```

### 400 Bad Request - Missing SMTP Configuration

```json
{
  "success": false,
  "message": "Campaign does not have SMTP credentials configured"
}
```

### 400 Bad Request - Missing Templates

```json
{
  "success": false,
  "message": "Campaign must have both subject_template and body_template configured"
}
```

### 500 Internal Server Error

```json
{
  "success": false,
  "message": "Internal server error"
}
```

## Response Fields

### Main Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation completed successfully |
| `message` | string | Human-readable status message |
| `emails_sent` | integer | Number of emails successfully sent |
| `emails_failed` | integer | Number of emails that failed to send |
| `total_recipients` | integer | Total number of recipients processed |
| `results` | array | Detailed results for each recipient |

### Result Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | Recipient's email address |
| `full_name` | string | Recipient's full name |
| `status` | string | Either "sent" or "failed" |
| `subject` | string | The personalized subject line that was sent |
| `message` | string | Success message (for sent emails) |
| `error` | string | Error message (for failed emails) |

## Rate Limiting

The endpoint respects the rate limiting configured in the SMTP credentials. If the SMTP configuration has a `rate_limit_per_hour`, the system will:

1. Check current usage against the limit
2. Throttle sending if the limit would be exceeded
3. Return appropriate error messages for rate-limited emails

## Security Considerations

1. **SMTP Password Encryption**: SMTP passwords are encrypted in the database and decrypted only during email sending
2. **Input Validation**: All email addresses are validated before sending
3. **Error Handling**: Sensitive SMTP configuration details are not exposed in error messages
4. **Logging**: All email sending attempts are logged for audit purposes

## Best Practices

1. **Test First**: Test with a small number of recipients before sending to large lists
2. **Validate Templates**: Ensure your templates render correctly with the personalization variables
3. **Monitor Results**: Check the response to identify any failed sends
4. **Respect Limits**: Be aware of your SMTP provider's rate limits and daily sending quotas
5. **Error Handling**: Implement proper error handling in your client code

## Integration Examples

### React Component

```jsx
import React, { useState } from 'react';

const CustomEmailSender = ({ campaignId }) => {
  const [recipients, setRecipients] = useState([
    { email: '', full_name: '' }
  ]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const sendEmails = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/campaigns/${campaignId}/send-custom-emails`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ recipients })
      });
      
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error sending emails:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      {/* Recipients form */}
      {recipients.map((recipient, index) => (
        <div key={index}>
          <input
            type="email"
            placeholder="Email"
            value={recipient.email}
            onChange={(e) => {
              const newRecipients = [...recipients];
              newRecipients[index].email = e.target.value;
              setRecipients(newRecipients);
            }}
          />
          <input
            type="text"
            placeholder="Full Name"
            value={recipient.full_name}
            onChange={(e) => {
              const newRecipients = [...recipients];
              newRecipients[index].full_name = e.target.value;
              setRecipients(newRecipients);
            }}
          />
        </div>
      ))}
      
      <button onClick={sendEmails} disabled={loading}>
        {loading ? 'Sending...' : 'Send Emails'}
      </button>
      
      {results && (
        <div>
          <h3>Results</h3>
          <p>Sent: {results.emails_sent}</p>
          <p>Failed: {results.emails_failed}</p>
        </div>
      )}
    </div>
  );
};
```

## Troubleshooting

### Common Issues

1. **Campaign Not Found**
   - Verify the campaign ID exists in your database
   - Check that the campaign hasn't been deleted

2. **SMTP Not Configured**
   - Ensure the campaign has an `smtp_credential_id` set
   - Verify the SMTP credentials exist and are verified

3. **Missing Templates**
   - Check that both `subject_template` and `body_template` are set in the campaign
   - Ensure templates are not empty strings

4. **Email Sending Failures**
   - Verify SMTP credentials are correct and verified
   - Check SMTP server connectivity
   - Ensure recipient email addresses are valid
   - Check if you've hit rate limits

5. **Template Rendering Issues**
   - Ensure personalization variables `{full_name}` and `{email}` are correctly formatted
   - Test templates with sample data first

### Debug Tips

1. **Check Logs**: Monitor server logs for detailed error messages
2. **Test SMTP**: Use the SMTP verification endpoint to ensure credentials work
3. **Validate Campaign**: Use the get campaign endpoint to verify configuration
4. **Start Small**: Test with 1-2 recipients before sending to larger lists

## Related Endpoints

- `GET /api/campaigns/{campaign_id}` - Get campaign details and templates
- `POST /smtp-credentials/{smtp_id}/verify` - Verify SMTP credentials
- `GET /smtp-credentials/{smtp_id}` - Get SMTP configuration
- `PUT /api/campaigns/{campaign_id}` - Update campaign templates

## Support

For additional support or questions about this API:

1. Check the server logs for detailed error messages
2. Verify all prerequisites are met
3. Test with minimal data first
4. Review the campaign and SMTP configuration

This endpoint provides a flexible way to send personalized emails using your existing campaign infrastructure while maintaining full control over the recipient list and timing.