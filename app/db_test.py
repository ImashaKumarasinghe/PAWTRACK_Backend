from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def test_db_connection():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found. Check your .env file.")
        return

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]

        print("✅ Connected to PostgreSQL successfully!")
        print("PostgreSQL version:", version)

    except Exception as e:
        print("❌ Connection failed!")
        print("Error:", e)

if __name__ == "__main__":
    test_db_connection()
