"""
file_merger.py
--------------
Merge multiple files into a single output file.

Supported file types
--------------------
    txt / log   Concatenate text files (optionally separated by a header/divider).
    csv         Stack CSV files row-by-row (headers are preserved from the first file
                and skipped for subsequent files).

Usage
-----
    python file_merger.py [--pattern PATTERN] [--type {txt,csv}] [--output OUTPUT]
                          [--separator] [--directory DIRECTORY]

Arguments
---------
    --pattern     Glob pattern to select files (default: "*.txt").
    --type        File type to merge: "txt" or "csv" (auto-detected from pattern).
    --output      Path for the merged output file (default: "merged.<ext>").
    --separator   (txt only) Insert a divider between each file's content.
    --directory   Directory to search in (default: current directory).

Examples
--------
    # Merge all .txt files in ./reports/ into merged.txt
    python file_merger.py --pattern "*.txt" --directory ./reports --separator

    # Merge all .csv files in ./data/ into merged.csv
    python file_merger.py --pattern "*.csv" --directory ./data --output combined.csv

    # Merge specific files listed on stdin (pipe them)
    python file_merger.py --pattern "part_*.txt" --directory . --output full_doc.txt
"""

import argparse
import csv
import fnmatch
import os


# ---------------------------------------------------------------------------
# Text / log merger
# ---------------------------------------------------------------------------

def merge_text_files(
    files: list[str],
    output_path: str,
    separator: bool = True,
) -> str:
    """Concatenate a list of text files into *output_path*.

    Returns the output path.
    """
    with open(output_path, "w", encoding="utf-8") as out:
        for index, filepath in enumerate(files):
            if separator and index > 0:
                out.write("\n" + "-" * 60 + "\n\n")
            if separator:
                out.write(f"--- {os.path.basename(filepath)} ---\n\n")

            with open(filepath, encoding="utf-8", errors="replace") as f:
                out.write(f.read())

            # Ensure file ends with a newline before the next separator
            out.write("\n")

    print(f"Merged {len(files)} text file(s) → {output_path!r}")
    return output_path


# ---------------------------------------------------------------------------
# CSV merger
# ---------------------------------------------------------------------------

def merge_csv_files(files: list[str], output_path: str) -> str:
    """Stack CSV files row-by-row into *output_path*.

    The header row is taken from the first file; subsequent files' headers are
    skipped (they must have the same columns).

    Returns the output path.
    """
    total_rows = 0

    with open(output_path, "w", newline="", encoding="utf-8") as out_file:
        writer: csv.DictWriter | None = None

        for file_index, filepath in enumerate(files):
            with open(filepath, newline="", encoding="utf-8", errors="replace") as in_file:
                reader = csv.DictReader(in_file)
                if reader.fieldnames is None:
                    print(f"  Skipping {filepath!r} — no headers detected.")
                    continue

                if writer is None:
                    writer = csv.DictWriter(out_file, fieldnames=reader.fieldnames)
                    writer.writeheader()

                rows = list(reader)
                writer.writerows(rows)
                total_rows += len(rows)
                print(f"  Added {len(rows):>6} rows from {os.path.basename(filepath)!r}")

    print(f"\nMerged {len(files)} CSV file(s) → {output_path!r}  (total rows: {total_rows})")
    return output_path


# ---------------------------------------------------------------------------
# Helper: discover files matching a pattern in a directory
# ---------------------------------------------------------------------------

def find_files(directory: str, pattern: str) -> list[str]:
    """Return sorted list of file paths matching *pattern* in *directory*."""
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Directory not found: {directory!r}")

    return sorted(
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if fnmatch.fnmatch(f, pattern) and os.path.isfile(os.path.join(directory, f))
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Merge multiple text or CSV files into one.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--pattern",
        default="*.txt",
        help='Glob pattern to select files (default: "*.txt").',
    )
    parser.add_argument(
        "--type",
        choices=["txt", "csv"],
        help='File type to merge: "txt" or "csv" (auto-detected from --pattern if omitted).',
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: merged.txt or merged.csv).",
    )
    parser.add_argument(
        "--separator",
        action="store_true",
        help="(txt only) Insert a divider/header between each file's content.",
    )
    parser.add_argument(
        "--directory",
        default=".",
        help="Directory to search for files (default: current directory).",
    )
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()

    # Auto-detect file type from pattern
    file_type = args.type
    if file_type is None:
        if args.pattern.endswith(".csv"):
            file_type = "csv"
        else:
            file_type = "txt"

    output = args.output or f"merged.{file_type}"

    files = find_files(args.directory, args.pattern)
    if not files:
        raise SystemExit(f"No files matched pattern {args.pattern!r} in {args.directory!r}")

    print(f"Found {len(files)} file(s) to merge:\n  " + "\n  ".join(os.path.basename(f) for f in files))
    print()

    if file_type == "csv":
        merge_csv_files(files, output)
    else:
        merge_text_files(files, output, separator=args.separator)
