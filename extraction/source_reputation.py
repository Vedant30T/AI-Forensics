import os
import json


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "source_reputation"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    return str(value).strip()


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value, minimum=0.0, maximum=100.0):
    return max(
        minimum,
        min(maximum, value)
    )


# ============================================================
# SOURCE TYPE
# ============================================================

SOURCE_TYPE_SCORES = {
    "forensic_image": 100,
    "system_log": 90,
    "mobile_device": 85,
    "computer": 85,
    "cctv": 80,
    "usb": 75,
    "document": 70,
    "pdf": 70,
    "image": 65,
    "video": 65,
    "audio": 65,
    "email": 65,
    "sms": 65,
    "browser": 60,
    "unknown": 50
}


def normalize_source_type(source_type):

    value = safe_text(
        source_type
    ).lower()

    value = value.replace(
        " ",
        "_"
    )

    value = value.replace(
        "-",
        "_"
    )

    if not value:
        return "unknown"

    aliases = {
        "phone": "mobile_device",
        "mobile": "mobile_device",
        "android": "mobile_device",
        "pen_drive": "usb",
        "pendrive": "usb",
        "flash_drive": "usb",
        "log": "system_log",
        "logs": "system_log",
        "forensic": "forensic_image"
    }

    return aliases.get(
        value,
        value
    )


def calculate_source_type_score(
    source_type
):

    normalized = normalize_source_type(
        source_type
    )

    return SOURCE_TYPE_SCORES.get(
        normalized,
        SOURCE_TYPE_SCORES["unknown"]
    )


# ============================================================
# SOURCE IDENTITY
# ============================================================

def calculate_identity_score(
    source_information
):

    if not isinstance(
        source_information,
        dict
    ):
        source_information = {}

    fields = [
        "source_name",
        "source_device",
        "device_id",
        "serial_number",
        "collector",
        "collection_location"
    ]

    available = 0

    for field in fields:

        if safe_text(
            source_information.get(field)
        ):
            available += 1

    if not fields:
        return 0.0

    score = (
        available
        / len(fields)
    ) * 100

    return round(
        clamp(score),
        2
    )


# ============================================================
# VERIFICATION SCORE
# ============================================================

def calculate_verification_score(
    verification_information
):

    if not isinstance(
        verification_information,
        dict
    ):
        verification_information = {}

    score = 0.0

    hash_verified = (
        verification_information.get(
            "hash_verified",
            False
        )
    )

    integrity_verified = (
        verification_information.get(
            "integrity_verified",
            False
        )
    )

    registered = (
        verification_information.get(
            "registered",
            False
        )
    )

    custody_available = (
        verification_information.get(
            "chain_of_custody_available",
            False
        )
    )

    if hash_verified:
        score += 35

    if integrity_verified:
        score += 30

    if registered:
        score += 20

    if custody_available:
        score += 15

    return round(
        clamp(score),
        2
    )


# ============================================================
# CONSISTENCY SCORE
# ============================================================

def calculate_consistency_score(
    conflict_result
):

    if not isinstance(
        conflict_result,
        dict
    ):
        return 50.0

    conflict_score = safe_float(
        conflict_result.get(
            "conflict_score",
            0
        )
    )

    score = (
        100.0
        - conflict_score
    )

    return round(
        clamp(score),
        2
    )


# ============================================================
# CORROBORATION SCORE
# ============================================================

def calculate_corroboration_score(
    correlation_information
):

    if not isinstance(
        correlation_information,
        dict
    ):
        return 0.0

    corroborating = safe_float(
        correlation_information.get(
            "corroborating_relationships",
            0
        )
    )

    total = safe_float(
        correlation_information.get(
            "evidence_relationships",
            0
        )
    )

    if total <= 0:
        return 0.0

    score = (
        corroborating
        / total
    ) * 100

    return round(
        clamp(score),
        2
    )


# ============================================================
# SOURCE HISTORY SCORE
# ============================================================

def calculate_history_score(
    history_information
):

    if not isinstance(
        history_information,
        dict
    ):
        return 50.0

    previous_checks = safe_float(
        history_information.get(
            "previous_checks",
            0
        )
    )

    successful_checks = safe_float(
        history_information.get(
            "successful_checks",
            0
        )
    )

    if previous_checks <= 0:
        return 50.0

    score = (
        successful_checks
        / previous_checks
    ) * 100

    return round(
        clamp(score),
        2
    )


# ============================================================
# RELIABILITY LEVEL
# ============================================================

def get_reliability_level(score):

    if score >= 85:
        return "VERY_HIGH"

    if score >= 70:
        return "HIGH"

    if score >= 50:
        return "MODERATE"

    if score >= 30:
        return "LOW"

    return "VERY_LOW"


# ============================================================
# MAIN SOURCE REPUTATION
# ============================================================

def calculate_source_reputation(
    source_information=None,
    verification_information=None,
    conflict_result=None,
    correlation_information=None,
    history_information=None
):

    source_information = (
        source_information
        if isinstance(
            source_information,
            dict
        )
        else {}
    )

    source_type = (
        source_information.get(
            "source_type",
            "unknown"
        )
    )

    identity_score = (
        calculate_identity_score(
            source_information
        )
    )

    verification_score = (
        calculate_verification_score(
            verification_information
        )
    )

    consistency_score = (
        calculate_consistency_score(
            conflict_result
        )
    )

    source_type_score = (
        calculate_source_type_score(
            source_type
        )
    )

    corroboration_score = (
        calculate_corroboration_score(
            correlation_information
        )
    )

    history_score = (
        calculate_history_score(
            history_information
        )
    )

    # --------------------------------------------------------
    # WEIGHTED RELIABILITY SCORE
    # --------------------------------------------------------

    reliability_score = (

        identity_score * 0.15

        + verification_score * 0.25

        + consistency_score * 0.20

        + source_type_score * 0.10

        + corroboration_score * 0.20

        + history_score * 0.10
    )

    reliability_score = round(
        clamp(
            reliability_score
        ),
        2
    )

    reliability_level = (
        get_reliability_level(
            reliability_score
        )
    )

    reliability_factors = {

        "source_identity":
            identity_score,

        "source_verification":
            verification_score,

        "source_consistency":
            consistency_score,

        "source_type":
            source_type_score,

        "corroboration":
            corroboration_score,

        "source_history":
            history_score
    }

    result = {

        "source_type":
            normalize_source_type(
                source_type
            ),

        "source_reputation_score":
            reliability_score,

        "source_reliability_level":
            reliability_level,

        "source_reliability_factors":
            reliability_factors,

        "interpretation": (
            "The source reputation score represents "
            "a forensic reliability factor based on "
            "available source information, verification, "
            "consistency and corroboration. It does not "
            "represent absolute truth or a final legal "
            "authenticity decision."
        )
    }

    return result


# ============================================================
# SAVE RESULT
# ============================================================

def save_source_reputation(
    result,
    evidence_uid="UNKNOWN"
):

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "_-"
        else "_"
        for character in str(
            evidence_uid
        )
    )

    file_path = os.path.join(
        OUTPUT_DIR,
        f"Source_Reputation_{safe_uid}.json"
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
            ensure_ascii=False
        )

    return file_path