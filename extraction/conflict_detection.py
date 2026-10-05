import re
from datetime import datetime


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return str(value)

    return str(value)


def parse_timestamp(value):
    if not value:
        return None

    value = safe_text(value).strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(
            value.replace("Z", "")
        )
    except Exception:
        return None


def normalize(value):
    return safe_text(value).strip().lower()


# ============================================================
# EXTRACT VALUE FROM RECORD
# ============================================================

def get_value(record, keys):
    if not isinstance(record, dict):
        return ""

    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]

    return ""


# ============================================================
# TIMESTAMP CONFLICT
# ============================================================

def detect_timestamp_conflicts(records):

    conflicts = []

    previous_record = None
    previous_time = None

    for index, record in enumerate(records):

        timestamp = get_value(
            record,
            [
                "timestamp",
                "datetime",
                "date_time",
                "time",
                "date"
            ]
        )

        current_time = parse_timestamp(timestamp)

        if current_time and previous_time:

            difference = (
                current_time - previous_time
            ).total_seconds()

            if difference < 0:

                conflicts.append({
                    "type": "TIMESTAMP_CONFLICT",
                    "severity": "HIGH",
                    "record_index": index,
                    "description":
                        "Current timestamp occurs before "
                        "the previous timestamp.",
                    "previous_timestamp":
                        str(previous_time),
                    "current_timestamp":
                        str(current_time)
                })

        if current_time:
            previous_time = current_time
            previous_record = record

    return conflicts


# ============================================================
# LOCATION CONFLICT
# ============================================================

def detect_location_conflicts(records):

    conflicts = []

    known_locations = {}

    for index, record in enumerate(records):

        location = get_value(
            record,
            [
                "location",
                "place",
                "address",
                "geo_location"
            ]
        )

        location = normalize(location)

        if not location:
            continue

        timestamp = get_value(
            record,
            [
                "timestamp",
                "datetime",
                "date_time"
            ]
        )

        time_key = timestamp[:16] if timestamp else "unknown"

        if time_key in known_locations:

            previous_location = known_locations[
                time_key
            ]

            if previous_location != location:

                conflicts.append({
                    "type": "LOCATION_CONFLICT",
                    "severity": "MEDIUM",
                    "record_index": index,
                    "timestamp": timestamp,
                    "previous_location":
                        previous_location,
                    "current_location":
                        location,
                    "description":
                        "Different locations detected "
                        "for the same time period."
                })

        else:
            known_locations[time_key] = location

    return conflicts


# ============================================================
# ENTITY CONFLICT
# ============================================================

def detect_entity_conflicts(records):

    conflicts = []

    entity_values = {}

    entity_keys = [
        "person",
        "person_name",
        "device",
        "device_id",
        "account",
        "username"
    ]

    for index, record in enumerate(records):

        for key in entity_keys:

            value = get_value(
                record,
                [key]
            )

            if not value:
                continue

            normalized_value = normalize(
                value
            )

            if key not in entity_values:

                entity_values[key] = {
                    normalized_value: index
                }

            elif normalized_value not in entity_values[key]:

                conflicts.append({
                    "type": "ENTITY_CONFLICT",
                    "severity": "MEDIUM",
                    "record_index": index,
                    "entity_type": key,
                    "previous_values":
                        list(
                            entity_values[key].keys()
                        ),
                    "current_value":
                        normalized_value,
                    "description":
                        "Multiple different entity values "
                        "were detected."
                })

                entity_values[key][
                    normalized_value
                ] = index

    return conflicts


# ============================================================
# CONTENT CONFLICT
# ============================================================

def detect_content_conflicts(records):

    conflicts = []

    for index, record in enumerate(records):

        text = get_value(
            record,
            [
                "text",
                "content",
                "description",
                "claim_text",
                "message"
            ]
        )

        if not text:
            continue

        text = safe_text(text)

        contradiction_pairs = [
            ("present", "absent"),
            ("connected", "disconnected"),
            ("enabled", "disabled"),
            ("active", "inactive"),
            ("created", "deleted"),
            ("available", "unavailable"),
            ("success", "failure"),
            ("successful", "failed")
        ]

        lower_text = text.lower()

        for first, second in contradiction_pairs:

            if (
                first in lower_text
                and second in lower_text
            ):

                conflicts.append({
                    "type": "CONTENT_CONFLICT",
                    "severity": "MEDIUM",
                    "record_index": index,
                    "description":
                        "Potentially contradictory "
                        "content detected.",
                    "content": text
                })

    return conflicts


