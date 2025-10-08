"""
Leads management utilities
Handles LinkedIn profile enrichment using Apify API
"""

import os
import json
import requests
import time
import uuid
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class LeadsManager:
    def __init__(self):
        """Initialize Supabase client and Apify API credentials"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Apify API credentials - loaded from environment
        self.apify_api_token = os.getenv('APIFY_API_TOKEN')
        if not self.apify_api_token:
            raise ValueError("Missing APIFY_API_TOKEN in environment")
        
        self.apify_base_url = "https://api.apify.com/v2"
        self.linkedin_actor_id = "apimaestro~linkedin-profile-detail"
    
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
    
    # ===================== LEADS CRUD OPERATIONS =====================
    
    def create_lead(self, account_id: str, company_id: str, created_by: str,
                   profile_url: str, source_query_id: str = None,
                   first_name: str = None, last_name: str = None,
                   title: str = None, company_name: str = None,
                   location: str = None, notes: str = None) -> Dict[str, Any]:
        """
        Create new lead
        Returns: {'success': bool, 'message': str, 'lead': dict or None}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'lead': None
                }
            
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'lead': None
                }
            
            # Verify user exists
            if not self.verify_user_exists(created_by):
                return {
                    'success': False,
                    'message': 'User (created_by) not found or inactive',
                    'lead': None
                }
            
            # Validate profile URL
            if not profile_url or not profile_url.strip():
                return {
                    'success': False,
                    'message': 'Profile URL is required',
                    'lead': None
                }
            
            profile_url = profile_url.strip()
            
            # Basic LinkedIn URL validation
            if 'linkedin.com' not in profile_url.lower():
                return {
                    'success': False,
                    'message': 'Profile URL must be a LinkedIn URL',
                    'lead': None
                }
            
            # Check for duplicate profile URL
            existing_result = self.supabase.table('leads').select('id').eq('profile_url', profile_url).eq('account_id', account_id).execute()
            if existing_result.data:
                return {
                    'success': False,
                    'message': 'Lead with this profile URL already exists in this account',
                    'lead': None
                }
            
            # Create lead
            lead_data = {
                'account_id': account_id,
                'company_id': company_id,
                'source_query_id': source_query_id,
                'created_by': created_by,
                'profile_url': profile_url,
                'first_name': first_name.strip() if first_name else None,
                'last_name': last_name.strip() if last_name else None,
                'title': title.strip() if title else None,
                'company_name': company_name.strip() if company_name else None,
                'location': location.strip() if location else None,
                'notes': notes.strip() if notes else None,
                'enrichment_status': 'pending',
                'is_enriched': False
            }
            
            result = self.supabase.table('leads').insert(lead_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Lead created successfully',
                    'lead': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create lead',
                    'lead': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating lead: {str(e)}',
                'lead': None
            }
    
    def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Get lead by ID
        Returns: {'success': bool, 'message': str, 'lead': dict or None}
        """
        try:
            result = self.supabase.table('leads').select('*').eq('id', lead_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Lead retrieved successfully',
                    'lead': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Lead not found',
                    'lead': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving lead: {str(e)}',
                'lead': None
            }
    
    def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update lead information
        Returns: {'success': bool, 'message': str, 'lead': dict or None}
        """
        try:
            # Verify lead exists
            existing = self.get_lead(lead_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Lead not found',
                    'lead': None
                }
            
            # Filter allowed fields
            allowed_fields = ['first_name', 'last_name', 'title', 'company_name', 'location',
                            'notes', 'profile_url', 'enrichment_status', 'is_enriched',
                            'enriched_data', 'last_enriched_at', 'apify_actor_run_id']
            filtered_updates = {}
            
            for key, value in updates.items():
                if key in allowed_fields:
                    if key == 'enrichment_status':
                        # Validate enrichment status
                        if value not in ['pending', 'running', 'completed', 'failed']:
                            return {
                                'success': False,
                                'message': 'Invalid enrichment_status. Must be: pending, running, completed, or failed',
                                'lead': None
                            }
                    elif key == 'profile_url' and value:
                        # Validate LinkedIn URL
                        if 'linkedin.com' not in value.lower():
                            return {
                                'success': False,
                                'message': 'Profile URL must be a LinkedIn URL',
                                'lead': None
                            }
                    
                    filtered_updates[key] = value
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'lead': None
                }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            # Update lead
            result = self.supabase.table('leads').update(filtered_updates).eq('id', lead_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Lead updated successfully',
                    'lead': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update lead',
                    'lead': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating lead: {str(e)}',
                'lead': None
            }
    
    def delete_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Delete lead
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify lead exists
            existing = self.get_lead(lead_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Lead not found'
                }
            
            # Delete lead
            result = self.supabase.table('leads').delete().eq('id', lead_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Lead deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete lead'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting lead: {str(e)}'
            }
    
    def get_leads_by_account(self, account_id: str, enriched_only: bool = False) -> Dict[str, Any]:
        """
        Get all leads for an account
        Returns: {'success': bool, 'message': str, 'leads': list}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'leads': []
                }
            
            query_builder = self.supabase.table('leads').select('*').eq('account_id', account_id)
            
            if enriched_only:
                query_builder = query_builder.eq('is_enriched', True)
            
            result = query_builder.order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} leads',
                'leads': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving leads: {str(e)}',
                'leads': []
            }
    
    def get_leads_by_company(self, company_id: str, enriched_only: bool = False) -> Dict[str, Any]:
        """
        Get all leads for a company
        Returns: {'success': bool, 'message': str, 'leads': list}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'leads': []
                }
            
            query_builder = self.supabase.table('leads').select('*').eq('company_id', company_id)
            
            if enriched_only:
                query_builder = query_builder.eq('is_enriched', True)
            
            result = query_builder.order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} leads',
                'leads': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving leads: {str(e)}',
                'leads': []
            }
    
    def get_leads_by_query(self, query_id: str) -> Dict[str, Any]:
        """
        Get all leads created from a specific search query
        Returns: {'success': bool, 'message': str, 'leads': list}
        """
        try:
            result = self.supabase.table('leads').select('*').eq('source_query_id', query_id).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} leads from query',
                'leads': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving leads by query: {str(e)}',
                'leads': []
            }
    
    # ===================== HELPER METHODS =====================
    
    def _generate_or_validate_uuid(self, lead_id: str) -> str:
        """
        Generate a proper UUID if the provided lead_id is not a valid UUID
        Returns: A valid UUID string
        """
        try:
            # Try to parse as UUID to validate
            uuid.UUID(lead_id)
            return lead_id
        except ValueError:
            # Generate a new UUID if the provided ID is not valid
            return str(uuid.uuid4())
    
    def get_profile_url_from_search_result(self, google_result_id: str) -> Dict[str, Any]:
        """
        Get LinkedIn profile URL from google_search_results table using google_result_id
        Returns: {'success': bool, 'message': str, 'profile_url': str or None}
        """
        try:
            search_result = self.supabase.table('google_search_results').select('link, title').eq('id', google_result_id).execute()
            
            if not search_result.data:
                return {
                    'success': False,
                    'message': 'No search result found for this google_result_id',
                    'profile_url': None
                }
            
            profile_url = search_result.data[0]['link']
            
            # Validate it's a LinkedIn URL
            if 'linkedin.com' not in profile_url.lower():
                return {
                    'success': False,
                    'message': 'Search result does not contain a LinkedIn profile URL',
                    'profile_url': None
                }
            
            return {
                'success': True,
                'message': 'Profile URL retrieved successfully',
                'profile_url': profile_url
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving profile URL: {str(e)}',
                'profile_url': None
            }
    
    # ===================== APIFY INTEGRATION =====================
    
    def start_apify_enrichment(self, profile_urls: List[str]) -> Dict[str, Any]:
        """
        Run Apify actor synchronously for LinkedIn profile enrichment
        Returns: {'success': bool, 'message': str, 'results': list}
        """
        try:
            # Prepare input for Apify LinkedIn scraper
            apify_input = {
                "profileUrls": profile_urls,
                "proxyConfig": {"useApifyProxy": True}
            }
            
            # Use sync API endpoint
            url = f"{self.apify_base_url}/acts/{self.linkedin_actor_id}/run-sync-get-dataset-items"
            params = {
                "token": self.apify_api_token
            }
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=apify_input, headers=headers, params=params, timeout=300)
            
            if response.status_code in [200, 201]:
                results = response.json()
                
                return {
                    'success': True,
                    'message': f'Apify enrichment completed successfully',
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to run Apify enrichment: {response.status_code} - {response.text}',
                    'results': []
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error running Apify enrichment: {str(e)}',
                'results': []
            }
    
    def check_apify_run_status(self, run_id: str) -> Dict[str, Any]:
        """
        Check the status of an Apify actor run
        Returns: {'success': bool, 'message': str, 'status': str, 'data': dict}
        """
        try:
            url = f"{self.apify_base_url}/actor-runs/{run_id}"
            headers = {
                "Authorization": f"Bearer {self.apify_api_token}"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                run_data = response.json()
                status = run_data['data']['status']
                
                return {
                    'success': True,
                    'message': f'Run status retrieved successfully',
                    'status': status,
                    'data': run_data['data']
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to get run status: {response.status_code} - {response.text}',
                    'status': 'unknown',
                    'data': {}
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error checking run status: {str(e)}',
                'status': 'error',
                'data': {}
            }
    
    def get_apify_run_results(self, run_id: str) -> Dict[str, Any]:
        """
        Get results from completed Apify actor run
        Returns: {'success': bool, 'message': str, 'results': list}
        """
        try:
            url = f"{self.apify_base_url}/actor-runs/{run_id}/dataset/items"
            headers = {
                "Authorization": f"Bearer {self.apify_api_token}"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                results = response.json()
                
                return {
                    'success': True,
                    'message': f'Retrieved {len(results)} enrichment results',
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to get run results: {response.status_code} - {response.text}',
                    'results': []
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error getting run results: {str(e)}',
                'results': []
            }
    
    # ===================== LEAD ENRICHMENT WORKFLOW =====================
    
    def enrich_lead(self, lead_id: str, account_id: str = None, company_id: str = None, created_by: str = None,
                   company_banner_id: str = None, source_query_id: str = None, google_result_id: str = None) -> Dict[str, Any]:
        """
        Enrich a single lead using Apify
        If lead doesn't exist, gets LinkedIn URL from google_search_results table and creates lead after enrichment
        Returns: {'success': bool, 'message': str, 'lead': dict or None}
        """
        try:
            # Try to get lead details
            lead_result = self.get_lead(lead_id)
            lead_exists = lead_result['success']
            
            if lead_exists:
                lead = lead_result['lead']
                # Check if already enriched
                if lead.get('enrichment_status') == 'enriched':
                    return {
                        'success': False,
                        'message': 'Lead already enriched',
                        'lead': lead
                    }
                profile_url = lead.get('source_link')
                if not profile_url and google_result_id:
                    # Get LinkedIn URL from google_search_results table using google_result_id
                    url_result = self.get_profile_url_from_search_result(google_result_id)
                    if not url_result['success']:
                        return {
                            'success': False,
                            'message': url_result['message'],
                            'lead': lead
                        }
                    profile_url = url_result['profile_url']
                elif not profile_url:
                    return {
                        'success': False,
                        'message': 'No profile URL found for existing lead and no google_result_id provided',
                        'lead': lead
                    }
            else:
                # Lead doesn't exist, google_result_id is required to get LinkedIn URL
                if not google_result_id:
                    return {
                        'success': False,
                        'message': 'For non-existing leads, google_result_id is required to get LinkedIn profile URL',
                        'lead': None
                    }
                
                url_result = self.get_profile_url_from_search_result(google_result_id)
            
                if not url_result['success']:
                    return {
                        'success': False,
                        'message': url_result['message'],
                        'lead': None
                    }
                profile_url = url_result['profile_url']
                
                # Validate required parameters for creating new lead
                if not account_id or not company_id or not created_by:
                    return {
                        'success': False,
                        'message': 'For non-existing leads, account_id, company_id, and created_by are required',
                        'lead': None
                    }
            
            # Update status to running (only if lead exists)
            if lead_exists:
                self.update_lead(lead_id, {
                    'enrichment_status': 'in_progress'
                })
            
            # Run Apify enrichment synchronously
            apify_result = self.start_apify_enrichment([profile_url])
            
            if not apify_result['success']:
                if lead_exists:
                    self.update_lead(lead_id, {
                        'enrichment_status': 'failed'
                    })
                    return {
                        'success': False,
                        'message': f"Failed to run enrichment: {apify_result['message']}",
                        'lead': self.get_lead(lead_id)['lead']
                    }
                else:
                    return {
                        'success': False,
                        'message': f"Failed to run enrichment: {apify_result['message']}",
                        'lead': None
                    }
            
            # Get results directly from sync response
            results = apify_result['results']
            
            if results and len(results) > 0:
                enriched_data = results[0]  # First result
                
                if lead_exists:
                    # Update existing lead with enriched data
                    update_data = {
                        'enrichment_status': 'enriched',
                        'enrichment_payload': enriched_data,
                        'last_enriched_at': datetime.now().isoformat()
                    }
                    
                    # Extract key fields from enriched data
                    basic_info = enriched_data.get('basic_info', {})
                    if basic_info.get('fullname'):
                        update_data['full_name'] = basic_info['fullname']
                    if basic_info.get('headline'):
                        update_data['title'] = basic_info['headline']
                    if basic_info.get('current_company'):
                        update_data['company_name'] = basic_info['current_company']
                    if basic_info.get('email'):
                        update_data['email'] = basic_info['email']
                    if basic_info.get('location', {}).get('full'):
                        update_data['location'] = basic_info['location']['full']
                    if basic_info.get('public_identifier'):
                        update_data['source_username'] = basic_info['public_identifier']
                    if basic_info.get('profile_url'):
                        update_data['source_link'] = basic_info['profile_url']
                    
                    self.update_lead(lead_id, update_data)
                    
                    return {
                        'success': True,
                        'message': 'Lead enriched successfully',
                        'lead': self.get_lead(lead_id)['lead']
                    }
                else:
                    # Create new lead with enriched data
                    valid_uuid = self._generate_or_validate_uuid(lead_id)
                    lead_data = {
                        'id': valid_uuid,  # Use a valid UUID
                        'account_id': account_id,
                        'company_id': company_id,
                        'company_banner_id': company_banner_id,
                        'source_query_id': source_query_id,
                        'google_result_id': google_result_id,
                        'source_link': profile_url,
                        'full_name': enriched_data.get('basic_info', {}).get('fullname'),
                        'title': enriched_data.get('basic_info', {}).get('headline'),
                        'company_name': enriched_data.get('basic_info', {}).get('current_company'),
                        'email': enriched_data.get('basic_info', {}).get('email'),
                        'location': enriched_data.get('basic_info', {}).get('location', {}).get('full'),
                        'source_username': enriched_data.get('basic_info', {}).get('public_identifier'),
                        'enrichment_status': 'enriched',
                        'enrichment_payload': enriched_data,
                        'last_enriched_at': datetime.now().isoformat()
                    }
                    
                    result = self.supabase.table('leads').insert(lead_data).execute()
                    
                    if result.data:
                        return {
                            'success': True,
                            'message': 'Lead created and enriched successfully',
                            'lead': result.data[0]
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'Failed to create lead with enriched data',
                            'lead': None
                        }
            else:
                # No enrichment data returned
                if lead_exists:
                    self.update_lead(lead_id, {
                        'enrichment_status': 'failed'
                    })
                    return {
                        'success': False,
                        'message': 'No enrichment data returned',
                        'lead': self.get_lead(lead_id)['lead']
                    }
                else:
                    return {
                        'success': False,
                        'message': 'No enrichment data returned',
                        'lead': None
                    }
                
        except Exception as e:
            # Mark as failed (only if lead exists)
            if 'lead_exists' in locals() and lead_exists:
                self.update_lead(lead_id, {
                    'enrichment_status': 'failed'
                })
            
            return {
                'success': False,
                'message': f'Error enriching lead: {str(e)}',
                'lead': None
            }
    
    def bulk_enrich_leads(self, google_result_ids: List[str], account_id: str, company_id: str, created_by: str,
                         company_banner_id: str = None, source_query_id: str = None) -> Dict[str, Any]:
        """
        Enrich multiple leads in batch using Apify
        Gets LinkedIn URLs from google_search_results table based on google_result_ids
        Returns: {'success': bool, 'message': str, 'results': list}
        """
        try:
            if not google_result_ids:
                return {
                    'success': False,
                    'message': 'No google result IDs provided',
                    'results': []
                }
            
            # Get all LinkedIn URLs from google_search_results table
            profile_urls = []
            valid_google_results = []
            
            for google_result_id in google_result_ids:
                url_result = self.get_profile_url_from_search_result(google_result_id)
                
                if url_result['success']:
                    profile_urls.append(url_result['profile_url'])
                    valid_google_results.append({
                        'google_result_id': google_result_id,
                        'profile_url': url_result['profile_url']
                    })
            
            if not profile_urls:
                return {
                    'success': False,
                    'message': 'No valid LinkedIn URLs found in search results',
                    'results': []
                }
            
            # Run Apify enrichment synchronously for each profile one by one
            processed_leads = []
            
            for i, google_result_info in enumerate(valid_google_results):
                profile_url = google_result_info['profile_url']
                google_result_id = google_result_info['google_result_id']
                
                # Run enrichment for this single URL
                apify_result = self.start_apify_enrichment([profile_url])
                
                if not apify_result['success']:
                    # Add error entry for this failed enrichment
                    processed_leads.append({
                        'error': f'Failed to enrich profile: {apify_result["message"]}',
                        'google_result_id': google_result_id,
                        'profile_url': profile_url
                    })
                    continue
                
                # Get results from this enrichment
                enrichment_results = apify_result['results']
                
                if not enrichment_results or len(enrichment_results) == 0:
                    # Add error entry for no data returned
                    processed_leads.append({
                        'error': 'No enrichment data returned from Apify',
                        'google_result_id': google_result_id,
                        'profile_url': profile_url
                    })
                    continue
                
                # Process the enrichment result and create lead
                enriched_data = enrichment_results[0]  # First (and only) result
                
                # Generate a proper UUID for the lead
                lead_id = self._generate_or_validate_uuid(None)  # Generate new UUID
                
                # Create new lead with enriched data
                basic_info = enriched_data.get('basic_info', {})
                lead_data = {
                    'id': lead_id,
                    'account_id': account_id,
                    'company_id': company_id,
                    'company_banner_id': company_banner_id,
                    'source_query_id': source_query_id,
                    'google_result_id': google_result_id,
                    'source_link': profile_url,
                    'full_name': basic_info.get('fullname'),
                    'title': basic_info.get('headline'),
                    'company_name': basic_info.get('current_company'),
                    'email': basic_info.get('email'),
                    'location': basic_info.get('location', {}).get('full'),
                    'source_username': basic_info.get('public_identifier'),
                    'enrichment_status': 'enriched',
                    'enrichment_payload': enriched_data,
                    'last_enriched_at': datetime.now().isoformat()
                }
                
                # Insert lead into database
                result = self.supabase.table('leads').insert(lead_data).execute()
                
                if result.data:
                    processed_leads.append(result.data[0])
                else:
                    # Failed to create lead
                    processed_leads.append({
                        'error': f'Failed to create lead in database for google_result_id: {google_result_id}',
                        'google_result_id': google_result_id,
                        'profile_url': profile_url
                    })
            
            return {
                'success': True,
                'message': f'Batch enrichment completed for {len(processed_leads)} leads',
                'results': processed_leads
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error in batch enrichment: {str(e)}',
                'results': []
            }
    
    # ===================== SEARCH INTEGRATION =====================
    
    def create_leads_from_search_results(self, query_id: str, account_id: str, 
                                       company_id: str, created_by: str) -> Dict[str, Any]:
        """
        Create leads from Google search results (LinkedIn profiles)
        Uses google_search_results.id as the lead_id for direct mapping
        Returns: {'success': bool, 'message': str, 'leads_created': int, 'leads': list}
        """
        try:
            # Get search results directly from google_search_results table
            search_results = self.supabase.table('google_search_results').select('*').eq('query_id', query_id).execute()
            
            if not search_results.data:
                return {
                    'success': False,
                    'message': 'No search results found for this query',
                    'leads_created': 0,
                    'leads': []
                }
            
            created_leads = []
            leads_created = 0
            
            for result in search_results.data:
                # Check if URL is a LinkedIn profile
                url = result.get('link', '')
                if 'linkedin.com/in/' in url.lower():
                    # Check if lead already exists for this search result
                    existing_lead = self.supabase.table('leads').select('id').eq('id', result['id']).execute()
                    
                    if existing_lead.data:
                        continue  # Skip if lead already exists
                    
                    # Extract basic info from search result
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    
                    # Try to extract name and title from title/snippet
                    first_name = None
                    last_name = None
                    job_title = None
                    company_name = None
                    
                    # Basic parsing of LinkedIn title format: "Name - Title at Company | LinkedIn"
                    if ' - ' in title and ' | LinkedIn' in title:
                        name_part = title.split(' - ')[0].strip()
                        title_company_part = title.split(' - ')[1].replace(' | LinkedIn', '').strip()
                        
                        # Parse name
                        name_parts = name_part.split()
                        if len(name_parts) >= 2:
                            first_name = name_parts[0]
                            last_name = ' '.join(name_parts[1:])
                        
                        # Parse title and company
                        if ' at ' in title_company_part:
                            job_title = title_company_part.split(' at ')[0].strip()
                            company_name = title_company_part.split(' at ')[1].strip()
                        else:
                            job_title = title_company_part
                    
                    # Create lead with google_search_results.id as the lead.id
                    lead_data = {
                        'id': result['id'],  # Use search result ID as lead ID
                        'account_id': account_id,
                        'company_id': company_id,
                        'source_query_id': query_id,
                        'created_by': created_by,
                        'profile_url': url,
                        'first_name': first_name,
                        'last_name': last_name,
                        'title': job_title,
                        'company_name': company_name,
                        'location': None,
                        'notes': f"Created from search result: {snippet[:200] if snippet else 'No snippet available'}",
                        'enrichment_status': 'pending',
                        'is_enriched': False
                    }
                    
                    try:
                        # Insert lead with specific ID
                        insert_result = self.supabase.table('leads').insert(lead_data).execute()
                        
                        if insert_result.data:
                            created_leads.append(insert_result.data[0])
                            leads_created += 1
                            
                    except Exception as insert_error:
                        # Handle potential duplicate or other insertion errors
                        continue
            
            return {
                'success': True,
                'message': f'Created {leads_created} leads from search results',
                'leads_created': leads_created,
                'leads': created_leads
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating leads from search results: {str(e)}',
                'leads_created': 0,
                'leads': []
            }