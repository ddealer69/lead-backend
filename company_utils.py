"""
Company and Company Banner management utilities
Handles CRUD operations for companies and their associated banners
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class CompanyManager:
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
    
    def verify_company_exists(self, company_id: str) -> bool:
        """Verify that the company exists and is active"""
        try:
            result = self.supabase.table('companies').select('id').eq('id', company_id).eq('is_active', True).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    # ===================== COMPANY CRUD OPERATIONS =====================
    
    def create_company(self, account_id: str, name: str, domain: str = None, 
                      notes: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """
        Create a new company
        Returns: {'success': bool, 'message': str, 'company': dict or None}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'company': None
                }
            
            # Check if company name already exists for this account
            result = self.supabase.table('companies').select('id').eq('account_id', account_id).eq('name', name).eq('is_active', True).execute()
            
            if result.data:
                return {
                    'success': False,
                    'message': 'Company with this name already exists for this account',
                    'company': None
                }
            
            # Create company
            company_data = {
                'account_id': account_id,
                'name': name.strip(),
                'domain': domain.strip() if domain else None,
                'notes': notes.strip() if notes else None,
                'metadata': metadata or {},
                'is_active': True
            }
            
            result = self.supabase.table('companies').insert(company_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company created successfully',
                    'company': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create company',
                    'company': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating company: {str(e)}',
                'company': None
            }
    
    def get_company(self, company_id: str) -> Dict[str, Any]:
        """
        Get company by ID
        Returns: {'success': bool, 'message': str, 'company': dict or None}
        """
        try:
            result = self.supabase.table('companies').select('*').eq('id', company_id).eq('is_active', True).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company retrieved successfully',
                    'company': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Company not found',
                    'company': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving company: {str(e)}',
                'company': None
            }
    
    def update_company(self, company_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update company information
        Returns: {'success': bool, 'message': str, 'company': dict or None}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'company': None
                }
            
            # Filter allowed fields
            allowed_fields = ['name', 'domain', 'notes', 'metadata']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'company': None
                }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            # Check for name uniqueness if name is being updated
            if 'name' in filtered_updates:
                company_result = self.supabase.table('companies').select('account_id').eq('id', company_id).execute()
                if company_result.data:
                    account_id = company_result.data[0]['account_id']
                    name_check = self.supabase.table('companies').select('id').eq('account_id', account_id).eq('name', filtered_updates['name']).neq('id', company_id).eq('is_active', True).execute()
                    if name_check.data:
                        return {
                            'success': False,
                            'message': 'Company name already exists for this account',
                            'company': None
                        }
            
            # Update company
            result = self.supabase.table('companies').update(filtered_updates).eq('id', company_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company updated successfully',
                    'company': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update company',
                    'company': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating company: {str(e)}',
                'company': None
            }
    
    def delete_company(self, company_id: str) -> Dict[str, Any]:
        """
        Delete company (soft delete)
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or already inactive'
                }
            
            # Soft delete company
            result = self.supabase.table('companies').update({
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('id', company_id).execute()
            
            # Also soft delete associated banners
            self.supabase.table('company_banners').update({
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('company_id', company_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company and associated banners deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete company'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting company: {str(e)}'
            }
    
    def get_companies_by_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get all companies for an account
        Returns: {'success': bool, 'message': str, 'companies': list}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'companies': []
                }
            
            result = self.supabase.table('companies').select('*').eq('account_id', account_id).eq('is_active', True).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} companies',
                'companies': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving companies: {str(e)}',
                'companies': []
            }
    
    # ===================== COMPANY BANNER CRUD OPERATIONS =====================
    
    def create_company_banner(self, company_id: str, name: str, logo_url: str = None, 
                             signature: str = None, metadata: Dict = None, created_by: str = None) -> Dict[str, Any]:
        """
        Create a new company banner
        Returns: {'success': bool, 'message': str, 'banner': dict or None}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'banner': None
                }
            
            # Create banner
            banner_data = {
                'company_id': company_id,
                'name': name.strip(),
                'logo_url': logo_url.strip() if logo_url else None,
                'signature': signature.strip() if signature else None,
                'metadata': metadata or {},
                'created_by': created_by,
                'is_active': True
            }
            
            result = self.supabase.table('company_banners').insert(banner_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company banner created successfully',
                    'banner': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create company banner',
                    'banner': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating company banner: {str(e)}',
                'banner': None
            }
    
    def get_company_banner(self, banner_id: str) -> Dict[str, Any]:
        """
        Get company banner by ID
        Returns: {'success': bool, 'message': str, 'banner': dict or None}
        """
        try:
            result = self.supabase.table('company_banners').select('*').eq('id', banner_id).eq('is_active', True).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company banner retrieved successfully',
                    'banner': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Company banner not found',
                    'banner': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving company banner: {str(e)}',
                'banner': None
            }
    
    def update_company_banner(self, banner_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update company banner information
        Returns: {'success': bool, 'message': str, 'banner': dict or None}
        """
        try:
            # Verify banner exists
            banner_check = self.supabase.table('company_banners').select('id').eq('id', banner_id).eq('is_active', True).execute()
            if not banner_check.data:
                return {
                    'success': False,
                    'message': 'Company banner not found or inactive',
                    'banner': None
                }
            
            # Filter allowed fields
            allowed_fields = ['name', 'logo_url', 'signature', 'metadata']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'banner': None
                }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            # Update banner
            result = self.supabase.table('company_banners').update(filtered_updates).eq('id', banner_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company banner updated successfully',
                    'banner': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update company banner',
                    'banner': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating company banner: {str(e)}',
                'banner': None
            }
    
    def delete_company_banner(self, banner_id: str) -> Dict[str, Any]:
        """
        Delete company banner (soft delete)
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify banner exists
            banner_check = self.supabase.table('company_banners').select('id').eq('id', banner_id).eq('is_active', True).execute()
            if not banner_check.data:
                return {
                    'success': False,
                    'message': 'Company banner not found or already inactive'
                }
            
            # Soft delete banner
            result = self.supabase.table('company_banners').update({
                'is_active': False,
                'updated_at': datetime.now().isoformat()
            }).eq('id', banner_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Company banner deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete company banner'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting company banner: {str(e)}'
            }
    
    def get_banners_by_company(self, company_id: str) -> Dict[str, Any]:
        """
        Get all banners for a company
        Returns: {'success': bool, 'message': str, 'banners': list}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'banners': []
                }
            
            result = self.supabase.table('company_banners').select('*').eq('company_id', company_id).eq('is_active', True).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} banners',
                'banners': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving banners: {str(e)}',
                'banners': []
            }
    
    # ===================== COMBINED OPERATIONS =====================
    
    def get_account_companies_with_banners(self, account_id: str) -> Dict[str, Any]:
        """
        Get all companies and their banners for an account
        Returns: {'success': bool, 'message': str, 'data': dict}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'data': {}
                }
            
            # Get companies
            companies_result = self.supabase.table('companies').select('*').eq('account_id', account_id).eq('is_active', True).order('created_at', desc=True).execute()
            
            companies_with_banners = []
            
            for company in companies_result.data:
                # Get banners for each company
                banners_result = self.supabase.table('company_banners').select('*').eq('company_id', company['id']).eq('is_active', True).order('created_at', desc=True).execute()
                
                company_with_banners = {
                    **company,
                    'banners': banners_result.data
                }
                companies_with_banners.append(company_with_banners)
            
            return {
                'success': True,
                'message': f'Retrieved {len(companies_with_banners)} companies with their banners',
                'data': {
                    'account_id': account_id,
                    'companies': companies_with_banners,
                    'total_companies': len(companies_with_banners),
                    'total_banners': sum(len(c['banners']) for c in companies_with_banners)
                }
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving account data: {str(e)}',
                'data': {}
            }
    
    def create_company_with_banner(self, account_id: str, company_name: str, company_domain: str = None,
                                  company_notes: str = None, company_metadata: Dict = None,
                                  banner_name: str = None, logo_url: str = None, signature: str = None,
                                  banner_metadata: Dict = None, created_by: str = None) -> Dict[str, Any]:
        """
        Create company and banner in one operation
        Returns: {'success': bool, 'message': str, 'company': dict, 'banner': dict}
        """
        try:
            # Create company first
            company_result = self.create_company(account_id, company_name, company_domain, company_notes, company_metadata)
            
            if not company_result['success']:
                return {
                    'success': False,
                    'message': company_result['message'],
                    'company': None,
                    'banner': None
                }
            
            company = company_result['company']
            
            # Create banner with same name as company if banner_name not provided
            banner_name = banner_name or company_name
            
            banner_result = self.create_company_banner(
                company['id'], banner_name, logo_url, signature, banner_metadata, created_by
            )
            
            return {
                'success': True,
                'message': 'Company and banner created successfully',
                'company': company,
                'banner': banner_result['banner'] if banner_result['success'] else None
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating company with banner: {str(e)}',
                'company': None,
                'banner': None
            }