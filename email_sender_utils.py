"""
Email Sender utilities
Handles campaign email sending with SMTP integration, template rendering, and lead status management
"""

import os
import json
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone
from cryptography.fernet import Fernet
import base64

# Load environment variables
load_dotenv()

class EmailSenderManager:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Encryption key for decrypting passwords (you should store this securely)
        # For demo purposes, using a fixed key - in production, use environment variable
        self.encryption_key = os.getenv('ENCRYPTION_KEY', 'your-32-byte-base64-encoded-key-here')
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """
        Decrypt the encrypted password
        Note: This is a basic implementation - adjust based on your encryption method
        """
        try:
            # If using Fernet encryption
            if self.encryption_key and self.encryption_key != 'your-32-byte-base64-encoded-key-here':
                key = base64.urlsafe_b64decode(self.encryption_key)
                fernet = Fernet(key)
                decrypted = fernet.decrypt(encrypted_password.encode()).decode()
                return decrypted
            else:
                # For demo purposes, return as-is (assuming it's already decrypted for testing)
                # In production, implement proper decryption
                return encrypted_password
        except Exception as e:
            # Fallback - return as-is for testing
            return encrypted_password
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Render template with variables using {{variable_name}} syntax
        """
        if not template:
            return ""
        
        rendered = template
        for key, value in variables.items():
            if value is not None:
                placeholder = f"{{{{{key}}}}}"
                rendered = rendered.replace(placeholder, str(value))
        
        return rendered
    
    def get_campaign_details(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign details including SMTP credentials
        """
        try:
            # Get campaign details
            campaign_result = self.supabase.table('campaigns').select(
                'id, subject_template, body_template, smtp_credential_id, name, status'
            ).eq('id', campaign_id).execute()
            
            if not campaign_result.data:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'data': None
                }
            
            campaign = campaign_result.data[0]
            
            # Check if campaign is in a sendable state
            if campaign['status'] not in ['running', 'draft']:
                return {
                    'success': False,
                    'message': f'Campaign status is {campaign["status"]}, cannot send emails',
                    'data': None
                }
            
            if not campaign['smtp_credential_id']:
                return {
                    'success': False,
                    'message': 'No SMTP credentials configured for this campaign',
                    'data': None
                }
            
            # Get SMTP credentials
            smtp_result = self.supabase.table('smtp_credentials').select(
                'id, username, encrypted_password_ciphertext, smtp_host, smtp_port, auth_type'
            ).eq('id', campaign['smtp_credential_id']).execute()
            
            if not smtp_result.data:
                return {
                    'success': False,
                    'message': 'SMTP credentials not found',
                    'data': None
                }
            
            smtp_creds = smtp_result.data[0]
            
            return {
                'success': True,
                'message': 'Campaign details retrieved successfully',
                'data': {
                    'campaign': campaign,
                    'smtp_credentials': smtp_creds
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign details: {str(e)}',
                'data': None
            }
    
    def get_queued_leads(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get all queued campaign leads with their lead details
        """
        try:
            # Get queued campaign leads
            campaign_leads_result = self.supabase.table('campaign_leads').select(
                'id, query_id, personalization_vars'
            ).eq('campaign_id', campaign_id).eq('status', 'queued').execute()
            
            if not campaign_leads_result.data:
                return {
                    'success': True,
                    'message': 'No queued leads found for this campaign',
                    'leads': []
                }
            
            leads_data = []
            
            for campaign_lead in campaign_leads_result.data:
                # Get lead details
                lead_result = self.supabase.table('leads').select(
                    'id, full_name, company_name, email'
                ).eq('id', campaign_lead['query_id']).execute()
                
                if lead_result.data:
                    lead = lead_result.data[0]
                    leads_data.append({
                        'campaign_lead_id': campaign_lead['id'],
                        'lead_id': lead['id'],
                        'full_name': lead['full_name'],
                        'company_name': lead['company_name'],
                        'email': lead['email'],
                        'personalization_vars': campaign_lead['personalization_vars'] or {}
                    })
            
            return {
                'success': True,
                'message': f'Retrieved {len(leads_data)} queued leads',
                'leads': leads_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving queued leads: {str(e)}',
                'leads': []
            }
    
    def send_email_smtp(self, smtp_config: Dict[str, Any], sender_email: str, 
                       recipient_email: str, subject: str, html_content: str) -> Dict[str, Any]:
        """
        Send email using SMTP configuration
        """
        try:
            # Get password from SMTP config (handle both old and new field names)
            if 'password' in smtp_config:
                # New format - password is already decrypted
                decrypted_password = smtp_config['password']
            elif 'encrypted_password_ciphertext' in smtp_config:
                # Old format - need to decrypt
                decrypted_password = self.decrypt_password(smtp_config['encrypted_password_ciphertext'])
            else:
                raise ValueError("No password field found in SMTP configuration")
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = sender_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            smtp_host = smtp_config['smtp_host']
            smtp_port = smtp_config['smtp_port']
            
            # Determine if we need SSL/TLS based on port
            if smtp_port == 465:
                # Use SSL
                with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                    server.login(sender_email, decrypted_password)
                    server.send_message(msg)
            else:
                # Use TLS (port 587) or plain (port 25)
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    if smtp_port == 587:
                        server.starttls()
                    server.login(sender_email, decrypted_password)
                    server.send_message(msg)
            
            return {
                'success': True,
                'message': 'Email sent successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error sending email: {str(e)}'
            }
    
    def update_campaign_lead_status(self, campaign_lead_id: str, status: str, 
                                  error_message: str = None) -> Dict[str, Any]:
        """
        Update campaign lead status after email attempt
        """
        try:
            update_data = {
                'status': status,
                'send_attempts': 1,  # Increment this in production
                'last_sent_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            if error_message:
                update_data['error'] = error_message
            
            result = self.supabase.table('campaign_leads').update(update_data).eq(
                'id', campaign_lead_id
            ).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign lead status updated successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update campaign lead status'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating campaign lead status: {str(e)}'
            }
    
    def create_email_delivery_log(self, campaign_lead_id: str, campaign_id: str, 
                                smtp_credential_id: str, recipient: str, 
                                event_type: str = 'sent', provider_event: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create email delivery log entry
        """
        try:
            if provider_event is None:
                provider_event = {"admin": "system_generated", "sent_at": datetime.now(timezone.utc).isoformat()}
            
            log_data = {
                'campaign_lead_id': campaign_lead_id,
                'campaign_id': campaign_id,
                'smtp_credential_id': smtp_credential_id,
                'recipient': recipient,
                'event_type': event_type,
                'provider_event': provider_event,
                'occurred_at': datetime.now(timezone.utc).isoformat()
            }
            
            result = self.supabase.table('email_delivery_logs').insert(log_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Email delivery log created successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create email delivery log'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating email delivery log: {str(e)}'
            }
    
    def send_campaign_emails(self, campaign_id: str) -> Dict[str, Any]:
        """
        Main function to send emails for a campaign
        """
        try:
            # Get campaign details and SMTP credentials
            campaign_details = self.get_campaign_details(campaign_id)
            if not campaign_details['success']:
                return campaign_details
            
            campaign = campaign_details['data']['campaign']
            smtp_config = campaign_details['data']['smtp_credentials']
            
            # Get queued leads
            leads_result = self.get_queued_leads(campaign_id)
            if not leads_result['success']:
                return leads_result
            
            if not leads_result['leads']:
                return {
                    'success': True,
                    'message': 'No queued leads found for this campaign',
                    'emails_sent': 0,
                    'emails_failed': 0,
                    'results': []
                }
            
            sender_email = smtp_config['username']
            subject_template = campaign['subject_template'] or "No subject"
            body_template = campaign['body_template'] or "No content"
            
            results = []
            emails_sent = 0
            emails_failed = 0
            
            for lead in leads_result['leads']:
                try:
                    # Skip if no email or empty/whitespace email
                    if not lead['email'] or not lead['email'].strip():
                        error_msg = "No email address available"
                        self.update_campaign_lead_status(lead['campaign_lead_id'], 'failed', error_msg)
                        results.append({
                            'lead_id': lead['lead_id'],
                            'email': None,
                            'status': 'failed',
                            'error': error_msg
                        })
                        emails_failed += 1
                        continue
                    
                    # Prepare template variables
                    template_vars = {
                        'full_name': lead['full_name'] or 'Friend',
                        'name': lead['full_name'] or 'Friend',  # Support both {{name}} and {{full_name}}
                        'company_name': lead['company_name'] or 'your company',
                        'email': lead['email']
                    }
                    
                    # Add personalization variables if available
                    if lead['personalization_vars']:
                        template_vars.update(lead['personalization_vars'])
                    
                    # Render templates
                    rendered_subject = self.render_template(subject_template, template_vars)
                    rendered_body = self.render_template(body_template, template_vars)
                    
                    # Send email
                    email_result = self.send_email_smtp(
                        smtp_config=smtp_config,
                        sender_email=sender_email,
                        recipient_email=lead['email'],
                        subject=rendered_subject,
                        html_content=rendered_body
                    )
                    
                    if email_result['success']:
                        # Update status to sent
                        self.update_campaign_lead_status(lead['campaign_lead_id'], 'sent')
                        
                        # Create delivery log
                        self.create_email_delivery_log(
                            campaign_lead_id=lead['campaign_lead_id'],
                            campaign_id=campaign_id,
                            smtp_credential_id=smtp_config['id'],
                            recipient=lead['email'],
                            event_type='sent',
                            provider_event={
                                "admin": "system_generated",
                                "sent_at": datetime.now(timezone.utc).isoformat(),
                                "recipient": lead['email'],
                                "subject": rendered_subject
                            }
                        )
                        
                        results.append({
                            'lead_id': lead['lead_id'],
                            'email': lead['email'],
                            'status': 'sent',
                            'subject': rendered_subject
                        })
                        emails_sent += 1
                        
                    else:
                        # Update status to failed
                        self.update_campaign_lead_status(
                            lead['campaign_lead_id'], 'failed', email_result['message']
                        )
                        
                        results.append({
                            'lead_id': lead['lead_id'],
                            'email': lead['email'],
                            'status': 'failed',
                            'error': email_result['message']
                        })
                        emails_failed += 1
                
                except Exception as e:
                    # Handle individual lead processing errors
                    error_msg = f"Error processing lead: {str(e)}"
                    self.update_campaign_lead_status(lead['campaign_lead_id'], 'failed', error_msg)
                    
                    results.append({
                        'lead_id': lead['lead_id'],
                        'email': lead.get('email'),
                        'status': 'failed',
                        'error': error_msg
                    })
                    emails_failed += 1
            
            return {
                'success': True,
                'message': f'Campaign emails processed. {emails_sent} sent, {emails_failed} failed',
                'campaign_id': campaign_id,
                'campaign_name': campaign['name'],
                'emails_sent': emails_sent,
                'emails_failed': emails_failed,
                'total_processed': len(leads_result['leads']),
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error sending campaign emails: {str(e)}',
                'emails_sent': 0,
                'emails_failed': 0,
                'results': []
            }