"""
Flask Authentication API
Provides endpoints for user authentication, registration, and account management
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_utils import DatabaseManager
from company_utils import CompanyManager
from campaign_utils import CampaignManager, EmailDeliveryLogsManager
from email_sender_utils import EmailSenderManager
from smtp_utils import SMTPManager
from social_utils import SocialManager
from search_utils import SearchManager
from leads_utils import LeadsManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email_direct_smtp(smtp_config, recipient_email, subject, body):
    """Send email using direct SMTP approach (similar to OTP sending method)."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = smtp_config['username']
        msg["To"] = recipient_email
        msg["Subject"] = subject

        # Attach body (support both HTML and plain text)
        if body.strip().startswith('<!DOCTYPE') or body.strip().startswith('<html'):
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port'])
        server.starttls()  # Enable encryption
        
        # Login using decrypted password
        server.login(smtp_config['username'], smtp_config['password'])
        
        # Send message
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Direct SMTP: Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Direct SMTP error sending to {recipient_email}: {str(e)}")
        return False

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize managers
user_manager = DatabaseManager()
company_manager = CompanyManager()
campaign_manager = CampaignManager()
email_delivery_manager = EmailDeliveryLogsManager()
email_sender_manager = EmailSenderManager()
smtp_manager = SMTPManager()
social_manager = SocialManager()
search_manager = SearchManager()
leads_manager = LeadsManager()

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
# SEARCH QUERY MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/search/queries', methods=['POST'])
def create_search_query():
    """
    Create new search query endpoint
    Expected JSON: {
        "account_id": "uuid",
        "company_id": "uuid",
        "created_by": "uuid",
        "query_string": "site:linkedin.com/in/ software engineer",
        "name": "Software Engineers Search",          // optional
        "company_banner_id": "uuid",                  // optional
        "pages_requested": 5,                         // optional, default 1
        "dedupe_mode": "per_company",                 // optional, default per_company
        "notes": "Search for senior engineers"       // optional
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
        company_id = data.get('company_id', '').strip()
        created_by = data.get('created_by', '').strip()
        query_string = data.get('query_string', '').strip()
        
        # Extract optional fields
        name = data.get('name', '').strip() if data.get('name') else None
        company_banner_id = data.get('company_banner_id', '').strip() if data.get('company_banner_id') else None
        pages_requested = data.get('pages_requested', 1)
        dedupe_mode = data.get('dedupe_mode', 'per_company')
        notes = data.get('notes', '').strip() if data.get('notes') else None
        
        # Validation
        if not all([account_id, company_id, created_by, query_string]):
            return jsonify({
                'success': False,
                'message': 'account_id, company_id, created_by, and query_string are required'
            }), 400
        
        result = search_manager.create_query(
            account_id=account_id,
            company_id=company_id,
            created_by=created_by,
            query_string=query_string,
            name=name,
            company_banner_id=company_banner_id,
            pages_requested=pages_requested,
            dedupe_mode=dedupe_mode,
            notes=notes
        )
        
        if result['success']:
            logger.info(f"Search query created: {query_string} for account: {account_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create search query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>', methods=['GET'])
def get_search_query(query_id):
    """Get search query by ID"""
    try:
        result = search_manager.get_query(query_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get search query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>', methods=['PUT'])
def update_search_query(query_id):
    """
    Update search query endpoint
    Expected JSON: {
        "name": "Updated Search Name",     // optional
        "query_string": "new query",      // optional
        "pages_requested": 10,            // optional
        "status": "paused",               // optional
        "notes": "Updated notes"          // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = search_manager.update_query(query_id, data)
        
        if result['success']:
            logger.info(f"Search query updated: {query_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update search query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>', methods=['DELETE'])
def delete_search_query(query_id):
    """Delete search query and all associated results"""
    try:
        result = search_manager.delete_query(query_id)
        
        if result['success']:
            logger.info(f"Search query deleted: {query_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete search query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/accounts/<account_id>/queries', methods=['GET'])
def get_search_queries_by_account(account_id):
    """Get all search queries for an account"""
    try:
        result = search_manager.get_queries_by_account(account_id)
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get search queries by account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/companies/<company_id>/queries', methods=['GET'])
def get_search_queries_by_company(company_id):
    """Get all search queries for a company"""
    try:
        result = search_manager.get_queries_by_company(company_id)
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get search queries by company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>/process', methods=['POST'])
def process_search_query(query_id):
    """Process search query by executing Google searches for all requested pages"""
    try:
        result = search_manager.process_query(query_id)
        
        if result['success']:
            logger.info(f"Search query processed: {query_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Process search query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>/results', methods=['GET'])
def get_search_results(query_id):
    """Get all search results for a query"""
    try:
        processed_only = request.args.get('processed_only', 'false').lower() == 'true'
        result = search_manager.get_search_results_by_query(query_id, processed_only)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get search results error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>/results', methods=['DELETE'])
def delete_search_results(query_id):
    """Delete all search results for a query"""
    try:
        result = search_manager.delete_search_results_by_query(query_id)
        
        if result['success']:
            logger.info(f"Search results deleted for query: {query_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete search results error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/search/queries/<query_id>/results/mark-processed', methods=['POST'])
def mark_search_results_processed(query_id):
    """Mark all search results for a query as processed"""
    try:
        result = search_manager.mark_results_processed(query_id)
        
        if result['success']:
            logger.info(f"Search results marked as processed for query: {query_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Mark search results processed error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# LEADS MANAGEMENT ROUTES
# ============================================================================

@app.route('/api/leads', methods=['POST'])
def create_lead():
    """
    Create new lead endpoint
    Expected JSON: {
        "account_id": "uuid",
        "company_id": "uuid",
        "created_by": "uuid",
        "profile_url": "https://linkedin.com/in/johndoe",
        "source_query_id": "uuid",                    // optional
        "first_name": "John",                         // optional
        "last_name": "Doe",                           // optional
        "title": "Software Engineer",                 // optional
        "company_name": "Tech Corp",                  // optional
        "location": "San Francisco, CA",              // optional
        "notes": "Potential candidate"                // optional
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
        company_id = data.get('company_id', '').strip()
        created_by = data.get('created_by', '').strip()
        profile_url = data.get('profile_url', '').strip()
        
        # Extract optional fields
        source_query_id = data.get('source_query_id', '').strip() if data.get('source_query_id') else None
        first_name = data.get('first_name', '').strip() if data.get('first_name') else None
        last_name = data.get('last_name', '').strip() if data.get('last_name') else None
        title = data.get('title', '').strip() if data.get('title') else None
        company_name = data.get('company_name', '').strip() if data.get('company_name') else None
        location = data.get('location', '').strip() if data.get('location') else None
        notes = data.get('notes', '').strip() if data.get('notes') else None
        
        # Validation
        if not all([account_id, company_id, created_by, profile_url]):
            return jsonify({
                'success': False,
                'message': 'account_id, company_id, created_by, and profile_url are required'
            }), 400
        
        result = leads_manager.create_lead(
            account_id=account_id,
            company_id=company_id,
            created_by=created_by,
            profile_url=profile_url,
            source_query_id=source_query_id,
            first_name=first_name,
            last_name=last_name,
            title=title,
            company_name=company_name,
            location=location,
            notes=notes
        )
        
        if result['success']:
            logger.info(f"Lead created: {profile_url} for account: {account_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/<lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Get lead by ID"""
    try:
        result = leads_manager.get_lead(lead_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """
    Update lead endpoint
    Expected JSON: {
        "first_name": "John",                // optional
        "last_name": "Doe",                  // optional
        "title": "Senior Software Engineer", // optional
        "company_name": "New Corp",          // optional
        "location": "New York, NY",          // optional
        "notes": "Updated notes"             // optional
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        result = leads_manager.update_lead(lead_id, data)
        
        if result['success']:
            logger.info(f"Lead updated: {lead_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/<lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Delete lead"""
    try:
        result = leads_manager.delete_lead(lead_id)
        
        if result['success']:
            logger.info(f"Lead deleted: {lead_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Delete lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/accounts/<account_id>', methods=['GET'])
def get_leads_by_account(account_id):
    """Get all leads for an account"""
    try:
        enriched_only = request.args.get('enriched_only', 'false').lower() == 'true'
        result = leads_manager.get_leads_by_account(account_id, enriched_only)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get leads by account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/companies/<company_id>', methods=['GET'])
def get_leads_by_company(company_id):
    """Get all leads for a company"""
    try:
        enriched_only = request.args.get('enriched_only', 'false').lower() == 'true'
        result = leads_manager.get_leads_by_company(company_id, enriched_only)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get leads by company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/queries/<query_id>', methods=['GET'])
def get_leads_by_query(query_id):
    """Get all leads created from a specific search query"""
    try:
        result = leads_manager.get_leads_by_query(query_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get leads by query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/<lead_id>/enrich', methods=['POST'])
def enrich_lead(lead_id):
    """Enrich a single lead using Apify LinkedIn scraper"""
    try:
        # Get optional parameters for creating new leads
        account_id = None
        company_id = None
        created_by = None
        company_banner_id = None
        source_query_id = None
        google_result_id = None
        
        # Check if request has JSON data
        if request.is_json:
            data = request.get_json() or {}
            account_id = data.get('account_id')
            company_id = data.get('company_id')
            created_by = data.get('created_by')
            company_banner_id = data.get('company_banner_id')
            source_query_id = data.get('source_query_id')
            google_result_id = data.get('google_result_id')
        
        result = leads_manager.enrich_lead(lead_id, account_id, company_id, created_by, 
                                         company_banner_id, source_query_id, google_result_id)
        
        if result['success']:
            logger.info(f"Lead enriched: {lead_id}")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Enrich lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/bulk-enrich', methods=['POST'])
def bulk_enrich_leads():
    """
    Enrich multiple leads in batch using Apify
    Expected JSON: {
        "google_result_ids": ["uuid1", "uuid2", "uuid3"],
        "account_id": "uuid",
        "company_id": "uuid", 
        "created_by": "uuid",
        "company_banner_id": "uuid" (optional),
        "source_query_id": "uuid" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        google_result_ids = data.get('google_result_ids', [])
        account_id = data.get('account_id')
        company_id = data.get('company_id')
        created_by = data.get('created_by')
        company_banner_id = data.get('company_banner_id')
        source_query_id = data.get('source_query_id')
        
        if not google_result_ids or not isinstance(google_result_ids, list):
            return jsonify({
                'success': False,
                'message': 'google_result_ids must be a non-empty array'
            }), 400
            
        if not account_id or not company_id or not created_by:
            return jsonify({
                'success': False,
                'message': 'account_id, company_id, and created_by are required'
            }), 400
        
        result = leads_manager.bulk_enrich_leads(google_result_ids, account_id, company_id, created_by, 
                                               company_banner_id, source_query_id)
        
        if result['success']:
            logger.info(f"Bulk enrichment completed for {len(google_result_ids)} leads")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Bulk enrich leads error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/leads/from-search/<query_id>', methods=['POST'])
def create_leads_from_search(query_id):
    """
    Create leads from Google search results containing LinkedIn profiles
    Expected JSON: {
        "account_id": "uuid",
        "company_id": "uuid",
        "created_by": "uuid"
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
        company_id = data.get('company_id', '').strip()
        created_by = data.get('created_by', '').strip()
        
        if not all([account_id, company_id, created_by]):
            return jsonify({
                'success': False,
                'message': 'account_id, company_id, and created_by are required'
            }), 400
        
        result = leads_manager.create_leads_from_search_results(
            query_id=query_id,
            account_id=account_id,
            company_id=company_id,
            created_by=created_by
        )
        
        if result['success']:
            logger.info(f"Created {result['leads_created']} leads from search query: {query_id}")
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create leads from search error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# CAMPAIGN MANAGEMENT API
# ============================================================================

@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    """Create new campaign"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Required fields
        account_id = data.get('account_id')
        company_id = data.get('company_id')
        name = data.get('name')
        
        if not all([account_id, company_id, name]):
            return jsonify({
                'success': False,
                'message': 'account_id, company_id, and name are required'
            }), 400
        
        # Optional fields
        campaign_type = data.get('campaign_type', 'email')
        created_by = data.get('created_by')
        company_banner_id = data.get('company_banner_id')
        smtp_credential_id = data.get('smtp_credential_id')
        subject_template = data.get('subject_template')
        body_template = data.get('body_template')
        send_rate_per_hour = data.get('send_rate_per_hour')
        max_retries = data.get('max_retries', 3)
        status = data.get('status', 'draft')
        
        result = campaign_manager.create_campaign(
            account_id=account_id,
            company_id=company_id,
            name=name,
            campaign_type=campaign_type,
            created_by=created_by,
            company_banner_id=company_banner_id,
            smtp_credential_id=smtp_credential_id,
            subject_template=subject_template,
            body_template=body_template,
            send_rate_per_hour=send_rate_per_hour,
            max_retries=max_retries,
            status=status
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create campaign error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get campaign by ID"""
    try:
        result = campaign_manager.get_campaign(campaign_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get campaign error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaigns/<campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """Update campaign"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        result = campaign_manager.update_campaign(campaign_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update campaign error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaigns/<campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Delete campaign"""
    try:
        result = campaign_manager.delete_campaign(campaign_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Delete campaign error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaigns/companies/<company_id>', methods=['GET'])
def get_campaigns_by_company(company_id):
    """Get all campaigns for a company"""
    try:
        status = request.args.get('status')
        result = campaign_manager.get_campaigns_by_company(company_id, status)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get campaigns by company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaigns/accounts/<account_id>', methods=['GET'])
def get_campaigns_by_account(account_id):
    """Get all campaigns for an account"""
    try:
        status = request.args.get('status')
        result = campaign_manager.get_campaigns_by_account(account_id, status)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get campaigns by account error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaigns/<campaign_id>/stats', methods=['GET'])
def get_campaign_stats(campaign_id):
    """Get campaign statistics"""
    try:
        result = campaign_manager.get_campaign_stats(campaign_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get campaign stats error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# CAMPAIGN LEADS MANAGEMENT API
# ============================================================================

@app.route('/api/campaign-leads', methods=['POST'])
def create_campaign_lead():
    """Create new campaign lead"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Required fields
        campaign_id = data.get('campaign_id')
        query_id = data.get('query_id')
        
        if not all([campaign_id, query_id]):
            return jsonify({
                'success': False,
                'message': 'campaign_id and query_id are required'
            }), 400
        
        # Optional fields
        status = data.get('status', 'queued')
        send_attempts = data.get('send_attempts', 0)
        last_sent_at = data.get('last_sent_at')
        scheduled_at = data.get('scheduled_at')
        personalization_vars = data.get('personalization_vars')
        error = data.get('error')
        
        result = campaign_manager.create_campaign_lead(
            campaign_id=campaign_id,
            query_id=query_id,
            status=status,
            send_attempts=send_attempts,
            last_sent_at=last_sent_at,
            scheduled_at=scheduled_at,
            personalization_vars=personalization_vars,
            error=error
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create campaign lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaign-leads/<campaign_lead_id>', methods=['GET'])
def get_campaign_lead(campaign_lead_id):
    """Get campaign lead by ID"""
    try:
        result = campaign_manager.get_campaign_lead(campaign_lead_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get campaign lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaign-leads/<campaign_lead_id>', methods=['PUT'])
def update_campaign_lead(campaign_lead_id):
    """Update campaign lead"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        result = campaign_manager.update_campaign_lead(campaign_lead_id, data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update campaign lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaign-leads/<campaign_lead_id>', methods=['DELETE'])
def delete_campaign_lead(campaign_lead_id):
    """Delete campaign lead"""
    try:
        result = campaign_manager.delete_campaign_lead(campaign_lead_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Delete campaign lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaign-leads/campaigns/<campaign_id>', methods=['GET'])
def get_campaign_leads_by_campaign(campaign_id):
    """Get all campaign leads for a campaign"""
    try:
        status = request.args.get('status')
        result = campaign_manager.get_campaign_leads_by_campaign(campaign_id, status)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get campaign leads by campaign error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaign-leads/queries/<query_id>', methods=['GET'])
def get_campaign_leads_by_query(query_id):
    """Get all campaign leads for a query"""
    try:
        result = campaign_manager.get_campaign_leads_by_query(query_id)
        
        return jsonify(result), 200
            
    except Exception as e:
        logger.error(f"Get campaign leads by query error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/campaign-leads/bulk', methods=['POST'])
def bulk_create_campaign_leads():
    """Create multiple campaign leads for a campaign"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Required fields
        campaign_id = data.get('campaign_id')
        query_ids = data.get('query_ids')
        
        if not all([campaign_id, query_ids]):
            return jsonify({
                'success': False,
                'message': 'campaign_id and query_ids are required'
            }), 400
        
        if not isinstance(query_ids, list) or len(query_ids) == 0:
            return jsonify({
                'success': False,
                'message': 'query_ids must be a non-empty list'
            }), 400
        
        # Optional fields
        status = data.get('status', 'queued')
        scheduled_at = data.get('scheduled_at')
        
        result = campaign_manager.bulk_create_campaign_leads(
            campaign_id=campaign_id,
            query_ids=query_ids,
            status=status,
            scheduled_at=scheduled_at
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Bulk create campaign leads error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# CAMPAIGN LEADS BY COMPANY ROUTES
# ============================================================================

@app.route('/api/campaign-leads/companies/<company_id>', methods=['GET'])
def get_campaign_leads_by_company(company_id):
    """Get all campaign leads for a company"""
    try:
        status = request.args.get('status')
        result = campaign_manager.get_campaign_leads_by_company(company_id, status)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get campaign leads by company error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# EMAIL DELIVERY LOGS ROUTES
# ============================================================================

@app.route('/api/email-delivery-logs', methods=['POST'])
def create_email_delivery_log():
    """Create new email delivery log"""
    try:
        data = request.get_json()
        
        # Optional fields
        campaign_lead_id = data.get('campaign_lead_id')
        campaign_id = data.get('campaign_id')
        smtp_credential_id = data.get('smtp_credential_id')
        recipient = data.get('recipient')
        event_type = data.get('event_type', 'delivered')
        provider_event = data.get('provider_event')
        
        result = email_delivery_manager.create_email_delivery_log(
            campaign_lead_id=campaign_lead_id,
            campaign_id=campaign_id,
            smtp_credential_id=smtp_credential_id,
            recipient=recipient,
            event_type=event_type,
            provider_event=provider_event
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Create email delivery log error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/email-delivery-logs/<log_id>', methods=['GET'])
def get_email_delivery_log(log_id):
    """Get email delivery log by ID"""
    try:
        result = email_delivery_manager.get_delivery_log(log_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get email delivery log error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/email-delivery-logs/<log_id>', methods=['DELETE'])
def delete_email_delivery_log(log_id):
    """Delete email delivery log"""
    try:
        result = email_delivery_manager.delete_delivery_log(log_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Delete email delivery log error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/email-delivery-logs/campaigns/<campaign_id>', methods=['GET'])
def get_delivery_logs_by_campaign(campaign_id):
    """Get all delivery logs for a campaign"""
    try:
        event_type = request.args.get('event_type')
        result = email_delivery_manager.get_delivery_logs_by_campaign(campaign_id, event_type)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get delivery logs by campaign error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@app.route('/api/email-delivery-logs/campaign-leads/<campaign_lead_id>', methods=['GET'])
def get_delivery_logs_by_campaign_lead(campaign_lead_id):
    """Get all delivery logs for a campaign lead"""
    try:
        result = email_delivery_manager.get_delivery_logs_by_campaign_lead(campaign_lead_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get delivery logs by campaign lead error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

# ============================================================================
# EMAIL SENDER ROUTES
# ============================================================================

@app.route('/api/campaigns/<campaign_id>/send-emails', methods=['POST'])
def send_campaign_emails(campaign_id):
    """Send emails to all queued leads in a campaign"""
    try:
        result = email_sender_manager.send_campaign_emails(campaign_id)
        
        if result['success']:
            # Determine HTTP status code based on results
            if result.get('emails_failed', 0) > 0 and result.get('emails_sent', 0) == 0:
                # All failed
                return jsonify(result), 400
            elif result.get('emails_failed', 0) > 0:
                # Partial success
                return jsonify(result), 207  # Multi-status
            else:
                # All successful
                return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Send campaign emails error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'emails_sent': 0,
            'emails_failed': 0,
            'results': []
        }), 500

# ============================================================================
# DEBUG ENDPOINT FOR SMTP CREDENTIALS
# ============================================================================

@app.route('/api/campaigns/<campaign_id>/debug-smtp', methods=['GET'])
def debug_smtp_config(campaign_id):
    """Debug endpoint to check SMTP configuration for a campaign"""
    try:
        # Get campaign details
        campaign_result = campaign_manager.get_campaign(campaign_id)
        if not campaign_result['success']:
            return jsonify({
                'success': False,
                'message': 'Campaign not found'
            }), 404
        
        campaign = campaign_result['campaign']
        smtp_credential_id = campaign.get('smtp_credential_id')
        
        if not smtp_credential_id:
            return jsonify({
                'success': False,
                'message': 'Campaign does not have SMTP credentials configured'
            }), 400
        
        # Get SMTP credentials (with password for debugging)
        smtp_result = smtp_manager.get_smtp_credentials(smtp_credential_id, include_password=True)
        if not smtp_result['success']:
            return jsonify({
                'success': False,
                'message': 'SMTP credentials not found'
            }), 404
        
        smtp_config = smtp_result['smtp_credentials']
        
        return jsonify({
            'success': True,
            'message': 'SMTP configuration retrieved',
            'smtp_config': {
                'smtp_host': smtp_config.get('smtp_host'),
                'smtp_port': smtp_config.get('smtp_port'),
                'username': smtp_config.get('username'),
                'password': smtp_config.get('password', 'NOT_FOUND'),  # Show decrypted password
                'auth_type': smtp_config.get('auth_type'),
                'display_name': smtp_config.get('display_name')
            },
            'campaign_info': {
                'campaign_id': campaign_id,
                'campaign_name': campaign.get('name'),
                'subject_template': campaign.get('subject_template'),
                'body_template': campaign.get('body_template', '')[:100] + '...' if campaign.get('body_template') else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Debug SMTP config error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Debug error: {str(e)}'
        }), 500

# ============================================================================
# CUSTOM EMAIL SENDING ENDPOINT
# ============================================================================

@app.route('/api/campaigns/<campaign_id>/send-custom-emails', methods=['POST'])
def send_custom_emails(campaign_id):
    """
    Send personalized emails to a custom list using campaign templates and SMTP settings
    Expected JSON: {
        "recipients": [
            {
                "email": "john@example.com",
                "full_name": "John Doe"
            },
            {
                "email": "jane@example.com", 
                "full_name": "Jane Smith"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No JSON data provided'
            }), 400
        
        recipients = data.get('recipients', [])
        
        if not recipients or not isinstance(recipients, list):
            return jsonify({
                'success': False,
                'message': 'Recipients list is required and must be an array'
            }), 400
        
        # Validate recipients format
        for recipient in recipients:
            if not isinstance(recipient, dict) or 'email' not in recipient or 'full_name' not in recipient:
                return jsonify({
                    'success': False,
                    'message': 'Each recipient must have email and full_name fields'
                }), 400
        
        # Get campaign details including templates and SMTP ID
        campaign_result = campaign_manager.get_campaign(campaign_id)
        if not campaign_result['success']:
            return jsonify({
                'success': False,
                'message': 'Campaign not found'
            }), 404
        
        campaign = campaign_result['campaign']
        smtp_credential_id = campaign.get('smtp_credential_id')
        subject_template = campaign.get('subject_template', '')
        body_template = campaign.get('body_template', '')
        
        if not smtp_credential_id:
            return jsonify({
                'success': False,
                'message': 'Campaign does not have SMTP credentials configured'
            }), 400
        
        if not subject_template or not body_template:
            return jsonify({
                'success': False,
                'message': 'Campaign does not have email templates configured'
            }), 400
        
        # Get SMTP credentials (with password for sending)
        smtp_result = smtp_manager.get_smtp_credentials(smtp_credential_id, include_password=True)
        if not smtp_result['success']:
            return jsonify({
                'success': False,
                'message': 'SMTP credentials not found'
            }), 404
        
        smtp_config = smtp_result['smtp_credentials']
        
        # Debug: Print SMTP configuration (including decrypted password)
        logger.info(f"=== SMTP CONFIG DEBUG ===")
        logger.info(f"Host: {smtp_config.get('smtp_host')}")
        logger.info(f"Port: {smtp_config.get('smtp_port')}")
        logger.info(f"Username: {smtp_config.get('username')}")
        logger.info(f"Password: {smtp_config.get('password')}")  # This will show the decrypted password
        logger.info(f"Auth Type: {smtp_config.get('auth_type')}")
        logger.info(f"========================")
        
        # Prepare results tracking
        emails_sent = 0
        emails_failed = 0
        results = []
        
        # Send email to each recipient
        for recipient in recipients:
            try:
                email = recipient['email'].strip()
                full_name = recipient['full_name'].strip()
                
                # Simple template personalization (like your OTP method)
                personalized_subject = subject_template.replace('{full_name}', full_name)
                personalized_subject = personalized_subject.replace('{email}', email)
                
                personalized_body = body_template.replace('{full_name}', full_name)
                personalized_body = personalized_body.replace('{email}', email)
                
                logger.info(f"Sending email to: {email}")
                logger.info(f"Subject: {personalized_subject}")
                logger.info(f"Body preview: {personalized_body[:100]}...")
                
                # Send email using direct SMTP approach (like your OTP method)
                success = send_email_direct_smtp(
                    smtp_config=smtp_config,
                    recipient_email=email,
                    subject=personalized_subject,
                    body=personalized_body
                )
                
                if success:
                    emails_sent += 1
                    results.append({
                        'email': email,
                        'full_name': full_name,
                        'status': 'sent',
                        'subject': personalized_subject,
                        'message': 'Email sent successfully'
                    })
                    logger.info(f"✅ Custom email sent successfully to: {email}")
                else:
                    emails_failed += 1
                    results.append({
                        'email': email,
                        'full_name': full_name,
                        'status': 'failed',
                        'subject': personalized_subject,
                        'error': 'SMTP sending failed - check logs for details'
                    })
                    logger.error(f"❌ Failed to send custom email to: {email}")
                    
            except Exception as recipient_error:
                emails_failed += 1
                results.append({
                    'email': recipient.get('email', 'unknown'),
                    'full_name': recipient.get('full_name', 'unknown'),
                    'status': 'failed',
                    'subject': subject_template,
                    'error': f'Error processing recipient: {str(recipient_error)}'
                })
                logger.error(f"Exception processing recipient {recipient.get('email', 'unknown')}: {str(recipient_error)}")
        
        # Return comprehensive results
        return jsonify({
            'success': True,
            'message': f'Custom email sending completed. {emails_sent} sent, {emails_failed} failed',
            'campaign_id': campaign_id,
            'emails_sent': emails_sent,
            'emails_failed': emails_failed,
            'total_recipients': len(recipients),
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Send custom emails error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error',
            'emails_sent': 0,
            'emails_failed': 0,
            'results': []
        }), 500

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
