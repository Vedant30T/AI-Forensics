import json
import os
import shutil
from datetime import datetime


def find_files(root_folder, extensions=None):
    """
    Recursively find files inside an Android evidence folder.
    """

    if not os.path.exists(root_folder):
        return []

    found_files = []

    if extensions:
        extensions = {
            ext.lower() if ext.startswith(".") else "." + ext.lower()
            for ext in extensions
        }

    for root, _, files in os.walk(root_folder):

        for filename in files:

            file_path = os.path.join(root, filename)

            if extensions:
                if os.path.splitext(filename)[1].lower() not in extensions:
                    continue

            found_files.append(file_path)

    return found_files


def extract_android_data(
    backup_folder,
    output_folder=None
):
    """
    Process acquired Android evidence.

    The original backup is not modified.
    Extracted/organized information is copied to a separate folder.
    """

    if not backup_folder:
        raise ValueError("Android backup folder is required.")

    if not os.path.exists(backup_folder):
        raise FileNotFoundError(
            "Android backup folder not found."
        )

    if output_folder is None:

        output_folder = os.path.join(
            backup_folder,
            "extracted_data"
        )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    # ---------------------------------------------------------
    # Create category folders
    # ---------------------------------------------------------

    categories = {
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        "videos": [".mp4", ".avi", ".mkv", ".mov", ".3gp"],
        "audio": [".mp3", ".wav", ".aac", ".m4a", ".ogg"],
        "documents": [".pdf", ".doc", ".docx", ".txt"],
        "json_data": [".json"],
        "other": []
    }

    result = {
        "success": True,
        "backup_folder": os.path.abspath(backup_folder),
        "output_folder": os.path.abspath(output_folder),
        "files_found": 0,
        "categories": {},
        "processed_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    # ---------------------------------------------------------
    # Find all files
    # ---------------------------------------------------------

    all_files = find_files(backup_folder)

    # Do not process files already inside output folder.
    output_abs = os.path.abspath(output_folder)

    filtered_files = []

    for file_path in all_files:

        file_abs = os.path.abspath(file_path)

        if file_abs.startswith(output_abs):
            continue

        filtered_files.append(file_path)

    all_files = filtered_files

    result["files_found"] = len(all_files)

    # ---------------------------------------------------------
    # Organize evidence copies
    # ---------------------------------------------------------

    for category, extensions in categories.items():

        category_folder = os.path.join(
            output_folder,
            category
        )

        os.makedirs(
            category_folder,
            exist_ok=True
        )

        result["categories"][category] = 0

        for source_file in all_files:

            extension = os.path.splitext(
                source_file
            )[1].lower()

            if category == "other":

                known_extensions = set()

                for ext_list in categories.values():
                    known_extensions.update(ext_list)

                if extension in known_extensions:
                    continue

            elif extension not in extensions:
                continue

            try:

                relative_path = os.path.relpath(
                    source_file,
                    backup_folder
                )

                safe_name = relative_path.replace(
                    os.sep,
                    "_"
                )

                destination = os.path.join(
                    category_folder,
                    safe_name
                )

                shutil.copy2(
                    source_file,
                    destination
                )

                result["categories"][category] += 1

            except (
                PermissionError,
                OSError,
                shutil.Error
            ):
                continue

    # ---------------------------------------------------------
    # Create extraction summary
    # ---------------------------------------------------------

    summary_path = os.path.join(
        output_folder,
        "android_extraction_summary.json"
    )

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    result["summary_file"] = summary_path

    return result