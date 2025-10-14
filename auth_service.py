"""
Supabase Authentication Service
Handles user authentication with email/password, magic links, and OAuth
"""
from supabase import create_client, Client
from fastapi import HTTPException, Depends, Header
from typing import Optional
import os
from dotenv import load_dotenv
import jwt

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

if not all([supabase_url, supabase_key]):
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")

# Client for user operations (uses anon key)
supabase: Client = create_client(supabase_url, supabase_key)

# Admin client for privileged operations (uses service role key)
supabase_admin: Client = create_client(supabase_url, supabase_service_key) if supabase_service_key else None


class AuthService:
    """Service for handling Supabase authentication"""
    
    @staticmethod
    async def sign_up_with_email(email: str, password: str, metadata: dict = None):
        """Sign up a new user with email and password"""
        try:
            # Sign up the user
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "created_at": response.user.created_at,
                        "user_metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token if response.session else None,
                        "refresh_token": response.session.refresh_token if response.session else None,
                        "expires_in": response.session.expires_in if response.session else None
                    } if response.session else None,
                    "message": "Sign up successful! Please check your email to verify your account."
                }
            else:
                raise HTTPException(status_code=400, detail="Sign up failed")
                
        except Exception as e:
            error_message = str(e)
            if "already registered" in error_message.lower():
                raise HTTPException(status_code=400, detail="Email already registered")
            raise HTTPException(status_code=400, detail=f"Sign up failed: {error_message}")
    
    @staticmethod
    async def sign_in_with_email(email: str, password: str):
        """Sign in a user with email and password"""
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email,
                        "email_confirmed_at": response.user.email_confirmed_at,
                        "user_metadata": response.user.user_metadata
                    },
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_in": response.session.expires_in,
                        "token_type": response.session.token_type
                    },
                    "message": "Sign in successful!"
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except Exception as e:
            error_message = str(e)
            if "invalid" in error_message.lower() or "credentials" in error_message.lower():
                raise HTTPException(status_code=401, detail="Invalid email or password")
            raise HTTPException(status_code=400, detail=f"Sign in failed: {error_message}")
    
    @staticmethod
    async def sign_in_with_magic_link(email: str):
        """Send a magic link to the user's email"""
        try:
            response = supabase.auth.sign_in_with_otp({
                "email": email,
                "options": {
                    "email_redirect_to": "http://localhost:8000/auth/callback"
                }
            })
            
            return {
                "message": "Magic link sent! Please check your email.",
                "email": email
            }
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to send magic link: {str(e)}")
    
    @staticmethod
    async def sign_in_with_google(redirect_url: str = "http://localhost:8000/auth/callback"):
        """Get Google OAuth URL"""
        try:
            response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_url
                }
            })
            
            return {
                "url": response.url,
                "provider": "google"
            }
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to initiate Google sign in: {str(e)}")
    
    @staticmethod
    async def sign_out(access_token: str):
        """Sign out the current user"""
        try:
            # Set the session
            supabase.auth.set_session(access_token, access_token)
            
            # Sign out
            supabase.auth.sign_out()
            
            return {"message": "Sign out successful!"}
                
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Sign out failed: {str(e)}")
    
    @staticmethod
    async def refresh_session(refresh_token: str):
        """Refresh the user's session"""
        try:
            response = supabase.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "session": {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "expires_in": response.session.expires_in
                    },
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email
                    } if response.user else None
                }
            else:
                raise HTTPException(status_code=401, detail="Failed to refresh session")
                
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Session refresh failed: {str(e)}")
    
    @staticmethod
    async def get_current_user(access_token: str):
        """Get the current authenticated user"""
        try:
            # Set the session
            supabase.auth.set_session(access_token, access_token)
            
            # Get user
            response = supabase.auth.get_user(access_token)
            
            if response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "email_confirmed_at": response.user.email_confirmed_at,
                    "user_metadata": response.user.user_metadata,
                    "created_at": response.user.created_at
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
                
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    
    @staticmethod
    async def verify_token(access_token: str) -> dict:
        """Verify JWT token and return user data"""
        try:
            if not jwt_secret:
                raise HTTPException(status_code=500, detail="JWT secret not configured")
            
            # Decode JWT
            payload = jwt.decode(access_token, jwt_secret, algorithms=["HS256"])
            
            return payload
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


# Dependency for protected routes
async def get_current_user_dependency(authorization: Optional[str] = Header(None)):
    """Dependency to get current authenticated user from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    return await AuthService.get_current_user(token)


auth_service = AuthService()
