import unittest
import os
import sqlite3
from src.db import initialize_db, store_md5sum_in_db, is_duplicate, get_files_by_md5sum, DB_PATH  # Add get_files_by_md5sum here
from src.md5sum import compute_md5sum

class TestDatabaseInitialization(unittest.TestCase):

    def setUp(self):
        # Remove the database file if it exists before each test
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    def test_initialize_db_creates_file(self):
        initialize_db()
        self.assertTrue(os.path.exists(DB_PATH))

    def test_initialize_db_creates_table(self):
        initialize_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='files'")
        table = cursor.fetchone()
        self.assertIsNotNone(table)

        # Check if the columns 'path' and 'md5sum' exist in the 'files' table
        cursor.execute("PRAGMA table_info(files)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        self.assertIn('path', column_names)
        self.assertIn('md5sum', column_names)
        conn.close()

class TestStoreMd5sumInDb(unittest.TestCase):

    def setUp(self):
        # Remove the database file if it exists before each test
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        # Initialize the database
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

    def test_store_md5sum_in_db(self):
        test_file_path = "test_file.txt"
        test_md5sum = "dummy_md5sum"
        store_md5sum_in_db(test_file_path, test_md5sum)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE path = ?", (test_file_path,))
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[1], test_file_path)
        self.assertEqual(result[2], test_md5sum)

class TestGetFilesByMd5sum(unittest.TestCase):

    def setUp(self):
        # Remove the database file if it exists before each test
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        # Initialize the database
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

    def test_get_files_by_md5sum(self):
        test_file_path_1 = "test_file_1.txt"
        test_file_path_2 = "test_file_2.txt"
        test_md5sum = "dummy_md5sum"
        store_md5sum_in_db(test_file_path_1, test_md5sum)
        store_md5sum_in_db(test_file_path_2, test_md5sum)

        result = get_files_by_md5sum(test_md5sum)

        self.assertEqual(len(result), 2)
        self.assertIn(test_file_path_1, result)
        self.assertIn(test_file_path_2, result)

class TestDuplicateCheck(unittest.TestCase):
    def setUp(self):
        # Ensure a clean state by removing the database file if it exists
        self.db_path = DB_PATH  # Use DB_PATH here
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        initialize_db()

        # Create a temporary test file
        self.test_file_path = 'test_file.txt'
        with open(self.test_file_path, 'w') as f:
            f.write('This is a test file.')

        # Compute its md5sum and store it in the database
        self.md5sum = compute_md5sum(self.test_file_path)
        store_md5sum_in_db(self.test_file_path, self.md5sum)

    def tearDown(self):
        # Clean up test file and database
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_is_duplicate(self):
        # Test that the file is identified as a duplicate
        self.assertTrue(is_duplicate(self.md5sum))  # Use self.md5sum here

        # Modify the file and test that it is not identified as a duplicate
        with open(self.test_file_path, 'w') as f:
            f.write('This is a modified test file.')
        new_md5sum = compute_md5sum(self.test_file_path)
        self.assertFalse(is_duplicate(new_md5sum))  # Use new_md5sum here

if __name__ == "__main__":
    unittest.main()