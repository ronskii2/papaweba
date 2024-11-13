from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.crud.users import user
from sqlalchemy import text
import uuid

# Загружаем переменные окружения
load_dotenv()

def test_user_operations():
    db = SessionLocal()
    try:
        # 1. Создаем тестового пользователя
        test_user = user.create(
            db,
            email="test@example.com",
            username=f"testuser_{uuid.uuid4().hex[:8]}", # уникальное имя
            password="testpassword123",
            full_name="Test User"
        )
        print(f"Created user: {test_user.username}")
        
        # 2. Получаем пользователя по email
        found_user = user.get_by_email(db, email="test@example.com")
        print(f"Found user by email: {found_user.username}")
        
        # 3. Обновляем данные пользователя
        updated_user = user.update(
            db,
            db_obj=found_user,
            full_name="Updated Test User",
            about_me="This is a test user"
        )
        print(f"Updated user name: {updated_user.full_name}")
        
        # 4. Получаем список пользователей
        users = user.get_multi(db, skip=0, limit=10)
        print(f"Total users found: {len(users)}")
        
        # 5. Тестируем поиск по несуществующему email
        non_existent = user.get_by_email(db, email="nonexistent@example.com")
        print(f"Non-existent user found: {'Yes' if non_existent else 'No'}")
        
        # Можем также удалить тестового пользователя
        # if found_user:
        #     user.delete(db, user_id=str(found_user.id))
        #     print("Test user deleted")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting CRUD operations test...")
    test_user_operations()
    print("CRUD operations test completed!")
