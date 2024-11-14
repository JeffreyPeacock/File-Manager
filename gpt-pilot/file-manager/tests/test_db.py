# tests/test_db.py

import unittest
import os
import sqlite3
from src.db import initialize_db, DB_PATH

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

if __name__ == '__main__':
    unittest.main()