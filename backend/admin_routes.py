"""
Admin Routes
Handles admin-only user management endpoints
"""
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from auth_utils import hash_password, create_access_token
from auth_middleware import require_admin

# Create blueprint
admin_blueprint = Blueprint('admin', __name__, url_prefix='/api/admin')


def init_admin_routes(mongo):
    """
    Initialize admin routes with MongoDB connection
    
    Args:
        mongo: MongoDBManager instance
    """
    
    @admin_blueprint.route('/users', methods=['GET', 'OPTIONS'])
    @require_admin
    def list_users():
        """
        List all users with pagination and search
        
        Query params:
            skip: int (default 0)
            limit: int (default 20)
            search: str (optional, search by username/email/name)
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            users_collection = mongo.db['users']
            
            skip = request.args.get('skip', default=0, type=int)
            limit = request.args.get('limit', default=20, type=int)
            search = request.args.get('search', default='', type=str).strip()
            
            # Build query filter
            query = {}
            if search:
                query = {
                    '$or': [
                        {'username': {'$regex': search, '$options': 'i'}},
                        {'email': {'$regex': search, '$options': 'i'}},
                        {'name': {'$regex': search, '$options': 'i'}},
                    ]
                }
            
            # Get total count
            total = users_collection.count_documents(query)
            
            # Get paginated users
            cursor = users_collection.find(query).sort('created_at', -1).skip(skip).limit(limit)
            
            users = []
            for user in cursor:
                users.append({
                    'id': str(user['_id']),
                    'username': user.get('username', ''),
                    'email': user.get('email', ''),
                    'name': user.get('name', ''),
                    'role': user.get('role', 'user'),  # Backward compat
                    'auth_method': user.get('auth_method', 'unknown'),
                    'created_at': user.get('created_at', '').isoformat() if isinstance(user.get('created_at'), datetime) else str(user.get('created_at', '')),
                    'last_login': user.get('last_login', '').isoformat() if isinstance(user.get('last_login'), datetime) else str(user.get('last_login', '')),
                })
            
            return jsonify({
                "status": "success",
                "data": {
                    "users": users,
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to list users: {str(e)}"
            }), 500
    
    
    @admin_blueprint.route('/users', methods=['POST', 'OPTIONS'])
    @require_admin
    def create_user():
        """
        Create a new user (admin creates with username/password)
        
        Request JSON:
        {
            "username": "newuser",
            "password": "password123",
            "name": "New User" (optional),
            "role": "user" (optional, default "user")
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
            role = data.get('role', 'user').strip()
            
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
            
            if role not in ('user', 'admin'):
                return jsonify({
                    "status": "error",
                    "message": "Role must be 'user' or 'admin'"
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
                'role': role,
                'auth_method': 'password',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
            }
            
            result = users_collection.insert_one(new_user)
            user_id = str(result.inserted_id)
            
            return jsonify({
                "status": "success",
                "message": "User created successfully",
                "user": {
                    "id": user_id,
                    "username": username,
                    "name": name,
                    "role": role,
                    "auth_method": "password",
                }
            }), 201
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to create user: {str(e)}"
            }), 500
    
    
    @admin_blueprint.route('/users/<user_id>', methods=['DELETE', 'OPTIONS'])
    @require_admin
    def delete_user(user_id):
        """
        Delete a user by ID
        Admin cannot delete themselves
        """
        if request.method == 'OPTIONS':
            return '', 204
        
        try:
            # Prevent admin from deleting themselves
            current_user_id = getattr(request, 'user_id', None)
            if current_user_id == user_id:
                return jsonify({
                    "status": "error",
                    "message": "Cannot delete your own account"
                }), 400
            
            users_collection = mongo.db['users']
            
            # Check if user exists
            try:
                user = users_collection.find_one({'_id': ObjectId(user_id)})
            except Exception:
                return jsonify({"status": "error", "message": "Invalid user ID"}), 400
            
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404
            
            # Delete user
            users_collection.delete_one({'_id': ObjectId(user_id)})
            
            return jsonify({
                "status": "success",
                "message": f"User '{user.get('username', user.get('email', user_id))}' deleted successfully"
            }), 200
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to delete user: {str(e)}"
            }), 500
    
    
    return admin_blueprint
