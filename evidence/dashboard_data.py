import os
from datetime import datetime

from evidence.registry_search import get_all_registered_evidence
from evidence.chain_of_custody import load_chain_of_custody
from evidence.blockchain_registry import load_blockchain_records
from evidence.security import load_access_logs
from evidence.audit_logger import load_audit_logs


def get_dashboard_summary():
    """
    Prepare summary information for the main GUI dashboard.
    """

    evidence_records = get_all_registered_evidence()
    custody_records = load_chain_of_custody()
    blockchain_records = load_blockchain_records()
    access_records = load_access_logs()
    audit_records = load_audit_logs()

    cases = set()

    for record in evidence_records:
        case_id = record.get("case_id")

        if case_id:
            cases.add(case_id)

    registered_count = len(evidence_records)

    secure_storage_count = sum(
        1
        for record in evidence_records
        if record.get("storage_reference")
    )

    blockchain_count = sum(
        1
        for record in blockchain_records
        if record.get("blockchain_status")
        == "REFERENCE_CREATED"
    )

    authorized_access_count = sum(
        1
        for record in access_records
        if record.get("authorization_status")
        == "AUTHORIZED"
    )

    return {
        "total_cases": len(cases),
        "total_evidence": registered_count,
        "secure_storage_records": secure_storage_count,
        "custody_events": len(custody_records),
        "blockchain_records": blockchain_count,
        "authorized_accesses": authorized_access_count,
        "audit_events": len(audit_records),
        "last_updated": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


def get_recent_evidence(limit=10):
    """
    Return the most recently registered evidence.
    """

    records = get_all_registered_evidence()

    return records[-limit:][::-1]


def get_evidence_status(evidence_uid):
    """
    Return a compact status object for an Evidence UID.
    """

    if not evidence_uid:
        return None

    evidence_records = get_all_registered_evidence()

    evidence = None

    for record in evidence_records:

        if record.get("evidence_uid") == evidence_uid:
            evidence = record
            break

    if not evidence:
        return None

    blockchain_records = load_blockchain_records()

    blockchain = None

    for record in blockchain_records:

        if record.get("evidence_uid") == evidence_uid:
            blockchain = record
            break

    custody_records = load_chain_of_custody()

    custody = [
        record
        for record in custody_records
        if record.get("evidence_uid") == evidence_uid
    ]

    access_records = load_access_logs()

    accesses = [
        record
        for record in access_records
        if record.get("evidence_uid") == evidence_uid
    ]

    return {
        "evidence_uid": evidence_uid,
        "registration_status": evidence.get(
            "registration_status",
            "UNKNOWN"
        ),
        "storage_reference": evidence.get(
            "storage_reference",
            ""
        ),
        "sha256_hash": evidence.get(
            "sha256_hash",
            ""
        ),
        "custody_event_count": len(custody),
        "access_event_count": len(accesses),
        "blockchain_registered": (
            blockchain is not None
        ),
        "blockchain_status": (
            blockchain.get(
                "blockchain_status",
                "NOT REGISTERED"
            )
            if blockchain
            else "NOT REGISTERED"
        )
    }