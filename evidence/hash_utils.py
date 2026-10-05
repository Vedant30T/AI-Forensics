import hashlib
import os


def calculate_sha256(file_path, chunk_size=1024 * 1024):
    """
    Calculate SHA-256 hash of an evidence file.

    The file is read in chunks so large files such as CCTV videos
    can also be processed efficiently.
    """

    if not file_path:
        raise ValueError("File path is required.")

    if not os.path.exists(file_path):
        raise FileNotFoundError("Evidence file not found.")

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(chunk_size)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def verify_sha256(file_path, expected_hash):
    """
    Verify whether an evidence file matches its registered SHA-256 hash.
    """

    if not expected_hash:
        return False

    current_hash = calculate_sha256(file_path)

    return current_hash.lower() == expected_hash.lower()


def get_file_size(file_path):
    """
    Return evidence file size in bytes.
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError("Evidence file not found.")

    return os.path.getsize(file_path)