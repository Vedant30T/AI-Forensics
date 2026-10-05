import os
import shutil
from datetime import datetime

from evidence.hash_utils import calculate_sha256
from utils.paths import get_pen_drive_backup_path


def is_valid_drive(path):
    """
    Check whether the selected path exists and is accessible.
    """

    if not path:
        return False

    return os.path.exists(path)


def get_drive_contents(drive_path):
    """
    Return files and folders available in the selected Pen Drive.
    """

    if not is_valid_drive(drive_path):
        return []

    try:
        return os.listdir(drive_path)
    except (PermissionError, OSError):
        return []


def copy_pen_drive_evidence(source_path):
    """
    Create a forensic-style backup of the selected Pen Drive
    evidence without modifying the source.
    """

    if not is_valid_drive(source_path):
        raise FileNotFoundError(
            "Selected Pen Drive or evidence folder was not found."
        )

    backup_root = get_pen_drive_backup_path()

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_folder = os.path.join(
        backup_root,
        "pendrive_" + timestamp
    )

    os.makedirs(backup_folder, exist_ok=True)

    source_name = os.path.basename(
        os.path.normpath(source_path)
    )

    destination = os.path.join(
        backup_folder,
        source_name
    )

    if os.path.isdir(source_path):

        shutil.copytree(
            source_path,
            destination,
            dirs_exist_ok=True
        )

    else:

        shutil.copy2(
            source_path,
            destination
        )

    return {
        "success": True,
        "source": os.path.abspath(source_path),
        "backup_path": os.path.abspath(destination),
        "timestamp": timestamp
    }


def create_file_hash_list(folder_path):
    """
    Generate SHA-256 hashes for all files inside the
    selected Pen Drive evidence folder.
    """

    if not os.path.isdir(folder_path):
        return []

    hash_records = []

    for root, _, files in os.walk(folder_path):

        for filename in files:

            file_path = os.path.join(
                root,
                filename
            )

            try:

                file_hash = calculate_sha256(
                    file_path
                )

                relative_path = os.path.relpath(
                    file_path,
                    folder_path
                )

                hash_records.append({
                    "file_name": filename,
                    "relative_path": relative_path,
                    "sha256_hash": file_hash,
                    "file_size_bytes": os.path.getsize(
                        file_path
                    )
                })

            except (PermissionError, OSError):
                continue

    return hash_records