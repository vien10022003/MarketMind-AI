"""
Authentication Routes
Handles user registration and login endpoints
Supports both username/password and Google OAuth
"""
import os
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Create blueprint
auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/auth')


def init_auth_routes(mongo):
    """
    Initialize auth routes with MongoDB connection
    
    Args:
        mongo: MongoDBManager instance
    """
    
    @auth_blueprint.route('/register', methods=['POST', 'OPTIONS'])
    def register():
        """
        Register a new user with username and password
        
        Request JSON:
        {
            "username": "user@example.com",
            "password": "secure_password",
            "name": "User Name" (optional)
        }
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"status": "error", "message": "Missing request body"}), 400
            
            username = data.get('username', '').strip().lower()
            password = data.get('password', '').strip()
            name = data.get('name', username).strip()
            
            # Validation
            if not username or not password:
                return jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400
            
            if len(password) < 6:
                return jsonify({
                    "status": "error",
                    "message": "Password must be at least 6 characters"
                }), 400
            
            # Check if user already exists
            users_collection = mongo.db['users']
            existing_user = users_collection.find_one({'username': username})
            
            if existing_user:
                return jsonify({
                    "status": "error",
                    "message": "Username already exists"
                }), 409
            
            # Create new user
            hashed_password = hash_password(password)
            new_user = {
                'username': username,
                'password_hash': hashed_password,
                'name': name,
                'auth_method': 'password',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            
            result = users_collection.insert_one(new_user)
            user_id = str(result.inserted_id)
            
            # Create access token
            token_data = create_access_token(user_id, username)
            
            return jsonify({
                "status": "success",
                "message": "User registered successfully",
                "access_token": token_data['access_token'],
                "token_type": token_data['token_type'],
                "expires_in": token_data['expires_in'],
                "user": {
                    "id": user_id,
                    "username": username,
                    "name": name,
                }
            }), 201
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Registration error: {str(e)}"
            }), 500
    
    
    @auth_blueprint.route('/login', methods=['POST', 'OPTIONS'])
    def login():
        """
        Login with username and password
        
        Request JSON:
        {
            "username": "user@example.com",
            "password": "secure_password"
        }
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({"status": "error", "message": "Missing request body"}), 400
            
            username = data.get('username', '').strip().lower()
            password = data.get('password', '').strip()
            
            if not username or not password:
                return jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400
            
            # Find user
            users_collection = mongo.db['users']
            user = users_collection.find_one({'username': username})
            
            if not user or not verify_password(password, user.get('password_hash', '')):
                return jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401
            
            # Create access token
            user_id = str(user['_id'])
            token_data = create_access_token(user_id, username)
            
            # Update last login
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.now()}}
            )
            
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "access_token": token_data['access_token'],
                "token_type": token_data['token_type'],
                "expires_in": token_data['expires_in'],
                "user": {
                    "id": user_id,
                    "username": username,
                    "name": user.get('name', username),
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Login error: {str(e)}"
            }), 500
    
    
    @auth_blueprint.route('/google-login', methods=['POST', 'OPTIONS'])
    def google_login():
        """
        Login or register with Google OAuth token
        
        Request JSON:
        {
            "token": "google_id_token_from_frontend",
            "name": "User Name" (optional, from Google)
        }
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            data = request.get_json()
            
            if not data or not data.get('token'):
                return jsonify({
                    "status": "error",
                    "message": "Google token is required"
                }), 400
            
            google_token = data.get('token')
            google_name = data.get('name', 'User')
            
            # Verify Google token
            # Note: Replace with your actual Google Client ID
            GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-client-id')
            
            try:
                payload = id_token.verify_oauth2_token(
                    google_token,
                    google_requests.Request(),
                    GOOGLE_CLIENT_ID
                )
                google_email = payload['email']
                google_id = payload['sub']  # Google's unique user ID
                
            except ValueError as e:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid Google token: {str(e)}"
                }), 401
            
            # Find or create user by Google ID
            users_collection = mongo.db['users']
            user = users_collection.find_one({'google_id': google_id})
            
            if not user:
                # Create new user from Google account
                new_user = {
                    'google_id': google_id,
                    'email': google_email,
                    'name': google_name,
                    'auth_method': 'google',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now(),
                }
                
                result = users_collection.insert_one(new_user)
                user_id = str(result.inserted_id)
                
            else:
                # Update existing user
                user_id = str(user['_id'])
                users_collection.update_one(
                    {'_id': user['_id']},
                    {
                        '$set': {
                            'last_login': datetime.now(),
                            'email': google_email,
                            'name': google_name,
                        }
                    }
                )
            
            # Create access token
            token_data = create_access_token(user_id, google_email)
            
            return jsonify({
                "status": "success",
                "message": "Google login successful",
                "access_token": token_data['access_token'],
                "token_type": token_data['token_type'],
                "expires_in": token_data['expires_in'],
                "user": {
                    "id": user_id,
                    "email": google_email,
                    "name": google_name,
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Google login error: {str(e)}"
            }), 500
    
    
    @auth_blueprint.route('/verify-token', methods=['POST', 'OPTIONS'])
    def verify_token():
        """
        Verify if a token is still valid
        
        Request JSON:
        {
            "token": "jwt_token"
        }
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            data = request.get_json()
            token = data.get('token') if data else None
            
            if not token:
                return jsonify({"status": "error", "message": "Token is required"}), 400
            
            payload = verify_access_token(token)
            
            return jsonify({
                "status": "success",
                "message": "Token is valid",
                "user_id": payload.get('user_id'),
                "email": payload.get('email'),
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 401
    
    
    return auth_blueprint
