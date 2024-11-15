import sqlite3
import logging
from .md5sum import compute_md5sum

DB_PATH = 'file_manager.db'

def initialize_db():
    try:
        logging.info("Initializing database")
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
        logging.info(f"Storing md5sum for file {file_path}")
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

def get_files_by_md5sum(md5sum):
    try:
        logging.info(f"Querying database for md5sum {md5sum}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT path FROM files WHERE md5sum = ?
        ''', (md5sum,))
        files = cursor.fetchall()
        conn.close()
        logging.info(f"Queried database for md5sum {md5sum}. Found {len(files)} file(s).")
        return [file[0] for file in files]
    except Exception as e:
        logging.error(f"Error querying database for md5sum {md5sum}: {e}", exc_info=True)
        raise

def is_duplicate(md5sum):
    try:
        logging.info(f"Checking duplicate status for md5sum {md5sum}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM files WHERE md5sum = ?
        ''', (md5sum,))
        count = cursor.fetchone()[0]
        conn.close()
        logging.info(f"Checked duplicate status for md5sum {md5sum}. Duplicate: {count > 0}")
        return count > 0
    except Exception as e:
        logging.error(f"Error checking duplicate status for md5sum {md5sum}: {e}", exc_info=True)
        raise