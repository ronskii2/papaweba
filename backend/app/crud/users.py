from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.core.security import verify_password, get_password_hash

class CRUDUser:
    @staticmethod
    def get(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, *, email: str, username: str, password: str, full_name: Optional[str] = None) -> Optional[User]:
        try:
            db_obj = User(
                email=email,
                username=username,
                password_hash=get_password_hash(password),
                full_name=full_name
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            return None

    @staticmethod
    def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
        user = CRUDUser.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update(db: Session, *, db_obj: User, full_name: Optional[str] = None, 
               avatar_url: Optional[str] = None, about_me: Optional[str] = None) -> User:
        if full_name is not None:
            db_obj.full_name = full_name
        if avatar_url is not None:
            db_obj.avatar_url = avatar_url
        if about_me is not None:
            db_obj.about_me = about_me
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, *, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True

user = CRUDUser()
