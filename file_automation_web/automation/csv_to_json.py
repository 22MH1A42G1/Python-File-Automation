import os
import csv
import json


def convert_csv_to_json(upload_folder: str, processed_folder: str) -> dict:
    """
    Convert every CSV file in *upload_folder* to a JSON file in
    *processed_folder*.

    Parameters
    ----------
    upload_folder    : source directory
    processed_folder : destination directory

    Returns
    -------
    dict with keys: success, message, files
    """
    csv_files = [
        f for f in os.listdir(upload_folder)
        if f.lower().endswith(".csv") and os.path.isfile(os.path.join(upload_folder, f))
    ]

    if not csv_files:
        return {"success": False, "message": "No CSV files found in the uploads folder."}

    converted = []
    errors    = []

    for csv_file in csv_files:
        src           = os.path.join(upload_folder, csv_file)
        json_filename = os.path.splitext(csv_file)[0] + ".json"
        dst           = os.path.join(processed_folder, json_filename)

        try:
            with open(src, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                data   = list(reader)

            with open(dst, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            converted.append({
                "csv":     csv_file,
                "json":    json_filename,
                "records": len(data),
            })

        except Exception as exc:
            errors.append({"file": csv_file, "error": str(exc)})

    result = {
        "success": bool(converted),
        "message": f"{len(converted)} CSV file(s) converted to JSON.",
        "files":   converted,
    }
    if errors:
        result["errors"] = errors

    return result
