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
        conn.close()
        self.assertIsNotNone(table)

if __name__ == '__main__':
    unittest.main()