# ============================================================
# EVENT CONFLICT
# ============================================================

def detect_event_conflicts(records):

    conflicts = []

    event_map = {}

    for index, record in enumerate(records):

        event = get_value(
            record,
            [
                "event",
                "event_type",
                "event_name",
                "activity",
                "description"
            ]
        )

        if not event:
            continue

        event_normalized = normalize(event)

        timestamp = get_value(
            record,
            [
                "timestamp",
                "datetime",
                "date_time"
            ]
        )

        time_obj = parse_timestamp(
            timestamp
        )

        if not time_obj:
            continue

        time_key = time_obj.strftime(
            "%Y-%m-%d %H:%M"
        )

        if time_key in event_map:

            previous_event = event_map[
                time_key
            ]

            if normalize(
                previous_event
            ) != event_normalized:

                conflicts.append({
                    "type": "EVENT_CONFLICT",
                    "severity": "MEDIUM",
                    "record_index": index,
                    "timestamp": timestamp,
                    "previous_event":
                        previous_event,
                    "current_event":
                        event,
                    "description":
                        "Different events detected "
                        "within the same time period."
                })

        else:
            event_map[
                time_key
            ] = event


    return conflicts


# ============================================================
# COMPLETE CONFLICT ANALYSIS
# ============================================================

def detect_conflicts(records):

    if not isinstance(records, list):
        records = []

    timestamp_conflicts = (
        detect_timestamp_conflicts(
            records
        )
    )

    location_conflicts = (
        detect_location_conflicts(
            records
        )
    )

    entity_conflicts = (
        detect_entity_conflicts(
            records
        )
    )

    content_conflicts = (
        detect_content_conflicts(
            records
        )
    )

    event_conflicts = (
        detect_event_conflicts(
            records
        )
    )

    all_conflicts = (
        timestamp_conflicts
        + location_conflicts
        + entity_conflicts
        + content_conflicts
        + event_conflicts
    )

    high_count = sum(
        1
        for item in all_conflicts
        if item.get("severity") == "HIGH"
    )

    medium_count = sum(
        1
        for item in all_conflicts
        if item.get("severity") == "MEDIUM"
    )

    low_count = sum(
        1
        for item in all_conflicts
        if item.get("severity") == "LOW"
    )

    total = len(all_conflicts)

    if total == 0:
        conflict_score = 0.0
    else:
        conflict_score = min(
            100.0,
            (
                high_count * 15
                + medium_count * 8
                + low_count * 3
            )
        )

    return {
        "total_conflicts": total,

        "conflict_score": round(
            conflict_score,
            2
        ),

        "timestamp_conflicts":
            timestamp_conflicts,

        "location_conflicts":
            location_conflicts,

        "entity_conflicts":
            entity_conflicts,

        "content_conflicts":
            content_conflicts,

        "event_conflicts":
            event_conflicts,

        "high_severity":
            high_count,

        "medium_severity":
            medium_count,

        "low_severity":
            low_count,

        "interpretation":
            (
                "Detected conflicts are forensic "
                "signals only. A conflict does not "
                "automatically mean that evidence is "
                "false, fabricated, or invalid."
            )
    }


# ============================================================
# SUMMARY
# ============================================================

def get_conflict_summary(result):

    return {
        "total_conflicts":
            result.get(
                "total_conflicts",
                0
            ),

        "conflict_score":
            result.get(
                "conflict_score",
                0
            ),

        "high_severity":
            result.get(
                "high_severity",
                0
            ),

        "medium_severity":
            result.get(
                "medium_severity",
                0
            ),

        "low_severity":
            result.get(
                "low_severity",
                0
            )
    }