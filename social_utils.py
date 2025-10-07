"""
Social Media Content Generation Module
====================================

This module handles AI-powered social media content generation using Google's Gemini API.
Supports multiple platforms: LinkedIn, Instagram, YouTube, Facebook, and Blog posts.

Features:
- Platform-specific content generation
- Structured JSON output format
- Error handling and validation
- Database integration with social_generations table
- Secure API key management

Author: Lead Management System
Date: October 7, 2025
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import hashlib

import google.generativeai as genai
from supabase import create_client, Client


class SocialManager:
    """
    Manages social media content generation using Google's Gemini API.
    
    Handles content generation for multiple platforms with platform-specific
    prompts and structured JSON output formats.
    """
    
    def __init__(self, supabase_client: Client = None):
        """
        Initialize SocialManager with Supabase client and Gemini API.
        
        Args:
            supabase_client: Optional Supabase client instance
        """
        self.supabase = supabase_client or self._create_supabase_client()
        self.gemini_api_key = "AIzaSyD1vW1f-BWip1_MZcqAm2ECUhk40WNZwFU"
        
        # Configure Gemini AI
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _create_supabase_client(self) -> Client:
        """Create Supabase client from environment variables."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("Supabase credentials not found in environment")
        
        return create_client(url, key)

    def get_platform_prompt(self, platform: str, query: str, company_info: Dict = None) -> str:
        """
        Get platform-specific system prompt for content generation.
        
        Args:
            platform: Social media platform (linkedin, instagram, youtube, facebook, blog)
            query: User's content generation query
            company_info: Optional company information for context
            
        Returns:
            Formatted system prompt for the platform
        """
        
        company_context = ""
        if company_info:
            company_context = f"""
Company Context:
- Company: {company_info.get('name', 'Unknown Company')}
- Website: {company_info.get('website', 'N/A')}
- Description: {company_info.get('description', 'N/A')}
"""

        base_instructions = f"""
{company_context}

User Query: {query}

CRITICAL REQUIREMENTS:
1. Generate EXACTLY 5 unique posts - no duplicates
2. Each post must be significantly different in approach, tone, and content
3. Follow the exact JSON structure provided
4. Include relevant hashtags for each post
5. Ensure content is engaging, professional, and platform-appropriate
6. All posts must relate to the user's query but with different angles

"""

        platform_prompts = {
            "linkedin": f"""{base_instructions}
Platform: LinkedIn Professional Network

Generate 5 unique LinkedIn posts focusing on:
1. Professional insights and industry trends
2. Business tips and career advice
3. Company achievements or industry news
4. Thought leadership content
5. Professional networking and engagement

Each post should be 150-300 words, professional tone, include 3-5 relevant hashtags.

Required JSON Format:
{{
  "posts": [
    {{
      "id": 1,
      "title": "Engaging professional headline",
      "content": "Professional LinkedIn post content here...",
      "hashtags": ["#ProfessionalTag1", "#Industry", "#Business"],
      "call_to_action": "What's your experience with this?",
      "post_type": "professional_insight"
    }}
  ]
}}""",

            "instagram": f"""{base_instructions}
Platform: Instagram Visual Storytelling

Generate 5 unique Instagram posts focusing on:
1. Visual storytelling and brand narrative
2. Behind-the-scenes content ideas
3. User engagement and community building
4. Product/service showcases
5. Inspirational and motivational content

Each post should include engaging captions (50-150 words), visual descriptions, and 5-10 hashtags.

Required JSON Format:
{{
  "posts": [
    {{
      "id": 1,
      "title": "Catchy post title",
      "caption": "Engaging Instagram caption with emojis...",
      "visual_description": "Description of recommended image/video",
      "hashtags": ["#InstagramTag1", "#Visual", "#Engagement", "#Brand"],
      "story_ideas": ["Story idea 1", "Story idea 2"],
      "post_type": "visual_content"
    }}
  ]
}}""",

            "youtube": f"""{base_instructions}
Platform: YouTube Video Content

Generate 5 unique YouTube video concepts focusing on:
1. Educational and tutorial content
2. Industry insights and analysis
3. Entertainment and engagement
4. Product demonstrations or reviews
5. Storytelling and case studies

Each video should include title, description, script outline, and tags.

Required JSON Format:
{{
  "posts": [
    {{
      "id": 1,
      "title": "Compelling YouTube Video Title",
      "description": "Video description for YouTube (100-200 words)",
      "script_outline": [
        "Introduction hook",
        "Main content points",
        "Call to action"
      ],
      "duration_estimate": "5-10 minutes",
      "hashtags": ["#YouTubeTag1", "#Video", "#Content"],
      "thumbnail_description": "Suggested thumbnail visual",
      "post_type": "video_content"
    }}
  ]
}}""",

            "facebook": f"""{base_instructions}
Platform: Facebook Community Engagement

Generate 5 unique Facebook posts focusing on:
1. Community engagement and discussion
2. Brand storytelling and values
3. Event promotion and announcements
4. Customer testimonials and success stories
5. Interactive content and polls

Each post should encourage engagement, be conversational, and include 3-7 hashtags.

Required JSON Format:
{{
  "posts": [
    {{
      "id": 1,
      "title": "Engaging Facebook post title",
      "content": "Facebook post content with community focus...",
      "engagement_type": "question/poll/discussion/announcement",
      "hashtags": ["#FacebookTag1", "#Community", "#Engagement"],
      "call_to_action": "Encourage likes, comments, shares",
      "target_audience": "Description of target audience",
      "post_type": "community_engagement"
    }}
  ]
}}""",

            "blog": f"""{base_instructions}
Platform: Blog Content Creation

Generate 5 unique blog post concepts focusing on:
1. In-depth industry analysis and insights
2. How-to guides and tutorials
3. Case studies and success stories
4. Opinion pieces and thought leadership
5. Resource compilations and listicles

Each blog post should include detailed outline, key points, and SEO considerations.

Required JSON Format:
{{
  "posts": [
    {{
      "id": 1,
      "title": "SEO-Optimized Blog Post Title",
      "meta_description": "SEO meta description (150-160 characters)",
      "outline": [
        "Introduction",
        "Main sections with key points",
        "Conclusion and next steps"
      ],
      "key_points": ["Point 1", "Point 2", "Point 3"],
      "word_count_estimate": "1500-2000 words",
      "hashtags": ["#BlogTag1", "#Content", "#SEO"],
      "cta": "Subscribe to our newsletter for more insights",
      "post_type": "long_form_content"
    }}
  ]
}}"""
        }
        
        return platform_prompts.get(platform.lower(), platform_prompts["linkedin"])

    def generate_social_content(
        self, 
        account_id: str, 
        company_id: str, 
        platform: str, 
        query: str,
        company_banner_id: Optional[str] = None,
        requested_by: Optional[str] = None,
        include_past: bool = False
    ) -> Dict[str, Any]:
        """
        Generate social media content using Gemini AI.
        
        Args:
            account_id: UUID of the account
            company_id: UUID of the company
            platform: Target platform (linkedin, instagram, youtube, facebook, blog)
            query: Content generation query
            company_banner_id: Optional company banner ID
            requested_by: Optional user ID who requested generation
            include_past: Whether to include past generations in context
            
        Returns:
            Dictionary with success status, message, and generation data
        """
        try:
            # Validate inputs
            validation_result = self._validate_generation_inputs(
                account_id, company_id, platform, query
            )
            if not validation_result["success"]:
                return validation_result

            # Get company information for context
            company_info = self._get_company_info(company_id)
            
            # Create generation record
            generation_id = self._create_generation_record(
                account_id=account_id,
                company_id=company_id,
                company_banner_id=company_banner_id,
                requested_by=requested_by,
                platform=platform,
                query=query,
                include_past=include_past
            )
            
            if not generation_id:
                return {
                    "success": False,
                    "message": "Failed to create generation record",
                    "generation": None
                }

            # Generate content with Gemini AI
            try:
                prompt = self.get_platform_prompt(platform, query, company_info)
                
                # Prepare request payload
                request_payload = {
                    "model": "gemini-2.0-flash",
                    "prompt": prompt,
                    "platform": platform,
                    "query": query,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Update generation record with request payload
                self._update_generation_payload(generation_id, request_payload)
                
                # Generate content using Gemini
                response = self.model.generate_content(prompt)
                
                # Parse and validate response
                generated_posts = self._parse_gemini_response(response.text)
                
                if not generated_posts:
                    raise ValueError("Failed to parse Gemini response or empty content")
                
                # Update generation record with results
                self._complete_generation(generation_id, generated_posts)
                
                # Get final generation record
                final_generation = self._get_generation_by_id(generation_id)
                
                return {
                    "success": True,
                    "message": f"Successfully generated {len(generated_posts.get('posts', []))} {platform} posts",
                    "generation": final_generation
                }
                
            except Exception as ai_error:
                # Update generation record with error
                error_message = f"AI generation failed: {str(ai_error)}"
                self._fail_generation(generation_id, error_message)
                
                return {
                    "success": False,
                    "message": error_message,
                    "generation": {"id": generation_id, "status": "failed"}
                }
                
        except Exception as e:
            self.logger.error(f"Social content generation error: {str(e)}")
            return {
                "success": False,
                "message": f"Generation failed: {str(e)}",
                "generation": None
            }

    def _validate_generation_inputs(
        self, account_id: str, company_id: str, platform: str, query: str
    ) -> Dict[str, Any]:
        """Validate generation input parameters."""
        
        # Validate required fields
        if not all([account_id, company_id, platform, query]):
            return {
                "success": False,
                "message": "Missing required fields: account_id, company_id, platform, query"
            }
        
        # Validate platform
        valid_platforms = ["linkedin", "instagram", "youtube", "facebook", "blog"]
        if platform.lower() not in valid_platforms:
            return {
                "success": False,
                "message": f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
            }
        
        # Validate query length
        if len(query.strip()) < 10:
            return {
                "success": False,
                "message": "Query must be at least 10 characters long"
            }
        
        # Validate account exists
        try:
            account_check = self.supabase.table("accounts").select("id").eq("id", account_id).execute()
            if not account_check.data:
                return {
                    "success": False,
                    "message": "Account not found"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Account validation failed: {str(e)}"
            }
        
        # Validate company exists and belongs to account
        try:
            company_check = self.supabase.table("companies").select("id, account_id").eq("id", company_id).execute()
            if not company_check.data:
                return {
                    "success": False,
                    "message": "Company not found"
                }
            if company_check.data[0]["account_id"] != account_id:
                return {
                    "success": False,
                    "message": "Company does not belong to the specified account"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Company validation failed: {str(e)}"
            }
        
        return {"success": True}

    def _get_company_info(self, company_id: str) -> Optional[Dict]:
        """Get company information for content generation context."""
        try:
            result = self.supabase.table("companies").select(
                "name, website, description"
            ).eq("id", company_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            self.logger.error(f"Error fetching company info: {str(e)}")
            return None

    def _create_generation_record(
        self, 
        account_id: str, 
        company_id: str, 
        platform: str, 
        query: str,
        company_banner_id: Optional[str] = None,
        requested_by: Optional[str] = None,
        include_past: bool = False
    ) -> Optional[str]:
        """Create a new generation record in the database."""
        try:
            generation_data = {
                "account_id": account_id,
                "company_id": company_id,
                "platform": platform.lower(),
                "query": query,
                "include_past": include_past,
                "status": "pending"
            }
            
            if company_banner_id:
                generation_data["company_banner_id"] = company_banner_id
            if requested_by:
                generation_data["requested_by"] = requested_by
            
            result = self.supabase.table("social_generations").insert(generation_data).execute()
            
            if result.data:
                return result.data[0]["id"]
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating generation record: {str(e)}")
            return None

    def _update_generation_payload(self, generation_id: str, payload: Dict) -> bool:
        """Update generation record with request payload."""
        try:
            self.supabase.table("social_generations").update({
                "request_payload": payload
            }).eq("id", generation_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error updating generation payload: {str(e)}")
            return False

    def _parse_gemini_response(self, response_text: str) -> Optional[Dict]:
        """Parse and validate Gemini AI response."""
        try:
            # Clean up response text
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            parsed_response = json.loads(cleaned_text)
            
            # Validate structure
            if "posts" not in parsed_response:
                raise ValueError("Response missing 'posts' array")
            
            posts = parsed_response["posts"]
            if not isinstance(posts, list) or len(posts) != 5:
                raise ValueError("Response must contain exactly 5 posts")
            
            # Validate each post has required fields
            for i, post in enumerate(posts):
                if "id" not in post:
                    post["id"] = i + 1
                if "title" not in post:
                    raise ValueError(f"Post {i+1} missing title")
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Response parsing error: {str(e)}")
            return None

    def _complete_generation(self, generation_id: str, generated_posts: Dict) -> bool:
        """Mark generation as completed with results."""
        try:
            self.supabase.table("social_generations").update({
                "generated_posts": generated_posts,
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "error": None
            }).eq("id", generation_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error completing generation: {str(e)}")
            return False

    def _fail_generation(self, generation_id: str, error_message: str) -> bool:
        """Mark generation as failed with error message."""
        try:
            self.supabase.table("social_generations").update({
                "status": "failed",
                "error": error_message,
                "completed_at": datetime.utcnow().isoformat()
            }).eq("id", generation_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error failing generation: {str(e)}")
            return False

    def get_generation_by_id(self, generation_id: str) -> Dict[str, Any]:
        """
        Get a specific social media generation by ID.
        
        Args:
            generation_id: UUID of the generation
            
        Returns:
            Dictionary with success status and generation data
        """
        try:
            result = self.supabase.table("social_generations").select("*").eq("id", generation_id).execute()
            
            if not result.data:
                return {
                    "success": False,
                    "message": "Generation not found",
                    "generation": None
                }
            
            return {
                "success": True,
                "message": "Generation retrieved successfully",
                "generation": result.data[0]
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving generation: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to retrieve generation: {str(e)}",
                "generation": None
            }

    def _get_generation_by_id(self, generation_id: str) -> Optional[Dict]:
        """Internal method to get generation by ID."""
        try:
            result = self.supabase.table("social_generations").select("*").eq("id", generation_id).execute()
            return result.data[0] if result.data else None
        except Exception:
            return None

    def get_generations_by_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get all social media generations for an account.
        
        Args:
            account_id: UUID of the account
            
        Returns:
            Dictionary with success status and generations list
        """
        try:
            result = self.supabase.table("social_generations").select(
                "*"
            ).eq("account_id", account_id).order("created_at", desc=True).execute()
            
            return {
                "success": True,
                "message": f"Retrieved {len(result.data)} generations",
                "generations": result.data
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving generations by account: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to retrieve generations: {str(e)}",
                "generations": []
            }

    def get_generations_by_company(self, company_id: str) -> Dict[str, Any]:
        """
        Get all social media generations for a company.
        
        Args:
            company_id: UUID of the company
            
        Returns:
            Dictionary with success status and generations list
        """
        try:
            result = self.supabase.table("social_generations").select(
                "*"
            ).eq("company_id", company_id).order("created_at", desc=True).execute()
            
            return {
                "success": True,
                "message": f"Retrieved {len(result.data)} generations for company",
                "generations": result.data
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving generations by company: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to retrieve generations: {str(e)}",
                "generations": []
            }

    def delete_generation(self, generation_id: str) -> Dict[str, Any]:
        """
        Delete a social media generation.
        
        Args:
            generation_id: UUID of the generation to delete
            
        Returns:
            Dictionary with success status and message
        """
        try:
            # Check if generation exists
            existing = self.supabase.table("social_generations").select("id").eq("id", generation_id).execute()
            
            if not existing.data:
                return {
                    "success": False,
                    "message": "Generation not found"
                }
            
            # Delete the generation
            self.supabase.table("social_generations").delete().eq("id", generation_id).execute()
            
            return {
                "success": True,
                "message": "Generation deleted successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting generation: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to delete generation: {str(e)}"
            }

    def get_generations_by_platform(self, account_id: str, platform: str) -> Dict[str, Any]:
        """
        Get all generations for an account filtered by platform.
        
        Args:
            account_id: UUID of the account
            platform: Platform to filter by
            
        Returns:
            Dictionary with success status and filtered generations
        """
        try:
            result = self.supabase.table("social_generations").select(
                "*"
            ).eq("account_id", account_id).eq("platform", platform.lower()).order("created_at", desc=True).execute()
            
            return {
                "success": True,
                "message": f"Retrieved {len(result.data)} {platform} generations",
                "generations": result.data
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving generations by platform: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to retrieve {platform} generations: {str(e)}",
                "generations": []
            }