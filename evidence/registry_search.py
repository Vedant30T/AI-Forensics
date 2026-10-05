import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REGISTRY_FILE = os.path.join(
    BASE_DIR,
    "evidence_registry.json"
)


def load_registry():
    """
    Load all registered evidence records.
    """

    if not os.path.exists(REGISTRY_FILE):
        return []

    try:
        with open(
            REGISTRY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    return []


def find_by_uid(evidence_uid):
    """
    Find evidence using Evidence UID.
    """

    if not evidence_uid:
        return None

    records = load_registry()

    for record in records:

        if record.get("evidence_uid") == evidence_uid:
            return record

    return None


def find_by_case_id(case_id):
    """
    Find all evidence belonging to a Case ID.
    """

    if not case_id:
        return []

    records = load_registry()

    return [
        record
        for record in records
        if record.get("case_id") == case_id
    ]


def find_by_hash(sha256_hash):
    """
    Find evidence using SHA-256 hash.
    """

    if not sha256_hash:
        return None

    records = load_registry()

    for record in records:

        if (
            record.get("sha256_hash", "").lower()
            == sha256_hash.lower()
        ):
            return record

    return None


def get_all_registered_evidence():
    """
    Return all registered evidence records.
    """

    return load_registry()


def evidence_exists(evidence_uid):
    """
    Check whether an Evidence UID exists.
    """

    return find_by_uid(evidence_uid) is not None