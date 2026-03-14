"""
data_extractor.py
-----------------
Extract data from files and print or save a summary.

Supported file types
--------------------
    .txt / .log   Word count, line count, character count, and a keyword search.
    .csv          Row/column count, column names, and optional column statistics.
    .json         Key/value structure summary and optional field search.

Usage
-----
    python data_extractor.py <file> [--keyword KEYWORD] [--column COLUMN] [--output OUTPUT]

Arguments
---------
    file          Path to the file to extract data from.
    --keyword     (txt/log/json) Search for a keyword and show matching lines/keys.
    --column      (csv) Show statistics for a specific column.
    --output      Save the extraction report to this file (optional).

Examples
--------
    python data_extractor.py report.txt --keyword "error"
    python data_extractor.py sales.csv --column "revenue"
    python data_extractor.py config.json --keyword "host"
    python data_extractor.py data.csv --output summary.txt
"""

import argparse
import csv
import json
import os


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_report(lines: list[str], output_path: str | None) -> None:
    report = "\n".join(lines)
    print(report)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"\nReport saved to {output_path!r}")


# ---------------------------------------------------------------------------
# Text / log extractor
# ---------------------------------------------------------------------------

def extract_text(filepath: str, keyword: str | None = None, output: str | None = None) -> dict:
    """Extract statistics from a plain-text or log file."""
    with open(filepath, encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    words = content.split()

    result = {
        "file": filepath,
        "lines": len(lines),
        "words": len(words),
        "characters": len(content),
    }

    report = [
        f"File        : {filepath}",
        f"Lines       : {len(lines)}",
        f"Words       : {len(words)}",
        f"Characters  : {len(content)}",
    ]

    if keyword:
        matches = [(i + 1, line) for i, line in enumerate(lines) if keyword.lower() in line.lower()]
        result["keyword"] = keyword
        result["keyword_matches"] = len(matches)
        report.append(f"\nKeyword     : {keyword!r}  ({len(matches)} matches)")
        for lineno, text in matches[:20]:  # show up to 20 matches
            report.append(f"  Line {lineno:>5}: {text.strip()}")
        if len(matches) > 20:
            report.append(f"  … and {len(matches) - 20} more.")

    _write_report(report, output)
    return result


# ---------------------------------------------------------------------------
# CSV extractor
# ---------------------------------------------------------------------------

def extract_csv(filepath: str, column: str | None = None, output: str | None = None) -> dict:
    """Extract statistics from a CSV file."""
    with open(filepath, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    result = {
        "file": filepath,
        "rows": len(rows),
        "columns": len(fieldnames),
        "column_names": list(fieldnames),
    }

    report = [
        f"File        : {filepath}",
        f"Rows        : {len(rows)}",
        f"Columns     : {len(fieldnames)}",
        f"Column names: {', '.join(fieldnames)}",
    ]

    if column:
        if column not in fieldnames:
            report.append(f"\nColumn {column!r} not found. Available: {', '.join(fieldnames)}")
        else:
            values_raw = [row[column] for row in rows]
            numeric_values = []
            for v in values_raw:
                try:
                    numeric_values.append(float(v))
                except (ValueError, TypeError):
                    pass

            report.append(f"\nColumn      : {column!r}")
            report.append(f"  Total values : {len(values_raw)}")
            report.append(f"  Non-empty    : {sum(1 for v in values_raw if v.strip())}")

            if numeric_values:
                report.append(f"  Numeric count: {len(numeric_values)}")
                report.append(f"  Min          : {min(numeric_values)}")
                report.append(f"  Max          : {max(numeric_values)}")
                report.append(f"  Sum          : {sum(numeric_values)}")
                report.append(f"  Average      : {sum(numeric_values) / len(numeric_values):.4f}")
                result["column_stats"] = {
                    "column": column,
                    "count": len(numeric_values),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "sum": sum(numeric_values),
                    "average": sum(numeric_values) / len(numeric_values),
                }

    _write_report(report, output)
    return result


# ---------------------------------------------------------------------------
# JSON extractor
# ---------------------------------------------------------------------------

def _summarize_structure(obj, depth: int = 0, max_depth: int = 3) -> list[str]:
    """Recursively summarize the structure of a JSON object."""
    indent = "  " * depth
    lines = []
    if isinstance(obj, dict):
        for key, value in list(obj.items())[:20]:
            type_name = type(value).__name__
            if isinstance(value, (dict, list)) and depth < max_depth:
                lines.append(f"{indent}{key!r} ({type_name}):")
                lines.extend(_summarize_structure(value, depth + 1, max_depth))
            else:
                preview = repr(value)
                if len(preview) > 60:
                    preview = preview[:57] + "…"
                lines.append(f"{indent}{key!r}: {preview}")
        if len(obj) > 20:
            lines.append(f"{indent}… and {len(obj) - 20} more keys")
    elif isinstance(obj, list):
        lines.append(f"{indent}[list of {len(obj)} items]")
        if obj and depth < max_depth:
            lines.extend(_summarize_structure(obj[0], depth + 1, max_depth))
    else:
        lines.append(f"{indent}{repr(obj)}")
    return lines


def extract_json(filepath: str, keyword: str | None = None, output: str | None = None) -> dict:
    """Extract structure information from a JSON file."""
    with open(filepath, encoding="utf-8", errors="replace") as f:
        data = json.load(f)

    top_type = type(data).__name__
    result: dict = {"file": filepath, "top_level_type": top_type}

    report = [
        f"File        : {filepath}",
        f"Top-level   : {top_type}",
    ]

    if isinstance(data, dict):
        result["keys"] = len(data)
        report.append(f"Keys        : {len(data)}")
        report.append("\nStructure:")
        report.extend(_summarize_structure(data))
    elif isinstance(data, list):
        result["items"] = len(data)
        report.append(f"Items       : {len(data)}")
        if data:
            report.append("\nFirst item structure:")
            report.extend(_summarize_structure(data[0]))

    if keyword:
        raw = json.dumps(data)
        count = raw.lower().count(keyword.lower())
        result["keyword"] = keyword
        result["keyword_occurrences"] = count
        report.append(f"\nKeyword {keyword!r} appears ~{count} time(s) in the raw JSON.")

    _write_report(report, output)
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract data and statistics from text, CSV, or JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("file", help="Path to the file to extract data from.")
    parser.add_argument("--keyword", help="(txt/log/json) Search for this keyword.")
    parser.add_argument("--column", help="(csv) Show statistics for this column.")
    parser.add_argument("--output", help="Save the extraction report to this file.")
    return parser


if __name__ == "__main__":
    args = _build_parser().parse_args()

    if not os.path.isfile(args.file):
        raise SystemExit(f"File not found: {args.file!r}")

    ext = os.path.splitext(args.file)[1].lower()

    if ext in (".txt", ".log"):
        extract_text(args.file, keyword=args.keyword, output=args.output)
    elif ext == ".csv":
        extract_csv(args.file, column=args.column, output=args.output)
    elif ext == ".json":
        extract_json(args.file, keyword=args.keyword, output=args.output)
    else:
        raise SystemExit(
            f"Unsupported file type {ext!r}. Supported: .txt, .log, .csv, .json"
        )
