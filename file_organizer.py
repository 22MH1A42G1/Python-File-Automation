"""
file_organizer.py
-----------------
Automatically move files in a directory into subfolders.

Two organization strategies are supported:

    by-type   Group files into subfolders based on their extension
              (e.g. Images/, Documents/, Videos/, …).
    by-date   Group files into subfolders based on their last-modified date
              (e.g. 2024-01/, 2024-02/, …).

Usage
-----
    python file_organizer.py by-type [directory] [--dry-run]
    python file_organizer.py by-date [directory] [--dry-run]

Examples
--------
    python file_organizer.py by-type ./downloads
    python file_organizer.py by-date ./downloads --dry-run
"""

import argparse
import os
import shutil
from datetime import datetime


# ---------------------------------------------------------------------------
# Extension → folder mapping
# ---------------------------------------------------------------------------

EXTENSION_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".svg": "Images",
    ".webp": "Images",
    ".tiff": "Images",
    # Videos
    ".mp4": "Videos",
    ".avi": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio",
    ".flac": "Audio",
    ".ogg": "Audio",
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".odt": "Documents",
    ".rtf": "Documents",
    # Spreadsheets
    ".xls": "Spreadsheets",
    ".xlsx": "Spreadsheets",
    ".ods": "Spreadsheets",
    ".csv": "Spreadsheets",
    # Presentations
    ".ppt": "Presentations",
    ".pptx": "Presentations",
    # Data / Code
    ".json": "Data",
    ".xml": "Data",
    ".yaml": "Data",
    ".yml": "Data",
    ".toml": "Data",
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".html": "Code",
    ".css": "Code",
    # Archives
    ".zip": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    # Text
    ".txt": "Text",
    ".md": "Text",
    ".log": "Text",
}

OTHER_FOLDER = "Others"


# ---------------------------------------------------------------------------
# Organize by file type
# ---------------------------------------------------------------------------

def organize_by_type(directory: str, dry_run: bool) -> list[tuple[str, str]]:
    """Move files into subfolders based on extension.

    Returns a list of (source_path, destination_path) tuples.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Directory not found: {directory!r}")

    moves: list[tuple[str, str]] = []

    for filename in sorted(os.listdir(directory)):
        src = os.path.join(directory, filename)
        if not os.path.isfile(src):
            continue  # skip subdirectories

        ext = os.path.splitext(filename)[1].lower()
        folder = EXTENSION_MAP.get(ext, OTHER_FOLDER)
        dest_dir = os.path.join(directory, folder)
        dest = os.path.join(dest_dir, filename)
        moves.append((src, dest))

        if dry_run:
            print(f"[DRY RUN] {filename}  →  {folder}/")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(src, dest)
            print(f"Moved: {filename}  →  {folder}/")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total files processed: {len(moves)}")
    return moves


# ---------------------------------------------------------------------------
# Organize by modification date
# ---------------------------------------------------------------------------

def organize_by_date(directory: str, dry_run: bool) -> list[tuple[str, str]]:
    """Move files into YYYY-MM subfolders based on their last-modified date.

    Returns a list of (source_path, destination_path) tuples.
    """
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Directory not found: {directory!r}")

    moves: list[tuple[str, str]] = []

    for filename in sorted(os.listdir(directory)):
        src = os.path.join(directory, filename)
        if not os.path.isfile(src):
            continue

        mtime = os.path.getmtime(src)
        date_folder = datetime.fromtimestamp(mtime).strftime("%Y-%m")
        dest_dir = os.path.join(directory, date_folder)
        dest = os.path.join(dest_dir, filename)
        moves.append((src, dest))

        if dry_run:
            print(f"[DRY RUN] {filename}  →  {date_folder}/")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(src, dest)
            print(f"Moved: {filename}  →  {date_folder}/")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total files processed: {len(moves)}")
    return moves


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automatically move files into subfolders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd, help_text in [
        ("by-type", "Group files by extension (Images/, Documents/, …)."),
        ("by-date", "Group files by last-modified date (YYYY-MM/)."),
    ]:
        p = sub.add_parser(cmd, help=help_text)
        p.add_argument(
            "directory",
            nargs="?",
            default=".",
            help="Directory to organize (default: current directory).",
        )
        p.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview moves without making changes.",
        )

    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()

    if args.command == "by-type":
        organize_by_type(args.directory, args.dry_run)
    elif args.command == "by-date":
        organize_by_date(args.directory, args.dry_run)
