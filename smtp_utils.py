"""
SMTP Credentials management utilities
Handles CRUD operations for SMTP email configurations with plain text password storage
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class SMTPManager:
    def __init__(self):
        """Initialize Supabase client with service role key to bypass RLS"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def verify_account_exists(self, account_id: str) -> bool:
        """Verify that the account exists and is active"""
        try:
            result = self.supabase.table('accounts').select('id').eq('id', account_id).eq('is_active', True).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    def verify_user_exists(self, user_id: str) -> bool:
        """Verify that the user exists and is active"""
        try:
            result = self.supabase.table('users').select('id').eq('id', user_id).eq('is_active', True).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    # ===================== SMTP CREDENTIALS CRUD OPERATIONS =====================
    
    def create_smtp_credentials(self, account_id: str, display_name: str, smtp_host: str, 
                               smtp_port: int, username: str, password: str, 
                               auth_type: str = 'plain', rate_limit_per_hour: int = None,
                               metadata: Dict = None, created_by: str = None) -> Dict[str, Any]:
        """
        Create new SMTP credentials
        Returns: {'success': bool, 'message': str, 'smtp_credentials': dict or None}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'smtp_credentials': None
                }
            
            # Verify user exists if created_by is provided
            if created_by and not self.verify_user_exists(created_by):
                return {
                    'success': False,
                    'message': 'User (created_by) not found or inactive',
                    'smtp_credentials': None
                }
            
            # Validate auth_type
            if auth_type not in ['plain', 'oauth2', 'app_password']:
                return {
                    'success': False,
                    'message': 'Invalid auth_type. Must be: plain, oauth2, or app_password',
                    'smtp_credentials': None
                }
            
            # Validate SMTP port
            if not isinstance(smtp_port, int) or smtp_port < 1 or smtp_port > 65535:
                return {
                    'success': False,
                    'message': 'Invalid SMTP port. Must be between 1 and 65535',
                    'smtp_credentials': None
                }
            
            # Check if display name already exists for this account
            result = self.supabase.table('smtp_credentials').select('id').eq('account_id', account_id).eq('display_name', display_name).execute()
            
            if result.data:
                return {
                    'success': False,
                    'message': 'SMTP credentials with this display name already exists for this account',
                    'smtp_credentials': None
                }
            
            # Create SMTP credentials
            current_time = datetime.now().isoformat()
            smtp_data = {
                'account_id': account_id,
                'created_by': created_by,
                'display_name': display_name.strip(),
                'smtp_host': smtp_host.strip(),
                'smtp_port': smtp_port,
                'username': username.strip(),
                'encrypted_password_ciphertext': password,  # Store password as plain text
                'auth_type': auth_type,
                'verified': False,
                'last_verified_at': current_time,
                'rate_limit_per_hour': rate_limit_per_hour,
                'metadata': metadata or {}
            }
            
            result = self.supabase.table('smtp_credentials').insert(smtp_data).execute()
            
            if result.data:
                # Remove password from response for security
                response_data = result.data[0].copy()
                response_data.pop('encrypted_password_ciphertext', None)
                
                return {
                    'success': True,
                    'message': 'SMTP credentials created successfully',
                    'smtp_credentials': response_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create SMTP credentials',
                    'smtp_credentials': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating SMTP credentials: {str(e)}',
                'smtp_credentials': None
            }
    
    def get_smtp_credentials(self, smtp_id: str, include_password: bool = False) -> Dict[str, Any]:
        """
        Get SMTP credentials by ID
        Returns: {'success': bool, 'message': str, 'smtp_credentials': dict or None}
        """
        try:
            if include_password:
                result = self.supabase.table('smtp_credentials').select('*').eq('id', smtp_id).execute()
            else:
                # Exclude encrypted password from normal queries
                fields = 'id, account_id, created_by, display_name, smtp_host, smtp_port, username, auth_type, verified, last_verified_at, rate_limit_per_hour, metadata, created_at, updated_at'
                result = self.supabase.table('smtp_credentials').select(fields).eq('id', smtp_id).execute()
            
            if result.data:
                smtp_data = result.data[0].copy()
                
                # If password is requested, get plain text password and add to response
                if include_password and 'encrypted_password_ciphertext' in smtp_data:
                    plain_password = smtp_data.get('encrypted_password_ciphertext')
                    if plain_password:
                        smtp_data['password'] = plain_password
                    else:
                        smtp_data['password'] = "NO_PASSWORD_STORED"
                    
                    # Remove the database field from response
                    smtp_data.pop('encrypted_password_ciphertext', None)
                
                return {
                    'success': True,
                    'message': 'SMTP credentials retrieved successfully',
                    'smtp_credentials': smtp_data
                }
            else:
                return {
                    'success': False,
                    'message': 'SMTP credentials not found',
                    'smtp_credentials': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving SMTP credentials: {str(e)}',
                'smtp_credentials': None
            }
    
    def update_smtp_credentials(self, smtp_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update SMTP credentials information
        Returns: {'success': bool, 'message': str, 'smtp_credentials': dict or None}
        """
        try:
            # Verify SMTP credentials exist
            existing = self.get_smtp_credentials(smtp_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'SMTP credentials not found',
                    'smtp_credentials': None
                }
            
            # Filter allowed fields
            allowed_fields = ['display_name', 'smtp_host', 'smtp_port', 'username', 'auth_type', 
                            'verified', 'rate_limit_per_hour', 'metadata']
            filtered_updates = {}
            
            for key, value in updates.items():
                if key in allowed_fields:
                    if key == 'smtp_port':
                        # Validate SMTP port
                        if not isinstance(value, int) or value < 1 or value > 65535:
                            return {
                                'success': False,
                                'message': 'Invalid SMTP port. Must be between 1 and 65535',
                                'smtp_credentials': None
                            }
                        filtered_updates[key] = value
                    elif key == 'auth_type':
                        # Validate auth_type
                        if value not in ['plain', 'oauth2', 'app_password']:
                            return {
                                'success': False,
                                'message': 'Invalid auth_type. Must be: plain, oauth2, or app_password',
                                'smtp_credentials': None
                            }
                        filtered_updates[key] = value
                    else:
                        filtered_updates[key] = value
            
            # Handle password update separately
            if 'password' in updates:
                filtered_updates['encrypted_password_ciphertext'] = updates['password']  # Store password as plain text
                filtered_updates['last_verified_at'] = datetime.now().isoformat()
                filtered_updates['verified'] = False  # Reset verification when password changes
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'smtp_credentials': None
                }
            
            # Check for display name uniqueness if display_name is being updated
            if 'display_name' in filtered_updates:
                account_id = existing['smtp_credentials']['account_id']
                name_check = self.supabase.table('smtp_credentials').select('id').eq('account_id', account_id).eq('display_name', filtered_updates['display_name']).neq('id', smtp_id).execute()
                if name_check.data:
                    return {
                        'success': False,
                        'message': 'Display name already exists for this account',
                        'smtp_credentials': None
                    }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            # Update SMTP credentials
            result = self.supabase.table('smtp_credentials').update(filtered_updates).eq('id', smtp_id).execute()
            
            if result.data:
                # Remove password from response for security
                response_data = result.data[0].copy()
                response_data.pop('encrypted_password_ciphertext', None)
                
                return {
                    'success': True,
                    'message': 'SMTP credentials updated successfully',
                    'smtp_credentials': response_data
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update SMTP credentials',
                    'smtp_credentials': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating SMTP credentials: {str(e)}',
                'smtp_credentials': None
            }
    
    def delete_smtp_credentials(self, smtp_id: str) -> Dict[str, Any]:
        """
        Delete SMTP credentials (hard delete since it's sensitive data)
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify SMTP credentials exist
            existing = self.get_smtp_credentials(smtp_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'SMTP credentials not found'
                }
            
            # Hard delete SMTP credentials (sensitive data)
            result = self.supabase.table('smtp_credentials').delete().eq('id', smtp_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'SMTP credentials deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete SMTP credentials'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting SMTP credentials: {str(e)}'
            }
    
    def get_smtp_credentials_by_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get all SMTP credentials for an account (without passwords)
        Returns: {'success': bool, 'message': str, 'smtp_credentials': list}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'smtp_credentials': []
                }
            
            # Exclude encrypted password from results
            fields = 'id, account_id, created_by, display_name, smtp_host, smtp_port, username, auth_type, verified, last_verified_at, rate_limit_per_hour, metadata, created_at, updated_at'
            result = self.supabase.table('smtp_credentials').select(fields).eq('account_id', account_id).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} SMTP credentials',
                'smtp_credentials': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving SMTP credentials: {str(e)}',
                'smtp_credentials': []
            }
    
    def verify_smtp_credentials(self, smtp_id: str, test_connection: bool = False) -> Dict[str, Any]:
        """
        Verify SMTP credentials (mark as verified and update timestamp)
        In production, this would actually test the SMTP connection
        Returns: {'success': bool, 'message': str, 'verified': bool}
        """
        try:
            # Get SMTP credentials
            existing = self.get_smtp_credentials(smtp_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'SMTP credentials not found',
                    'verified': False
                }
            
            # In production, you would test the actual SMTP connection here
            if test_connection:
                # TODO: Implement actual SMTP connection test
                # For now, we'll simulate a successful test
                pass
            
            # Update verification status
            current_time = datetime.now().isoformat()
            result = self.supabase.table('smtp_credentials').update({
                'verified': True,
                'last_verified_at': current_time,
                'updated_at': current_time
            }).eq('id', smtp_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'SMTP credentials verified successfully',
                    'verified': True
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to verify SMTP credentials',
                    'verified': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error verifying SMTP credentials: {str(e)}',
                'verified': False
            }
    
    def get_verified_smtp_credentials(self, account_id: str) -> Dict[str, Any]:
        """
        Get only verified SMTP credentials for an account
        Returns: {'success': bool, 'message': str, 'smtp_credentials': list}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'smtp_credentials': []
                }
            
            # Get only verified SMTP credentials
            fields = 'id, account_id, created_by, display_name, smtp_host, smtp_port, username, auth_type, verified, last_verified_at, rate_limit_per_hour, metadata, created_at, updated_at'
            result = self.supabase.table('smtp_credentials').select(fields).eq('account_id', account_id).eq('verified', True).order('last_verified_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} verified SMTP credentials',
                'smtp_credentials': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving verified SMTP credentials: {str(e)}',
                'smtp_credentials': []
            }