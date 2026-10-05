import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")

SECURE_STORAGE_DIR = os.path.join(
    BASE_DIR,
    "secure_storage"
)

ANDROID_BACKUP_DIR = os.path.join(
    BASE_DIR,
    "android_backups"
)

PEN_DRIVE_BACKUP_DIR = os.path.join(
    BASE_DIR,
    "pen_drive_backups"
)

REGISTRY_FILE = os.path.join(
    BASE_DIR,
    "evidence_registry.json"
)

CHAIN_OF_CUSTODY_FILE = os.path.join(
    BASE_DIR,
    "chain_of_custody.json"
)

BLOCKCHAIN_RECORD_FILE = os.path.join(
    BASE_DIR,
    "blockchain_records.json"
)


def create_evidence_folders():
    """
    Create all required project storage folders.
    """

    folders = [
        EVIDENCE_DIR,
        SECURE_STORAGE_DIR,
        ANDROID_BACKUP_DIR,
        PEN_DRIVE_BACKUP_DIR
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    return {
        "evidence": EVIDENCE_DIR,
        "secure_storage": SECURE_STORAGE_DIR,
        "android_backups": ANDROID_BACKUP_DIR,
        "pen_drive_backups": PEN_DRIVE_BACKUP_DIR
    }


def get_secure_storage_path(evidence_uid):
    """
    Return the secure storage directory for a specific Evidence UID.
    """

    if not evidence_uid:
        raise ValueError("Evidence UID is required.")

    path = os.path.join(
        SECURE_STORAGE_DIR,
        evidence_uid
    )

    os.makedirs(path, exist_ok=True)

    return path


def get_android_backup_path():
    """
    Return the Android backup directory.
    """

    os.makedirs(ANDROID_BACKUP_DIR, exist_ok=True)

    return ANDROID_BACKUP_DIR


def get_pen_drive_backup_path():
    """
    Return the Pen Drive backup directory.
    """

    os.makedirs(PEN_DRIVE_BACKUP_DIR, exist_ok=True)

    return PEN_DRIVE_BACKUP_DIR