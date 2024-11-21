# File-Manager
A special purpose file-manager.

    Usage:
        main.py <action> <path> [--db-path <db_path>] [--threads <num_threads>]
        [--prefix <prefix>] [--dirA <dirA>] [--dirB <dirB>] [--use-gui] [--min-duplicates <min_duplicates>]

    Actions:
        scan                Scan a comma-separated list of directories or files.
        check-file          Check a file for duplicates.
        scan-dir-report     Scan a directory and report duplicates.
        report-duplicates   Report all duplicates in the database.
        audit-db            Audit the database for file changes.
        report-duplicate-sizes Report the total size of duplicate files.
        report-prefix-count Report the number of files that match a given prefix.
        remove-record       Remove the record associated with the specified path
                            from the database.
        compare-directories Compare two directories and report unique files.
        help                Show this help message.

    Options:
        --db-path           Path to the database file or directory.
        --threads           Number of threads to use for concurrent operations.
        --prefix            Prefix to match files (required for
                            report-prefix-count action).
        --dirA              Path to the first directory for comparison (required for
                            compare-directories action).
        --dirB              Path to the second directory for comparison (required for
                            compare-directories action).
        --use-gui           Use GUI for displaying duplicates.
        --min-duplicates    Minimum number of duplicates to search for (default: 1).

    Examples:
        python main.py scan /path/to/dir1,/path/to/dir2 --db-path /path/to/db --threads 4
        python main.py check-file /path/to/file --db-path /path/to/db --threads 4
        python main.py scan-dir-report /path/to/dir --db-path /path/to/db --threads 4
        python main.py report-duplicates --db-path /path/to/db --threads 4 --use-gui
        python main.py audit-db --db-path /path/to/db --threads 4
        python main.py report-duplicate-sizes --db-path /path/to/db
        python main.py report-prefix-count --db-path /path/to/db --prefix <prefix>
        python main.py remove-record /path/to/file --db-path /path/to/db
        python main.py compare-directories --dirA /path/to/dirA --dirB /path/to/dirB
