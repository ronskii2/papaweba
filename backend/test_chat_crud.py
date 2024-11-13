from dotenv import load_dotenv
from app.db.session import SessionLocal
from app.crud.users import user
from app.crud.chats import chat
from uuid import uuid4
import uuid

# Загружаем переменные окружения
load_dotenv()

def test_chat_operations():
    db = SessionLocal()
    try:
        # 1. Создаем тестового пользователя
        test_user = user.create(
            db,
            email=f"test_{uuid.uuid4().hex[:8]}@example.com",
            username=f"testuser_{uuid.uuid4().hex[:8]}",
            password="testpassword123",
            full_name="Test User"
        )
        print(f"Created test user: {test_user.username}")

        # 2. Создаем папку для чатов
        folder = chat.create_folder(
            db,
            user_id=test_user.id,
            name="Test Folder",
            emoji="📁"
        )
        print(f"Created folder: {folder.name}")

        # 3. Создаем чат
        test_chat = chat.create_chat(
            db,
            user_id=test_user.id,
            folder_id=folder.id,
            title="Test Chat"
        )
        print(f"Created chat: {test_chat.title}")

        # 4. Добавляем сообщения
        message1 = chat.create_message(
            db,
            chat_id=test_chat.id,
            role="user",
            content="Hello, AI!",
            tokens_used=10
        )
        message2 = chat.create_message(
            db,
            chat_id=test_chat.id,
            role="assistant",
            content="Hello! How can I help you today?",
            tokens_used=15
        )
        print(f"Added {2} messages to chat")

        # 5. Получаем чаты пользователя
        user_chats = chat.get_user_chats(db, test_user.id)
        print(f"User has {len(user_chats)} chats")

        # 6. Получаем сообщения чата
        chat_messages = chat.get_chat_messages(db, test_chat.id)
        print(f"Chat has {len(chat_messages)} messages")

        # 7. Обновляем название чата
        updated_chat = chat.update_chat_title(
            db,
            chat_id=test_chat.id,
            title="Updated Test Chat"
        )
        print(f"Updated chat title: {updated_chat.title}")

        # Можно раскомментировать для тестирования удаления
        # # 8. Удаляем чат
        # chat.delete_chat(db, test_chat.id)
        # print("Chat deleted")
        
        # # 9. Удаляем папку
        # chat.delete_folder(db, folder.id)
        # print("Folder deleted")

    finally:
        db.close()

if __name__ == "__main__":
    print("Starting chat CRUD operations test...")
    test_chat_operations()
    print("Chat CRUD operations test completed!")

