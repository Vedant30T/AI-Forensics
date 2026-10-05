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

COC_FILE = os.path.join(
    BASE_DIR,
    "chain_of_custody.json"
)


# ============================================================
# LOAD CHAIN OF CUSTODY
# ============================================================

def load_chain_of_custody():

    if not os.path.exists(
        COC_FILE
    ):

        return []

    try:

        with open(
            COC_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


# ============================================================
# SAVE CHAIN OF CUSTODY
# ============================================================

def save_chain_of_custody(
    records
):

    with open(
        COC_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            records,
            file,
            indent=4
        )


# ============================================================
# ADD CUSTODY EVENT
# ============================================================

def add_custody_event(
    evidence_uid,
    action,
    person,
    location,
    reason,
    previous_handler="",
    new_handler="",
    access_details="",
    authorization_status="AUTHORIZED"
):

    if not evidence_uid:

        raise ValueError(
            "Evidence UID is required."
        )

    current_datetime = datetime.now()

    event = {

        "evidence_uid":
            evidence_uid,

        "action":
            action,

        "person":
            person,

        "date":
            current_datetime.strftime(
                "%Y-%m-%d"
            ),

        "time":
            current_datetime.strftime(
                "%H:%M:%S"
            ),

        "location":
            location,

        "reason":
            reason,

        "previous_handler":
            previous_handler,

        "new_handler":
            new_handler,

        "access_processing_details":
            access_details,

        "authorization_status":
            authorization_status

    }

    records = load_chain_of_custody()

    records.append(
        event
    )

    save_chain_of_custody(
        records
    )

    return event


# ============================================================
# GET EVIDENCE HISTORY
# ============================================================

def get_custody_history(
    evidence_uid
):

    records = load_chain_of_custody()

    return [
        record
        for record in records
        if record.get(
            "evidence_uid"
        ) == evidence_uid
    ]