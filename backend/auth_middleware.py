"""
Authentication Middleware
Provides decorator for protecting Flask routes with JWT validation
"""
from functools import wraps
from flask import request, jsonify
import jwt
from auth_utils import verify_access_token, extract_user_id_from_token


def require_auth(f):
    """
    Decorator to protect Flask routes with JWT authentication
    
    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            user_id = request.user_id
            # Access user_id from request context
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"status": "error", "message": "Missing authorization header"}), 401
        
        # Check if header is in correct format: "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({"status": "error", "message": "Invalid authorization header format"}), 401
        
        token = parts[1]
        
        try:
            # Verify token and extract payload
            payload = verify_access_token(token)
            user_id = payload.get("user_id")
            
            if not user_id:
                return jsonify({"status": "error", "message": "Invalid token payload"}), 401
            
            # Attach user_id to request context for use in the route handler
            request.user_id = user_id
            request.user_email = payload.get("email")
            
            return f(*args, **kwargs)
            
        except jwt.InvalidTokenError as e:
            return jsonify({"status": "error", "message": str(e)}), 401
        except Exception as e:
            return jsonify({"status": "error", "message": f"Authentication error: {str(e)}"}), 401
    
    return decorated_function


def get_user_id_from_request() -> str:
    """
    Get the user_id from the current request context
    Should be used inside a @require_auth protected route
    
    Returns:
        The user_id extracted from the JWT token
    
    Raises:
        AttributeError: If not in an authenticated context
    """
    return getattr(request, 'user_id', None)


def get_user_email_from_request() -> str:
    """
    Get the user email from the current request context
    Should be used inside a @require_auth protected route
    
    Returns:
        The user email from the JWT token (may be None)
    """
    return getattr(request, 'user_email', None)
