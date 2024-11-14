import unittest
from unittest.mock import patch
from src.cli import scan_file, scan_directory

class TestCLI(unittest.TestCase):

    @patch('src.cli.compute_md5sum')
    def test_scan_file(self, mock_compute_md5sum):
        mock_compute_md5sum.return_value = "dummy_md5sum"
        args = type('', (), {})()  # Create an empty args object
        args.path = "test_file.txt"
        with patch('builtins.print') as mocked_print:
            scan_file(args)
            mocked_print.assert_called_with("MD5 checksum for file test_file.txt: dummy_md5sum")

    @patch('src.cli.compute_md5sum')
    @patch('src.cli.store_md5sum_in_db')
    def test_scan_directory(self, mock_store_md5sum_in_db, mock_compute_md5sum):
        mock_compute_md5sum.return_value = "dummy_md5sum"
        args = type('', (), {})()  # Create an empty args object
        args.path = "test_directory"
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ("test_directory", ("subdir",), ("file1.txt", "file2.txt")),
                ("test_directory/subdir", (), ("file3.txt",))
            ]
            scan_directory(args)
            self.assertEqual(mock_store_md5sum_in_db.call_count, 3)

if __name__ == "__main__":
    unittest.main()