import re
from datetime import datetime


# ============================================================
# HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    if isinstance(value, (dict, list)):
        return str(value)

    return str(value).strip()


def normalize(value):
    return safe_text(value).lower().strip()


def parse_timestamp(value):
    if not value:
        return None

    value = safe_text(value)

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(
                value,
                fmt
            )
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(
            value.replace("Z", "")
        )
    except Exception:
        return None


# ============================================================
# ENTITY EXTRACTION
# ============================================================

def extract_entities(record):

    entities = []

    if not isinstance(record, dict):
        return entities

    entity_keys = [
        "person",
        "person_name",
        "device",
        "device_id",
        "location",
        "place",
        "account",
        "username",
        "email",
        "ip",
        "ip_address"
    ]

    for key in entity_keys:

        value = record.get(key)

        if value in (None, ""):
            continue

        if isinstance(value, list):

            for item in value:

                if safe_text(item):
                    entities.append(
                        normalize(item)
                    )

        else:

            entities.append(
                normalize(value)
            )

    return list(
        set(entities)
    )


# ============================================================
# ACTIVITY TYPE
# ============================================================

def detect_activity_type(record):

    text = normalize(record)

    activity_rules = {

        "LOGIN": [
            "login",
            "signin",
            "sign in",
            "authentication"
        ],

        "FILE_ACCESS": [
            "file",
            "opened",
            "accessed",
            "modified",
            "deleted"
        ],

        "USB": [
            "usb",
            "pendrive",
            "pen drive",
            "removable"
        ],

        "NETWORK": [
            "network",
            "internet",
            "wifi",
            "connection",
            "ip address"
        ],

        "DEVICE": [
            "device",
            "phone",
            "mobile",
            "android",
            "computer"
        ],

        "APPLICATION": [
            "application",
            "app",
            "browser",
            "chrome",
            "software"
        ],

        "COMMUNICATION": [
            "sms",
            "message",
            "email",
            "call",
            "chat"
        ]
    }

    detected = []

    for activity, keywords in activity_rules.items():

        for keyword in keywords:

            if keyword in text:

                detected.append(
                    activity
                )

                break

    if not detected:
        detected.append("OTHER")

    return detected


# ============================================================
# TEMPORAL CORRELATION
# ============================================================

def temporal_correlation(
    records,
    time_window_seconds=300
):

    correlations = []

    parsed_records = []

    for index, record in enumerate(records):

        if not isinstance(record, dict):
            continue

        timestamp = (
            record.get("timestamp")
            or record.get("datetime")
            or record.get("date_time")
            or record.get("time")
        )

        parsed = parse_timestamp(
            timestamp
        )

        if parsed:

            parsed_records.append({
                "index": index,
                "record": record,
                "timestamp": parsed
            })

    for i in range(
        len(parsed_records)
    ):

        first = parsed_records[i]

        for j in range(
            i + 1,
            len(parsed_records)
        ):

            second = parsed_records[j]

            difference = abs(
                (
                    second["timestamp"]
                    - first["timestamp"]
                ).total_seconds()
            )

            if (
                difference
                <= time_window_seconds
            ):

                correlations.append({

                    "type":
                        "TEMPORAL",

                    "record_1":
                        first["index"],

                    "record_2":
                        second["index"],

                    "time_difference_seconds":
                        difference,

                    "relationship":
                        "TEMPORALLY_CORRELATED"
                })

    return correlations


# ============================================================
# ENTITY CORRELATION
# ============================================================

def entity_correlation(records):

    correlations = []

    entity_map = {}

    for index, record in enumerate(records):

        entities = extract_entities(
            record
        )

        for entity in entities:

            if entity in entity_map:

                for previous_index in entity_map[
                    entity
                ]:

                    correlations.append({

                        "type":
                            "ENTITY",

                        "entity":
                            entity,

                        "record_1":
                            previous_index,

                        "record_2":
                            index,

                        "relationship":
                            "SAME_ENTITY"
                    })

                entity_map[
                    entity
                ].append(index)

            else:

                entity_map[
                    entity
                ] = [index]

    return correlations


