import logging
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import get_db
from app.crud.users import user
from app.schemas.auth import Token, UserCreate, User

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=User)
async def register_user(
    *,
    db: Session = Depends(get_db),
    user_data: UserCreate
) -> Any:
    """
    Register a new user.
    """
    logger.info(f"Registration attempt for email: {user_data.email}")
    
    # Check if user with this email exists
    if user.get_by_email(db, email=user_data.email):
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
    
    # Check if user with this username exists
    if user.get_by_username(db, username=user_data.username):
        raise HTTPException(
            status_code=400,
            detail="User with this username already exists"
        )
    
    try:
        new_user = user.create(
            db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name
        )
        logger.info(f"User registered successfully: {new_user.email}")
        return new_user
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Check user exists
        user_obj = user.get_by_email(db, email=form_data.username)
        logger.info(f"User found: {user_obj is not None}")
        
        if not user_obj:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password"
            )
            
        # Verify authentication
        authenticated_user = user.authenticate(
            db, email=form_data.username, password=form_data.password
        )
        logger.info(f"Authentication result: {authenticated_user is not None}")
        
        if not authenticated_user:
            logger.warning(f"Authentication failed for user: {form_data.username}")
            raise HTTPException(
                status_code=400,
                detail="Incorrect email or password"
            )
            
        if not authenticated_user.is_active:
            logger.warning(f"Inactive user attempted login: {form_data.username}")
            raise HTTPException(
                status_code=400,
                detail="Inactive user"
            )
            
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            authenticated_user.id, expires_delta=access_token_expires
        )
        logger.info(f"Token created for user: {form_data.username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
        
    except Exception as e:
        logger.error(f"Login error for user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Дополнительные эндпоинты для тестирования...
@router.get("/test", response_model=dict)
async def test_auth():
    """
    Test endpoint to verify router is working.
    """
    return {"message": "Auth router is working"}

@router.post("/make_admin")
async def make_admin(
    *,
    db: Session = Depends(get_db),
    user_id: str
):
    """Временный эндпоинт для тестирования."""
    user_obj = user.get(db, user_id=user_id)
    if user_obj:
        user_obj.is_admin = True
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="User not found")
