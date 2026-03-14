# Python File Automation

File automation means using Python to automatically perform repetitive tasks on files instead of doing them manually — saving time and eliminating human error.

---

## Features

| Script | What it does |
|---|---|
| [`file_renamer.py`](#1-bulk-file-renaming) | Rename hundreds of files automatically |
| [`file_converter.py`](#2-file-format-conversion) | Convert CSV ↔ JSON and Excel → CSV |
| [`file_organizer.py`](#3-automatic-file-organization) | Move files into folders automatically |
| [`data_extractor.py`](#4-data-extraction) | Extract statistics and data from files |
| [`file_merger.py`](#5-merge-multiple-files) | Merge multiple files into one |

---

## Requirements

- Python 3.10+
- `openpyxl` (for Excel conversion only)

```bash
pip install -r requirements.txt
```

---

## 1. Bulk File Renaming

**Script:** `file_renamer.py`

Automatically renames hundreds of files in a directory.

### Example

You have 100 files like:
```
file1.txt
file2.txt
file3.txt
```

Run:
```bash
python file_renamer.py ./files
```

Result:
```
file1.txt  →  report_1.txt
file2.txt  →  report_2.txt
file3.txt  →  report_3.txt
```

### Usage

```
python file_renamer.py [directory] [--prefix PREFIX] [--pattern PATTERN] [--dry-run]
```

| Argument | Default | Description |
|---|---|---|
| `directory` | `.` | Directory containing the files to rename |
| `--prefix` | `report` | Prefix for the new file names |
| `--pattern` | `file*.txt` | Glob pattern to select files |
| `--dry-run` | — | Preview without making changes |

### Examples

```bash
# Rename file1.txt … fileN.txt → report_1.txt … report_N.txt
python file_renamer.py ./files

# Custom prefix and pattern
python file_renamer.py ./data --prefix data_backup --pattern "*.csv"

# Preview without renaming
python file_renamer.py ./files --dry-run
```

---

## 2. File Format Conversion

**Script:** `file_converter.py`

Convert between CSV, JSON, and Excel formats.

### Subcommands

| Command | Description |
|---|---|
| `csv-to-json` | Convert a CSV file to JSON |
| `json-to-csv` | Convert a JSON array file to CSV |
| `excel-to-csv` | Convert each sheet of an Excel workbook to a separate CSV |

### Usage

```bash
python file_converter.py csv-to-json  <input.csv>  [output.json]
python file_converter.py json-to-csv  <input.json> [output.csv]
python file_converter.py excel-to-csv <input.xlsx> [output_dir]
```

### Examples

```bash
# CSV → JSON
python file_converter.py csv-to-json data/sales.csv data/sales.json

# JSON → CSV
python file_converter.py json-to-csv data/sales.json data/sales.csv

# Excel → CSV (one CSV file per sheet)
python file_converter.py excel-to-csv report.xlsx ./csv_output/
```

---

## 3. Automatic File Organization

**Script:** `file_organizer.py`

Move files from a directory into subfolders — either by file type or by date.

### Subcommands

| Command | Description |
|---|---|
| `by-type` | Group files by extension (`Images/`, `Documents/`, `Videos/`, …) |
| `by-date` | Group files by last-modified date (`2024-01/`, `2024-02/`, …) |

### Usage

```bash
python file_organizer.py by-type [directory] [--dry-run]
python file_organizer.py by-date [directory] [--dry-run]
```

### Examples

```bash
# Move files by type
python file_organizer.py by-type ./downloads

# Move files by date (preview first)
python file_organizer.py by-date ./downloads --dry-run
```

**Type groupings include:** Images, Videos, Audio, Documents, Spreadsheets, Presentations, Data, Code, Archives, Text, Others.

---

## 4. Data Extraction

**Script:** `data_extractor.py`

Extract statistics and content from text, CSV, or JSON files.

### Supported Formats

| Format | Extracts |
|---|---|
| `.txt` / `.log` | Line count, word count, character count, keyword search |
| `.csv` | Row count, column names, optional column statistics (min/max/avg) |
| `.json` | Structure summary, key count, optional keyword search |

### Usage

```bash
python data_extractor.py <file> [--keyword KEYWORD] [--column COLUMN] [--output OUTPUT]
```

### Examples

```bash
# Count lines, words, characters; search for "error"
python data_extractor.py server.log --keyword "error"

# Show CSV structure and stats for the "revenue" column
python data_extractor.py sales.csv --column "revenue"

# Summarise a JSON file and search for "host"
python data_extractor.py config.json --keyword "host"

# Save extraction report to a file
python data_extractor.py data.csv --output summary.txt
```

---

## 5. Merge Multiple Files

**Script:** `file_merger.py`

Merge multiple text or CSV files into a single output file.

### Supported Formats

| Format | Behaviour |
|---|---|
| `txt` / `log` | Concatenate content; optional file dividers |
| `csv` | Stack rows; headers are taken from the first file |

### Usage

```bash
python file_merger.py [--pattern PATTERN] [--type {txt,csv}]
                      [--output OUTPUT] [--separator] [--directory DIRECTORY]
```

### Examples

```bash
# Merge all .txt files in ./reports/ into merged.txt (with dividers)
python file_merger.py --pattern "*.txt" --directory ./reports --separator

# Merge all .csv files in ./data/ into combined.csv
python file_merger.py --pattern "*.csv" --directory ./data --output combined.csv

# Merge part_*.txt files into full_doc.txt
python file_merger.py --pattern "part_*.txt" --directory . --output full_doc.txt
```

---

## Quick Reference

```bash
# 1. Bulk rename
python file_renamer.py ./files --prefix report

# 2. Convert formats
python file_converter.py csv-to-json input.csv
python file_converter.py excel-to-csv report.xlsx

# 3. Organise files
python file_organizer.py by-type ./downloads

# 4. Extract data
python data_extractor.py data.csv --column price

# 5. Merge files
python file_merger.py --pattern "*.csv" --directory ./data
```
