import os
import re
import json
from datetime import datetime

from extraction.evidence_preprocessor import (
    preprocess_evidence,
    load_preprocessed_result,
    save_preprocessed_result
)


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "extracted_data"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


def unique_list(values):

    result = []

    seen = set()

    for value in values:

        value = clean_text(value)

        if not value:
            continue

        key = value.lower()

        if key not in seen:

            seen.add(key)
            result.append(value)

    return result


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_dates(text):

    if not text:
        return []

    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
        r"\b\d{1,2}\s+"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\s+\d{2,4}\b"
    ]

    dates = []

    for pattern in patterns:

        dates.extend(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return unique_list(dates)


# ============================================================
# TIME EXTRACTION
# ============================================================

def extract_times(text):

    if not text:
        return []

    patterns = [
        r"\b\d{1,2}:\d{2}(?::\d{2})?\s*"
        r"(?:AM|PM)?\b",

        r"\b\d{1,2}\s*"
        r"(?:AM|PM)\b"
    ]

    times = []

    for pattern in patterns:

        times.extend(
            re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )
        )

    return unique_list(times)


# ============================================================
# EMAIL EXTRACTION
# ============================================================

def extract_emails(text):

    if not text:
        return []

    pattern = (
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\."
        r"[A-Za-z]{2,}\b"
    )

    return unique_list(
        re.findall(
            pattern,
            text
        )
    )


# ============================================================
# IP ADDRESS EXTRACTION
# ============================================================

def extract_ip_addresses(text):

    if not text:
        return []

    pattern = (
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    )

    candidates = re.findall(
        pattern,
        text
    )

    valid = []

    for ip in candidates:

        parts = ip.split(".")

        if all(
            0 <= int(part) <= 255
            for part in parts
        ):

            valid.append(ip)

    return unique_list(valid)


# ============================================================
# URL EXTRACTION
# ============================================================

def extract_urls(text):

    if not text:
        return []

    pattern = (
        r"https?://[^\s]+"
    )

    return unique_list(
        re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )
    )


# ============================================================
# DEVICE EXTRACTION
# ============================================================

def extract_devices(text):

    if not text:
        return []

    device_keywords = [
        "phone",
        "mobile",
        "smartphone",
        "laptop",
        "computer",
        "desktop",
        "tablet",
        "iphone",
        "android",
        "usb",
        "pendrive",
        "pen drive",
        "camera",
        "cctv",
        "router",
        "server",
        "device"
    ]

    found = []

    lines = text.splitlines()

    for line in lines:

        clean_line = clean_text(line)

        lower_line = clean_line.lower()

        for keyword in device_keywords:

            if keyword in lower_line:

                found.append(clean_line)

                break

    return unique_list(found)


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_locations(text):

    if not text:
        return []

    location_keywords = [
        "building",
        "office",
        "home",
        "house",
        "room",
        "station",
        "road",
        "street",
        "city",
        "location",
        "address",
        "airport",
        "school",
        "college",
        "hospital",
        "bank",
        "shop",
        "store"
    ]

    locations = []

    lines = text.splitlines()

    for line in lines:

        clean_line = clean_text(line)

        lower_line = clean_line.lower()

        for keyword in location_keywords:

            if keyword in lower_line:

                locations.append(
                    clean_line
                )

                break

    return unique_list(locations)


# ============================================================
# PERSON EXTRACTION
# ============================================================

def extract_persons(text):

    if not text:
        return []

    persons = []

    # Pattern:
    # Person A
    # Person B
    # User A
    # Suspect A
    # Investigator A

    pattern = (
        r"\b(?:Person|User|Suspect|"
        r"Investigator|Witness|Officer)"
        r"\s+[A-Z][A-Za-z0-9_-]*\b"
    )

    persons.extend(
        re.findall(
            pattern,
            text
        )
    )

    # Common name format:
    # First Last
    name_pattern = (
        r"\b[A-Z][a-z]{2,}\s+"
        r"[A-Z][a-z]{2,}\b"
    )

    possible_names = re.findall(
        name_pattern,
        text
    )

    excluded = {
        "Evidence Report",
        "Digital Evidence",
        "Verification Result",
        "Chain Custody",
        "Integrity Score",
        "Dynamic Trust",
        "Evidence Analysis"
    }

    for name in possible_names:

        if name not in excluded:

            persons.append(name)

    return unique_list(persons)


# ============================================================
# OBJECT EXTRACTION
# ============================================================

