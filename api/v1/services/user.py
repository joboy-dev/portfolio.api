from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from api.utils.loggers import create_logger
from api.v1.models.token import TokenType
from api.v1.models.user import User
from api.v1.schemas.auth import CreateUser
from api.v1.schemas.user import UpdateUser
from api.v1.services.auth import AuthService
from api.v1.services.token import TokenService


logger = create_logger(__name__)

class UserService:
    @classmethod
    def create(cls, db: Session, payload: CreateUser, bg_tasks: BackgroundTasks):
        """Creates a new user"""
        
        payload.email = payload.email.lower().strip()
        user_with_email_exists = User.fetch_one_by_field(db, throw_error=False, email=payload.email)
        if user_with_email_exists:
            raise HTTPException(400, 'User with email already exist')
        
        payload.password = AuthService.hash_secret(payload.password) if payload.password else None
        
        new_user = User.create(
            db=db,
            **payload.model_dump(exclude_unset=True),
        )
        
        access_token = AuthService.create_access_token(db, new_user.id)
        refresh_token = AuthService.create_refresh_token(db, new_user.id)
        
        return new_user, access_token, refresh_token
    
    @classmethod
    def verify_password_change(cls, db: Session, email: str, old_password: str, new_password: str):
        """Fucntion to change user password"""
        
        user, _, _ = AuthService.authenticate(
            db, 
            email=email, 
            password=old_password, 
            create_token=False
        )
        
        if new_password == old_password:
            raise HTTPException(400, 'New and old password cannot be the same')
        
        password_hash = AuthService.hash_secret(new_password)
        
        return password_hash
    
    @classmethod
    def change_email(cls, db: Session, payload: UpdateUser, user_id: str):
        user = User.fetch_one_by_field(db, throw_error=False, email=payload.email)
        if user:
            raise HTTPException(400, 'Email already in use')
        
        user = User.update(db, user_id, email=payload.email)
        return user

    @classmethod
    async def send_account_reactivation_token(cls, db: Session, email: str, bg_tasks: BackgroundTasks):
        """Function to send account reactivation token to user"""
        
        user = User.fetch_one_by_field(db=db, email=email)
        
        # Generate a account reactivation token
        expiry_minutes = 1440  # 24 hours
        account_reactivation_token = TokenService.create_token(
            db=db, 
            token_type=TokenType.ACCOUNT_REACTIVATION.value,
            expiry_in_minutes=expiry_minutes,
            user_id=user.id,
        )
    
        return account_reactivation_token

    @classmethod
    def verify_account_reactivation_token(cls, db: Session, token: str):
        """Function to verify the account reactivation token"""
        
        credentials_exception = HTTPException(
            status_code=401, detail="Invalid token"
        )
        
        user_id = AuthService.verify_token(
            db=db,
            token=token,
            expected_token_type=TokenType.ACCOUNT_REACTIVATION.value,
            credentials_exception=credentials_exception
        )
        
        TokenService.revoke_token(db, token, user_id)
        
        return user_id  
