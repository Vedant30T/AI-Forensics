import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPORT_DIR = os.path.join(BASE_DIR, "report")
os.makedirs(REPORT_DIR, exist_ok=True)


def generate_integrity_report(verification_result):
    """
    Generate a final JSON integrity verification report.

    verification_result should be the dictionary returned by
    integrity_engine.verify_evidence_by_uid()
    """

    if not verification_result:
        raise ValueError("No verification result provided.")

    evidence_uid = verification_result.get(
        "evidence_uid",
        verification_result.get("uid", "UNKNOWN")
    )

    report = {
        "report_title": "Evidence Integrity & Dynamic Trust Report",

        "report_generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "evidence_uid": evidence_uid,

        "sha256_hash": verification_result.get(
            "current_hash",
            verification_result.get("sha256_hash", "")
        ),

        "hash_verification": verification_result.get(
            "hash_verification",
            {}
        ),

        "metadata": verification_result.get(
            "metadata",
            {}
        ),

        "metadata_verification": verification_result.get(
            "metadata_verification",
            {}
        ),

        "integrity_score": verification_result.get(
            "integrity_score",
            {}
        ),

        "dynamic_trust": verification_result.get(
            "dynamic_trust",
            {}
        ),

        "blockchain_verification": verification_result.get(
            "blockchain_verification",
            {}
        ),

        "chain_of_custody": verification_result.get(
            "chain_of_custody",
            []
        ),

        "verification_status": verification_result.get(
            "verification_status",
            ""
        ),

        "methodology_note": (
            "The integrity and dynamic trust results are verification "
            "signals and do not represent the final authenticity or "
            "legal decision regarding the evidence."
        )
    }

    return report


def save_integrity_report(verification_result):
    """
    Save the integrity report as a JSON file.
    """

    report = generate_integrity_report(verification_result)

    evidence_uid = report["evidence_uid"]

    safe_uid = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in str(evidence_uid)
    )

    filename = f"Integrity_Report_{safe_uid}.json"
    report_path = os.path.join(REPORT_DIR, filename)

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return report_path


def get_report_path(evidence_uid):
    """
    Return the existing report path for an Evidence UID.
    """

    safe_uid = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in str(evidence_uid)
    )

    path = os.path.join(
        REPORT_DIR,
        f"Integrity_Report_{safe_uid}.json"
    )

    if os.path.exists(path):
        return path

    return None


def read_integrity_report(evidence_uid):
    """
    Read an existing integrity report.
    """

    report_path = get_report_path(evidence_uid)

    if not report_path:
        return None

    with open(report_path, "r", encoding="utf-8") as file:
        return json.load(file)


def export_report_text(verification_result):
    """
    Create a readable text version of the integrity report.
    """

    report = generate_integrity_report(verification_result)

    lines = []

    lines.append("=" * 70)
    lines.append("EVIDENCE INTEGRITY & DYNAMIC TRUST REPORT")
    lines.append("=" * 70)

    lines.append(
        f"Report Generated: {report['report_generated_at']}"
    )

    lines.append(
        f"Evidence UID: {report['evidence_uid']}"
    )

    lines.append("-" * 70)
    lines.append("SHA-256 HASH")
    lines.append("-" * 70)

    lines.append(str(report["sha256_hash"]))

    lines.append("-" * 70)
    lines.append("HASH VERIFICATION")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["hash_verification"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("METADATA")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["metadata"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("METADATA VERIFICATION")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["metadata_verification"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("INTEGRITY SCORE")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["integrity_score"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("DYNAMIC TRUST")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["dynamic_trust"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("BLOCKCHAIN VERIFICATION")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["blockchain_verification"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("CHAIN OF CUSTODY")
    lines.append("-" * 70)

    lines.append(
        json.dumps(
            report["chain_of_custody"],
            indent=4,
            default=str
        )
    )

    lines.append("-" * 70)
    lines.append("VERIFICATION STATUS")
    lines.append("-" * 70)

    lines.append(str(report["verification_status"]))

    lines.append("-" * 70)
    lines.append("METHODOLOGY NOTE")
    lines.append("-" * 70)

    lines.append(report["methodology_note"])

    lines.append("=" * 70)

    return "\n".join(lines)


def save_text_report(verification_result):
    """
    Save readable text report.
    """

    report = generate_integrity_report(verification_result)

    evidence_uid = report["evidence_uid"]

    safe_uid = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in str(evidence_uid)
    )

    filename = f"Integrity_Report_{safe_uid}.txt"
    report_path = os.path.join(REPORT_DIR, filename)

    text_report = export_report_text(verification_result)

    with open(report_path, "w", encoding="utf-8") as file:
        file.write(text_report)

    return report_path