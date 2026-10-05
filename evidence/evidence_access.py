import os
from datetime import datetime

from evidence.security import log_evidence_access


def access_evidence(
    evidence_uid,
    evidence_path,
    user,
    action="VIEW"
):
    """
    Controlled access to registered evidence.

    Evidence remains in secure storage.
    This function does not modify the evidence file.
    """

    if not evidence_uid:
        raise ValueError("Evidence UID is required.")

    if not evidence_path:
        raise ValueError("Evidence path is required.")

    if not user:
        raise ValueError("User / investigator is required.")

    if not os.path.exists(evidence_path):
        raise FileNotFoundError(
            "Secure evidence file not found."
        )

    if not os.access(evidence_path, os.R_OK):
        log_evidence_access(
            evidence_uid=evidence_uid,
            user=user,
            action=action,
            authorization_status="DENIED",
            details="Evidence file is not readable."
        )

        return {
            "success": False,
            "authorization_status": "DENIED",
            "message": "Access denied."
        }

    access_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_evidence_access(
        evidence_uid=evidence_uid,
        user=user,
        action=action,
        authorization_status="AUTHORIZED",
        details=(
            f"Evidence accessed in read-only mode. "
            f"Path: {evidence_path}"
        )
    )

    return {
        "success": True,
        "evidence_uid": evidence_uid,
        "evidence_path": os.path.abspath(
            evidence_path
        ),
        "user": user,
        "action": action,
        "authorization_status": "AUTHORIZED",
        "access_time": access_time,
        "read_only": True
    }


def check_evidence_access(
    evidence_path
):
    """
    Check whether protected evidence can be read.
    """

    if not evidence_path:
        return False

    if not os.path.exists(evidence_path):
        return False

    return os.access(
        evidence_path,
        os.R_OK
    )


def get_read_only_status():
    """
    Return the intended evidence handling mode.
    """

    return {
        "mode": "READ_ONLY",
        "original_modified": False,
        "evidence_protected": True
    }