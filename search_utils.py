"""
Search Query management utilities
Handles CRUD operations for search queries with Google Custom Search API integration
"""

import os
import hashlib
import requests
import time
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class SearchManager:
    def __init__(self):
        """Initialize Supabase client and Google API credentials"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Google Custom Search API credentials
        self.google_api_key = os.getenv('GOOGLE_API_KEY', "AIzaSyC4ERfdrOcLi2WDmQUanEbLm0ElZO5hqE8")
        self.google_cx = os.getenv('GOOGLE_CX', "e4c60fbadcc3c41b3")
        self.google_base_url = "https://www.googleapis.com/customsearch/v1"
    
    def generate_unique_hash(self, content: str) -> str:
        """Generate unique hash for deduplication"""
        return hashlib.md5(content.encode()).hexdigest()
    
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
    
    def verify_banner_exists(self, banner_id: str) -> bool:
        """Verify that the company banner exists and is active"""
        try:
            result = self.supabase.table('company_banners').select('id').eq('id', banner_id).eq('is_active', True).execute()
            return len(result.data) > 0
        except Exception:
            return False
    
    # ===================== SEARCH QUERIES CRUD OPERATIONS =====================
    
    def create_query(self, account_id: str, company_id: str, created_by: str, 
                    query_string: str, name: str = None, company_banner_id: str = None,
                    pages_requested: int = 1, dedupe_mode: str = 'per_company',
                    notes: str = None) -> Dict[str, Any]:
        """
        Create new search query
        Returns: {'success': bool, 'message': str, 'query': dict or None}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'query': None
                }
            
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'query': None
                }
            
            # Verify user exists
            if not self.verify_user_exists(created_by):
                return {
                    'success': False,
                    'message': 'User (created_by) not found or inactive',
                    'query': None
                }
            
            # Verify banner exists if provided
            if company_banner_id and not self.verify_banner_exists(company_banner_id):
                return {
                    'success': False,
                    'message': 'Company banner not found or inactive',
                    'query': None
                }
            
            # Validate pages_requested
            if not isinstance(pages_requested, int) or pages_requested < 1 or pages_requested > 100:
                return {
                    'success': False,
                    'message': 'Invalid pages_requested. Must be between 1 and 100',
                    'query': None
                }
            
            # Validate dedupe_mode
            if dedupe_mode not in ['per_query', 'per_company', 'per_account']:
                return {
                    'success': False,
                    'message': 'Invalid dedupe_mode. Must be: per_query, per_company, or per_account',
                    'query': None
                }
            
            # Create query
            query_data = {
                'account_id': account_id,
                'company_id': company_id,
                'company_banner_id': company_banner_id,
                'created_by': created_by,
                'name': name.strip() if name else None,
                'query_string': query_string.strip(),
                'pages_requested': pages_requested,
                'pages_fetched': 0,
                'next_page_start': '1',  # Start from page 1
                'status': 'pending',
                'locked_by': account_id,  # Lock with account_id as requested
                'locked_at': datetime.now().isoformat(),
                'notes': notes.strip() if notes else None,
                'dedupe_mode': dedupe_mode
            }
            
            result = self.supabase.table('queries').insert(query_data).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Search query created successfully',
                    'query': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create search query',
                    'query': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating search query: {str(e)}',
                'query': None
            }
    
    def get_query(self, query_id: str) -> Dict[str, Any]:
        """
        Get search query by ID
        Returns: {'success': bool, 'message': str, 'query': dict or None}
        """
        try:
            result = self.supabase.table('queries').select('*').eq('id', query_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Search query retrieved successfully',
                    'query': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Search query not found',
                    'query': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving search query: {str(e)}',
                'query': None
            }
    
    def update_query(self, query_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update search query information
        Returns: {'success': bool, 'message': str, 'query': dict or None}
        """
        try:
            # Verify query exists
            existing = self.get_query(query_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Search query not found',
                    'query': None
                }
            
            # Filter allowed fields
            allowed_fields = ['name', 'query_string', 'pages_requested', 'status', 'notes', 
                            'pages_fetched', 'next_page_start', 'last_run_at', 'finished_at']
            filtered_updates = {}
            
            for key, value in updates.items():
                if key in allowed_fields:
                    if key == 'pages_requested':
                        # Validate pages_requested
                        if not isinstance(value, int) or value < 1 or value > 100:
                            return {
                                'success': False,
                                'message': 'Invalid pages_requested. Must be between 1 and 100',
                                'query': None
                            }
                    elif key == 'status':
                        # Validate status
                        if value not in ['pending', 'running', 'paused', 'completed', 'failed']:
                            return {
                                'success': False,
                                'message': 'Invalid status. Must be: pending, running, paused, completed, or failed',
                                'query': None
                            }
                    
                    filtered_updates[key] = value
            
            if not filtered_updates:
                return {
                    'success': False,
                    'message': 'No valid fields to update',
                    'query': None
                }
            
            # Add updated timestamp
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            # Update query
            result = self.supabase.table('queries').update(filtered_updates).eq('id', query_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Search query updated successfully',
                    'query': result.data[0]
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update search query',
                    'query': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating search query: {str(e)}',
                'query': None
            }
    
    def delete_query(self, query_id: str) -> Dict[str, Any]:
        """
        Delete search query and all associated results
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify query exists
            existing = self.get_query(query_id)
            if not existing['success']:
                return {
                    'success': False,
                    'message': 'Search query not found'
                }
            
            # Delete associated search results first (cascade should handle this, but being explicit)
            self.supabase.table('google_search_results').delete().eq('query_id', query_id).execute()
            
            # Delete query
            result = self.supabase.table('queries').delete().eq('id', query_id).execute()
            
            if result.data:
                return {
                    'success': True,
                    'message': 'Search query deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to delete search query'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting search query: {str(e)}'
            }
    
    def get_queries_by_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get all search queries for an account
        Returns: {'success': bool, 'message': str, 'queries': list}
        """
        try:
            # Verify account exists
            if not self.verify_account_exists(account_id):
                return {
                    'success': False,
                    'message': 'Account not found or inactive',
                    'queries': []
                }
            
            result = self.supabase.table('queries').select('*').eq('account_id', account_id).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} search queries',
                'queries': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving search queries: {str(e)}',
                'queries': []
            }
    
    def get_queries_by_company(self, company_id: str) -> Dict[str, Any]:
        """
        Get all search queries for a company
        Returns: {'success': bool, 'message': str, 'queries': list}
        """
        try:
            # Verify company exists
            if not self.verify_company_exists(company_id):
                return {
                    'success': False,
                    'message': 'Company not found or inactive',
                    'queries': []
                }
            
            result = self.supabase.table('queries').select('*').eq('company_id', company_id).order('created_at', desc=True).execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} search queries',
                'queries': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving search queries: {str(e)}',
                'queries': []
            }
    
    # ===================== GOOGLE SEARCH OPERATIONS =====================
    
    def execute_google_search(self, query_string: str, start_index: int = 1) -> Dict[str, Any]:
        """
        Execute Google Custom Search API request
        Returns: {'success': bool, 'message': str, 'data': dict or None, 'total_results': int}
        """
        try:
            params = {
                "key": self.google_api_key,
                "cx": self.google_cx,
                "q": query_string,
                "start": start_index
            }
            
            response = requests.get(self.google_base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                total_results = int(data.get('searchInformation', {}).get('totalResults', 0))
                
                return {
                    'success': True,
                    'message': 'Google search executed successfully',
                    'data': data,
                    'total_results': total_results
                }
            else:
                return {
                    'success': False,
                    'message': f'Google API error: {response.status_code} - {response.text}',
                    'data': None,
                    'total_results': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error executing Google search: {str(e)}',
                'data': None,
                'total_results': 0
            }
    
    def save_search_results(self, query_id: str, page_number: int, search_data: Dict) -> Dict[str, Any]:
        """
        Save Google search results to database
        Returns: {'success': bool, 'message': str, 'results_saved': int}
        """
        try:
            items = search_data.get('items', [])
            results_saved = 0
            
            for index, item in enumerate(items):
                position = index + 1  # Position within the page (1-10)
                
                # Generate unique hash for deduplication
                content_for_hash = f"{item.get('title', '')}{item.get('link', '')}{item.get('snippet', '')}"
                unique_hash = self.generate_unique_hash(content_for_hash)
                
                result_data = {
                    'query_id': query_id,
                    'page_number': page_number,
                    'position': position,
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet'),
                    'raw_response': item,
                    'unique_hash': unique_hash,
                    'is_processed': False
                }
                
                try:
                    # Insert result (will skip if unique constraint is violated)
                    self.supabase.table('google_search_results').insert(result_data).execute()
                    results_saved += 1
                except Exception as insert_error:
                    # Handle duplicate entries gracefully
                    if 'duplicate key' in str(insert_error).lower():
                        continue
                    else:
                        raise insert_error
            
            return {
                'success': True,
                'message': f'Saved {results_saved} search results',
                'results_saved': results_saved
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving search results: {str(e)}',
                'results_saved': 0
            }
    
    def process_query(self, query_id: str) -> Dict[str, Any]:
        """
        Process a search query by executing Google searches for all requested pages
        Returns: {'success': bool, 'message': str, 'query': dict, 'total_results_saved': int}
        """
        try:
            # Get query details
            query_result = self.get_query(query_id)
            if not query_result['success']:
                return {
                    'success': False,
                    'message': 'Search query not found',
                    'query': None,
                    'total_results_saved': 0
                }
            
            query = query_result['query']
            
            # Check if query is already completed
            if query['status'] == 'completed':
                return {
                    'success': False,
                    'message': 'Query already completed',
                    'query': query,
                    'total_results_saved': 0
                }
            
            # Update query status to running
            self.update_query(query_id, {
                'status': 'running',
                'last_run_at': datetime.now().isoformat()
            })
            
            total_results_saved = 0
            pages_requested = query['pages_requested']
            
            # Process each page
            for page in range(1, pages_requested + 1):
                # Calculate start index for Google API (1, 11, 21, 31, ...)
                start_index = (page - 1) * 10 + 1
                
                # Execute Google search
                search_result = self.execute_google_search(query['query_string'], start_index)
                
                if search_result['success']:
                    # Save results to database
                    save_result = self.save_search_results(query_id, page, search_result['data'])
                    total_results_saved += save_result['results_saved']
                    
                    # Update query progress
                    next_page_start = str(page + 1) if page < pages_requested else None
                    self.update_query(query_id, {
                        'pages_fetched': page,
                        'next_page_start': next_page_start
                    })
                    
                    # Add delay between requests to respect API limits
                    if page < pages_requested:
                        time.sleep(1)
                else:
                    # Handle search failure
                    self.update_query(query_id, {
                        'status': 'failed',
                        'finished_at': datetime.now().isoformat(),
                        'notes': f"Failed at page {page}: {search_result['message']}"
                    })
                    
                    return {
                        'success': False,
                        'message': f"Search failed at page {page}: {search_result['message']}",
                        'query': self.get_query(query_id)['query'],
                        'total_results_saved': total_results_saved
                    }
            
            # Mark query as completed
            self.update_query(query_id, {
                'status': 'completed',
                'finished_at': datetime.now().isoformat(),
                'pages_fetched': pages_requested
            })
            
            return {
                'success': True,
                'message': f'Query processed successfully. Saved {total_results_saved} results across {pages_requested} pages',
                'query': self.get_query(query_id)['query'],
                'total_results_saved': total_results_saved
            }
                
        except Exception as e:
            # Mark query as failed
            self.update_query(query_id, {
                'status': 'failed',
                'finished_at': datetime.now().isoformat(),
                'notes': f"Processing error: {str(e)}"
            })
            
            return {
                'success': False,
                'message': f'Error processing query: {str(e)}',
                'query': None,
                'total_results_saved': 0
            }
    
    # ===================== SEARCH RESULTS OPERATIONS =====================
    
    def get_search_results_by_query(self, query_id: str, processed_only: bool = False) -> Dict[str, Any]:
        """
        Get all search results for a query
        Returns: {'success': bool, 'message': str, 'results': list}
        """
        try:
            # Verify query exists
            query_result = self.get_query(query_id)
            if not query_result['success']:
                return {
                    'success': False,
                    'message': 'Search query not found',
                    'results': []
                }
            
            query_builder = self.supabase.table('google_search_results').select('*').eq('query_id', query_id)
            
            if processed_only:
                query_builder = query_builder.eq('is_processed', True)
            
            result = query_builder.order('page_number').order('position').execute()
            
            return {
                'success': True,
                'message': f'Retrieved {len(result.data)} search results',
                'results': result.data
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving search results: {str(e)}',
                'results': []
            }
    
    def delete_search_results_by_query(self, query_id: str) -> Dict[str, Any]:
        """
        Delete all search results for a query
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Verify query exists
            query_result = self.get_query(query_id)
            if not query_result['success']:
                return {
                    'success': False,
                    'message': 'Search query not found'
                }
            
            # Delete all results for this query
            result = self.supabase.table('google_search_results').delete().eq('query_id', query_id).execute()
            
            return {
                'success': True,
                'message': 'Search results deleted successfully'
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting search results: {str(e)}'
            }
    
    def mark_results_processed(self, query_id: str) -> Dict[str, Any]:
        """
        Mark all search results for a query as processed
        Returns: {'success': bool, 'message': str, 'updated_count': int}
        """
        try:
            # Verify query exists
            query_result = self.get_query(query_id)
            if not query_result['success']:
                return {
                    'success': False,
                    'message': 'Search query not found',
                    'updated_count': 0
                }
            
            # Update all unprocessed results
            result = self.supabase.table('google_search_results').update({
                'is_processed': True
            }).eq('query_id', query_id).eq('is_processed', False).execute()
            
            return {
                'success': True,
                'message': f'Marked {len(result.data)} results as processed',
                'updated_count': len(result.data)
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error marking results as processed: {str(e)}',
                'updated_count': 0
            }