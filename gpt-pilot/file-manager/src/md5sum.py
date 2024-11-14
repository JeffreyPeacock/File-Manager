import hashlib
import logging

def compute_md5sum(file_path):
    """
    Compute the MD5 checksum of a given file.

    :param file_path: Path to the file
    :return: MD5 checksum as a string
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        logging.info(f"MD5 checksum computed for file {file_path}")
        return hash_md5.hexdigest()
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.", exc_info=True)
        raise FileNotFoundError(f"File {file_path} not found.")
    except Exception as e:
        logging.error(f"Error computing md5sum for file {file_path}: {e}", exc_info=True)
        raise Exception(f"Error computing md5sum for file {file_path}: {e}")