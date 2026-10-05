import os
import json
import hashlib
from datetime import datetime

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REGISTRY_FILE = os.path.join(
    BASE_DIR,
    "evidence_registry.json"
)

BLOCKCHAIN_FILE = os.path.join(
    BASE_DIR,
    "blockchain_records.json"
)

CHAIN_OF_CUSTODY_FILE = os.path.join(
    BASE_DIR,
    "chain_of_custody.json"
)

VERIFICATION_HISTORY_FILE = os.path.join(
    BASE_DIR,
    "verification_history.json"
)


# =========================================================
# JSON HELPERS
# =========================================================

def load_json_file(
    file_path,
    default_value
):

    if not os.path.exists(file_path):
        return default_value

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return default_value


def save_json_file(
    file_path,
    data
):

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# EVIDENCE REGISTRY
# =========================================================

def load_evidence_registry():

    data = load_json_file(
        REGISTRY_FILE,
        []
    )

    return data if isinstance(
        data,
        list
    ) else []


def get_evidence_by_uid(
    evidence_uid
):

    evidence_uid = str(
        evidence_uid
    ).strip()

    records = load_evidence_registry()

    for record in records:

        if str(
            record.get(
                "evidence_uid",
                ""
            )
        ).strip() == evidence_uid:

            return record

    return None


# =========================================================
# BLOCKCHAIN RECORD
# =========================================================

def get_blockchain_record(
    evidence_uid
):

    data = load_json_file(
        BLOCKCHAIN_FILE,
        []
    )

    if isinstance(data, dict):

        data = [
            data
        ]

    for record in data:

        if str(
            record.get(
                "evidence_uid",
                ""
            )
        ).strip() == str(
            evidence_uid
        ).strip():

            return record

    return None


# =========================================================
# CHAIN OF CUSTODY
# =========================================================

def get_chain_of_custody(
    evidence_uid
):

    data = load_json_file(
        CHAIN_OF_CUSTODY_FILE,
        []
    )

    if isinstance(data, dict):

        data = [
            data
        ]

    history = []

    for record in data:

        if str(
            record.get(
                "evidence_uid",
                ""
            )
        ).strip() == str(
            evidence_uid
        ).strip():

            history.append(
                record
            )

    return history


# =========================================================
# SHA-256 - SINGLE FILE
# =========================================================

