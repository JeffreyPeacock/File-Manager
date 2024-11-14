# src/cli.py

import argparse
import logging
import sys
import os

# Add the parent directory of 'src' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import initialize_db, store_md5sum_in_db  # Import the initialize_db and store_md5sum_in_db functions
from src.md5sum import compute_md5sum  # Import the compute_md5sum function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database when the CLI is used
initialize_db()

def scan_directory(args):
    try:
        logging.info(f"Scanning directory {args.path}")
        for root, dirs, files in os.walk(args.path):
            for file in files:
                file_path = os.path.join(root, file)
                md5sum = compute_md5sum(file_path)
                store_md5sum_in_db(file_path, md5sum)
                logging.info(f"Stored MD5 checksum for file {file_path}")
    except Exception as e:
        logging.error(f"Error scanning directory {args.path}: {e}", exc_info=True)

def scan_file(args):
    try:
        logging.info(f"Scanning file {args.path}")
        md5sum = compute_md5sum(args.path)
        store_md5sum_in_db(args.path, md5sum)
        print(f"MD5 checksum for file {args.path}: {md5sum}")
    except Exception as e:
        logging.error(f"Error scanning file {args.path}: {e}", exc_info=True)

def check_duplicate(args):
    try:
        logging.info(f"Checking if file {args.path} is a duplicate")
        print(f"Placeholder: Checking if file {args.path} is a duplicate")
    except Exception as e:
        logging.error(f"Error checking duplicate for file {args.path}: {e}", exc_info=True)

def report_duplicates(args):
    try:
        logging.info(f"Reporting duplicates in directory {args.path}")
        print(f"Placeholder: Reporting duplicates in directory {args.path}")
    except Exception as e:
        logging.error(f"Error reporting duplicates in directory {args.path}: {e}", exc_info=True)

def display_duplicates_gui(args):
    try:
        logging.info("Displaying duplicates in GUI")
        print("Placeholder: Displaying duplicates in GUI")
    except Exception as e:
        logging.error(f"Error displaying duplicates in GUI: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="File Manager CLI")

    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Command: scan directory
    parser_scan_dir = subparsers.add_parser("scan-dir", help="Recursively scan a directory and compute md5sums")
    parser_scan_dir.add_argument("path", type=str, help="Path to the directory to scan")
    parser_scan_dir.set_defaults(func=scan_directory)

    # Command: scan file
    parser_scan_file = subparsers.add_parser("scan-file", help="Compute the md5sum for a given file")
    parser_scan_file.add_argument("path", type=str, help="Path to the file to scan")
    parser_scan_file.set_defaults(func=scan_file)

    # Command: check duplicate
    parser_check = subparsers.add_parser("check", help="Check if a given file is a duplicate")
    parser_check.add_argument("path", type=str, help="Path to the file to check")
    parser_check.set_defaults(func=check_duplicate)

    # Command: report duplicates
    parser_report = subparsers.add_parser("report", help="Report duplicates in a directory")
    parser_report.add_argument("path", type=str, help="Path to the directory to scan for duplicates")
    parser_report.set_defaults(func=report_duplicates)

    # Command: display duplicates in GUI
    parser_display_gui = subparsers.add_parser("display-gui", help="Display duplicates in a graphical user interface")
    parser_display_gui.set_defaults(func=display_duplicates_gui)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()