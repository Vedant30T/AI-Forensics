import os
import json
from datetime import datetime


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BLOCKCHAIN_FILE = os.path.join(
    BASE_DIR,
    "blockchain_records.json"
)


# ============================================================
# LOAD BLOCKCHAIN RECORDS
# ============================================================

def load_blockchain_records():

    if not os.path.exists(
        BLOCKCHAIN_FILE
    ):

        return []

    try:

        with open(
            BLOCKCHAIN_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


# ============================================================
# SAVE BLOCKCHAIN RECORDS
# ============================================================

def save_blockchain_records(
    records
):

    with open(
        BLOCKCHAIN_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4
        )


# ============================================================
# CREATE BLOCKCHAIN REFERENCE
# ============================================================

def register_blockchain_reference(
    evidence_uid,
    case_id,
    evidence_hash,
    storage_reference,
    collector,
    provenance
):

    if not evidence_uid:

        raise ValueError(
            "Evidence UID is required."
        )

    if not evidence_hash:

        raise ValueError(
            "Evidence hash is required."
        )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # --------------------------------------------------------
    # Blockchain Reference Record
    # --------------------------------------------------------

    record = {

        "evidence_uid":
            evidence_uid,

        "case_id":
            case_id,

        "sha256_hash":
            evidence_hash,

        "registration_timestamp":
            timestamp,

        "storage_reference":
            storage_reference,

        "collector":
            collector,

        "provenance":
            provenance,

        "blockchain_status":
            "REFERENCE_CREATED"

    }

    records = load_blockchain_records()

    records.append(
        record
    )

    save_blockchain_records(
        records
    )

    return record


# ============================================================
# GET BLOCKCHAIN RECORD
# ============================================================

def get_blockchain_record(
    evidence_uid
):

    records = load_blockchain_records()

    for record in records:

        if record.get(
            "evidence_uid"
        ) == evidence_uid:

            return record

    return None