# packing_app/database/db_manager.py

import sqlite3

def create_connection():
    conn = sqlite3.connect("packing.db", check_same_thread=False)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Create table for packing slip (header) information without an image column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_slip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_id TEXT,
            customer_name TEXT,
            location TEXT,
            time_of_packing TEXT
        )
    ''')

    # Create table for packing items related to a header with an image column (BLOB)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS packing_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header_id TEXT,
            item_id TEXT,
            description TEXT,
            quantity INTEGER,
            image BLOB
        )
    ''')

    conn.commit()
    conn.close()

def save_packing_slip(header_info, item_list):
    # header_info is a dict with:
    #   header_id, customer_name, location, time_of_packing
    # item_list is a list of dicts with keys:
    #   item_id, description, quantity, image (BLOB or file path)
    conn = create_connection()
    cursor = conn.cursor()

    # Insert header info without image
    cursor.execute('''
        INSERT INTO packing_slip (header_id, customer_name, location, time_of_packing)
        VALUES (?, ?, ?, ?)
    ''', (
        header_info['header_id'],
        header_info['customer_name'],
        header_info['location'],
        header_info['time_of_packing']
    ))
    
    # Loop through each item and insert it (each item may have an image)
    for item in item_list:
        cursor.execute('''
            INSERT INTO packing_items (header_id, item_id, description, quantity, image)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            header_info['header_id'],   # Link item to header
            item['item_id'],
            item['description'],
            item['quantity'],
            item.get('image')  # binary image data or file path, as needed
        ))

    conn.commit()
    conn.close()


