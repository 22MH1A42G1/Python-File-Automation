# Copilot Instructions

## Project Overview

**Python-File-Automation** is a Flask-based web application that lets users upload files and apply automated file-processing operations in the browser. The three core operations are:

1. **Rename files** – copies uploaded files to a `processed/` folder with a sequential `<prefix>_N.ext` naming scheme.
2. **CSV → JSON conversion** – converts every uploaded CSV file to a UTF-8 JSON file using Python's standard `csv` and `json` modules (pandas is available but not used here).
3. **Organize by type** – sorts uploaded files into category sub-folders (`images/`, `documents/`, `data/`, etc.) based on file extension.

## Repository Structure

```
Python-File-Automation/
├── README.md
└── file_automation_web/          # Main application package
    ├── app.py                    # Flask entry point and route definitions
    ├── requirements.txt          # Python dependencies (flask, werkzeug, pandas)
    ├── automation/               # Pure-Python automation modules (no Flask coupling)
    │   ├── __init__.py
    │   ├── rename_files.py
    │   ├── csv_to_json.py
    │   └── sort_files.py
    ├── templates/
    │   └── index.html            # Single-page Jinja2 template
    └── static/
        ├── style.css
        └── script.js
```

Runtime directories created automatically by `app.py`:

- `file_automation_web/uploads/`   – where uploaded files land
- `file_automation_web/processed/` – where processed output is written

## Development Setup

```bash
cd file_automation_web
pip install -r requirements.txt
python app.py          # runs on http://127.0.0.1:5000 with debug=True
```

No database or external services are required.

## Architecture & Conventions

- **Separation of concerns** – all file-processing logic lives in `automation/` as plain functions that accept folder paths and return a `dict` with keys `success`, `message`, and `files`. Flask routes in `app.py` call these functions and return `jsonify(result)`.
- **Automation module contract** – every public function in `automation/` must return a `dict` with at minimum `{"success": bool, "message": str}`. Add a `"files"` key (list) when there are per-file results.
- **Path safety** – the `/download/<path:filename>` route uses `os.path.realpath` to guard against directory traversal. Preserve this pattern for any new download or file-access routes.
- **No global state** – upload and processed folders are resolved from `BASE_DIR` at startup; avoid module-level mutable state.
- **Dependencies** – the application depends on `flask`, `werkzeug`, and `pandas` (declared in `requirements.txt`). The existing automation modules rely only on the standard library; prefer that approach for new modules and reach for `pandas` only when its data-manipulation capabilities are genuinely needed. Do not add new third-party packages without updating `requirements.txt`.
- **Python style** – follow PEP 8. Use type hints on function signatures. Write NumPy-style docstrings for public functions (see existing modules for examples).

## Adding a New Automation Feature

1. Create `file_automation_web/automation/<feature>.py` with a single public function matching the module contract above.
2. Import and call that function from a new route in `app.py`.
3. Wire up any UI in `templates/index.html` and `static/script.js` / `static/style.css`.

## Testing

There is no automated test suite yet. When adding tests, place them in a `tests/` directory at the repo root and use `pytest`. Test the automation modules in isolation by passing temporary directories (use `tmp_path` from pytest fixtures).