def extract_objects(text):

    if not text:
        return []

    object_keywords = [
        "file",
        "document",
        "image",
        "video",
        "audio",
        "phone",
        "laptop",
        "computer",
        "usb",
        "pendrive",
        "camera",
        "vehicle",
        "car",
        "door",
        "card",
        "passport",
        "email",
        "message",
        "device"
    ]

    objects = []

    words_text = text.lower()

    for keyword in object_keywords:

        if keyword in words_text:

            objects.append(keyword)

    return unique_list(objects)


# ============================================================
# EVENT EXTRACTION
# ============================================================

def extract_events(text):

    if not text:
        return []

    event_keywords = [
        "login",
        "logout",
        "entered",
        "exit",
        "exited",
        "accessed",
        "opened",
        "closed",
        "copied",
        "deleted",
        "created",
        "modified",
        "downloaded",
        "uploaded",
        "connected",
        "disconnected",
        "transferred",
        "sent",
        "received",
        "called",
        "message",
        "recorded",
        "captured",
        "installed",
        "uninstalled",
        "searched",
        "visited"
    ]

    events = []

    lines = text.splitlines()

    for line in lines:

        clean_line = clean_text(line)

        lower_line = clean_line.lower()

        for keyword in event_keywords:

            if keyword in lower_line:

                events.append(
                    {
                        "event": keyword,
                        "description": clean_line
                    }
                )

                break

    return events


# ============================================================
# CLAIM GENERATION
# ============================================================

