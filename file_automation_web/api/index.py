import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from automation.rename_files import rename_files
from automation.csv_to_json import convert_csv_to_json
from automation.sort_files import organize_files

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_ROOT, "templates"),
    static_folder=os.path.join(PROJECT_ROOT, "static"),
)

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
PROCESSED_FOLDER = os.path.join(PROJECT_ROOT, "processed")

app.config["UPLOAD_FOLDER"]    = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB

os.makedirs(UPLOAD_FOLDER,    exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def list_processed_recursive(folder):
    """Return relative paths for every file inside processed/ (incl. sub-dirs)."""
    result = []
    for root, _, files in os.walk(folder):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), folder)
            result.append(rel.replace("\\", "/"))
    return result


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        return jsonify({"success": False, "message": "No files provided."}), 400

    files = request.files.getlist("files")
    uploaded = []

    for file in files:
        if not file.filename:
            continue
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        uploaded.append(filename)

    if not uploaded:
        return jsonify({"success": False, "message": "No valid files uploaded."}), 400

    return jsonify({
        "success": True,
        "message": f"{len(uploaded)} file(s) uploaded successfully.",
        "files": uploaded,
    })


@app.route("/files", methods=["GET"])
def list_files():
    uploads   = [f for f in os.listdir(UPLOAD_FOLDER)
                 if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]
    processed = list_processed_recursive(PROCESSED_FOLDER)
    return jsonify({"uploads": uploads, "processed": processed})


@app.route("/rename", methods=["POST"])
def rename():
    data   = request.get_json() or {}
    prefix = data.get("prefix", "file").strip() or "file"
    result = rename_files(UPLOAD_FOLDER, PROCESSED_FOLDER, prefix)
    return jsonify(result)


@app.route("/csv-to-json", methods=["POST"])
def csv_json():
    result = convert_csv_to_json(UPLOAD_FOLDER, PROCESSED_FOLDER)
    return jsonify(result)


@app.route("/organize", methods=["POST"])
def organize():
    result = organize_files(UPLOAD_FOLDER, PROCESSED_FOLDER)
    return jsonify(result)


@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    # Guard against path traversal
    safe_path = os.path.realpath(os.path.join(PROCESSED_FOLDER, filename))
    if not safe_path.startswith(os.path.realpath(PROCESSED_FOLDER)):
        return jsonify({"error": "Invalid path."}), 400
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)


@app.route("/clear-uploads", methods=["POST"])
def clear_uploads():
    for f in os.listdir(UPLOAD_FOLDER):
        fpath = os.path.join(UPLOAD_FOLDER, f)
        if os.path.isfile(fpath):
            os.remove(fpath)
    return jsonify({"success": True, "message": "Uploads cleared."})


@app.route("/clear-processed", methods=["POST"])
def clear_processed():
    import shutil
    for item in os.listdir(PROCESSED_FOLDER):
        ipath = os.path.join(PROCESSED_FOLDER, item)
        if os.path.isdir(ipath):
            shutil.rmtree(ipath)
        else:
            os.remove(ipath)
    return jsonify({"success": True, "message": "Processed files cleared."})


if __name__ == "__main__":
    app.run(debug=True)
