from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.models.user_images import UserImage
from uuid import UUID
from datetime import datetime

class CRUDImage:
    @staticmethod
    def create(
        db: Session,
        *,
        user_id: UUID,
        prompt: str,
        translated_prompt: str,
        image_url: str,
        aspect_ratio: str = "1:1",
        style: Optional[str] = None
    ) -> UserImage:
        db_obj = UserImage(
            user_id=user_id,
            prompt=prompt,
            translated_prompt=translated_prompt,
            image_url=image_url,
            aspect_ratio=aspect_ratio,
            style=style
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_user_images(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[UserImage]:
        return db.query(UserImage).filter(
            UserImage.user_id == user_id
        ).order_by(UserImage.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_images_filtered(
        db: Session,
        *,
        user_id: UUID,
        style: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[UserImage]:
        query = db.query(UserImage).filter(UserImage.user_id == user_id)
        
        if style:
            query = query.filter(UserImage.style == style)
        
        if start_date:
            query = query.filter(UserImage.created_at >= start_date)
        
        if end_date:
            query = query.filter(UserImage.created_at <= end_date)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    UserImage.prompt.ilike(search_term),
                    UserImage.translated_prompt.ilike(search_term)
                )
            )
        
        return query.order_by(UserImage.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_user_images_filtered(
        db: Session,
        *,
        user_id: UUID,
        style: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> int:
        query = db.query(UserImage).filter(UserImage.user_id == user_id)
        
        if style:
            query = query.filter(UserImage.style == style)
        
        if start_date:
            query = query.filter(UserImage.created_at >= start_date)
        
        if end_date:
            query = query.filter(UserImage.created_at <= end_date)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    UserImage.prompt.ilike(search_term),
                    UserImage.translated_prompt.ilike(search_term)
                )
            )
        
        return query.count()

    @staticmethod
    def get_image(db: Session, image_id: UUID) -> Optional[UserImage]:
        return db.query(UserImage).filter(UserImage.id == image_id).first()

    @staticmethod
    def delete_image(db: Session, image_id: UUID, user_id: UUID) -> bool:
        image = db.query(UserImage).filter(
            UserImage.id == image_id,
            UserImage.user_id == user_id
        ).first()
        if image:
            db.delete(image)
            db.commit()
            return True
        return False

image = CRUDImage()
