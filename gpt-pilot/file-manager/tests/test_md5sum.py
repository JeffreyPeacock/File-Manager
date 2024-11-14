import unittest
import os
from src.md5sum import compute_md5sum

class TestComputeMd5sum(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for testing
        self.test_file_path = "test_file.txt"
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file.")

    def tearDown(self):
        # Remove the temporary file after testing
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_compute_md5sum(self):
        expected_md5sum = "3de8f8b0dc94b8c2230fab9ec0ba0506"  # Precomputed md5sum for the test file content
        actual_md5sum = compute_md5sum(self.test_file_path)
        self.assertEqual(expected_md5sum, actual_md5sum)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            compute_md5sum("non_existent_file.txt")

if __name__ == "__main__":
    unittest.main()