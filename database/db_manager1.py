import sqlite3
import os
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "packing1.db")

def create_connection():
    """Create thread-safe database connection"""
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_tables():
    """Initialize database schema"""
    conn = create_connection()
    cursor = conn.cursor()
    
    # Packing slip header table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS packing_slip (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        header_id TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        location TEXT,
        time_of_packing TEXT NOT NULL
    )""")
    
    # Packing items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS packing_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        header_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        description TEXT,
        quantity INTEGER DEFAULT 1,
        image BLOB,
        FOREIGN KEY (header_id) REFERENCES packing_slip (header_id),
        UNIQUE (header_id, item_id)
    )""")
    
    conn.commit()
    conn.close()

def save_packing_slip(header_info: Dict, items: List[Dict]):
    """Save complete packing slip with transaction handling"""
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        # Insert/update header
        cursor.execute("""
        INSERT OR REPLACE INTO packing_slip
        (header_id, customer_name, location, time_of_packing)
        VALUES (?, ?, ?, ?)
        """, (
            header_info["header_id"],
            header_info["customer_name"],
            header_info.get("location"),
            header_info["time_of_packing"]
        ))
        
        # Insert/update items
        for item in items:
            cursor.execute("""
            INSERT OR REPLACE INTO packing_items
            (header_id, item_id, description, quantity, image)
            VALUES (?, ?, ?, ?, ?)
            """, (
                header_info["header_id"],
                item["item_id"],
                item.get("description", ""),
                item.get("quantity", 1),
                item.get("image")
            ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Initialize tables on module import
create_tables()