import os
import shutil

# Maps a human-readable category name to a list of lowercase file extensions.
EXTENSION_MAP: dict[str, list[str]] = {
    "images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".odt"],
    "audio":     [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
    "video":     [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"],
    "data":      [".csv", ".json", ".xml", ".sql", ".db", ".sqlite"],
    "code":      [".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rb"],
    "archives":  [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
}


def _get_category(ext: str) -> str:
    ext = ext.lower()
    for category, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            return category
    return "others"


def organize_files(upload_folder: str, processed_folder: str) -> dict:
    """
    Copy each file from *upload_folder* into a category sub-folder inside
    *processed_folder* based on its extension.

    Folder layout example
    ---------------------
    processed/
        images/     photo.jpg
        documents/  report.pdf
        data/       data.csv
        others/     unknown.xyz

    Returns
    -------
    dict with keys: success, message, files
    """
    files = [
        f for f in os.listdir(upload_folder)
        if os.path.isfile(os.path.join(upload_folder, f))
    ]

    if not files:
        return {"success": False, "message": "No files found in the uploads folder."}

    organized = []
    for filename in files:
        ext      = os.path.splitext(filename)[1]
        category = _get_category(ext)

        dest_dir = os.path.join(processed_folder, category)
        os.makedirs(dest_dir, exist_ok=True)

        src = os.path.join(upload_folder, filename)
        dst = os.path.join(dest_dir, filename)
        shutil.copy2(src, dst)

        organized.append({"file": filename, "category": category})

    return {
        "success": True,
        "message": f"{len(organized)} file(s) organized into category folders.",
        "files":   organized,
    }
