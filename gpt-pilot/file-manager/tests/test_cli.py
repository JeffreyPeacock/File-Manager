import unittest
from unittest.mock import patch, MagicMock
from src.cli import scan_file, scan_directory, check_duplicate, report_duplicates
import sqlite3
from src.db import DB_PATH

class TestCLI(unittest.TestCase):

    @patch('src.cli.compute_md5sum')
    @patch('src.cli.store_md5sum_in_db')
    def test_scan_file(self, mock_store_md5sum_in_db, mock_compute_md5sum):
        mock_compute_md5sum.return_value = "dummy_md5sum"
        args = type('', (), {})()  # Create an empty args object
        args.path = "test_file.txt"
        with patch('builtins.print') as mocked_print:
            scan_file(args)
            mocked_print.assert_called_with("MD5 checksum for file test_file.txt: dummy_md5sum")
            mock_store_md5sum_in_db.assert_called_with("test_file.txt", "dummy_md5sum")

    @patch('src.cli.compute_md5sum')
    def test_scan_directory(self, mock_compute_md5sum):
        mock_compute_md5sum.return_value = "dummy_md5sum"
        args = type('', (), {})()  # Create an empty args object
        args.path = "test_directory"
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ("test_directory", ("subdir",), ("file1.txt", "file2.txt")),
                ("test_directory/subdir", (), ("file3.txt",))
            ]
            scan_directory(args)

            # Verify database entries
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files WHERE path = 'test_directory/file1.txt'")
            file1_entry = cursor.fetchone()
            cursor.execute("SELECT * FROM files WHERE path = 'test_directory/file2.txt'")
            file2_entry = cursor.fetchone()
            cursor.execute("SELECT * FROM files WHERE path = 'test_directory/subdir/file3.txt'")
            file3_entry = cursor.fetchone()
            conn.close()

            self.assertIsNotNone(file1_entry)
            self.assertIsNotNone(file2_entry)
            self.assertIsNotNone(file3_entry)
            self.assertEqual(file1_entry[2], "dummy_md5sum")
            self.assertEqual(file2_entry[2], "dummy_md5sum")
            self.assertEqual(file3_entry[2], "dummy_md5sum")

    @patch('src.cli.compute_md5sum')
    @patch('src.cli.is_duplicate')
    def test_check_duplicate(self, mock_is_duplicate, mock_compute_md5sum):
        mock_compute_md5sum.return_value = 'd41d8cd98f00b204e9800998ecf8427e'
        mock_is_duplicate.return_value = True

        with patch('builtins.print') as mock_print:
            args = MagicMock()
            args.path = 'test-file.txt'
            check_duplicate(args)
            mock_print.assert_called_with("The file 'test-file.txt' is a duplicate.")

        mock_is_duplicate.return_value = False

        with patch('builtins.print') as mock_print:
            check_duplicate(args)
            mock_print.assert_called_with("The file 'test-file.txt' is not a duplicate.")

    @patch('src.cli.compute_md5sum')
    @patch('src.cli.is_duplicate')
    def test_report_duplicates(self, mock_is_duplicate, mock_compute_md5sum):
        mock_compute_md5sum.return_value = 'dummy_md5sum'
        mock_is_duplicate.side_effect = lambda md5sum: md5sum == 'dummy_md5sum'

        args = type('', (), {})()  # Create an empty args object
        args.path = "test_directory"
        with patch('os.walk') as mock_walk, patch('builtins.print') as mock_print:
            mock_walk.return_value = [
                ("test_directory", ("subdir",), ("file1.txt", "file2.txt")),
                ("test_directory/subdir", (), ("file3.txt",))
            ]
            report_duplicates(args)

            mock_print.assert_any_call("Duplicate files for MD5 dummy_md5sum:")
            mock_print.assert_any_call(" - test_directory/file1.txt")
            mock_print.assert_any_call(" - test_directory/file2.txt")
            mock_print.assert_any_call(" - test_directory/subdir/file3.txt")

if __name__ == "__main__":
    unittest.main()