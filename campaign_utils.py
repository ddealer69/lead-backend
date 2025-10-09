"""
Campaign management utilities
Handles email campaigns and campaign leads with comprehensive CRUD operations
"""

import os
import json
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

class CampaignManager:
    def __init__(self):
        """Initialize Supabase client"""
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
    
    def verify_user_exists(self, user_id: str) -> bool:
        """Verify that the user exists and is active"""
        try:
            result = self.supabase.table('users').select('id').eq('id', user_id).eq('is_active', True).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    def verify_query_exists(self, query_id: str) -> bool:
        """Verify that the lead exists (query_id refers to lead id)"""
        try:
            result = self.supabase.table('leads').select('id').eq('id', query_id).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    def get_lead_details(self, lead_id: str) -> Dict[str, Any]:
        """
        Get lead details for personalization variables
        Returns: {'success': bool, 'data': dict or None}
        """
        try:
            result = self.supabase.table('leads').select(
                'id, source_link, full_name, source_name, title, company_name'
            ).eq('id', lead_id).execute()
            
            if result.data:
                lead_data = result.data[0]
                personalization_vars = {
                    'source_link': lead_data.get('source_link'),
                    'full_name': lead_data.get('full_name'),
                    'source_name': lead_data.get('source_name'),
                    'title': lead_data.get('title'),
                    'company_name': lead_data.get('company_name')
                }
                return {
                    'success': True,
                    'data': personalization_vars
                }
            else:
                return {
                    'success': False,
                    'data': None
                }
        except Exception:
            return {
                'success': False,
                'data': None
            }
    
    # ===================== CAMPAIGNS CRUD OPERATIONS =====================
    
    def create_campaign(self, account_id: str, company_id: str, name: str,
                       campaign_type: str = 'email', created_by: str = None,
                       company_banner_id: str = None, smtp_credential_id: str = None,
                       subject_template: str = None, body_template: str = None,
                       send_rate_per_hour: int = None, max_retries: int = 3,
                       status: str = 'draft') -> Dict[str, Any]:
        """
        Create new campaign
        Returns: {'success': bool, 'message': str, 'campaign': dict or None}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'campaign': None
                }
            
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'campaign': None
                }
            
            # Verify user exists if provided
            if created_by and not self.verify_user_exists(created_by):
                return {
                    'success': False,
                    'message': 'User (created_by) not found or inactive',
                    'campaign': None
                }
            
            # Validate required fields
            if not name or not name.strip():
                return {
                    'success': False,
                    'message': 'Campaign name is required',
                    'campaign': None
                }
            
            # Validate campaign_type
            valid_types = ['email', 'linkedin_extension', 'other']
            if campaign_type not in valid_types:
                return {
                    'success': False,
                    'message': f'Invalid campaign_type. Must be one of: {", ".join(valid_types)}',
                    'campaign': None
                }
            
            # Validate status
            valid_statuses = ['draft', 'running', 'paused', 'completed', 'cancelled']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'campaign': None
                }
            
            # Create campaign data
            campaign_data = {
                'account_id': account_id,
                'company_id': company_id,
                'name': name.strip(),
                'campaign_type': campaign_type,
                'created_by': created_by,
                'company_banner_id': company_banner_id,
                'smtp_credential_id': smtp_credential_id,
                'subject_template': subject_template.strip() if subject_template else None,
                'body_template': body_template.strip() if body_template else None,
                'send_rate_per_hour': send_rate_per_hour,
                'max_retries': max_retries,
                'status': status
            }
            
            result = self.supabase.table('campaigns').insert(campaign_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign created successfully',
                    'campaign': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create campaign',
                    'campaign': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating campaign: {str(e)}',
                'campaign': None
            }
    
    def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign by ID
        Returns: {'success': bool, 'message': str, 'campaign': dict or None}
        """
        try:
            result = self.supabase.table('campaigns').select('*').eq('id', campaign_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign retrieved successfully',
                    'campaign': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'campaign': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign: {str(e)}',
                'campaign': None
            }
    
    def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update campaign information
        Returns: {'success': bool, 'message': str, 'campaign': dict or None}
        """
        try:
            # Verify campaign exists
            existing = self.get_campaign(campaign_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'campaign': None
                }
            
            # Filter allowed fields
            allowed_fields = ['name', 'campaign_type', 'company_banner_id', 'smtp_credential_id',
                            'subject_template', 'body_template', 'send_rate_per_hour', 'max_retries',
                            'status', 'started_at', 'finished_at']
            filtered_updates = {}
            
            for key, value in updates.items():
                if key in allowed_fields:
                    if key == 'campaign_type':
                        valid_types = ['email', 'linkedin_extension', 'other']
                        if value not in valid_types:
                            return {
                                'success': False,
                                'message': f'Invalid campaign_type. Must be one of: {", ".join(valid_types)}',
                                'campaign': None
                            }
                    elif key == 'status':
                        valid_statuses = ['draft', 'running', 'paused', 'completed', 'cancelled']
                        if value not in valid_statuses:
                            return {
                                'success': False,
                                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                                'campaign': None
                            }
                    elif key == 'name' and (not value or not value.strip()):
                        return {
                            'success': False,
                            'message': 'Campaign name cannot be empty',
                            'campaign': None
                        }
                    
                    filtered_updates[key] = value
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'campaign': None
                }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Update campaign
            result = self.supabase.table('campaigns').update(filtered_updates).eq('id', campaign_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign updated successfully',
                    'campaign': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update campaign',
                    'campaign': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating campaign: {str(e)}',
                'campaign': None
            }
    
    def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Delete campaign
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify campaign exists
            existing = self.get_campaign(campaign_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Campaign not found'
                }
            
            # Delete campaign (this will cascade delete campaign_leads)
            result = self.supabase.table('campaigns').delete().eq('id', campaign_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete campaign'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting campaign: {str(e)}'
            }
    
    def get_campaigns_by_company(self, company_id: str, status: str = None) -> Dict[str, Any]:
        """
        Get all campaigns for a company
        Returns: {'success': bool, 'message': str, 'campaigns': list}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'campaigns': []
                }
            
            query_builder = self.supabase.table('campaigns').select('*').eq('company_id', company_id)
            
            if status:
                valid_statuses = ['draft', 'running', 'paused', 'completed', 'cancelled']
                if status not in valid_statuses:
                    return {
                        'success': False,
                        'message': f'Invalid status filter. Must be one of: {", ".join(valid_statuses)}',
                        'campaigns': []
                    }
                query_builder = query_builder.eq('status', status)
            
            result = query_builder.order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} campaigns',
                'campaigns': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaigns: {str(e)}',
                'campaigns': []
            }
    
    def get_campaigns_by_account(self, account_id: str, status: str = None) -> Dict[str, Any]:
        """
        Get all campaigns for an account
        Returns: {'success': bool, 'message': str, 'campaigns': list}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'campaigns': []
                }
            
            query_builder = self.supabase.table('campaigns').select('*').eq('account_id', account_id)
            
            if status:
                valid_statuses = ['draft', 'running', 'paused', 'completed', 'cancelled']
                if status not in valid_statuses:
                    return {
                        'success': False,
                        'message': f'Invalid status filter. Must be one of: {", ".join(valid_statuses)}',
                        'campaigns': []
                    }
                query_builder = query_builder.eq('status', status)
            
            result = query_builder.order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} campaigns',
                'campaigns': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaigns: {str(e)}',
                'campaigns': []
            }
    
    # ===================== CAMPAIGN LEADS CRUD OPERATIONS =====================
    
    def create_campaign_lead(self, campaign_id: str, query_id: str,
                           status: str = 'queued', send_attempts: int = 0,
                           last_sent_at: str = None, scheduled_at: str = None,
                           personalization_vars: Dict[str, Any] = None,
                           error: str = None) -> Dict[str, Any]:
        """
        Create new campaign lead
        Returns: {'success': bool, 'message': str, 'campaign_lead': dict or None}
        """
        try:
            # Verify campaign exists
            campaign_result = self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'campaign_lead': None
                }
            
            # Verify lead exists (query_id refers to lead id)
            if not self.verify_query_exists(query_id):
                return {
                    'success': False,
                    'message': 'Lead not found',
                    'campaign_lead': None
                }
            
            # Validate status
            valid_statuses = ['queued', 'sent', 'failed', 'bounced', 'opened', 'clicked', 'scheduled']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'campaign_lead': None
                }
            
            # Check for duplicate campaign_lead
            existing_result = self.supabase.table('campaign_leads').select('id').eq('campaign_id', campaign_id).eq('query_id', query_id).execute()
            if existing_result.data:
                return {
                    'success': False,
                    'message': 'Campaign lead already exists for this campaign and query combination',
                    'campaign_lead': None
                }
            
            # Get personalization variables from lead data if not provided
            if personalization_vars is None:
                lead_details = self.get_lead_details(query_id)
                if lead_details['success']:
                    personalization_vars = lead_details['data']
                else:
                    personalization_vars = {}
            
            # Create campaign lead data
            campaign_lead_data = {
                'campaign_id': campaign_id,
                'query_id': query_id,
                'status': status,
                'send_attempts': send_attempts,
                'last_sent_at': last_sent_at,
                'scheduled_at': scheduled_at,
                'personalization_vars': personalization_vars,
                'error': error.strip() if error else None
            }
            
            result = self.supabase.table('campaign_leads').insert(campaign_lead_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign lead created successfully',
                    'campaign_lead': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create campaign lead',
                    'campaign_lead': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating campaign lead: {str(e)}',
                'campaign_lead': None
            }
    
    def get_campaign_lead(self, campaign_lead_id: str) -> Dict[str, Any]:
        """
        Get campaign lead by ID
        Returns: {'success': bool, 'message': str, 'campaign_lead': dict or None}
        """
        try:
            result = self.supabase.table('campaign_leads').select('*').eq('id', campaign_lead_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign lead retrieved successfully',
                    'campaign_lead': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Campaign lead not found',
                    'campaign_lead': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign lead: {str(e)}',
                'campaign_lead': None
            }
    
    def update_campaign_lead(self, campaign_lead_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update campaign lead information
        Returns: {'success': bool, 'message': str, 'campaign_lead': dict or None}
        """
        try:
            # Verify campaign lead exists
            existing = self.get_campaign_lead(campaign_lead_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Campaign lead not found',
                    'campaign_lead': None
                }
            
            # Filter allowed fields
            allowed_fields = ['status', 'send_attempts', 'last_sent_at', 'scheduled_at',
                            'personalization_vars', 'error']
            filtered_updates = {}
            
            for key, value in updates.items():
                if key in allowed_fields:
                    if key == 'status':
                        valid_statuses = ['queued', 'sent', 'failed', 'bounced', 'opened', 'clicked', 'scheduled']
                        if value not in valid_statuses:
                            return {
                                'success': False,
                                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                                'campaign_lead': None
                            }
                    
                    filtered_updates[key] = value
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'campaign_lead': None
                }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            # Update campaign lead
            result = self.supabase.table('campaign_leads').update(filtered_updates).eq('id', campaign_lead_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign lead updated successfully',
                    'campaign_lead': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update campaign lead',
                    'campaign_lead': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating campaign lead: {str(e)}',
                'campaign_lead': None
            }
    
    def delete_campaign_lead(self, campaign_lead_id: str) -> Dict[str, Any]:
        """
        Delete campaign lead
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify campaign lead exists
            existing = self.get_campaign_lead(campaign_lead_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Campaign lead not found'
                }
            
            # Delete campaign lead
            result = self.supabase.table('campaign_leads').delete().eq('id', campaign_lead_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Campaign lead deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete campaign lead'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting campaign lead: {str(e)}'
            }
    
    def get_campaign_leads_by_campaign(self, campaign_id: str, status: str = None) -> Dict[str, Any]:
        """
        Get all campaign leads for a campaign
        Returns: {'success': bool, 'message': str, 'campaign_leads': list}
        """
        try:
            # Verify campaign exists
            campaign_result = self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'campaign_leads': []
                }
            
            query_builder = self.supabase.table('campaign_leads').select('*').eq('campaign_id', campaign_id)
            
            if status:
                valid_statuses = ['queued', 'sent', 'failed', 'bounced', 'opened', 'clicked', 'scheduled']
                if status not in valid_statuses:
                    return {
                        'success': False,
                        'message': f'Invalid status filter. Must be one of: {", ".join(valid_statuses)}',
                        'campaign_leads': []
                    }
                query_builder = query_builder.eq('status', status)
            
            result = query_builder.order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} campaign leads',
                'campaign_leads': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign leads: {str(e)}',
                'campaign_leads': []
            }
    
    def get_campaign_leads_by_query(self, query_id: str) -> Dict[str, Any]:
        """
        Get all campaign leads for a query
        Returns: {'success': bool, 'message': str, 'campaign_leads': list}
        """
        try:
            # Verify query exists
            if not self.verify_query_exists(query_id):
                return {
                    'success': False,
                    'message': 'Query not found',
                    'campaign_leads': []
                }
            
            result = self.supabase.table('campaign_leads').select('*').eq('query_id', query_id).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} campaign leads',
                'campaign_leads': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign leads: {str(e)}',
                'campaign_leads': []
            }
    
    def get_campaign_leads_by_company(self, company_id: str, status: str = None) -> Dict[str, Any]:
        """
        Get all campaign leads for a company (through campaigns)
        Returns: {'success': bool, 'message': str, 'campaign_leads': list}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'campaign_leads': []
                }
            
            # Get all campaigns for this company
            campaigns_result = self.get_campaigns_by_company(company_id)
            if not campaigns_result['success']:
                return {
                    'success': False,
                    'message': campaigns_result['message'],
                    'campaign_leads': []
                }
            
            campaign_ids = [campaign['id'] for campaign in campaigns_result['campaigns']]
            
            if not campaign_ids:
                return {
                    'success': True,
                    'message': 'No campaigns found for this company',
                    'campaign_leads': []
                }
            
            # Build query for campaign leads
            query_builder = self.supabase.table('campaign_leads').select('*').in_('campaign_id', campaign_ids)
            
            if status:
                valid_statuses = ['queued', 'sent', 'failed', 'bounced', 'opened', 'clicked', 'scheduled']
                if status not in valid_statuses:
                    return {
                        'success': False,
                        'message': f'Invalid status filter. Must be one of: {", ".join(valid_statuses)}',
                        'campaign_leads': []
                    }
                query_builder = query_builder.eq('status', status)
            
            result = query_builder.order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} campaign leads',
                'campaign_leads': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign leads: {str(e)}',
                'campaign_leads': []
            }
    
    # ===================== BULK OPERATIONS =====================
    
    def bulk_create_campaign_leads(self, campaign_id: str, query_ids: List[str],
                                 status: str = 'queued', scheduled_at: str = None) -> Dict[str, Any]:
        """
        Create multiple campaign leads for a campaign
        Returns: {'success': bool, 'message': str, 'results': list}
        """
        try:
            # Verify campaign exists
            campaign_result = self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'results': []
                }
            
            if not query_ids:
                return {
                    'success': False,
                    'message': 'No query IDs provided',
                    'results': []
                }
            
            # Validate status
            valid_statuses = ['queued', 'sent', 'failed', 'bounced', 'opened', 'clicked', 'scheduled']
            if status not in valid_statuses:
                return {
                    'success': False,
                    'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'results': []
                }
            
            results = []
            successful = 0
            failed = 0
            
            for query_id in query_ids:
                result = self.create_campaign_lead(
                    campaign_id=campaign_id,
                    query_id=query_id,
                    status=status,
                    scheduled_at=scheduled_at
                )
                
                if result['success']:
                    successful += 1
                    results.append(result['campaign_lead'])
                else:
                    failed += 1
                    results.append({
                        'error': result['message'],
                        'query_id': query_id
                    })
            
            return {
                'success': True,
                'message': f'Bulk creation completed. {successful} successful, {failed} failed',
                'total_processed': len(query_ids),
                'successful': successful,
                'failed': failed,
                'results': results
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error in bulk campaign lead creation: {str(e)}',
                'results': []
            }
    
    # ===================== CAMPAIGN STATISTICS =====================
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get campaign statistics including lead counts by status
        Returns: {'success': bool, 'message': str, 'stats': dict}
        """
        try:
            # Verify campaign exists
            campaign_result = self.get_campaign(campaign_id)
            if not campaign_result['success']:
                return {
                    'success': False,
                    'message': 'Campaign not found',
                    'stats': {}
                }
            
            # Get all campaign leads for this campaign
            leads_result = self.get_campaign_leads_by_campaign(campaign_id)
            if not leads_result['success']:
                return {
                    'success': False,
                    'message': leads_result['message'],
                    'stats': {}
                }
            
            campaign_leads = leads_result['campaign_leads']
            
            # Calculate statistics
            stats = {
                'total_leads': len(campaign_leads),
                'queued': 0,
                'sent': 0,
                'failed': 0,
                'bounced': 0,
                'opened': 0,
                'clicked': 0,
                'scheduled': 0
            }
            
            for lead in campaign_leads:
                status = lead.get('status', 'queued')
                if status in stats:
                    stats[status] += 1
            
            # Calculate rates
            if stats['total_leads'] > 0:
                stats['success_rate'] = round((stats['sent'] / stats['total_leads']) * 100, 2)
                stats['failure_rate'] = round((stats['failed'] / stats['total_leads']) * 100, 2)
                stats['bounce_rate'] = round((stats['bounced'] / stats['total_leads']) * 100, 2)
                
                if stats['sent'] > 0:
                    stats['open_rate'] = round((stats['opened'] / stats['sent']) * 100, 2)
                    stats['click_rate'] = round((stats['clicked'] / stats['sent']) * 100, 2)
                else:
                    stats['open_rate'] = 0.0
                    stats['click_rate'] = 0.0
            else:
                stats['success_rate'] = 0.0
                stats['failure_rate'] = 0.0
                stats['bounce_rate'] = 0.0
                stats['open_rate'] = 0.0
                stats['click_rate'] = 0.0
            
            return {
                'success': True,
                'message': 'Campaign statistics retrieved successfully',
                'stats': stats
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving campaign statistics: {str(e)}',
                'stats': {}
            }


class EmailDeliveryLogsManager:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def create_email_delivery_log(self, campaign_lead_id: str = None, campaign_id: str = None,
                                smtp_credential_id: str = None, recipient: str = None,
                                event_type: str = 'delivered', provider_event: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create new email delivery log
        Returns: {'success': bool, 'message': str, 'log': dict or None}
        """
        try:
            # Validate event_type
            valid_event_types = ['delivered', 'bounced', 'open', 'click', 'complaint']
            if event_type not in valid_event_types:
                return {
                    'success': False,
                    'message': f'Invalid event_type. Must be one of: {", ".join(valid_event_types)}',
                    'log': None
                }
            
            # Set default provider_event if not provided
            if provider_event is None:
                provider_event = {"admin": "system_generated"}
            
            # Create log data
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
                    'message': 'Email delivery log created successfully',
                    'log': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create email delivery log',
                    'log': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating email delivery log: {str(e)}',
                'log': None
            }
    
    def get_delivery_logs_by_campaign(self, campaign_id: str, event_type: str = None) -> Dict[str, Any]:
        """
        Get all delivery logs for a campaign
        Returns: {'success': bool, 'message': str, 'logs': list}
        """
        try:
            query_builder = self.supabase.table('email_delivery_logs').select('*').eq('campaign_id', campaign_id)
            
            if event_type:
                valid_event_types = ['delivered', 'bounced', 'open', 'click', 'complaint']
                if event_type not in valid_event_types:
                    return {
                        'success': False,
                        'message': f'Invalid event_type filter. Must be one of: {", ".join(valid_event_types)}',
                        'logs': []
                    }
                query_builder = query_builder.eq('event_type', event_type)
            
            result = query_builder.order('occurred_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} delivery logs',
                'logs': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving delivery logs: {str(e)}',
                'logs': []
            }
    
    def get_delivery_logs_by_campaign_lead(self, campaign_lead_id: str) -> Dict[str, Any]:
        """
        Get all delivery logs for a campaign lead
        Returns: {'success': bool, 'message': str, 'logs': list}
        """
        try:
            result = self.supabase.table('email_delivery_logs').select('*').eq('campaign_lead_id', campaign_lead_id).order('occurred_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} delivery logs',
                'logs': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving delivery logs: {str(e)}',
                'logs': []
            }
    
    def get_delivery_log(self, log_id: str) -> Dict[str, Any]:
        """
        Get delivery log by ID
        Returns: {'success': bool, 'message': str, 'log': dict or None}
        """
        try:
            result = self.supabase.table('email_delivery_logs').select('*').eq('id', log_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Delivery log retrieved successfully',
                    'log': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Delivery log not found',
                    'log': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving delivery log: {str(e)}',
                'log': None
            }
    
    def delete_delivery_log(self, log_id: str) -> Dict[str, Any]:
        """
        Delete delivery log
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify log exists
            existing = self.get_delivery_log(log_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Delivery log not found'
                }
            
            # Delete log
            result = self.supabase.table('email_delivery_logs').delete().eq('id', log_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Delivery log deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete delivery log'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting delivery log: {str(e)}'
            }