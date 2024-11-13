from dotenv import load_dotenv
import os
from app.db.session import engine, SessionLocal
from sqlalchemy import text

# Явно загружаем .env файл
load_dotenv()

# Печатаем переменные окружения для отладки
print("Environment variables:")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"SECRET_KEY exists: {'Yes' if os.getenv('SECRET_KEY') else 'No'}")

# Тестируем подключение
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print(f"Database connection test result: {result.scalar()}")

# Тестируем создание сессии
db = SessionLocal()
try:
    result = db.execute(text("SELECT current_timestamp"))
    print(f"Current database timestamp: {result.scalar()}")
finally:
    db.close()
