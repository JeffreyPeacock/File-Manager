import sqlite3
import logging

DB_PATH = 'file_manager.db'

def initialize_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                md5sum TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Error initializing database: {e}", exc_info=True)
        raise

def store_md5sum_in_db(file_path, md5sum):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (path, md5sum)
            VALUES (?, ?)
        ''', (file_path, md5sum))
        conn.commit()
        conn.close()
        logging.info(f"Stored md5sum for {file_path} in the database.")
    except Exception as e:
        logging.error(f"Error storing md5sum in database for {file_path}: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    initialize_db()