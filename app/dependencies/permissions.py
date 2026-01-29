from fastapi import Depends, HTTPException, status
from typing import Dict, Any

from app.dependencies.auth import get_current_user


def require_role(role: str):
    
    async def role_checker(
        user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        
        user_role = user.get("user_metadata", {}).get("role")
        
        if user_role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. {role.capitalize()} role required"
            )
        
        return user
    
    return role_checker


# Pre-built role dependencies
require_organizer = require_role("organizer")
require_admin = require_role("admin")


async def require_organizer_or_admin(
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    
    user_role = user.get("user_metadata", {}).get("role")
    
    if user_role not in ["organizer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Organizer or admin role required"
        )
    
    return user