def create_claims(
    persons,
    devices,
    locations,
    events,
    dates,
    times
):

    claims = []

    claim_number = 1

    # Event based claims

    for event in events:

        description = event.get(
            "description",
            ""
        )

        if not description:
            continue

        claims.append(
            {
                "claim_id": (
                    f"CLM-{claim_number:04d}"
                ),
                "claim": description,
                "claim_type": "EVENT",
                "source": "Evidence",
                "initial_status": "UNVALIDATED"
            }
        )

        claim_number += 1

    # Person + location

    for person in persons:

        for location in locations:

            claims.append(
                {
                    "claim_id": (
                        f"CLM-{claim_number:04d}"
                    ),
                    "claim": (
                        f"{person} is associated "
                        f"with {location}."
                    ),
                    "claim_type": "ENTITY_LOCATION",
                    "source": "Evidence",
                    "initial_status": "UNVALIDATED"
                }
            )

            claim_number += 1

    # Person + device

    for person in persons:

        for device in devices:

            claims.append(
                {
                    "claim_id": (
                        f"CLM-{claim_number:04d}"
                    ),
                    "claim": (
                        f"{person} is associated "
                        f"with {device}."
                    ),
                    "claim_type": "PERSON_DEVICE",
                    "source": "Evidence",
                    "initial_status": "UNVALIDATED"
                }
            )

            claim_number += 1

    # Event + time

    for event in events:

        for time_value in times:

            claims.append(
                {
                    "claim_id": (
                        f"CLM-{claim_number:04d}"
                    ),
                    "claim": (
                        f"Event '{event.get('event')}' "
                        f"occurred around {time_value}."
                    ),
                    "claim_type": "EVENT_TIME",
                    "source": "Evidence",
                    "initial_status": "UNVALIDATED"
                }
            )

            claim_number += 1

    # Event + date

    for event in events:

        for date_value in dates:

            claims.append(
                {
                    "claim_id": (
                        f"CLM-{claim_number:04d}"
                    ),
                    "claim": (
                        f"Event '{event.get('event')}' "
                        f"is associated with {date_value}."
                    ),
                    "claim_type": "EVENT_DATE",
                    "source": "Evidence",
                    "initial_status": "UNVALIDATED"
                }
            )

            claim_number += 1

    return claims


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_evidence_information(
    file_path=None,
    evidence_uid=None,
    verified_hash=None,
    metadata=None,
    integrity_result=None
):

    # --------------------------------------------------------
    # Load existing preprocessed data if available
    # --------------------------------------------------------

    preprocessed = None

    if evidence_uid:

        preprocessed = load_preprocessed_result(
            evidence_uid
        )

    # --------------------------------------------------------
    # Preprocess evidence if needed
    # --------------------------------------------------------

    if preprocessed is None:

        if not file_path:

            return {
                "success": False,
                "message": (
                    "Evidence file path is required."
                )
            }

        preprocessed = preprocess_evidence(
            file_path=file_path,
            evidence_uid=evidence_uid,
            verified_hash=verified_hash,
            metadata=metadata,
            integrity_result=integrity_result
        )

        if not preprocessed.get(
            "success",
            False
        ):

            return preprocessed

        save_preprocessed_result(
            preprocessed
        )

    # --------------------------------------------------------
    # Get text
    # --------------------------------------------------------

    preprocessing = preprocessed.get(
        "preprocessing_result",
        {}
    )

    extracted_text = preprocessing.get(
        "extracted_text",
        ""
    )

    # Log records
    records = preprocessing.get(
        "structured_records",
        []
    )

    if records:

        record_text = []

        for record in records:

            if isinstance(
                record,
                dict
            ):

                record_text.append(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    )
                )

            else:

                record_text.append(
                    str(record)
                )

        extracted_text += "\n".join(
            record_text
        )

    # Basic evidence information

    file_information = preprocessed.get(
        "file_information",
        {}
    )

    # --------------------------------------------------------
    # Extraction
    # --------------------------------------------------------

    persons = extract_persons(
        extracted_text
    )

    objects = extract_objects(
        extracted_text
    )

    devices = extract_devices(
        extracted_text
    )

    locations = extract_locations(
        extracted_text
    )

    events = extract_events(
        extracted_text
    )

    dates = extract_dates(
        extracted_text
    )

    times = extract_times(
        extracted_text
    )

    emails = extract_emails(
        extracted_text
    )

    ip_addresses = extract_ip_addresses(
        extracted_text
    )

    urls = extract_urls(
        extracted_text
    )

    claims = create_claims(
        persons=persons,
        devices=devices,
        locations=locations,
        events=events,
        dates=dates,
        times=times
    )

    # --------------------------------------------------------
    # AI Confidence
    # --------------------------------------------------------

    # This is a rule-based extraction confidence.
    # It is NOT an LLM confidence.

    extracted_items = (
        len(persons)
        + len(objects)
        + len(devices)
        + len(locations)
        + len(events)
        + len(dates)
        + len(times)
        + len(claims)
    )

    if extracted_items == 0:

        ai_confidence = 0

    elif extracted_items <= 3:

        ai_confidence = 60

    elif extracted_items <= 8:

        ai_confidence = 75

    else:

        ai_confidence = 85

    # --------------------------------------------------------
    # Final structured result
    # --------------------------------------------------------

    result = {

        "success": True,

        "module": (
            "AI Evidence Extraction & Correlation"
        ),

        "stage": (
            "AI-Based Evidence Extraction"
        ),

        "evidence_uid": (
            preprocessed.get(
                "evidence_uid",
                evidence_uid
            )
        ),

        "verified_hash": (
            preprocessed.get(
                "verified_hash",
                verified_hash
            )
        ),

        "integrity_result": (
            preprocessed.get(
                "integrity_result",
                integrity_result or {}
            )
        ),

        "metadata": (
            preprocessed.get(
                "verified_metadata",
                metadata or {}
            )
        ),

        "file_information": file_information,

        "evidence_type": (
            preprocessed.get(
                "evidence_type",
                "UNKNOWN"
            )
        ),

        "entities": {

            "persons": persons,

            "objects": objects,

            "devices": devices,

            "locations": locations
        },

        "events": events,

        "dates": dates,

        "times": times,

        "communication_indicators": {

            "emails": emails,

            "ip_addresses": ip_addresses,

            "urls": urls
        },

        "claims": claims,

        "ai_confidence": ai_confidence,

        "confidence_type": (
            "Rule-Based Extraction Confidence"
        ),

        "extraction_timestamp": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),

        "next_stage": (
            "Claim Creation & Evidence Correlation"
        )
    }

    return result


# ============================================================
# SAVE EXTRACTION RESULT
# ============================================================

def save_extraction_result(result):

    if not result:

        return None

    evidence_uid = result.get(
        "evidence_uid"
    )

    if not evidence_uid:

        evidence_uid = "UNKNOWN_EVIDENCE"

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in str(evidence_uid)
    )

    filename = (
        f"extracted_{safe_uid}.json"
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(
        output_path,
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

    return output_path


# ============================================================
# LOAD EXTRACTION RESULT
# ============================================================

def load_extraction_result(
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
        OUTPUT_DIR,
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
# STATUS
# ============================================================

def get_extractor_status():

    return {

        "module": (
            "AI Evidence Extraction & Correlation"
        ),

        "component": (
            "AI-Based Evidence Extraction"
        ),

        "status": "READY",

        "llm_required": False,

        "outputs": [

            "Persons",

            "Objects",

            "Devices",

            "Locations",

            "Events",

            "Dates",

            "Times",

            "Claims",

            "AI Confidence"
        ]
    }