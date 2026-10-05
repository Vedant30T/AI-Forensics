import os
import shutil
from datetime import datetime


def select_evidence_file(parent=None):
    """
    Open a GUI file selector and return the selected evidence file.
    """

    from PySide6.QtWidgets import QFileDialog

    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Evidence File",
        "",
        (
            "All Evidence Files (*.*);;"
            "Images (*.jpg *.jpeg *.png *.bmp);;"
            "Videos (*.mp4 *.avi *.mkv *.mov);;"
            "Audio (*.mp3 *.wav *.aac);;"
            "Documents (*.pdf *.doc *.docx *.txt);;"
            "Forensic Images (*.img *.dd *.iso)"
        )
    )

    return file_path


def select_evidence_folder(parent=None):
    """
    Open a GUI folder selector and return the selected folder.
    """

    from PySide6.QtWidgets import QFileDialog

    folder_path = QFileDialog.getExistingDirectory(
        parent,
        "Select Evidence Folder"
    )

    return folder_path


def copy_evidence_to_master_storage(
    source_path,
    destination_root
):
    """
    Create an immutable-style master copy of evidence.

    The source evidence is never modified.
    """

    if not source_path:
        raise ValueError("Evidence source is required.")

    if not os.path.exists(source_path):
        raise FileNotFoundError(
            "Selected evidence does not exist."
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    master_folder = os.path.join(
        destination_root,
        "MASTER_" + timestamp
    )

    os.makedirs(
        master_folder,
        exist_ok=True
    )

    source_name = os.path.basename(
        os.path.normpath(source_path)
    )

    destination = os.path.join(
        master_folder,
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

    return os.path.abspath(destination)


def get_evidence_files(folder_path):
    """
    Get all files from an evidence folder recursively.
    """

    if not os.path.isdir(folder_path):
        return []

    files = []

    for root, _, filenames in os.walk(folder_path):

        for filename in filenames:

            file_path = os.path.join(
                root,
                filename
            )

            files.append(
                os.path.abspath(file_path)
            )

    return files


def get_file_count(folder_path):
    """
    Return total number of evidence files.
    """

    return len(
        get_evidence_files(folder_path)
    )