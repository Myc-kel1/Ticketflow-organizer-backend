from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any

from app.core.supabase import supabase
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
   
    email: EmailStr
    password: str = Field(..., min_length=6)


class SignUpRequest(BaseModel):
   
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)


class AuthResponse(BaseModel):
    
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
    user: Dict[str, Any]


@router.post("/organizer/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def organizer_signup(user_data: SignUpRequest):
    
    try:
        # Supabase automatically hashes password and creates user
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name,
                    "role": "organizer" 
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create organizer account"
            )
        
        # Check if email confirmation is required
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="Organizer account created. Please check your email to confirm your account."
            )
        
        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": user_data.full_name,
                "role": "organizer",
                "user_metadata": response.user.user_metadata
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/organizer/login", response_model=AuthResponse)
async def organizer_login(credentials: LoginRequest):
  
    try:
        # Supabase automatically verifies password hash
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not response.user or not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify user has organizer role
        user_role = response.user.user_metadata.get("role")
        if user_role != "organizer":
            # Sign out if not an organizer
            supabase.auth.sign_out()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Organizer account required."
            )
        
        return AuthResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "role": user_role,
                "user_metadata": response.user.user_metadata
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed. Please check your credentials."
        )


@router.post("/organizer/logout")
async def organizer_logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    
    try:
        # Supabase invalidates the session
        supabase.auth.sign_out()
        return {
            "message": "Organizer logged out successfully",
            "user_id": current_user["user_id"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/organizer/me")
async def get_organizer_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "role": current_user.get("user_metadata", {}).get("role", "organizer"),
        "full_name": current_user.get("user_metadata", {}).get("full_name"),
        "user_metadata": current_user["user_metadata"]
    }


"""@router.post("/organizer/refresh")
async def refresh_organizer_token(refresh_token: str = Field(..., description="Refresh token")):
    """
#    Refresh access token using refresh token.
#    Supabase handles token refresh automatically.
    
#    Args:
#        refresh_token: Valid refresh token
        
#   Returns:
#       New access token and refresh token
"""
    try:
        # Supabase handles token refresh
        response = supabase.auth.refresh_session(refresh_token)
        
        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )"""