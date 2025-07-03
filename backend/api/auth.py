"""
auth.py

Authentication and authorization module for the ShipIt API.
Provides JWT token validation and user context.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
import os
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class User:
    """User model for authentication context."""
    def __init__(self, user_id: str, email: str):
        self.user_id = user_id
        self.email = email


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Could not validate credentials")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        User object with authentication context
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        # In a real implementation, you might fetch user details from database
        user = User(user_id=user_id, email=email)
        return user
        
    except JWTError:
        raise credentials_exception


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for optional authentication endpoints.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# Placeholder functions for demo/testing purposes
def create_demo_token(user_id: str = "demo-user", email: str = "demo@shipit.com") -> str:
    """
    Create a demo token for testing purposes.
    
    Args:
        user_id: User ID for the demo token
        email: Email for the demo token
        
    Returns:
        Demo JWT token
    """
    data = {"sub": user_id, "email": email}
    return create_access_token(data, expires_delta=timedelta(hours=24))


# For development/testing - this would be removed in production
DEMO_TOKEN = create_demo_token() 