"""
Database utilities for user authentication and management
Uses Supabase with service role key to bypass RLS
"""

import os
import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize Supabase client with service role key to bypass RLS"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == password_hash
    
    def get_or_create_account(self, account_name: str) -> str:
        """Get existing account or create new one, returns account_id"""
        try:
            # Check if account exists
            result = self.supabase.table('accounts').select('id').eq('name', account_name).eq('is_active', True).execute()
            
            if result.data:
                return result.data[0]['id']
            
            # Create new account
            account_data = {
                'name': account_name,
                'plan': 'free',
                'is_active': True
            }
            
            result = self.supabase.table('accounts').insert(account_data).execute()
            return result.data[0]['id']
            
        except Exception as e:
            raise Exception(f"Error managing account: {str(e)}")
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password
        Returns: {'success': bool, 'message': str, 'user': dict or None}
        """
        try:
            # Get user by email
            result = self.supabase.table('users').select('*').eq('email', email).eq('is_active', True).execute()
            
            if not result.data:
                return {
                    'success': False,
                    'message': 'Email not found. Please create a new account.',
                    'user': None
                }
            
            user = result.data[0]
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return {
                    'success': False,
                    'message': 'Password does not match.',
                    'user': None
                }
            
            # Update last login
            self.supabase.table('users').update({
                'last_login': datetime.now().isoformat()
            }).eq('id', user['id']).execute()
            
            # Remove password hash from response
            user.pop('password_hash', None)
            
            return {
                'success': True,
                'message': 'Authentication successful.',
                'user': user
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Authentication error: {str(e)}',
                'user': None
            }
    
    def create_user(self, email: str, password: str, full_name: str, account_name: str, role: str = 'member') -> Dict[str, Any]:
        """
        Create new user account
        Returns: {'success': bool, 'message': str, 'user': dict or None}
        """
        try:
            # Check if user already exists
            result = self.supabase.table('users').select('id').eq('email', email).eq('is_active', True).execute()
            
            if result.data:
                return {
                    'success': False,
                    'message': 'User with this email already exists.',
                    'user': None
                }
            
            # Get or create account
            account_id = self.get_or_create_account(account_name)
            
            # Create user
            user_data = {
                'account_id': account_id,
                'email': email,
                'full_name': full_name,
                'password_hash': self.hash_password(password),
                'role': role,
                'is_active': True
            }
            
            result = self.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user = result.data[0]
                # Remove password hash from response
                user.pop('password_hash', None)
                
                return {
                    'success': True,
                    'message': 'User created successfully.',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create user.',
                    'user': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating user: {str(e)}',
                'user': None
            }
    
    def delete_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Delete user account (soft delete by setting is_active to False)
        Returns: {'success': bool, 'message': str}
        """
        try:
            # First authenticate the user
            auth_result = self.authenticate_user(email, password)
            
            if not auth_result['success']:
                return {
                    'success': False,
                    'message': auth_result['message']
                }
            
            # Soft delete user
            result = self.supabase.table('users').update({
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('email', email).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'User account deleted successfully.'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete user account.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting user: {str(e)}'
            }
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user details by email (without password hash)"""
        try:
            result = self.supabase.table('users').select('id, account_id, email, full_name, role, last_login, is_active, prefs, created_at, updated_at').eq('email', email).eq('is_active', True).execute()
            
            return result.data[0] if result.data else None
            
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def update_user_profile(self, email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile (except password and email)"""
        try:
            allowed_fields = ['full_name', 'role', 'prefs']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update.'
                }
            
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            result = self.supabase.table('users').update(filtered_updates).eq('email', email).eq('is_active', True).execute()
            
            if result.data:
                user = result.data[0]
                user.pop('password_hash', None)
                
                return {
                    'success': True,
                    'message': 'Profile updated successfully.',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update profile.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            }
