"""
Leads management utilities
Handles LinkedIn profile enrichment using Apify API
"""

import os
import json
import requests
import time
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
        self.linkedin_actor_id = "apify/linkedin-profile-scraper"
    
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
    
    def get_profile_url_from_search_result(self, lead_id: str) -> Dict[str, Any]:
        """
        Get LinkedIn profile URL from google_search_results table using lead_id
        Returns: {'success': bool, 'message': str, 'profile_url': str or None}
        """
        try:
            search_result = self.supabase.table('google_search_results').select('link, title').eq('id', lead_id).execute()
            
            if not search_result.data:
                return {
                    'success': False,
                    'message': 'No search result found for this lead ID',
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
        Start Apify actor run for LinkedIn profile enrichment
        Returns: {'success': bool, 'message': str, 'run_id': str or None}
        """
        try:
            # Prepare input for Apify LinkedIn scraper
            apify_input = {
                "profileUrls": profile_urls,
                "proxyConfig": {"useApifyProxy": True}
            }
            
            # Start actor run
            url = f"{self.apify_base_url}/acts/{self.linkedin_actor_id}/runs"
            headers = {
                "Authorization": f"Bearer {self.apify_api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=apify_input, headers=headers, timeout=30)
            
            if response.status_code == 201:
                run_data = response.json()
                run_id = run_data['data']['id']
                
                return {
                    'success': True,
                    'message': f'Apify enrichment started successfully',
                    'run_id': run_id
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to start Apify enrichment: {response.status_code} - {response.text}',
                    'run_id': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error starting Apify enrichment: {str(e)}',
                'run_id': None
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
    
    def enrich_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Enrich a single lead using Apify
        Gets LinkedIn URL from google_search_results table based on lead_id
        Returns: {'success': bool, 'message': str, 'lead': dict or None}
        """
        try:
            # Get lead details
            lead_result = self.get_lead(lead_id)
            if not lead_result['success']:
                return {
                    'success': False,
                    'message': 'Lead not found',
                    'lead': None
                }
            
            lead = lead_result['lead']
            
            # Check if already enriched
            if lead['is_enriched']:
                return {
                    'success': False,
                    'message': 'Lead already enriched',
                    'lead': lead
                }
            
            # Get LinkedIn URL from google_search_results table using lead_id
            url_result = self.get_profile_url_from_search_result(lead_id)
            
            if not url_result['success']:
                return {
                    'success': False,
                    'message': url_result['message'],
                    'lead': lead
                }
            
            profile_url = url_result['profile_url']
            
            # Update status to running
            self.update_lead(lead_id, {
                'enrichment_status': 'running'
            })
            
            # Start Apify enrichment with URL from google_search_results
            apify_result = self.start_apify_enrichment([profile_url])
            
            if not apify_result['success']:
                self.update_lead(lead_id, {
                    'enrichment_status': 'failed'
                })
                return {
                    'success': False,
                    'message': f"Failed to start enrichment: {apify_result['message']}",
                    'lead': self.get_lead(lead_id)['lead']
                }
            
            run_id = apify_result['run_id']
            
            # Update lead with run ID
            self.update_lead(lead_id, {
                'apify_actor_run_id': run_id
            })
            
            # Wait for completion (with timeout)
            max_wait_time = 300  # 5 minutes
            check_interval = 10   # 10 seconds
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                status_result = self.check_apify_run_status(run_id)
                
                if status_result['success']:
                    status = status_result['status']
                    
                    if status == 'SUCCEEDED':
                        # Get results
                        results_response = self.get_apify_run_results(run_id)
                        
                        if results_response['success'] and results_response['results']:
                            enriched_data = results_response['results'][0]  # First result
                            
                            # Update lead with enriched data
                            update_data = {
                                'enrichment_status': 'completed',
                                'is_enriched': True,
                                'enriched_data': enriched_data,
                                'last_enriched_at': datetime.now().isoformat()
                            }
                            
                            # Extract key fields from enriched data
                            if enriched_data.get('firstName'):
                                update_data['first_name'] = enriched_data['firstName']
                            if enriched_data.get('lastName'):
                                update_data['last_name'] = enriched_data['lastName']
                            if enriched_data.get('headline'):
                                update_data['title'] = enriched_data['headline']
                            if enriched_data.get('company'):
                                update_data['company_name'] = enriched_data['company']
                            if enriched_data.get('location'):
                                update_data['location'] = enriched_data['location']
                            
                            self.update_lead(lead_id, update_data)
                            
                            return {
                                'success': True,
                                'message': 'Lead enriched successfully',
                                'lead': self.get_lead(lead_id)['lead']
                            }
                        else:
                            self.update_lead(lead_id, {
                                'enrichment_status': 'failed'
                            })
                            return {
                                'success': False,
                                'message': 'No enrichment data returned',
                                'lead': self.get_lead(lead_id)['lead']
                            }
                    
                    elif status == 'FAILED':
                        self.update_lead(lead_id, {
                            'enrichment_status': 'failed'
                        })
                        return {
                            'success': False,
                            'message': 'Apify enrichment failed',
                            'lead': self.get_lead(lead_id)['lead']
                        }
                    
                    elif status in ['RUNNING', 'READY']:
                        # Continue waiting
                        time.sleep(check_interval)
                        elapsed_time += check_interval
                    else:
                        # Unknown status
                        self.update_lead(lead_id, {
                            'enrichment_status': 'failed'
                        })
                        return {
                            'success': False,
                            'message': f'Unknown enrichment status: {status}',
                            'lead': self.get_lead(lead_id)['lead']
                        }
                else:
                    # Error checking status
                    time.sleep(check_interval)
                    elapsed_time += check_interval
            
            # Timeout
            self.update_lead(lead_id, {
                'enrichment_status': 'failed'
            })
            return {
                'success': False,
                'message': 'Enrichment timeout - process took too long',
                'lead': self.get_lead(lead_id)['lead']
            }
                
        except Exception as e:
            # Mark as failed
            self.update_lead(lead_id, {
                'enrichment_status': 'failed'
            })
            
            return {
                'success': False,
                'message': f'Error enriching lead: {str(e)}',
                'lead': None
            }
    
    def bulk_enrich_leads(self, lead_ids: List[str]) -> Dict[str, Any]:
        """
        Enrich multiple leads in batch using Apify
        Gets LinkedIn URLs from google_search_results table based on lead_ids
        Returns: {'success': bool, 'message': str, 'results': list}
        """
        try:
            if not lead_ids:
                return {
                    'success': False,
                    'message': 'No lead IDs provided',
                    'results': []
                }
            
            # Get all leads and their corresponding search results
            leads = []
            profile_urls = []
            
            for lead_id in lead_ids:
                lead_result = self.get_lead(lead_id)
                if lead_result['success']:
                    lead = lead_result['lead']
                    if not lead['is_enriched']:
                        # Get LinkedIn URL from google_search_results table
                        url_result = self.get_profile_url_from_search_result(lead_id)
                        
                        if url_result['success']:
                            profile_url = url_result['profile_url']
                            leads.append(lead)
                            profile_urls.append(profile_url)
                            
                            # Update status to running
                            self.update_lead(lead_id, {
                                'enrichment_status': 'running'
                            })
            
            if not leads:
                return {
                    'success': False,
                    'message': 'No valid leads to enrich',
                    'results': []
                }
            
            # Start Apify enrichment for all profiles
            apify_result = self.start_apify_enrichment(profile_urls)
            
            if not apify_result['success']:
                # Mark all as failed
                for lead in leads:
                    self.update_lead(lead['id'], {
                        'enrichment_status': 'failed'
                    })
                
                return {
                    'success': False,
                    'message': f"Failed to start batch enrichment: {apify_result['message']}",
                    'results': []
                }
            
            run_id = apify_result['run_id']
            
            # Update all leads with run ID
            for lead in leads:
                self.update_lead(lead['id'], {
                    'apify_actor_run_id': run_id
                })
            
            # Wait for completion
            max_wait_time = 600  # 10 minutes for batch
            check_interval = 15   # 15 seconds
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                status_result = self.check_apify_run_status(run_id)
                
                if status_result['success']:
                    status = status_result['status']
                    
                    if status == 'SUCCEEDED':
                        # Get results
                        results_response = self.get_apify_run_results(run_id)
                        
                        if results_response['success']:
                            enrichment_results = results_response['results']
                            processed_leads = []
                            
                            # Match results to leads by profile URL
                            # Note: profile_urls array matches leads array by index
                            for i, lead in enumerate(leads):
                                matching_result = None
                                lead_profile_url = profile_urls[i]  # Get corresponding URL
                                
                                for result in enrichment_results:
                                    if result.get('url') == lead_profile_url:
                                        matching_result = result
                                        break
                                
                                if matching_result:
                                    # Update lead with enriched data
                                    update_data = {
                                        'enrichment_status': 'completed',
                                        'is_enriched': True,
                                        'enriched_data': matching_result,
                                        'last_enriched_at': datetime.now().isoformat()
                                    }
                                    
                                    # Extract key fields
                                    if matching_result.get('firstName'):
                                        update_data['first_name'] = matching_result['firstName']
                                    if matching_result.get('lastName'):
                                        update_data['last_name'] = matching_result['lastName']
                                    if matching_result.get('headline'):
                                        update_data['title'] = matching_result['headline']
                                    if matching_result.get('company'):
                                        update_data['company_name'] = matching_result['company']
                                    if matching_result.get('location'):
                                        update_data['location'] = matching_result['location']
                                    
                                    self.update_lead(lead['id'], update_data)
                                    processed_leads.append(self.get_lead(lead['id'])['lead'])
                                else:
                                    # No matching result found
                                    self.update_lead(lead['id'], {
                                        'enrichment_status': 'failed'
                                    })
                                    processed_leads.append(self.get_lead(lead['id'])['lead'])
                            
                            return {
                                'success': True,
                                'message': f'Batch enrichment completed for {len(processed_leads)} leads',
                                'results': processed_leads
                            }
                        else:
                            # Mark all as failed
                            for lead in leads:
                                self.update_lead(lead['id'], {
                                    'enrichment_status': 'failed'
                                })
                            
                            return {
                                'success': False,
                                'message': 'No enrichment data returned',
                                'results': []
                            }
                    
                    elif status == 'FAILED':
                        # Mark all as failed
                        for lead in leads:
                            self.update_lead(lead['id'], {
                                'enrichment_status': 'failed'
                            })
                        
                        return {
                            'success': False,
                            'message': 'Batch enrichment failed',
                            'results': []
                        }
                    
                    elif status in ['RUNNING', 'READY']:
                        # Continue waiting
                        time.sleep(check_interval)
                        elapsed_time += check_interval
                    else:
                        # Unknown status - mark all as failed
                        for lead in leads:
                            self.update_lead(lead['id'], {
                                'enrichment_status': 'failed'
                            })
                        
                        return {
                            'success': False,
                            'message': f'Unknown enrichment status: {status}',
                            'results': []
                        }
                else:
                    # Error checking status
                    time.sleep(check_interval)
                    elapsed_time += check_interval
            
            # Timeout - mark all as failed
            for lead in leads:
                self.update_lead(lead['id'], {
                    'enrichment_status': 'failed'
                })
            
            return {
                'success': False,
                'message': 'Batch enrichment timeout - process took too long',
                'results': []
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