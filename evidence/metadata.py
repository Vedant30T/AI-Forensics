import os
from datetime import datetime


def get_file_metadata(file_path):
    """
    Extract basic metadata from an evidence file.
    """

    if not file_path:
        raise ValueError("File path is required.")

    if not os.path.exists(file_path):
        raise FileNotFoundError("Evidence file not found.")

    stat = os.stat(file_path)

    return {
        "file_name": os.path.basename(file_path),
        "file_extension": os.path.splitext(file_path)[1].lower(),
        "file_size_bytes": stat.st_size,
        "file_size_kb": round(stat.st_size / 1024, 2),
        "file_size_mb": round(stat.st_size / (1024 * 1024), 2),
        "created_time": datetime.fromtimestamp(
            stat.st_ctime
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "modified_time": datetime.fromtimestamp(
            stat.st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "accessed_time": datetime.fromtimestamp(
            stat.st_atime
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "absolute_path": os.path.abspath(file_path)
    }


def get_file_type(file_path):
    """
    Identify evidence file type using its extension.
    """

    extension = os.path.splitext(file_path)[1].lower()

    file_types = {
        ".jpg": "Image",
        ".jpeg": "Image",
        ".png": "Image",
        ".gif": "Image",
        ".bmp": "Image",
        ".mp4": "CCTV / Video",
        ".avi": "CCTV / Video",
        ".mkv": "CCTV / Video",
        ".mov": "CCTV / Video",
        ".mp3": "Audio",
        ".wav": "Audio",
        ".aac": "Audio",
        ".pdf": "PDF / Document",
        ".doc": "Document",
        ".docx": "Document",
        ".txt": "Text / System Log",
        ".log": "System Log",
        ".csv": "Data File",
        ".json": "Data / Extracted Evidence",
        ".zip": "Digital Evidence Archive",
        ".img": "Digital Forensic Image",
        ".dd": "Digital Forensic Image",
        ".iso": "Digital Forensic Image"
    }

    return file_types.get(
        extension,
        "Other Evidence"
    )