def calculate_file_hash(
    file_path
):

    sha256 = hashlib.sha256()

    with open(
        file_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# =========================================================
# SHA-256 - COMPLETE FOLDER
# =========================================================

def calculate_folder_hash(
    folder_path
):

    sha256 = hashlib.sha256()

    all_files = []

    for root, directories, files in os.walk(
        folder_path
    ):

        directories.sort()
        files.sort()

        for filename in files:

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                folder_path
            )

            all_files.append(
                (
                    relative_path,
                    full_path
                )
            )

    all_files.sort(
        key=lambda item: item[0]
    )

    for relative_path, full_path in all_files:

        normalized_path = (
            relative_path
            .replace(
                "\\",
                "/"
            )
        )

        sha256.update(
            normalized_path.encode(
                "utf-8"
            )
        )

        with open(
            full_path,
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                sha256.update(
                    chunk
                )

    return sha256.hexdigest()


# =========================================================
# GENERIC EVIDENCE HASH
# =========================================================

def calculate_evidence_hash(
    evidence_path
):

    if not evidence_path:

        raise ValueError(
            "Evidence path is empty."
        )

    if not os.path.exists(
        evidence_path
    ):

        raise FileNotFoundError(
            "Evidence path does not exist."
        )

    if os.path.isfile(
        evidence_path
    ):

        return calculate_file_hash(
            evidence_path
        )

    if os.path.isdir(
        evidence_path
    ):

        return calculate_folder_hash(
            evidence_path
        )

    raise ValueError(
        "Invalid evidence path."
    )


# =========================================================
# FIND CURRENT EVIDENCE PATH
# =========================================================

def get_registered_evidence_path(
    record
):

    original_path = record.get(
        "original_evidence_path"
    )

    if (
        original_path
        and os.path.exists(original_path)
    ):

        return original_path

    storage_reference = record.get(
        "storage_reference"
    )

    if storage_reference:

        storage_path = os.path.join(
            BASE_DIR,
            storage_reference
        )

        if os.path.exists(
            storage_path
        ):

            return storage_path

    return None


# =========================================================
# HASH VERIFICATION
# =========================================================

def verify_hash(
    evidence_uid
):

    record = get_evidence_by_uid(
        evidence_uid
    )

    if not record:

        return {
            "success": False,
            "message": (
                "Evidence UID not found."
            )
        }

    evidence_path = get_registered_evidence_path(
        record
    )

    if not evidence_path:

        return {
            "success": False,
            "message": (
                "Registered evidence file/folder "
                "could not be located."
            )
        }

    try:

        current_hash = calculate_evidence_hash(
            evidence_path
        )

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }

    reference_hash = str(
        record.get(
            "sha256_hash",
            ""
        )
    ).strip().lower()

    current_hash = current_hash.lower()

    match = (
        bool(reference_hash)
        and reference_hash == current_hash
    )

    return {

        "success": True,

        "evidence_uid": evidence_uid,

        "evidence_path": evidence_path,

        "reference_hash": reference_hash,

        "current_hash": current_hash,

        "hash_match": match,

        "integrity_status": (
            "MATCH"
            if match
            else "MISMATCH"
        ),

        "integrity_score": (
            100
            if match
            else 0
        ),

        "message": (
            "Integrity verified."
            if match
            else
            "Integrity mismatch detected. "
            "Further investigation required."
        )
    }


# =========================================================
# METADATA EXTRACTION
# =========================================================

