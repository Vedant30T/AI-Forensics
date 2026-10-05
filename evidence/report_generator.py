import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REPORTS_DIR = os.path.join(
    BASE_DIR,
    "reports"
)


def create_reports_folder():
    """
    Create the reports directory.
    """

    os.makedirs(
        REPORTS_DIR,
        exist_ok=True
    )

    return REPORTS_DIR


def generate_provenance_report(provenance_record):
    """
    Generate a JSON provenance report containing:

    - Evidence UID
    - Registration details
    - Secure storage reference
    - Chain of custody
    - Blockchain registration
    """

    if not provenance_record:
        raise ValueError(
            "Provenance record is required."
        )

    create_reports_folder()

    evidence_uid = provenance_record.get(
        "evidence_uid",
        "UNKNOWN"
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_name = (
        f"{evidence_uid}_provenance_{timestamp}.json"
    )

    report_path = os.path.join(
        REPORTS_DIR,
        report_name
    )

    report = {
        "report_title":
            "Digital Evidence Security & Provenance Report",

        "generated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "evidence_uid":
            evidence_uid,

        "registration":
            provenance_record.get(
                "registration",
                {}
            ),

        "secure_storage_reference":
            provenance_record.get(
                "storage_reference",
                ""
            ),

        "chain_of_custody":
            provenance_record.get(
                "chain_of_custody",
                []
            ),

        "blockchain_registration":
            provenance_record.get(
                "blockchain",
                {}
            ),

        "provenance_status":
            provenance_record.get(
                "provenance_status",
                "UNKNOWN"
            )
    }

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    return {
        "success": True,
        "report_path": os.path.abspath(
            report_path
        ),
        "report": report
    }


def load_provenance_report(report_path):
    """
    Load an existing provenance report.
    """

    if not os.path.exists(report_path):
        raise FileNotFoundError(
            "Provenance report not found."
        )

    with open(
        report_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)