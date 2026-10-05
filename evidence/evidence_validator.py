import os

from evidence.hash_utils import calculate_sha256
from evidence.metadata import get_file_metadata


def validate_evidence_file(file_path):
    """
    Validate an evidence file before registration.

    Checks:
    - File exists
    - File is accessible
    - File is not empty
    - Metadata can be read
    - SHA-256 hash can be generated
    """

    result = {
        "valid": False,
        "file_path": file_path,
        "file_exists": False,
        "accessible": False,
        "file_size": 0,
        "sha256_hash": "",
        "metadata": {},
        "errors": []
    }

    # ---------------------------------------------------------
    # File existence
    # ---------------------------------------------------------

    if not file_path:
        result["errors"].append(
            "Evidence file was not selected."
        )
        return result

    if not os.path.exists(file_path):
        result["errors"].append(
            "Evidence file does not exist."
        )
        return result

    result["file_exists"] = True

    # ---------------------------------------------------------
    # File access
    # ---------------------------------------------------------

    if not os.path.isfile(file_path):
        result["errors"].append(
            "Selected path is not a valid evidence file."
        )
        return result

    if not os.access(file_path, os.R_OK):
        result["errors"].append(
            "Evidence file cannot be read."
        )
        return result

    result["accessible"] = True

    # ---------------------------------------------------------
    # File size
    # ---------------------------------------------------------

    try:

        file_size = os.path.getsize(file_path)

        result["file_size"] = file_size

        if file_size == 0:
            result["errors"].append(
                "Evidence file is empty."
            )
            return result

    except OSError as error:

        result["errors"].append(
            f"Unable to read file size: {error}"
        )

        return result

    # ---------------------------------------------------------
    # Metadata
    # ---------------------------------------------------------

    try:

        result["metadata"] = get_file_metadata(
            file_path
        )

    except Exception as error:

        result["errors"].append(
            f"Metadata extraction failed: {error}"
        )

        return result

    # ---------------------------------------------------------
    # SHA-256
    # ---------------------------------------------------------

    try:

        result["sha256_hash"] = calculate_sha256(
            file_path
        )

    except Exception as error:

        result["errors"].append(
            f"SHA-256 generation failed: {error}"
        )

        return result

    # ---------------------------------------------------------
    # Final validation
    # ---------------------------------------------------------

    if (
        result["file_exists"]
        and result["accessible"]
        and result["file_size"] > 0
        and result["sha256_hash"]
        and not result["errors"]
    ):

        result["valid"] = True

    return result


def verify_evidence_integrity(
    file_path,
    registered_hash
):
    """
    Verify current evidence against its registered SHA-256 hash.
    """

    if not file_path or not registered_hash:
        return False

    if not os.path.exists(file_path):
        return False

    try:

        current_hash = calculate_sha256(
            file_path
        )

        return (
            current_hash.lower()
            == registered_hash.lower()
        )

    except Exception:
        return False