# ============================================================
# ACTIVITY CORRELATION
# ============================================================

def activity_correlation(records):

    correlations = []

    activity_map = {}

    for index, record in enumerate(records):

        activities = detect_activity_type(
            record
        )

        for activity in activities:

            if activity in activity_map:

                for previous_index in activity_map[
                    activity
                ]:

                    correlations.append({

                        "type":
                            "ACTIVITY",

                        "activity":
                            activity,

                        "record_1":
                            previous_index,

                        "record_2":
                            index,

                        "relationship":
                            "SAME_ACTIVITY_PATTERN"
                    })

                activity_map[
                    activity
                ].append(index)

            else:

                activity_map[
                    activity
                ] = [index]

    return correlations


# ============================================================
# CONTEXTUAL CORRELATION
# ============================================================

def contextual_correlation(records):

    correlations = []

    for i in range(
        len(records)
    ):

        first_text = normalize(
            records[i]
        )

        if not first_text:
            continue

        for j in range(
            i + 1,
            len(records)
        ):

            second_text = normalize(
                records[j]
            )

            if not second_text:
                continue

            first_words = set(
                re.findall(
                    r"\b[a-zA-Z0-9_]+\b",
                    first_text
                )
            )

            second_words = set(
                re.findall(
                    r"\b[a-zA-Z0-9_]+\b",
                    second_text
                )
            )

            if not first_words or not second_words:
                continue

            intersection = (
                first_words
                & second_words
            )

            union = (
                first_words
                | second_words
            )

            similarity = (
                len(intersection)
                / len(union)
            )

            if similarity >= 0.30:

                correlations.append({

                    "type":
                        "CONTEXTUAL",

                    "record_1":
                        i,

                    "record_2":
                        j,

                    "similarity":
                        round(
                            similarity,
                            3
                        ),

                    "relationship":
                        "CONTEXTUALLY_SIMILAR"
                })

    return correlations


# ============================================================
# CORRELATION SCORE
# ============================================================

def calculate_correlation_score(
    correlations,
    total_records
):

    if total_records <= 1:
        return 0.0

    if not correlations:
        return 0.0

    unique_pairs = set()

    for item in correlations:

        pair = (
            item.get("record_1"),
            item.get("record_2")
        )

        unique_pairs.add(pair)

    maximum_pairs = (
        total_records
        * (total_records - 1)
        / 2
    )

    if maximum_pairs <= 0:
        return 0.0

    score = (
        len(unique_pairs)
        / maximum_pairs
    ) * 100

    return round(
        min(
            100.0,
            score
        ),
        2
    )


# ============================================================
# MAIN CORRELATION FUNCTION
# ============================================================

def correlate_behavior(records):

    if not isinstance(
        records,
        list
    ):
        records = []

    temporal = temporal_correlation(
        records
    )

    entity = entity_correlation(
        records
    )

    activity = activity_correlation(
        records
    )

    contextual = contextual_correlation(
        records
    )

    all_correlations = (
        temporal
        + entity
        + activity
        + contextual
    )

    score = calculate_correlation_score(
        all_correlations,
        len(records)
    )

    return {

        "total_records":
            len(records),

        "total_correlations":
            len(all_correlations),

        "correlation_score":
            score,

        "temporal_correlations":
            temporal,

        "entity_correlations":
            entity,

        "activity_correlations":
            activity,

        "contextual_correlations":
            contextual,

        "all_correlations":
            all_correlations,

        "interpretation":
            (
                "Behaviour correlation identifies "
                "relationships between evidence "
                "activities based on time, entities, "
                "activity patterns and context. "
                "It does not establish guilt or "
                "legal responsibility."
            )
    }