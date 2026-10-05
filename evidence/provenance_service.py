import os
from datetime import datetime

from evidence.evidence_registry import register_evidence
from evidence.chain_of_custody import add_custody_event, get_custody_history
from evidence.blockchain_registry import register_blockchain_reference, get_blockchain_record


def create_provenance_record(
    evidence_file,
    case_id,
    evidence_type,
    description,
    source,
    collector,
    collection_location,
    acquisition_method
):
    """
    Complete Evidence Security & Provenance workflow:

    1. Evidence Registration
    2. Secure Storage
    3. Chain of Custody
    4. Blockchain Reference Registration
    """

    if not evidence_file:
        raise ValueError("Evidence file is required.")

    if not os.path.exists(evidence_file):
        raise FileNotFoundError("Evidence file not found.")

    if not case_id:
        raise ValueError("Case ID is required.")

    if not collector:
        raise ValueError("Collector / Investigator is required.")

    collection_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ---------------------------------------------------------
    # STEP 1: REGISTER EVIDENCE + SECURE STORAGE
    # ---------------------------------------------------------

    registration = register_evidence(
        evidence_file=evidence_file,
        case_id=case_id,
        evidence_type=evidence_type,
        description=description,
        source=source,
        collector=collector,
        collection_datetime=collection_datetime,
        collection_location=collection_location,
        acquisition_method=acquisition_method
    )

    evidence_uid = registration["evidence_uid"]
    evidence_hash = registration["sha256_hash"]
    storage_reference = registration["storage_reference"]

    # ---------------------------------------------------------
    # STEP 2: INITIAL CHAIN OF CUSTODY EVENT
    # ---------------------------------------------------------

    add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE COLLECTED",
        person=collector,
        location=collection_location,
        reason="Initial evidence collection",
        previous_handler="",
        new_handler=collector,
        access_details="Evidence collected and submitted for registration.",
        authorization_status="AUTHORIZED"
    )

    add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE REGISTERED",
        person=collector,
        location=storage_reference,
        reason="Evidence registration",
        previous_handler=collector,
        new_handler=collector,
        access_details="Evidence UID and SHA-256 hash generated.",
        authorization_status="AUTHORIZED"
    )

    add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE STORED",
        person=collector,
        location=storage_reference,
        reason="Secure evidence storage",
        previous_handler=collector,
        new_handler=collector,
        access_details="Original/master evidence copy stored in secure storage.",
        authorization_status="AUTHORIZED"
    )

    # ---------------------------------------------------------
    # STEP 3: BLOCKCHAIN REFERENCE REGISTRATION
    # ---------------------------------------------------------

    blockchain_record = register_blockchain_reference(
        evidence_uid=evidence_uid,
        case_id=case_id,
        evidence_hash=evidence_hash,
        storage_reference=storage_reference,
        collector=collector,
        provenance="Evidence collected, registered and securely stored."
    )

    # ---------------------------------------------------------
    # STEP 4: FINAL PROVENANCE RESULT
    # ---------------------------------------------------------

    custody_history = get_custody_history(evidence_uid)

    return {
        "evidence_uid": evidence_uid,
        "registration": registration,
        "storage_reference": storage_reference,
        "chain_of_custody": custody_history,
        "blockchain": blockchain_record,
        "provenance_status": "COMPLETE"
    }


def get_provenance_record(evidence_uid):
    """
    Retrieve complete provenance information for an Evidence UID.
    """

    if not evidence_uid:
        return None

    blockchain_record = get_blockchain_record(evidence_uid)
    custody_history = get_custody_history(evidence_uid)

    return {
        "evidence_uid": evidence_uid,
        "chain_of_custody": custody_history,
        "blockchain": blockchain_record
    }