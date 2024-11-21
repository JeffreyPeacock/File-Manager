# src/db.py
import logging
import os
import re
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils import get_file_mtime_in_ms

MAX_RETRIES = 10  # Define a global variable for the number of retries
RETRY_DELAY = 0.1  # Delay between retries in seconds


def initialize_db(db_path):
    """
    Initialize the database by creating the necessary tables if they do not exist.

    Args:
        db_path (str): The path to the database file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            md5sum TEXT,
            size INTEGER,
            last_modified INTEGER,
            path TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def get_file_info(db_path, file_path):
    """
    Retrieve the size and last modified time of a file from the database.

    Args:
        db_path (str): The path to the database file.
        file_path (str): The path to the file.

    Returns:
        tuple: A tuple containing the size and last modified time of the file, or None if the file is not found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT size, last_modified FROM files WHERE path = ?
    ''', (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_files_info(db_path):
    """
    Retrieve all file information from the database.

    Args:
        db_path (str): The path to the database file.

    Returns:
        list: A list of tuples, each containing the file path, size, and last modified time.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT path, size, last_modified FROM files")
    files_info = cursor.fetchall()
    conn.close()
    return files_info

def store_file_info(db_path, path, md5sum):
    """
    Store or update the information of a file in the database.

    Args:
        db_path (str): The path to the database file.
        path (str): The path to the file.
        md5sum (str): The MD5 checksum of the file.
    """
    size = os.path.getsize(path)
    last_modified = get_file_mtime_in_ms(path)  # Use the utility function
    retries = MAX_RETRIES
    while retries > 0:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO files (path, md5sum, size, last_modified) VALUES (?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET md5sum=excluded.md5sum, size=excluded.size, last_modified=excluded.last_modified
            ''', (path, md5sum, size, last_modified))
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries -= 1
                time.sleep(0.1)  # Wait for 100ms before retrying
            else:
                raise
        finally:
            if conn:
                conn.close()
    if retries == 0:
        raise Exception(f"Failed to store file info for {path} after {MAX_RETRIES} retries due to database lock")

def remove_file_info(db_path, file_path):
    """
    Remove the information of a file from the database.

    Args:
        db_path (str): The path to the database file.
        file_path (str): The path to the file.
    """
    retries = MAX_RETRIES
    while retries > 0:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE path = ?", (file_path,))
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries -= 1
                time.sleep(0.1)  # Wait for 100ms before retrying
            else:
                raise
        finally:
            if conn:
                conn.close()
    if retries == 0:
        raise Exception(f"Failed to remove file info for {file_path} after {MAX_RETRIES} retries due to database lock")

def remove_files_by_regex(db_path, regex_pattern):
    """
    Remove records associated with files matching the regex pattern from the database.

    Args:
        db_path (str): The path to the database file.
        regex_pattern (str): The regex pattern to match file paths.
    """
    retries = MAX_RETRIES
    while retries > 0:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM files")
            all_paths = cursor.fetchall()
            matching_paths = [path[0] for path in all_paths if re.match(regex_pattern, path[0])]
            if matching_paths:
                cursor.executemany("DELETE FROM files WHERE path = ?", [(path,) for path in matching_paths])
                conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries -= 1
                time.sleep(0.1)  # Wait for 100ms before retrying
            else:
                raise
        finally:
            if conn:
                conn.close()
    if retries == 0:
        raise Exception(f"Failed to remove file info matching pattern '{regex_pattern}' after {MAX_RETRIES} retries due to database lock")

def get_md5_by_path(db_path, file_path):
    """
    Retrieve the MD5 checksum of a file from the database.

    Args:
        db_path (str): The path to the database file.
        file_path (str): The path to the file.

    Returns:
        str: The MD5 checksum of the file, or None if the file is not found.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT md5sum FROM files WHERE path = ?
    ''', (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def check_for_duplicates(db_path, md5sum):
    """
    Check for duplicate files in the database based on the MD5 checksum.

    Args:
        db_path (str): The path to the database file.
        md5sum (str): The MD5 checksum to check for duplicates.

    Returns:
        list: A list of file paths that have the same MD5 checksum.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT path FROM files WHERE md5sum = ?
    ''', (md5sum,))
    duplicates = cursor.fetchall()
    conn.close()
    return duplicates

def find_duplicates_with_min_count(db_path, min_count=1):
    """
    Find duplicate files in the database with a minimum count of occurrences.

    Args:
        db_path (str): The path to the database file.
        min_count (int): The minimum number of duplicate occurrences to search for.

    Returns:
        dict: A dictionary where the keys are MD5 checksums and the values are lists of file paths that have the same MD5 checksum.
    """
    def fetch_in_chunks(cursor, chunk_size=1000):
        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break
            for row in rows:
                yield row

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT md5sum, GROUP_CONCAT(path) FROM files
        GROUP BY md5sum HAVING COUNT(*) > ?
    ''', (min_count,))

    duplicates = {}
    for row in fetch_in_chunks(cursor):
        md5sum, paths = row
        duplicates[md5sum] = paths.split(',')

    conn.close()
    return duplicates


def audit_db(db_path, num_threads, process_file):
    """
    Audit the database for file changes and reprocess files if necessary.

    Args:
        db_path (str): The path to the database file.
        num_threads (int): The number of threads to use for concurrent operations.
        process_file (function): The function to process a file.
    """
    batch_size = 100  # Adjust the batch size as needed
    processed_files_count = 0  # Initialize the counter

    def process_file_info(file_info):
        nonlocal processed_files_count
        file_path, db_size, db_last_modified = file_info
        if not os.path.exists(file_path):
            logging.info(f"REMOVED: {file_path} (File no longer exists)")
            remove_file_info(db_path, file_path)
        else:
            size = os.path.getsize(file_path)
            last_modified = get_file_mtime_in_ms(file_path)
            if size != db_size or last_modified != db_last_modified:
                logging.info(f"REPROCESSING: {file_path} (Size or last modified time changed)")
                process_file(file_path, db_path)
        processed_files_count += 1  # Increment the counter

    retries = MAX_RETRIES
    while retries > 0:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode
            cursor.execute("SELECT path, size, last_modified FROM files")

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                while True:
                    batch = cursor.fetchmany(batch_size)
                    if not batch:
                        break
                    futures = [executor.submit(process_file_info, file_info) for file_info in batch]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logging.error(f"Error processing file info: {e}")

            conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries -= 1
                logging.warning(f"Database is locked, retrying... ({MAX_RETRIES - retries}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                raise
        finally:
            if conn:
                conn.close()
    if retries == 0:
        raise Exception(f"Failed to audit database after {MAX_RETRIES} retries due to database lock")

    logging.info(f"Total files processed: {processed_files_count}")  # Report the total count

