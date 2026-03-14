"""
file_renamer.py
---------------
Bulk-rename files in a directory.

Default example (matches the problem statement):
    file1.txt, file2.txt, file3.txt  →  report_1.txt, report_2.txt, report_3.txt

Usage
-----
    python file_renamer.py [directory] [--prefix PREFIX] [--pattern PATTERN] [--dry-run]

Arguments
---------
    directory   Directory containing the files to rename (default: current directory).
    --prefix    Prefix to use for renamed files (default: "report").
    --pattern   Glob pattern to match files (default: "file*.txt").
    --dry-run   Print what would be renamed without actually renaming.

Examples
--------
    # Rename file1.txt … fileN.txt → report_1.txt … report_N.txt in ./files/
    python file_renamer.py ./files

    # Use a custom prefix and pattern
    python file_renamer.py ./data --prefix data_backup --pattern "*.csv"

    # Preview without making changes
    python file_renamer.py ./files --dry-run
"""

import os
import argparse


def rename_files(directory: str, prefix: str, pattern: str, dry_run: bool) -> list[tuple[str, str]]:
    """Rename files matching *pattern* in *directory* using *prefix*.

    Returns a list of (old_name, new_name) tuples for every file that was
    (or would be) renamed.
    """
    import fnmatch

    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Directory not found: {directory!r}")

    # Collect and sort files that match the pattern
    all_entries = os.listdir(directory)
    matched = sorted(
        f for f in all_entries
        if fnmatch.fnmatch(f, pattern) and os.path.isfile(os.path.join(directory, f))
    )

    if not matched:
        print(f"No files matched pattern {pattern!r} in {directory!r}.")
        return []

    renames: list[tuple[str, str]] = []
    for index, filename in enumerate(matched, start=1):
        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{index}{ext}"
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)
        renames.append((filename, new_name))

        if dry_run:
            print(f"[DRY RUN] {filename}  →  {new_name}")
        else:
            os.rename(old_path, new_path)
            print(f"Renamed: {filename}  →  {new_name}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total files processed: {len(renames)}")
    return renames


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bulk-rename files in a directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory containing the files to rename (default: current directory).",
    )
    parser.add_argument(
        "--prefix",
        default="report",
        help='Prefix for renamed files (default: "report").',
    )
    parser.add_argument(
        "--pattern",
        default="file*.txt",
        help='Glob pattern to match files (default: "file*.txt").',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview renames without making changes.",
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()
    rename_files(
        directory=args.directory,
        prefix=args.prefix,
        pattern=args.pattern,
        dry_run=args.dry_run,
    )
