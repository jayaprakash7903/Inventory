import os
import sqlite3

def create_connection():
    return sqlite3.connect("packing.db")

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    # Use "IF NOT EXISTS" so existing tables and data are unchanged.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packing_slip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_id TEXT,
            customer_name TEXT,
            location TEXT,
            time_of_packing TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_id TEXT,
            item_id TEXT,
            description TEXT,
            quantity INTEGER,
            image BLOB
        )
    """)
    conn.commit()
    conn.close()

def save_packing_slip(header_info, items):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO packing_slip (header_id, customer_name, location, time_of_packing)
        VALUES (?, ?, ?, ?)
    """, (
        header_info["header_id"],
        header_info["customer_name"],
        header_info["location"],
        header_info["time_of_packing"]
    ))
    for item in items:
        cursor.execute("""
            INSERT INTO packing_items (header_id, item_id, description, quantity, image)
            VALUES (?, ?, ?, ?, ?)
        """, (
            header_info["header_id"],
            item["item_id"],
            item["description"],
            item["quantity"],
            item["image"]
        ))
    conn.commit()
    conn.close()

# Call create_tables() on startup so that missing tables are added,
# but do not delete the database file.
create_tables()
