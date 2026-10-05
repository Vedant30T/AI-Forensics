import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

EXTRACTED_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "extracted_data"
)

CLAIM_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "claims"
)

os.makedirs(
    CLAIM_DIR,
    exist_ok=True
)


# ============================================================
# VALIDATION STATUSES
# ============================================================

SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
UNSUPPORTED = "UNSUPPORTED"
CONTRADICTED = "CONTRADICTED"
UNVALIDATED = "UNVALIDATED"


# ============================================================
# HELPERS
# ============================================================

def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


def normalize_text(value):

    value = clean_text(value)

    return " ".join(
        value.lower().split()
    )


def unique_values(values):

    result = []

    seen = set()

    for value in values:

        value = clean_text(value)

        if not value:
            continue

        key = normalize_text(value)

        if key not in seen:

            seen.add(key)
            result.append(value)

    return result


# ============================================================
# LOAD EXTRACTION RESULT
# ============================================================

def load_extraction_result(evidence_uid):

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in str(evidence_uid)
    )

    file_path = os.path.join(
        EXTRACTED_DIR,
        f"extracted_{safe_uid}.json"
    )

    if not os.path.exists(
        file_path
    ):

        return None

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return None


# ============================================================
# CREATE CLAIM FROM EVENT
# ============================================================

def create_event_claim(
    event,
    claim_number
):

    if isinstance(
        event,
        dict
    ):

        event_name = clean_text(
            event.get(
                "event",
                ""
            )
        )

        description = clean_text(
            event.get(
                "description",
                ""
            )
        )

    else:

        event_name = clean_text(
            event
        )

        description = event_name

    if not description:

        return None

    return {
        "claim_id": (
            f"CLM-{claim_number:04d}"
        ),

        "claim": description,

        "claim_type": "EVENT",

        "event": event_name,

        "source": "Evidence",

        "validation_status": UNVALIDATED,

        "supporting_evidence": [],

        "contradicting_evidence": [],

        "validation_reason": "",

        "confidence": 0
    }


# ============================================================
# CREATE ENTITY CLAIMS
# ============================================================

def create_entity_claims(
    entities,
    starting_number
):

    claims = []

    claim_number = starting_number

    persons = entities.get(
        "persons",
        []
    )

    devices = entities.get(
        "devices",
        []
    )

    locations = entities.get(
        "locations",
        []
    )

    objects = entities.get(
        "objects",
        []
    )

    # --------------------------------------------------------
    # Person + Location
    # --------------------------------------------------------

    for person in persons:

        for location in locations:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    f"{person} is associated with {location}.",

                "claim_type":
                    "PERSON_LOCATION",

                "person":
                    person,

                "location":
                    location,

                "source":
                    "Evidence",

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    # --------------------------------------------------------
    # Person + Device
    # --------------------------------------------------------

    for person in persons:

        for device in devices:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    f"{person} is associated with {device}.",

                "claim_type":
                    "PERSON_DEVICE",

                "person":
                    person,

                "device":
                    device,

                "source":
                    "Evidence",

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    # --------------------------------------------------------
    # Device + Location
    # --------------------------------------------------------

    for device in devices:

        for location in locations:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    f"{device} is associated with {location}.",

                "claim_type":
                    "DEVICE_LOCATION",

                "device":
                    device,

                "location":
                    location,

                "source":
                    "Evidence",

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    # --------------------------------------------------------
    # Person + Object
    # --------------------------------------------------------

    for person in persons:

        for object_name in objects:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    f"{person} is associated with {object_name}.",

                "claim_type":
                    "PERSON_OBJECT",

                "person":
                    person,

                "object":
                    object_name,

                "source":
                    "Evidence",

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    return claims


# ============================================================
# CREATE CLAIMS FROM EXTRACTION DATA
# ============================================================

