"""
Migration script to add photo_url column to pets table
Run this once: python add_photo_url_column.py
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

# Add the column
try:
    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='pets' AND column_name='photo_url'
        """))
        
        if result.fetchone():
            print("✅ Column 'photo_url' already exists!")
        else:
            # Add the column
            conn.execute(text("""
                ALTER TABLE pets 
                ADD COLUMN photo_url VARCHAR(500)
            """))
            conn.commit()
            print("✅ Successfully added 'photo_url' column to pets table!")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nAlternatively, run this SQL command directly in PostgreSQL:")
    print("ALTER TABLE pets ADD COLUMN photo_url VARCHAR(500);")
