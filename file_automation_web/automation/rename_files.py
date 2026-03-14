import os
import shutil


def rename_files(upload_folder: str, processed_folder: str, prefix: str = "file") -> dict:
    """
    Copy every file from *upload_folder* to *processed_folder* with a
    sequential name: <prefix>_1.ext, <prefix>_2.ext, …

    Parameters
    ----------
    upload_folder    : source directory
    processed_folder : destination directory
    prefix           : name prefix for renamed files (default "file")

    Returns
    -------
    dict with keys: success, message, files
    """
    files = sorted(
        f for f in os.listdir(upload_folder)
        if os.path.isfile(os.path.join(upload_folder, f))
    )

    if not files:
        return {"success": False, "message": "No files found in the uploads folder."}

    renamed = []
    for idx, filename in enumerate(files, start=1):
        ext      = os.path.splitext(filename)[1]
        new_name = f"{prefix}_{idx}{ext}"
        src      = os.path.join(upload_folder, filename)
        dst      = os.path.join(processed_folder, new_name)
        shutil.copy2(src, dst)
        renamed.append({"original": filename, "renamed": new_name})

    return {
        "success": True,
        "message": f"{len(renamed)} file(s) renamed successfully.",
        "files":   renamed,
    }