def create_claims_from_extraction(
    extraction_result
):

    if not extraction_result:

        return {
            "success": False,
            "message": "Extraction result is empty."
        }

    evidence_uid = extraction_result.get(
        "evidence_uid",
        ""
    )

    entities = extraction_result.get(
        "entities",
        {}
    )

    events = extraction_result.get(
        "events",
        []
    )

    dates = extraction_result.get(
        "dates",
        []
    )

    times = extraction_result.get(
        "times",
        []
    )

    claims = []

    claim_number = 1

    # --------------------------------------------------------
    # Event Claims
    # --------------------------------------------------------

    for event in events:

        claim = create_event_claim(
            event,
            claim_number
        )

        if claim:

            claims.append(
                claim
            )

            claim_number += 1

    # --------------------------------------------------------
    # Entity Claims
    # --------------------------------------------------------

    entity_claims = create_entity_claims(
        entities,
        claim_number
    )

    claims.extend(
        entity_claims
    )

    claim_number += len(
        entity_claims
    )

    # --------------------------------------------------------
    # Event + Time Claims
    # --------------------------------------------------------

    for event in events:

        if isinstance(
            event,
            dict
        ):

            event_name = clean_text(
                event.get(
                    "event",
                    ""
                )
            )

        else:

            event_name = clean_text(
                event
            )

        if not event_name:
            continue

        for time_value in times:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    (
                        f"Event '{event_name}' "
                        f"occurred around {time_value}."
                    ),

                "claim_type":
                    "EVENT_TIME",

                "event":
                    event_name,

                "time":
                    time_value,

                "source":
                    "Evidence",

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    # --------------------------------------------------------
    # Event + Date Claims
    # --------------------------------------------------------

    for event in events:

        if isinstance(
            event,
            dict
        ):

            event_name = clean_text(
                event.get(
                    "event",
                    ""
                )
            )

        else:

            event_name = clean_text(
                event
            )

        if not event_name:
            continue

        for date_value in dates:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    (
                        f"Event '{event_name}' "
                        f"is associated with {date_value}."
                    ),

                "claim_type":
                    "EVENT_DATE",

                "event":
                    event_name,

                "date":
                    date_value,

                "source":
                    "Evidence",

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    # --------------------------------------------------------
    # Existing Claims
    # --------------------------------------------------------

    existing_claims = extraction_result.get(
        "claims",
        []
    )

    for existing in existing_claims:

        if not isinstance(
            existing,
            dict
        ):
            continue

        existing_text = clean_text(
            existing.get(
                "claim",
                ""
            )
        )

        if not existing_text:
            continue

        duplicate = False

        for claim in claims:

            if normalize_text(
                claim.get(
                    "claim",
                    ""
                )
            ) == normalize_text(
                existing_text
            ):

                duplicate = True
                break

        if not duplicate:

            claims.append({

                "claim_id":
                    f"CLM-{claim_number:04d}",

                "claim":
                    existing_text,

                "claim_type":
                    existing.get(
                        "claim_type",
                        "GENERAL"
                    ),

                "source":
                    existing.get(
                        "source",
                        "Evidence"
                    ),

                "validation_status":
                    UNVALIDATED,

                "supporting_evidence":
                    [],

                "contradicting_evidence":
                    [],

                "validation_reason":
                    "",

                "confidence":
                    0
            })

            claim_number += 1

    return {

        "success": True,

        "module":
            "AI Evidence Extraction & Correlation",

        "stage":
            "Claim Creation",

        "evidence_uid":
            evidence_uid,

        "claims":
            claims,

        "claim_count":
            len(claims),

        "validation_statuses": [

            SUPPORTED,

            PARTIALLY_SUPPORTED,

            UNSUPPORTED,

            CONTRADICTED

        ],

        "created_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }


# ============================================================
# VALIDATE SINGLE CLAIM
# ============================================================

def validate_claim(
    claim,
    supporting_evidence=None,
    contradicting_evidence=None
):

    if not claim:

        return {
            "success": False,
            "message": "Claim is empty."
        }

    supporting_evidence = (
        supporting_evidence
        or []
    )

    contradicting_evidence = (
        contradicting_evidence
        or []
    )

    support_count = len(
        supporting_evidence
    )

    contradiction_count = len(
        contradicting_evidence
    )

    # --------------------------------------------------------
    # CONTRADICTED
    # --------------------------------------------------------

    if contradiction_count > 0:

        if support_count > 0:

            status = PARTIALLY_SUPPORTED

            reason = (
                "The claim has both supporting "
                "and contradicting evidence."
            )

        else:

            status = CONTRADICTED

            reason = (
                "Contradicting evidence was found."
            )

    # --------------------------------------------------------
    # SUPPORTED
    # --------------------------------------------------------

    elif support_count >= 2:

        status = SUPPORTED

        reason = (
            "The claim is supported by "
            "multiple evidence references."
        )

    elif support_count == 1:

        status = SUPPORTED

        reason = (
            "The claim is supported by "
            "an evidence reference."
        )

    # --------------------------------------------------------
    # UNSUPPORTED
    # --------------------------------------------------------

    else:

        status = UNSUPPORTED

        reason = (
            "No supporting evidence was found."
        )

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    if status == SUPPORTED:

        confidence = 90 if support_count >= 2 else 75

    elif status == PARTIALLY_SUPPORTED:

        confidence = 60

    elif status == CONTRADICTED:

        confidence = 20

    else:

        confidence = 10

    updated_claim = dict(
        claim
    )

    updated_claim[
        "validation_status"
    ] = status

    updated_claim[
        "supporting_evidence"
    ] = unique_values(
        supporting_evidence
    )

    updated_claim[
        "contradicting_evidence"
    ] = unique_values(
        contradicting_evidence
    )

    updated_claim[
        "validation_reason"
    ] = reason

    updated_claim[
        "confidence"
    ] = confidence

    return {

        "success": True,

        "claim": updated_claim
    }


# ============================================================
# APPLY INITIAL VALIDATION
# ============================================================

def validate_claims(
    claim_result
):

    if not claim_result:

        return {
            "success": False,
            "message": "Claim result is empty."
        }

    claims = claim_result.get(
        "claims",
        []
    )

    validated_claims = []

    for claim in claims:

        result = validate_claim(
            claim
        )

        if result.get(
            "success",
            False
        ):

            validated_claims.append(
                result["claim"]
            )

    counts = {

        SUPPORTED: 0,

        PARTIALLY_SUPPORTED: 0,

        UNSUPPORTED: 0,

        CONTRADICTED: 0
    }

    for claim in validated_claims:

        status = claim.get(
            "validation_status",
            UNVALIDATED
        )

        if status in counts:

            counts[status] += 1

    return {

        "success": True,

        "module":
            "AI Evidence Extraction & Correlation",

        "stage":
            "Claim Validation",

        "evidence_uid":
            claim_result.get(
                "evidence_uid",
                ""
            ),

        "claims":
            validated_claims,

        "claim_count":
            len(validated_claims),

        "validation_summary":
            counts,

        "validation_note":
            (
                "Claim validation is a verification "
                "signal and does not represent a "
                "final legal or guilt decision."
            ),

        "validated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }


# ============================================================
# SAVE CLAIM RESULT
# ============================================================

def save_claim_result(
    result
):

    if not result:

        return None

    evidence_uid = result.get(
        "evidence_uid",
        "UNKNOWN_EVIDENCE"
    )

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in str(evidence_uid)
    )

    file_path = os.path.join(
        CLAIM_DIR,
        f"claims_{safe_uid}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return file_path


# ============================================================
# LOAD CLAIM RESULT
# ============================================================

def load_claim_result(
    evidence_uid
):

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in str(evidence_uid)
    )

    file_path = os.path.join(
        CLAIM_DIR,
        f"claims_{safe_uid}.json"
    )

    if not os.path.exists(
        file_path
    ):

        return None

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return None


# ============================================================
# COMPLETE CLAIM PIPELINE
# ============================================================

def run_claim_pipeline(
    evidence_uid
):

    extraction_result = load_extraction_result(
        evidence_uid
    )

    if not extraction_result:

        return {
            "success": False,
            "message": (
                "Extraction result not found "
                "for the supplied Evidence UID."
            )
        }

    claim_result = create_claims_from_extraction(
        extraction_result
    )

    if not claim_result.get(
        "success",
        False
    ):

        return claim_result

    validation_result = validate_claims(
        claim_result
    )

    save_claim_result(
        validation_result
    )

    return validation_result


# ============================================================
# STATUS
# ============================================================

def get_claim_engine_status():

    return {

        "module":
            "AI Evidence Extraction & Correlation",

        "component":
            "Claim Creation & Validation",

        "status":
            "READY",

        "llm_required":
            False,

        "validation_statuses": [

            SUPPORTED,

            PARTIALLY_SUPPORTED,

            UNSUPPORTED,

            CONTRADICTED
        ]
    }