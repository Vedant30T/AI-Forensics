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
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M"
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


def get_timestamp(record):

    if not isinstance(record, dict):
        return None

    keys = [
        "timestamp",
        "datetime",
        "date_time",
        "time",
        "date",
        "created_at",
        "modified_at"
    ]

    for key in keys:

        value = record.get(key)

        if value not in (None, ""):
            parsed = parse_timestamp(
                value
            )

            if parsed:
                return parsed

    return None


def get_description(record):

    if not isinstance(record, dict):
        return safe_text(record)

    keys = [
        "description",
        "event",
        "event_text",
        "activity",
        "text",
        "claim_text",
        "message",
        "content"
    ]

    for key in keys:

        value = record.get(key)

        if value not in (None, ""):
            return safe_text(value)

    return ""


def get_source(record):

    if not isinstance(record, dict):
        return ""

    keys = [
        "source",
        "source_file",
        "evidence_uid",
        "evidence_id",
        "device"
    ]

    for key in keys:

        value = record.get(key)

        if value not in (None, ""):
            return safe_text(value)

    return ""


def detect_category(text):

    text = safe_text(
        text
    ).lower()

    rules = {

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
            "created",
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
            "ip"
        ],

        "DEVICE": [
            "device",
            "phone",
            "mobile",
            "android",
            "computer",
            "laptop"
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

    for category, keywords in rules.items():

        for keyword in keywords:

            if keyword in text:

                detected.append(
                    category
                )

                break

    if not detected:
        detected.append(
            "OTHER"
        )

    return detected


# ============================================================
# NORMALIZE RECORD
# ============================================================

def normalize_record(
    record,
    index
):

    timestamp = get_timestamp(
        record
    )

    description = get_description(
        record
    )

    source = get_source(
        record
    )

    return {

        "timeline_id":
            f"TL-{index:04d}",

        "original_index":
            index,

        "timestamp":
            (
                timestamp.isoformat()
                if timestamp
                else None
            ),

        "description":
            description,

        "source":
            source,

        "category":
            detect_category(
                description
            ),

        "timestamp_available":
            timestamp is not None
    }


# ============================================================
# BUILD TIMELINE
# ============================================================

def build_timeline(records):

    if not isinstance(
        records,
        list
    ):
        records = []

    timeline = []

    for index, record in enumerate(
        records,
        start=1
    ):

        timeline.append(
            normalize_record(
                record,
                index
            )
        )

    return timeline


# ============================================================
# SORT TIMELINE
# ============================================================

def sort_timeline(timeline):

    timestamped = []
    without_timestamp = []

    for item in timeline:

        timestamp = item.get(
            "timestamp"
        )

        if timestamp:

            parsed = parse_timestamp(
                timestamp
            )

            if parsed:

                timestamped.append(
                    (
                        parsed,
                        item
                    )
                )

                continue

        without_timestamp.append(
            item
        )

    timestamped.sort(
        key=lambda item: item[0]
    )

    sorted_items = [
        item
        for _, item
        in timestamped
    ]

    sorted_items.extend(
        without_timestamp
    )

    return sorted_items


# ============================================================
# CALCULATE TIME GAPS
# ============================================================

def calculate_time_gaps(
    timeline
):

    gaps = []

    timestamped = []

    for item in timeline:

        timestamp = item.get(
            "timestamp"
        )

        parsed = parse_timestamp(
            timestamp
        )

        if parsed:

            timestamped.append(
                (
                    parsed,
                    item
                )
            )

    timestamped.sort(
        key=lambda x: x[0]
    )

    for index in range(
        1,
        len(timestamped)
    ):

        previous_time = (
            timestamped[index - 1][0]
        )

        current_time = (
            timestamped[index][0]
        )

        difference = (
            current_time
            - previous_time
        ).total_seconds()

        gaps.append({

            "from_timeline_id":
                timestamped[
                    index - 1
                ][1]["timeline_id"],

            "to_timeline_id":
                timestamped[
                    index
                ][1]["timeline_id"],

            "gap_seconds":
                difference,

            "gap_minutes":
                round(
                    difference / 60,
                    2
                ),

            "gap_hours":
                round(
                    difference / 3600,
                    2
                )
        })

    return gaps


# ============================================================
# DETECT TIMELINE IRREGULARITIES
# ============================================================

def detect_irregularities(
    timeline,
    gaps
):

    irregularities = []

    # Large gaps
    for gap in gaps:

        if gap["gap_hours"] >= 24:

            irregularities.append({

                "type":
                    "LARGE_TIME_GAP",

                "severity":
                    "MEDIUM",

                "timeline_id":
                    gap["to_timeline_id"],

                "description":
                    "A large time gap exists "
                    "between consecutive activities.",

                "gap_hours":
                    gap["gap_hours"]
            })

    # Missing timestamps
    for item in timeline:

        if not item.get(
            "timestamp_available"
        ):

            irregularities.append({

                "type":
                    "MISSING_TIMESTAMP",

                "severity":
                    "LOW",

                "timeline_id":
                    item["timeline_id"],

                "description":
                    "Activity does not contain "
                    "a usable timestamp."
            })

    return irregularities


# ============================================================
# CATEGORY SUMMARY
# ============================================================

def category_summary(
    timeline
):

    summary = {}

    for item in timeline:

        for category in item.get(
            "category",
            []
        ):

            summary[category] = (
                summary.get(
                    category,
                    0
                ) + 1
            )

    return summary


# ============================================================
# COMPLETE TIMELINE ANALYSIS
# ============================================================

def reconstruct_timeline(
    records
):

    timeline = build_timeline(
        records
    )

    timeline = sort_timeline(
        timeline
    )

    gaps = calculate_time_gaps(
        timeline
    )

    irregularities = (
        detect_irregularities(
            timeline,
            gaps
        )
    )

    timestamp_count = sum(
        1
        for item in timeline
        if item.get(
            "timestamp_available"
        )
    )

    return {

        "total_activities":
            len(timeline),

        "timestamped_activities":
            timestamp_count,

        "activities_without_timestamp":
            len(timeline)
            - timestamp_count,

        "timeline":
            timeline,

        "time_gaps":
            gaps,

        "irregularities":
            irregularities,

        "category_summary":
            category_summary(
                timeline
            ),

        "interpretation":
            (
                "Timeline reconstruction organizes "
                "available evidence activities in "
                "chronological order. Missing timestamps "
                "and large gaps are treated as analysis "
                "signals and not as proof of wrongdoing."
            )
    }