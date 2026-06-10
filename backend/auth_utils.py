"""
Authentication Utilities
Handles JWT token creation/verification and password hashing
"""
import os
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT secret key (use environment variable or fallback)
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, email: str = None, role: str = "user") -> dict:
    """
    Create a JWT access token
    
    Args:
        user_id: The user's MongoDB ObjectId as string
        email: Optional user email
        role: User role ('user' or 'admin')
    
    Returns:
        Dictionary with token and expiration info
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRATION_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_DAYS * 24 * 3600,  # seconds
    }


def verify_access_token(token: str) -> dict:
    """
    Verify and decode a JWT access token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload with user_id and email
    
    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")


def extract_user_id_from_token(token: str) -> str:
    """
    Extract user_id from a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        The user_id from the token
    
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
    payload = verify_access_token(token)
    return payload.get("user_id")