def extract_metadata(
    evidence_path
):

    if not evidence_path:

        return {
            "success": False,
            "message": (
                "Evidence path is empty."
            )
        }

    if not os.path.exists(
        evidence_path
    ):

        return {
            "success": False,
            "message": (
                "Evidence path does not exist."
            )
        }

    metadata = {}

    # -----------------------------------------------------
    # Basic information
    # -----------------------------------------------------

    metadata["file_name"] = os.path.basename(
        os.path.normpath(
            evidence_path
        )
    )

    metadata["path_type"] = (
        "FOLDER"
        if os.path.isdir(evidence_path)
        else "FILE"
    )

    if os.path.isfile(
        evidence_path
    ):

        metadata["file_size_bytes"] = (
            os.path.getsize(
                evidence_path
            )
        )

        metadata["file_extension"] = (
            os.path.splitext(
                evidence_path
            )[1].lower()
        )

    else:

        total_size = 0
        file_count = 0

        for root, directories, files in os.walk(
            evidence_path
        ):

            for filename in files:

                file_count += 1

                full_path = os.path.join(
                    root,
                    filename
                )

                try:

                    total_size += os.path.getsize(
                        full_path
                    )

                except OSError:

                    pass

        metadata["file_size_bytes"] = total_size
        metadata["file_count"] = file_count

    # -----------------------------------------------------
    # Time information
    # -----------------------------------------------------

    try:

        metadata["creation_time"] = (
            datetime.fromtimestamp(
                os.path.getctime(
                    evidence_path
                )
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

    except Exception:

        metadata["creation_time"] = ""

    try:

        metadata["modification_time"] = (
            datetime.fromtimestamp(
                os.path.getmtime(
                    evidence_path
                )
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

    except Exception:

        metadata["modification_time"] = ""

    # -----------------------------------------------------
    # Image metadata / EXIF
    # -----------------------------------------------------

    extension = ""

    if os.path.isfile(
        evidence_path
    ):

        extension = (
            os.path.splitext(
                evidence_path
            )[1].lower()
        )

    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff",
        ".webp"
    ]

    if (
        os.path.isfile(evidence_path)
        and extension in image_extensions
        and PIL_AVAILABLE
    ):

        try:

            with Image.open(
                evidence_path
            ) as image:

                metadata["image_format"] = (
                    image.format
                )

                metadata["image_width"] = (
                    image.width
                )

                metadata["image_height"] = (
                    image.height
                )

                metadata["image_mode"] = (
                    image.mode
                )

                exif_data = image.getexif()

                exif = {}

                for key, value in exif_data.items():

                    exif[str(key)] = str(
                        value
                    )

                metadata["exif"] = exif

        except Exception as error:

            metadata["exif_error"] = str(
                error
            )

    elif extension in image_extensions:

        metadata["exif_status"] = (
            "Pillow not available"
        )

    # -----------------------------------------------------
    # Evidence type category
    # -----------------------------------------------------

    if extension in image_extensions:

        metadata["evidence_category"] = (
            "IMAGE"
        )

    elif extension in [
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
        ".3gp",
        ".wmv"
    ]:

        metadata["evidence_category"] = (
            "VIDEO"
        )

    elif extension in [
        ".pdf",
        ".doc",
        ".docx",
        ".txt"
    ]:

        metadata["evidence_category"] = (
            "DOCUMENT"
        )

    elif extension in [
        ".log",
        ".csv",
        ".json",
        ".xml"
    ]:

        metadata["evidence_category"] = (
            "LOG_DATA"
        )

    else:

        metadata["evidence_category"] = (
            "OTHER"
        )

    return {
        "success": True,
        "metadata": metadata
    }


# =========================================================
# METADATA CONSISTENCY
# =========================================================

def verify_metadata_consistency(
    evidence_uid,
    metadata
):

    record = get_evidence_by_uid(
        evidence_uid
    )

    if not record:

        return {
            "success": False,
            "message": (
                "Evidence UID not found."
            )
        }

    checks = []
    conflicts = []

    # -----------------------------------------------------
    # File name check
    # -----------------------------------------------------

    registered_name = record.get(
        "evidence_name",
        record.get(
            "file_name",
            ""
        )
    )

    current_name = metadata.get(
        "file_name",
        ""
    )

    if registered_name:

        name_match = (
            registered_name == current_name
        )

        checks.append(
            name_match
        )

        if not name_match:

            conflicts.append(
                "Evidence name differs from registration."
            )

    # -----------------------------------------------------
    # Size check
    # -----------------------------------------------------

    registered_size = record.get(
        "file_size_bytes"
    )

    current_size = metadata.get(
        "file_size_bytes"
    )

    if (
        registered_size is not None
        and current_size is not None
    ):

        size_match = (
            int(registered_size)
            == int(current_size)
        )

        checks.append(
            size_match
        )

        if not size_match:

            conflicts.append(
                "Evidence size differs from registration."
            )

    # -----------------------------------------------------
    # Modification indicator
    # -----------------------------------------------------

    modification_indicator = (
        "NONE"
    )

    if conflicts:

        modification_indicator = (
            "POSSIBLE_CHANGE"
        )

    if checks:

        consistency_score = (
            int(
                sum(checks)
                / len(checks)
                * 100
            )
        )

    else:

        consistency_score = 100

    return {

        "success": True,

        "evidence_uid": evidence_uid,

        "metadata_consistent": (
            len(conflicts) == 0
        ),

        "metadata_consistency_score": (
            consistency_score
        ),

        "modification_indicator": (
            modification_indicator
        ),

        "conflicts": conflicts,

        "checks_performed": len(
            checks
        )
    }


# =========================================================
# BLOCKCHAIN VERIFICATION
# =========================================================

def verify_blockchain_reference(
    evidence_uid,
    current_hash
):

    record = get_blockchain_record(
        evidence_uid
    )

    if not record:

        return {
            "success": False,
            "verified": False,
            "message": (
                "Blockchain reference not found."
            )
        }

    blockchain_hash = str(
        record.get(
            "sha256_hash",
            ""
        )
    ).strip().lower()

    hash_match = (
        blockchain_hash == str(
            current_hash
        ).lower()
    )

    return {

        "success": True,

        "verified": hash_match,

        "blockchain_status": record.get(
            "blockchain_status",
            "UNKNOWN"
        ),

        "reference_hash": blockchain_hash,

        "current_hash": current_hash,

        "hash_match": hash_match,

        "message": (
            "Blockchain reference verified."
            if hash_match
            else
            "Blockchain reference hash mismatch."
        )
    }


# =========================================================
# INTEGRITY SCORE
# =========================================================

def calculate_integrity_score(
    hash_result,
    metadata_result,
    blockchain_result
):

    hash_score = (
        100
        if hash_result.get(
            "hash_match",
            False
        )
        else 0
    )

    metadata_score = metadata_result.get(
        "metadata_consistency_score",
        0
    )

    blockchain_score = (
        100
        if blockchain_result.get(
            "verified",
            False
        )
        else 0
    )

    # -----------------------------------------------------
    # Integrity weighted model
    #
    # Hash       = 50%
    # Metadata   = 30%
    # Blockchain = 20%
    # -----------------------------------------------------

    integrity_score = (
        hash_score * 0.50
        + metadata_score * 0.30
        + blockchain_score * 0.20
    )

    return round(
        integrity_score,
        2
    )


# =========================================================
# DYNAMIC TRUST INFORMATION
# =========================================================

def calculate_dynamic_trust(
    evidence_uid,
    integrity_score,
    hash_result,
    metadata_result,
    blockchain_result,
    custody_history
):

    # -----------------------------------------------------
    # Individual signals
    # -----------------------------------------------------

    hash_signal = (
        100
        if hash_result.get(
            "hash_match",
            False
        )
        else 0
    )

    metadata_signal = metadata_result.get(
        "metadata_consistency_score",
        0
    )

    blockchain_signal = (
        100
        if blockchain_result.get(
            "verified",
            False
        )
        else 0
    )

    custody_signal = (
        100
        if len(custody_history) > 0
        else 50
    )

    # -----------------------------------------------------
    # Dynamic Trust Model
    #
    # Integrity       = 50%
    # Metadata        = 20%
    # Blockchain      = 15%
    # Chain of Custody= 15%
    # -----------------------------------------------------

    dynamic_trust_score = (
        integrity_score * 0.50
        + metadata_signal * 0.20
        + blockchain_signal * 0.15
        + custody_signal * 0.15
    )

    dynamic_trust_score = round(
        dynamic_trust_score,
        2
    )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    if dynamic_trust_score >= 80:

        status = "HIGH TRUST"

    elif dynamic_trust_score >= 60:

        status = "MEDIUM TRUST"

    else:

        status = "LOW TRUST"

    return {

        "evidence_uid": evidence_uid,

        "dynamic_trust_score": (
            dynamic_trust_score
        ),

        "trust_status": status,

        "signals": {

            "hash_integrity": hash_signal,

            "metadata_consistency": (
                metadata_signal
            ),

            "blockchain_verification": (
                blockchain_signal
            ),

            "chain_of_custody": (
                custody_signal
            ),

            "integrity_score": (
                integrity_score
            )
        },

        "decision_note": (
            "Dynamic trust information is a "
            "verification signal and not a final "
            "decision about evidence authenticity."
        )
    }


# =========================================================
# COMPLETE VERIFICATION
# =========================================================

def verify_evidence_by_uid(
    evidence_uid
):
    """
    Main entry point for Vedant's module.

    UID
      ↓
    Registration
      ↓
    Evidence
      ↓
    SHA-256
      ↓
    Metadata
      ↓
    Blockchain
      ↓
    Chain of Custody
      ↓
    Integrity Score
      ↓
    Dynamic Trust
    """

    # -----------------------------------------------------
    # Step 1 - Retrieve registration
    # -----------------------------------------------------

    registration = get_evidence_by_uid(
        evidence_uid
    )

    if not registration:

        return {
            "success": False,
            "message": (
                "Evidence UID not found in registry."
            )
        }

    evidence_path = get_registered_evidence_path(
        registration
    )

    if not evidence_path:

        return {
            "success": False,
            "message": (
                "Evidence associated with UID "
                "could not be located."
            )
        }

    # -----------------------------------------------------
    # Step 2 - Hash verification
    # -----------------------------------------------------

    hash_result = verify_hash(
        evidence_uid
    )

    if not hash_result.get(
        "success",
        False
    ):

        return hash_result

    # -----------------------------------------------------
    # Step 3 - Metadata
    # -----------------------------------------------------

    metadata_result = extract_metadata(
        evidence_path
    )

    if not metadata_result.get(
        "success",
        False
    ):

        return metadata_result

    metadata = metadata_result[
        "metadata"
    ]

    # -----------------------------------------------------
    # Step 4 - Metadata verification
    # -----------------------------------------------------

    metadata_verification = (
        verify_metadata_consistency(
            evidence_uid,
            metadata
        )
    )

    # -----------------------------------------------------
    # Step 5 - Blockchain
    # -----------------------------------------------------

    blockchain_result = (
        verify_blockchain_reference(
            evidence_uid,
            hash_result[
                "current_hash"
            ]
        )
    )

    # -----------------------------------------------------
    # Step 6 - Chain of Custody
    # -----------------------------------------------------

    custody_history = get_chain_of_custody(
        evidence_uid
    )

    # -----------------------------------------------------
    # Step 7 - Integrity Score
    # -----------------------------------------------------

    integrity_score = calculate_integrity_score(
        hash_result,
        metadata_verification,
        blockchain_result
    )

    # -----------------------------------------------------
    # Step 8 - Dynamic Trust
    # -----------------------------------------------------

    dynamic_trust = calculate_dynamic_trust(
        evidence_uid,
        integrity_score,
        hash_result,
        metadata_verification,
        blockchain_result,
        custody_history
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "success": True,

        "verification_timestamp": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),

        "evidence_uid": evidence_uid,

        "registration": registration,

        "evidence_path": evidence_path,

        "hash_verification": hash_result,

        "metadata": metadata,

        "metadata_verification": (
            metadata_verification
        ),

        "blockchain_verification": (
            blockchain_result
        ),

        "chain_of_custody": (
            custody_history
        ),

        "integrity_score": integrity_score,

        "dynamic_trust": dynamic_trust
    }


# =========================================================
# VERIFICATION HISTORY
# =========================================================

def save_verification_history(
    verification_result
):

    history = load_json_file(
        VERIFICATION_HISTORY_FILE,
        []
    )

    if not isinstance(
        history,
        list
    ):

        history = []

    history.append(
        verification_result
    )

    save_json_file(
        VERIFICATION_HISTORY_FILE,
        history
    )

    return True


def get_verification_history(
    evidence_uid=None
):

    history = load_json_file(
        VERIFICATION_HISTORY_FILE,
        []
    )

    if not isinstance(
        history,
        list
    ):

        return []

    if not evidence_uid:

        return history

    return [
        record
        for record in history
        if str(
            record.get(
                "evidence_uid",
                ""
            )
        ).strip()
        ==
        str(
            evidence_uid
        ).strip()
    ]


# =========================================================
# RE-HASH VERIFICATION
# =========================================================

def rehash_verify(
    evidence_uid
):

    result = verify_evidence_by_uid(
        evidence_uid
    )

    if not result.get(
        "success",
        False
    ):

        return result

    save_verification_history(
        result
    )

    return result