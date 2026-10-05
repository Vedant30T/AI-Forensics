import os
import json
import hashlib
import shutil
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REGISTRY_FILE = os.path.join(
    BASE_DIR,
    "evidence_registry.json"
)

SECURE_STORAGE_DIR = os.path.join(
    BASE_DIR,
    "secure_storage"
)


# =========================================================
# LOAD REGISTRY
# =========================================================

def load_registry():

    if not os.path.exists(REGISTRY_FILE):
        return []

    try:
        with open(
            REGISTRY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data if isinstance(data, list) else []

    except Exception:
        return []


# =========================================================
# SAVE REGISTRY
# =========================================================

def save_registry(records):

    with open(
        REGISTRY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# FILE HASH
# =========================================================

def calculate_file_sha256(file_path):

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

            sha256.update(chunk)

    return sha256.hexdigest()


# =========================================================
# FOLDER HASH
# =========================================================

def calculate_folder_sha256(folder_path):
    """
    Creates a deterministic SHA-256 hash for the
    complete evidence folder.

    File path + file content are included.
    """

    sha256 = hashlib.sha256()

    all_files = []

    for root, dirs, files in os.walk(
        folder_path
    ):

        dirs.sort()
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
        key=lambda x: x[0]
    )

    for relative_path, full_path in all_files:

        # Include relative path
        sha256.update(
            relative_path.replace(
                "\\",
                "/"
            ).encode(
                "utf-8"
            )
        )

        # Include file content
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
# CALCULATE EVIDENCE HASH
# =========================================================

def calculate_evidence_sha256(
    evidence_path
):

    if os.path.isfile(
        evidence_path
    ):

        return calculate_file_sha256(
            evidence_path
        )

    if os.path.isdir(
        evidence_path
    ):

        return calculate_folder_sha256(
            evidence_path
        )

    raise FileNotFoundError(
        "Evidence path does not exist."
    )


# =========================================================
# GENERATE EVIDENCE UID
# =========================================================

def generate_evidence_uid(
    case_id,
    records
):

    case_clean = str(
        case_id
    ).strip()

    if not case_clean:
        case_clean = "CASE"

    case_clean = (
        case_clean
        .replace(" ", "")
        .replace("/", "-")
        .replace("\\", "-")
    )

    counter = 1

    while True:

        uid = (
            f"{case_clean}-EVD-{counter:04d}"
        )

        exists = any(
            record.get(
                "evidence_uid"
            ) == uid
            for record in records
        )

        if not exists:
            return uid

        counter += 1


# =========================================================
# COPY EVIDENCE TO SECURE STORAGE
# =========================================================

def create_secure_storage(
    evidence_uid,
    source_path
):

    storage_folder = os.path.join(
        SECURE_STORAGE_DIR,
        evidence_uid
    )

    os.makedirs(
        storage_folder,
        exist_ok=True
    )

    evidence_name = os.path.basename(
        os.path.normpath(
            source_path
        )
    )

    destination = os.path.join(
        storage_folder,
        evidence_name
    )

    # -----------------------------------------------------
    # Folder evidence
    # -----------------------------------------------------

    if os.path.isdir(
        source_path
    ):

        if os.path.exists(
            destination
        ):

            destination = os.path.join(
                storage_folder,
                evidence_name + "_master"
            )

        shutil.copytree(
            source_path,
            destination
        )

    # -----------------------------------------------------
    # Single-file evidence
    # -----------------------------------------------------

    elif os.path.isfile(
        source_path
    ):

        if os.path.exists(
            destination
        ):

            name, extension = os.path.splitext(
                evidence_name
            )

            destination = os.path.join(
                storage_folder,
                f"{name}_master{extension}"
            )

        shutil.copy2(
            source_path,
            destination
        )

    else:

        raise FileNotFoundError(
            "Evidence source does not exist."
        )

    return (
        storage_folder,
        destination
    )


# =========================================================
# COUNT EVIDENCE FILES
# =========================================================

def count_evidence_files(
    evidence_path
):

    if os.path.isfile(
        evidence_path
    ):

        return 1

    count = 0

    for root, dirs, files in os.walk(
        evidence_path
    ):

        count += len(
            files
        )

    return count


# =========================================================
# CALCULATE EVIDENCE SIZE
# =========================================================

def calculate_evidence_size(
    evidence_path
):

    if os.path.isfile(
        evidence_path
    ):

        return os.path.getsize(
            evidence_path
        )

    total_size = 0

    for root, dirs, files in os.walk(
        evidence_path
    ):

        for filename in files:

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

    return total_size


# =========================================================
# REGISTER EVIDENCE
# =========================================================

def register_evidence(
    case_id,
    evidence_type,
    description,
    source,
    collector,
    collection_location,
    acquisition_method,
    evidence_file,
    collection_datetime=None,
    collection_date_time=None,
    collection_date=None,
    **kwargs
):

    # -----------------------------------------------------
    # Validate path
    # -----------------------------------------------------

    if not evidence_file:

        return {
            "success": False,
            "message": (
                "Please select an evidence file or folder."
            )
        }

    if not os.path.exists(
        evidence_file
    ):

        return {
            "success": False,
            "message": (
                "Selected evidence path does not exist."
            )
        }

    if not (
        os.path.isfile(evidence_file)
        or os.path.isdir(evidence_file)
    ):

        return {
            "success": False,
            "message": (
                "Selected evidence is not a valid "
                "file or folder."
            )
        }

    # -----------------------------------------------------
    # Registry
    # -----------------------------------------------------

    records = load_registry()

    # -----------------------------------------------------
    # Evidence UID
    # -----------------------------------------------------

    evidence_uid = generate_evidence_uid(
        case_id,
        records
    )

    # -----------------------------------------------------
    # Evidence type
    # -----------------------------------------------------

    if os.path.isdir(
        evidence_file
    ):

        evidence_structure = "FOLDER"

    else:

        evidence_structure = "FILE"

    # -----------------------------------------------------
    # Hash
    # -----------------------------------------------------

    evidence_hash = calculate_evidence_sha256(
        evidence_file
    )

    # -----------------------------------------------------
    # Size
    # -----------------------------------------------------

    evidence_size = calculate_evidence_size(
        evidence_file
    )

    # -----------------------------------------------------
    # File count
    # -----------------------------------------------------

    evidence_file_count = count_evidence_files(
        evidence_file
    )

    # -----------------------------------------------------
    # Name
    # -----------------------------------------------------

    evidence_name = os.path.basename(
        os.path.normpath(
            evidence_file
        )
    )

    # -----------------------------------------------------
    # Collection datetime
    # -----------------------------------------------------

    final_datetime = (
        collection_datetime
        or collection_date_time
        or collection_date
    )

    if not final_datetime:

        final_datetime = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    # -----------------------------------------------------
    # Secure storage
    # -----------------------------------------------------

    storage_folder, master_path = (
        create_secure_storage(
            evidence_uid,
            evidence_file
        )
    )

    # -----------------------------------------------------
    # Relative storage reference
    # -----------------------------------------------------

    storage_reference = os.path.relpath(
        master_path,
        BASE_DIR
    )

    # -----------------------------------------------------
    # Registration record
    # -----------------------------------------------------

    record = {

        "case_id": str(
            case_id
        ).strip(),

        "evidence_uid": evidence_uid,

        "evidence_type": str(
            evidence_type
        ).strip(),

        "description": str(
            description
        ).strip(),

        "source": str(
            source
        ).strip(),

        "collector": str(
            collector
        ).strip(),

        "collection_datetime": (
            final_datetime
        ),

        "collection_location": str(
            collection_location
        ).strip(),

        "acquisition_method": str(
            acquisition_method
        ).strip(),

        "evidence_name": evidence_name,

        "evidence_structure": evidence_structure,

        "file_count": evidence_file_count,

        "file_size_bytes": evidence_size,

        "sha256_hash": evidence_hash,

        "original_evidence_path": os.path.abspath(
            evidence_file
        ),

        "storage_reference": storage_reference,

        "secure_storage_folder": os.path.relpath(
            storage_folder,
            BASE_DIR
        ),

        "master_evidence": True,

        "registration_status": "REGISTERED",

        "provenance_status": "INITIALIZED",

        "registration_timestamp": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    }

    records.append(
        record
    )

    save_registry(
        records
    )

    return {

        "success": True,

        "message": (
            "Evidence registered successfully."
        ),

        "record": record,

        "evidence_uid": evidence_uid,

        "sha256_hash": evidence_hash,

        "storage_reference": storage_reference
    }


# =========================================================
# GET EVIDENCE BY UID
# =========================================================

def get_evidence_by_uid(
    evidence_uid
):

    records = load_registry()

    for record in records:

        if record.get(
            "evidence_uid"
        ) == evidence_uid:

            return record

    return None


# =========================================================
# GET ALL EVIDENCE
# =========================================================

def get_all_evidence():

    return load_registry()


# =========================================================
# VERIFY EVIDENCE
# =========================================================

def verify_evidence(
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

    master_path = os.path.join(
        BASE_DIR,
        record[
            "storage_reference"
        ]
    )

    if not os.path.exists(
        master_path
    ):

        return {
            "success": False,
            "message": (
                "Master evidence not found."
            )
        }

    current_hash = calculate_evidence_sha256(
        master_path
    )

    original_hash = record.get(
        "sha256_hash"
    )

    return {

        "success": True,

        "evidence_uid": evidence_uid,

        "original_hash": original_hash,

        "current_hash": current_hash,

        "integrity_verified": (
            current_hash == original_hash
        )
    }