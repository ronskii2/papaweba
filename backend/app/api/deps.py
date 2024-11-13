from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core import auth

get_current_user = auth.get_current_user
get_current_active_user = auth.get_current_active_user
get_current_admin_user = auth.get_current_admin_user
