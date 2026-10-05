from datetime import datetime

from evidence.chain_of_custody import add_custody_event
from evidence.security import log_evidence_access


def record_collection(
    evidence_uid,
    collector,
    location,
    details=""
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE COLLECTED",
        person=collector,
        location=location,
        reason="Digital evidence collection",
        previous_handler="",
        new_handler=collector,
        access_details=details,
        authorization_status="AUTHORIZED"
    )


def record_registration(
    evidence_uid,
    investigator,
    location,
    details=""
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE REGISTERED",
        person=investigator,
        location=location,
        reason="Evidence registration",
        previous_handler=investigator,
        new_handler=investigator,
        access_details=details,
        authorization_status="AUTHORIZED"
    )


def record_storage(
    evidence_uid,
    investigator,
    storage_reference
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE STORED",
        person=investigator,
        location=storage_reference,
        reason="Secure evidence storage",
        previous_handler=investigator,
        new_handler=investigator,
        access_details=(
            "Original/master evidence stored securely."
        ),
        authorization_status="AUTHORIZED"
    )


def record_transfer(
    evidence_uid,
    from_person,
    to_person,
    location,
    reason
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE TRANSFERRED",
        person=to_person,
        location=location,
        reason=reason,
        previous_handler=from_person,
        new_handler=to_person,
        access_details="Evidence custody transferred.",
        authorization_status="AUTHORIZED"
    )


def record_access(
    evidence_uid,
    investigator,
    location,
    reason
):
    event = add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE ACCESSED",
        person=investigator,
        location=location,
        reason=reason,
        previous_handler=investigator,
        new_handler=investigator,
        access_details="Evidence accessed in read-only mode.",
        authorization_status="AUTHORIZED"
    )

    log_evidence_access(
        evidence_uid=evidence_uid,
        user=investigator,
        action="ACCESS",
        authorization_status="AUTHORIZED",
        details=reason
    )

    return event


def record_analysis(
    evidence_uid,
    investigator,
    location,
    details=""
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="EVIDENCE ANALYSED",
        person=investigator,
        location=location,
        reason="Digital evidence analysis",
        previous_handler=investigator,
        new_handler=investigator,
        access_details=details,
        authorization_status="AUTHORIZED"
    )


def record_ai_analysis(
    evidence_uid,
    investigator,
    location,
    details=""
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="AI ANALYSIS",
        person=investigator,
        location=location,
        reason="AI-based evidence analysis",
        previous_handler=investigator,
        new_handler=investigator,
        access_details=details,
        authorization_status="AUTHORIZED"
    )


def record_report_generation(
    evidence_uid,
    investigator,
    location,
    report_reference=""
):
    return add_custody_event(
        evidence_uid=evidence_uid,
        action="REPORT GENERATED",
        person=investigator,
        location=location,
        reason="Digital evidence report generation",
        previous_handler=investigator,
        new_handler=investigator,
        access_details=(
            f"Report reference: {report_reference}"
        ),
        authorization_status="AUTHORIZED"
    )


def get_lifecycle_timestamp():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )