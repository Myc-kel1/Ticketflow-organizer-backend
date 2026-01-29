from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Any

from app.core.config import settings
from app.core.supabase import supabase


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    
    token = credentials.credentials
    
    try:
        # Verify JWT token
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        # Extract user info
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from Supabase
        try:
            user = supabase.auth.get_user(token)
            if not user or not user.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            return {
                "user_id": user.user.id,
                "email": user.user.email,
                "user_metadata": user.user.user_metadata or {},
                "token": token
            }
        except Exception:
            # Fallback to payload if Supabase call fails
            return {
                "user_id": user_id,
                "email": payload.get("email"),
                "user_metadata": payload.get("user_metadata", {}),
                "token": token
            }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )