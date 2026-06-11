"""
API Key Management Routes
Handles per-user API key CRUD: Discord webhooks, Gemini API key, Image Gen API key
Keys are stored in MongoDB users collection as an 'api_keys' sub-document.
Keys arrive AES-encrypted from frontend and are stored as-is (encrypted).
"""

from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
from auth_middleware import require_auth, get_user_id_from_request
import os
import requests as http_requests

# Create blueprint
apikey_blueprint = Blueprint('apikey', __name__, url_prefix='/api/user')

# Default webhook from environment
DEFAULT_DISCORD_WEBHOOK_URL = os.getenv(
    "DISCORD_WEBHOOK_URL",
    os.getenv("WEBHOOK_URL", "")
)


def _mask_key(key: str, visible_chars: int = 4) -> str:
    """Mask an API key, showing only the last N characters."""
    if not key or len(key) <= visible_chars:
        return key
    return "•" * (len(key) - visible_chars) + key[-visible_chars:]


def _mask_url(url: str) -> str:
    """Mask a webhook URL, showing domain + last 8 chars."""
    if not url:
        return url
    # Show protocol + domain + ...last8
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        return f"{domain}/...{url[-8:]}"
    except Exception:
        return f"...{url[-8:]}" if len(url) > 8 else url


def _try_get_discord_channel_name(webhook_url: str) -> str:
    """
    Try to fetch Discord channel name from a webhook URL.
    Discord GET on webhook URL returns JSON with channel info.
    Returns channel name or empty string if failed.
    """
    if not webhook_url:
        return ""
    try:
        resp = http_requests.get(webhook_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # Discord webhook GET returns: name, channel_id, guild_id, etc.
            return data.get("name", "")
    except Exception:
        pass
    return ""


def init_apikey_routes(mongo):
    """
    Initialize API key routes with MongoDB connection.

    Args:
        mongo: MongoDBManager instance
    """

    @apikey_blueprint.route('/api-keys', methods=['GET', 'OPTIONS'])
    @require_auth
    def get_api_keys():
        """
        Get current user's API keys (masked for display).
        Returns discord_webhooks, gemini_api_key, image_gen_api_key.
        """
        if request.method == 'OPTIONS':
            return '', 204

        try:
            user_id = get_user_id_from_request()
            users_collection = mongo.db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})

            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404

            api_keys = user.get('api_keys', {})

            # Build response with masked keys
            discord_webhooks = api_keys.get('discord_webhooks', [])
            masked_webhooks = []
            for wh in discord_webhooks:
                masked_webhooks.append({
                    'id': wh.get('id', ''),
                    'name': wh.get('name', 'Custom Webhook'),
                    'url_masked': _mask_url(wh.get('url', '')),
                    'url_encrypted': wh.get('url', ''),  # Return encrypted value for FE to decrypt
                    'created_at': wh.get('created_at', ''),
                })

            gemini_key = api_keys.get('gemini_api_key', '')
            image_gen_key = api_keys.get('image_gen_api_key', '')

            return jsonify({
                "status": "success",
                "data": {
                    "discord_webhooks": masked_webhooks,
                    "gemini_api_key_masked": _mask_key(gemini_key) if gemini_key else "",
                    "gemini_api_key_encrypted": gemini_key,  # Return encrypted for FE
                    "has_gemini_key": bool(gemini_key),
                    "image_gen_api_key_masked": _mask_key(image_gen_key) if image_gen_key else "",
                    "image_gen_api_key_encrypted": image_gen_key,
                    "has_image_gen_key": bool(image_gen_key),
                }
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to get API keys: {str(e)}"
            }), 500

    @apikey_blueprint.route('/api-keys', methods=['PUT', 'OPTIONS'])
    @require_auth
    def update_api_keys():
        """
        Update user's API keys.
        Keys arrive AES-encrypted from frontend.

        Request JSON:
        {
            "discord_webhooks": [{"id": "...", "name": "...", "url": "encrypted_url"}],
            "gemini_api_key": "encrypted_key",
            "image_gen_api_key": "encrypted_key"
        }
        All fields are optional — only provided fields are updated.
        """
        if request.method == 'OPTIONS':
            return '', 204

        try:
            user_id = get_user_id_from_request()
            data = request.get_json()

            if not data:
                return jsonify({"status": "error", "message": "Missing request body"}), 400

            users_collection = mongo.db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})

            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404

            # Get existing api_keys or create empty
            api_keys = user.get('api_keys', {})

            # Update discord webhooks
            if 'discord_webhooks' in data:
                webhooks = []
                for wh in data['discord_webhooks']:
                    webhook_entry = {
                        'id': wh.get('id', str(ObjectId())),
                        'name': wh.get('name', 'Custom Webhook'),
                        'url': wh.get('url', ''),  # Stored encrypted
                        'created_at': wh.get('created_at', datetime.now().isoformat()),
                    }
                    webhooks.append(webhook_entry)
                api_keys['discord_webhooks'] = webhooks

            # Update Gemini API key
            if 'gemini_api_key' in data:
                api_keys['gemini_api_key'] = data['gemini_api_key']  # Stored encrypted

            # Update Image Gen API key
            if 'image_gen_api_key' in data:
                api_keys['image_gen_api_key'] = data['image_gen_api_key']  # Stored encrypted

            # Save to MongoDB
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'api_keys': api_keys,
                        'updated_at': datetime.now(),
                    }
                }
            )

            return jsonify({
                "status": "success",
                "message": "API keys updated successfully",
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to update API keys: {str(e)}"
            }), 500

    @apikey_blueprint.route('/api-keys/<key_type>', methods=['DELETE', 'OPTIONS'])
    @require_auth
    def delete_api_key(key_type):
        """
        Delete a specific API key.
        key_type: 'gemini_api_key', 'image_gen_api_key', or 'discord_webhook:<id>'
        """
        if request.method == 'OPTIONS':
            return '', 204

        try:
            user_id = get_user_id_from_request()
            users_collection = mongo.db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})

            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 404

            api_keys = user.get('api_keys', {})

            if key_type == 'gemini_api_key':
                api_keys.pop('gemini_api_key', None)
            elif key_type == 'image_gen_api_key':
                api_keys.pop('image_gen_api_key', None)
            elif key_type.startswith('discord_webhook:'):
                webhook_id = key_type.split(':', 1)[1]
                api_keys['discord_webhooks'] = [
                    wh for wh in api_keys.get('discord_webhooks', [])
                    if wh.get('id') != webhook_id
                ]
            else:
                return jsonify({
                    "status": "error",
                    "message": f"Unknown key type: {key_type}"
                }), 400

            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'api_keys': api_keys,
                        'updated_at': datetime.now(),
                    }
                }
            )

            return jsonify({
                "status": "success",
                "message": f"API key '{key_type}' deleted",
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to delete API key: {str(e)}"
            }), 500

    @apikey_blueprint.route('/api-keys/discord-webhooks', methods=['GET', 'OPTIONS'])
    @require_auth
    def get_discord_webhooks():
        """
        Get all available Discord webhooks for the user.
        Returns: default webhook + user's custom webhooks.
        """
        if request.method == 'OPTIONS':
            return '', 204

        try:
            user_id = get_user_id_from_request()
            users_collection = mongo.db['users']
            user = users_collection.find_one({'_id': ObjectId(user_id)})

            webhooks = []

            # Add default webhook
            default_url = DEFAULT_DISCORD_WEBHOOK_URL
            if default_url:
                webhooks.append({
                    'id': 'default',
                    'name': 'Mặc định (Hệ thống)',
                    'url_masked': _mask_url(default_url),
                    'is_default': True,
                })

            # Add user's custom webhooks
            if user:
                api_keys = user.get('api_keys', {})
                for wh in api_keys.get('discord_webhooks', []):
                    webhooks.append({
                        'id': wh.get('id', ''),
                        'name': wh.get('name', 'Custom Webhook'),
                        'url_masked': _mask_url(wh.get('url', '')),
                        'url_encrypted': wh.get('url', ''),
                        'is_default': False,
                    })

            return jsonify({
                "status": "success",
                "data": {
                    "webhooks": webhooks,
                }
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to get webhooks: {str(e)}"
            }), 500

    @apikey_blueprint.route('/api-keys/discord-webhooks/probe', methods=['POST', 'OPTIONS'])
    @require_auth
    def probe_discord_webhook():
        """
        Probe a Discord webhook URL to get its channel/server name.
        Request JSON: { "url": "https://discord.com/api/webhooks/..." }
        """
        if request.method == 'OPTIONS':
            return '', 204

        try:
            data = request.get_json()
            url = data.get('url', '') if data else ''

            if not url:
                return jsonify({"status": "error", "message": "URL is required"}), 400

            # Try to GET the webhook info from Discord
            channel_name = _try_get_discord_channel_name(url)

            return jsonify({
                "status": "success",
                "data": {
                    "channel_name": channel_name,
                }
            }), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to probe webhook: {str(e)}"
            }), 500

    return apikey_blueprint
