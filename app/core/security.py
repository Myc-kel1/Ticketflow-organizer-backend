"""import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
#from passlib.context import CryptContext

from app.core.config import settings

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
# Create a JWT access token.
    
"""  Args:
        data: Data to encode in the token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token""""""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SUPABASE_JWT_SECRET,
        algorithm="HS256"
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
"""   Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        jwt.InvalidTokenError: If token is invalid
    """
 #   return jwt.decode(
  #      token,
   #     settings.SUPABASE_JWT_SECRET,
    #    algorithms=["HS256"],
     #   audience="authenticated"""
