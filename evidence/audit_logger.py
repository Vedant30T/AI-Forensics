import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

AUDIT_LOG_FILE = os.path.join(
    BASE_DIR,
    "audit_log.json"
)


def load_audit_logs():
    """
    Load complete system audit history.
    """

    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    try:
        with open(
            AUDIT_LOG_FILE,
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


def save_audit_logs(records):
    """
    Save audit records.
    """

    with open(
        AUDIT_LOG_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4,
            ensure_ascii=False
        )


def log_action(
    action,
    user,
    evidence_uid="",
    case_id="",
    details="",
    status="SUCCESS"
):
    """
    Create an audit log entry for an operation
    performed in the evidence system.
    """

    records = load_audit_logs()

    record = {
        "audit_id": (
            f"AUD-{len(records) + 1:06d}"
        ),
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "action": action,
        "user": user,
        "evidence_uid": evidence_uid,
        "case_id": case_id,
        "details": details,
        "status": status
    }

    records.append(record)

    save_audit_logs(records)

    return record


def get_evidence_audit_history(evidence_uid):
    """
    Get audit history for a specific Evidence UID.
    """

    records = load_audit_logs()

    return [
        record
        for record in records
        if record.get("evidence_uid") == evidence_uid
    ]


def get_case_audit_history(case_id):
    """
    Get audit history for a specific Case ID.
    """

    records = load_audit_logs()

    return [
        record
        for record in records
        if record.get("case_id") == case_id
    ]