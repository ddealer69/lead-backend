"""
Flask Authentication API
Provides endpoints for user authentication, registration, and account management
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_utils import DatabaseManager
from company_utils import CompanyManager
from smtp_utils import SMTPManager
from social_utils import SocialManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize managers
user_manager = DatabaseManager()
company_manager = CompanyManager()
smtp_manager = SMTPManager()
social_manager = SocialManager()

# Legacy variable names for existing frontend compatibility
db = user_manager
company_mgr = company_manager
smtp_mgr = smtp_manager


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Authentication API is running'
    }), 200

@app.route('/auth/login', methods=['POST'])
def login():
    """
    User login endpoint
    Expected JSON: {
        "email": "user@example.com",
        "password": "userpassword"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Authenticate user
        result = user_manager.authenticate_user(email, password)
        
        if result['success']:
            logger.info(f"Successful login for user: {email}")
            return jsonify(result), 200
        else:
            logger.warning(f"Failed login attempt for user: {email}")
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/auth/signup', methods=['POST'])
def signup():
    """
    User registration endpoint
    Expected JSON: {
        "email": "user@example.com",
        "password": "userpassword",
        "full_name": "John Doe",
        "account_name": "company_name",
        "role": "member"  // optional, defaults to 'member'
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        account_name = data.get('account_name', '').strip()
        role = data.get('role', 'member').strip()
        
        # Validation
        if not email or not password or not full_name or not account_name:
            return jsonify({
                'success': False,
                'message': 'Email, password, full_name, and account_name are required'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters long'
            }), 400
        
        if role not in ['owner', 'admin', 'member']:
            return jsonify({
                'success': False,
                'message': 'Role must be owner, admin, or member'
            }), 400
        
        # Create user
        result = user_manager.create_user(email, password, full_name, account_name, role)
        
        if result['success']:
            logger.info(f"New user created: {email}")
            return jsonify(result), 201
        else:
            logger.warning(f"Failed signup attempt for user: {email}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/auth/delete-account', methods=['DELETE'])
def delete_account():
    """
    Delete user account endpoint
    Expected JSON: {
        "email": "user@example.com",
        "password": "userpassword"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required for account deletion'
            }), 400
        
        # Delete user account
        result = user_manager.delete_user(email, password)
        
        if result['success']:
            logger.info(f"Account deleted for user: {email}")
            return jsonify(result), 200
        else:
            logger.warning(f"Failed account deletion attempt for user: {email}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/user/profile', methods=['GET'])
def get_profile():
    """
    Get user profile endpoint
    Expected query parameter: email
    """
    try:
        email = request.args.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email parameter is required'
            }), 400
        
        user = user_manager.get_user_by_email(email)
        
        if user:
            return jsonify({
                'success': True,
                'message': 'Profile retrieved successfully',
                'user': user
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/user/update-profile', methods=['PUT'])
def update_profile():
    """
    Update user profile endpoint
    Expected JSON: {
        "email": "user@example.com",
        "full_name": "New Name",  // optional
        "role": "admin",          // optional
        "prefs": {"theme": "dark"} // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        # Extract update fields
        updates = {}
        for field in ['full_name', 'role', 'prefs']:
            if field in data:
                updates[field] = data[field]
        
        if not updates:
            return jsonify({
                'success': False,
                'message': 'No valid fields to update'
            }), 400
        
        # Update profile
        result = user_manager.update_user_profile(email, updates)
        
        if result['success']:
            logger.info(f"Profile updated for user: {email}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ===================== COMPANY MANAGEMENT ENDPOINTS =====================

@app.route('/companies', methods=['POST'])
def create_company():
    """
    Create new company endpoint
    Expected JSON: {
        "account_id": "uuid",
        "name": "Company Name",
        "domain": "example.com",      // optional
        "notes": "Some notes",        // optional
        "metadata": {"key": "value"}  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        account_id = data.get('account_id', '').strip()
        name = data.get('name', '').strip()
        domain = data.get('domain', '').strip() if data.get('domain') else None
        notes = data.get('notes', '').strip() if data.get('notes') else None
        metadata = data.get('metadata', {})
        
        if not account_id or not name:
            return jsonify({
                'success': False,
                'message': 'account_id and name are required'
            }), 400
        
        result = company_manager.create_company(account_id, name, domain, notes, metadata)
        
        if result['success']:
            logger.info(f"Company created: {name} for account: {account_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/companies/<company_id>', methods=['GET'])
def get_company(company_id):
    """Get company by ID"""
    try:
        result = company_manager.get_company(company_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/companies/<company_id>', methods=['PUT'])
def update_company(company_id):
    """
    Update company endpoint
    Expected JSON: {
        "name": "New Name",           // optional
        "domain": "newdomain.com",    // optional
        "notes": "Updated notes",     // optional
        "metadata": {"key": "value"}  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = company_manager.update_company(company_id, data)
        
        if result['success']:
            logger.info(f"Company updated: {company_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/companies/<company_id>', methods=['DELETE'])
def delete_company(company_id):
    """Delete company (soft delete)"""
    try:
        result = company_manager.delete_company(company_id)
        
        if result['success']:
            logger.info(f"Company deleted: {company_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/accounts/<account_id>/companies', methods=['GET'])
def get_companies_by_account(account_id):
    """Get all companies for an account"""
    try:
        result = company_manager.get_companies_by_account(account_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get companies by account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ===================== COMPANY BANNER ENDPOINTS =====================

@app.route('/company-banners', methods=['POST'])
def create_company_banner():
    """
    Create new company banner endpoint
    Expected JSON: {
        "company_id": "uuid",
        "name": "Banner Name",
        "logo_url": "https://...",     // optional
        "signature": "Email sig",      // optional
        "metadata": {"key": "value"},  // optional
        "created_by": "user_uuid"      // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        company_id = data.get('company_id', '').strip()
        name = data.get('name', '').strip()
        logo_url = data.get('logo_url', '').strip() if data.get('logo_url') else None
        signature = data.get('signature', '').strip() if data.get('signature') else None
        metadata = data.get('metadata', {})
        created_by = data.get('created_by', '').strip() if data.get('created_by') else None
        
        if not company_id or not name:
            return jsonify({
                'success': False,
                'message': 'company_id and name are required'
            }), 400
        
        result = company_manager.create_company_banner(company_id, name, logo_url, signature, metadata, created_by)
        
        if result['success']:
            logger.info(f"Banner created: {name} for company: {company_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create banner error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/company-banners/<banner_id>', methods=['GET'])
def get_company_banner(banner_id):
    """Get company banner by ID"""
    try:
        result = company_manager.get_company_banner(banner_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get banner error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/company-banners/<banner_id>', methods=['PUT'])
def update_company_banner(banner_id):
    """
    Update company banner endpoint
    Expected JSON: {
        "name": "New Name",           // optional
        "logo_url": "https://...",    // optional
        "signature": "New signature", // optional
        "metadata": {"key": "value"}  // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = company_manager.update_company_banner(banner_id, data)
        
        if result['success']:
            logger.info(f"Banner updated: {banner_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update banner error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/company-banners/<banner_id>', methods=['DELETE'])
def delete_company_banner(banner_id):
    """Delete company banner (soft delete)"""
    try:
        result = company_manager.delete_company_banner(banner_id)
        
        if result['success']:
            logger.info(f"Banner deleted: {banner_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete banner error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/companies/<company_id>/banners', methods=['GET'])
def get_banners_by_company(company_id):
    """Get all banners for a company"""
    try:
        result = company_manager.get_banners_by_company(company_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get banners by company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ===================== COMBINED OPERATIONS =====================

@app.route('/accounts/<account_id>/companies-with-banners', methods=['GET'])
def get_account_companies_with_banners(account_id):
    """Get all companies and their banners for an account"""
    try:
        result = company_manager.get_account_companies_with_banners(account_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get account companies with banners error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/companies-with-banner', methods=['POST'])
def create_company_with_banner():
    """
    Create company and banner in one operation
    Expected JSON: {
        "account_id": "uuid",
        "company_name": "Company Name",
        "company_domain": "example.com",     // optional
        "company_notes": "Notes",            // optional
        "company_metadata": {},              // optional
        "banner_name": "Banner Name",        // optional (defaults to company_name)
        "logo_url": "https://...",           // optional
        "signature": "Email signature",      // optional
        "banner_metadata": {},               // optional
        "created_by": "user_uuid"            // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        account_id = data.get('account_id', '').strip()
        company_name = data.get('company_name', '').strip()
        
        if not account_id or not company_name:
            return jsonify({
                'success': False,
                'message': 'account_id and company_name are required'
            }), 400
        
        result = company_manager.create_company_with_banner(
            account_id=account_id,
            company_name=company_name,
            company_domain=data.get('company_domain'),
            company_notes=data.get('company_notes'),
            company_metadata=data.get('company_metadata'),
            banner_name=data.get('banner_name'),
            logo_url=data.get('logo_url'),
            signature=data.get('signature'),
            banner_metadata=data.get('banner_metadata'),
            created_by=data.get('created_by')
        )
        
        if result['success']:
            logger.info(f"Company with banner created: {company_name} for account: {account_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create company with banner error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ===================== SMTP CREDENTIALS MANAGEMENT ENDPOINTS =====================

@app.route('/smtp-credentials', methods=['POST'])
def create_smtp_credentials():
    """
    Create new SMTP credentials endpoint
    Expected JSON: {
        "account_id": "uuid",
        "display_name": "Gmail - Sales Team",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "username": "sales@company.com",
        "password": "app_password_or_regular_password",
        "auth_type": "app_password",      // optional: plain, oauth2, app_password
        "rate_limit_per_hour": 100,      // optional
        "metadata": {"provider": "gmail"}, // optional
        "created_by": "user_uuid"        // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        # Extract required fields
        account_id = data.get('account_id', '').strip()
        display_name = data.get('display_name', '').strip()
        smtp_host = data.get('smtp_host', '').strip()
        smtp_port = data.get('smtp_port')
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Extract optional fields
        auth_type = data.get('auth_type', 'plain').strip()
        rate_limit_per_hour = data.get('rate_limit_per_hour')
        metadata = data.get('metadata', {})
        created_by = data.get('created_by', '').strip() if data.get('created_by') else None
        
        # Validation
        if not all([account_id, display_name, smtp_host, username, password]):
            return jsonify({
                'success': False,
                'message': 'account_id, display_name, smtp_host, username, and password are required'
            }), 400
        
        if smtp_port is None:
            return jsonify({
                'success': False,
                'message': 'smtp_port is required'
            }), 400
        
        # Create SMTP credentials
        result = smtp_manager.create_smtp_credentials(
            account_id=account_id,
            display_name=display_name,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            username=username,
            password=password,
            auth_type=auth_type,
            rate_limit_per_hour=rate_limit_per_hour,
            metadata=metadata,
            created_by=created_by
        )
        
        if result['success']:
            logger.info(f"SMTP credentials created: {display_name} for account: {account_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create SMTP credentials error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/smtp-credentials/<smtp_id>', methods=['GET'])
def get_smtp_credentials(smtp_id):
    """Get SMTP credentials by ID (without password)"""
    try:
        result = smtp_manager.get_smtp_credentials(smtp_id, include_password=False)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get SMTP credentials error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/smtp-credentials/<smtp_id>', methods=['PUT'])
def update_smtp_credentials(smtp_id):
    """
    Update SMTP credentials endpoint
    Expected JSON: {
        "display_name": "Updated Name",     // optional
        "smtp_host": "smtp.newhost.com",   // optional
        "smtp_port": 465,                  // optional
        "username": "new@email.com",       // optional
        "password": "new_password",        // optional (will encrypt and reset verification)
        "auth_type": "oauth2",             // optional
        "rate_limit_per_hour": 200,        // optional
        "metadata": {"updated": "yes"}     // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = smtp_manager.update_smtp_credentials(smtp_id, data)
        
        if result['success']:
            logger.info(f"SMTP credentials updated: {smtp_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update SMTP credentials error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/smtp-credentials/<smtp_id>', methods=['DELETE'])
def delete_smtp_credentials(smtp_id):
    """Delete SMTP credentials (hard delete for security)"""
    try:
        result = smtp_manager.delete_smtp_credentials(smtp_id)
        
        if result['success']:
            logger.info(f"SMTP credentials deleted: {smtp_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete SMTP credentials error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/accounts/<account_id>/smtp-credentials', methods=['GET'])
def get_smtp_credentials_by_account(account_id):
    """Get all SMTP credentials for an account (without passwords)"""
    try:
        result = smtp_manager.get_smtp_credentials_by_account(account_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get SMTP credentials by account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/smtp-credentials/<smtp_id>/verify', methods=['POST'])
def verify_smtp_credentials(smtp_id):
    """
    Verify SMTP credentials endpoint
    Expected JSON: {
        "test_connection": true  // optional: whether to test actual connection
    }
    """
    try:
        data = request.get_json() or {}
        test_connection = data.get('test_connection', False)
        
        result = smtp_manager.verify_smtp_credentials(smtp_id, test_connection)
        
        if result['success']:
            logger.info(f"SMTP credentials verified: {smtp_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Verify SMTP credentials error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/accounts/<account_id>/smtp-credentials/verified', methods=['GET'])
def get_verified_smtp_credentials(account_id):
    """Get only verified SMTP credentials for an account"""
    try:
        result = smtp_manager.get_verified_smtp_credentials(account_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get verified SMTP credentials error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# SOCIAL MEDIA CONTENT GENERATION ROUTES
# ============================================================================

@app.route('/social-generate', methods=['POST'])
def generate_social_content():
    """
    Generate social media content using AI.
    
    Required fields: account_id, company_id, platform, query
    Optional fields: company_banner_id, requested_by, include_past
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['account_id', 'company_id', 'platform', 'query']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}',
                'generation': None
            }), 400
        
        # Generate content
        result = social_manager.generate_social_content(
            account_id=data['account_id'],
            company_id=data['company_id'],
            platform=data['platform'],
            query=data['query'],
            company_banner_id=data.get('company_banner_id'),
            requested_by=data.get('requested_by'),
            include_past=data.get('include_past', False)
        )
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Social content generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'generation': None
        }), 500

@app.route('/social-generations/<generation_id>', methods=['GET'])
def get_social_generation(generation_id):
    """Get a specific social media generation by ID."""
    try:
        result = social_manager.get_generation_by_id(generation_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Get social generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'generation': None
        }), 500

@app.route('/accounts/<account_id>/social-generations', methods=['GET'])
def get_social_generations_by_account(account_id):
    """Get all social media generations for an account."""
    try:
        # Check for platform filter
        platform = request.args.get('platform')
        
        if platform:
            result = social_manager.get_generations_by_platform(account_id, platform)
        else:
            result = social_manager.get_generations_by_account(account_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get social generations by account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'generations': []
        }), 500

@app.route('/companies/<company_id>/social-generations', methods=['GET'])
def get_social_generations_by_company(company_id):
    """Get all social media generations for a company."""
    try:
        result = social_manager.get_generations_by_company(company_id)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get social generations by company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'generations': []
        }), 500

@app.route('/social-generations/<generation_id>', methods=['DELETE'])
def delete_social_generation(generation_id):
    """Delete a social media generation."""
    try:
        result = social_manager.delete_generation(generation_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Delete social generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/social-platforms', methods=['GET'])
def get_supported_platforms():
    """Get list of supported social media platforms."""
    return jsonify({
        'success': True,
        'message': 'Supported social media platforms',
        'platforms': [
            {
                'id': 'linkedin',
                'name': 'LinkedIn',
                'description': 'Professional networking and business content'
            },
            {
                'id': 'instagram', 
                'name': 'Instagram',
                'description': 'Visual storytelling and brand narrative'
            },
            {
                'id': 'youtube',
                'name': 'YouTube', 
                'description': 'Video content and tutorials'
            },
            {
                'id': 'facebook',
                'name': 'Facebook',
                'description': 'Community engagement and social interaction'
            },
            {
                'id': 'blog',
                'name': 'Blog Posts',
                'description': 'Long-form content and thought leadership'
            }
        ]
    }), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'message': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
