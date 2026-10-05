import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

ACCESS_LOG_FILE = os.path.join(
    BASE_DIR,
    "evidence_access_log.json"
)


def load_access_logs():
    """
    Load evidence access logs.
    """

    if not os.path.exists(ACCESS_LOG_FILE):
        return []

    try:
        with open(
            ACCESS_LOG_FILE,
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


def save_access_logs(records):
    """
    Save evidence access logs.
    """

    with open(
        ACCESS_LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )


def log_evidence_access(
    evidence_uid,
    user,
    action,
    authorization_status="AUTHORIZED",
    details=""
):
    """
    Record access to protected evidence.
    """

    if not evidence_uid:
        raise ValueError(
            "Evidence UID is required."
        )

    if not user:
        raise ValueError(
            "User / investigator is required."
        )

    records = load_access_logs()

    record = {
        "evidence_uid": evidence_uid,
        "user": user,
        "action": action,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "authorization_status": authorization_status,
        "details": details
    }

    records.append(record)

    save_access_logs(records)

    return record


def get_evidence_access_history(evidence_uid):
    """
    Return access history for an Evidence UID.
    """

    records = load_access_logs()

    return [
        record
        for record in records
        if record.get("evidence_uid") == evidence_uid
    ]


def is_authorized(status):
    """
    Check authorization status.
    """

    return str(status).upper() == "AUTHORIZED"