#!/bin/bash

# Test script for personalized email sending
# Make sure to update the SMTP credentials and recipients

echo "🧪 Testing Personalized Direct Email API"
echo "========================================"

# Test Case 1: Personalized emails with full_names
echo ""
echo "📧 Test 1: Sending personalized emails with full names..."

curl -X POST http://localhost:5000/api/email/send-direct \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "recipients": [
      "test1@example.com",
      "test2@example.com"
    ],
    "full_names": [
      "John Doe",
      "Jane Smith"
    ],
    "subject": "Hello {{full_name}}, welcome to our platform!",
    "body": "<h1>Welcome {{full_name}}!</h1><p>We are excited to have you as part of our community.</p><p>Your personalized dashboard is ready for you.</p><p>Best regards,<br>The Team</p>",
    "sender_name": "Welcome Team"
  }'

echo ""
echo ""

# Test Case 2: Regular emails without personalization
echo "📧 Test 2: Sending regular emails without personalization..."

curl -X POST http://localhost:5000/api/email/send-direct \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "recipients": [
      "test3@example.com"
    ],
    "subject": "Regular Newsletter",
    "body": "<h1>Newsletter</h1><p>This is a regular newsletter without personalization.</p>",
    "sender_name": "Newsletter Team"
  }'

echo ""
echo ""

# Test Case 3: Error case - mismatched arrays
echo "📧 Test 3: Testing error handling for mismatched arrays..."

curl -X POST http://localhost:5000/api/email/send-direct \
  -H "Content-Type: application/json" \
  -d '{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_email": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "recipients": [
      "test1@example.com",
      "test2@example.com"
    ],
    "full_names": [
      "John Doe"
    ],
    "subject": "This should fail",
    "body": "This test should return an error"
  }'

echo ""
echo ""
echo "✅ Test completed!"