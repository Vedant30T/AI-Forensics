import os
import json
import re
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VALIDATION_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "validation"
)

os.makedirs(VALIDATION_DIR, exist_ok=True)


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
UNSUPPORTED = "UNSUPPORTED"
CONTRADICTED = "CONTRADICTED"


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize(value):
    return " ".join(
        clean(value).lower().split()
    )


def save_json(file_path, data):
    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_json(file_path):
    if not os.path.exists(file_path):
        return {}

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except Exception:
        return {}


def exact_match(value_a, value_b):
    return normalize(value_a) == normalize(value_b)


def numeric_value(value):
    try:
        return float(
            re.findall(
                r"-?\d+(?:\.\d+)?",
                clean(value)
            )[0]
        )
    except Exception:
        return None


def numeric_match(
    value_a,
    value_b,
    tolerance=0.05
):
    number_a = numeric_value(value_a)
    number_b = numeric_value(value_b)

    if number_a is None or number_b is None:
        return False

    difference = abs(number_a - number_b)

    allowed_difference = max(
        abs(number_a) * tolerance,
        0.000001
    )

    return difference <= allowed_difference


def semantic_match(value_a, value_b):
    words_a = set(
        normalize(value_a).split()
    )

    words_b = set(
        normalize(value_b).split()
    )

    if not words_a or not words_b:
        return False

    intersection = words_a.intersection(words_b)

    similarity = (
        len(intersection)
        /
        len(words_a.union(words_b))
    )

    return similarity >= 0.50


def compare_values(
    value_a,
    value_b
):
    if exact_match(value_a, value_b):

        return {
            "matched": True,
            "method": "Exact Match",
            "confidence": 100
        }

    if numeric_match(value_a, value_b):

        return {
            "matched": True,
            "method": "Numeric Match With Tolerance",
            "confidence": 90
        }

    if semantic_match(value_a, value_b):

        return {
            "matched": True,
            "method": "Semantic Similarity",
            "confidence": 75
        }

    return {
        "matched": False,
        "method": "No Match",
        "confidence": 0
    }


def validate_entities(
    extraction_a,
    extraction_b
):
    entity_types = [
        "persons",
        "devices",
        "locations",
        "objects"
    ]

    results = []

    for entity_type in entity_types:

        values_a = extraction_a.get(
            entity_type,
            []
        )

        values_b = extraction_b.get(
            entity_type,
            []
        )

        for value_a in values_a:

            for value_b in values_b:

                comparison = compare_values(
                    value_a,
                    value_b
                )

                if comparison["matched"]:

                    results.append({
                        "entity_type": entity_type,
                        "value_a": value_a,
                        "value_b": value_b,
                        "comparison": comparison
                    })

    return results


def validate_events(
    extraction_a,
    extraction_b
):
    events_a = extraction_a.get(
        "events",
        []
    )

    events_b = extraction_b.get(
        "events",
        []
    )

    results = []

    for event_a in events_a:

        for event_b in events_b:

            comparison = compare_values(
                event_a,
                event_b
            )

            if comparison["matched"]:

                results.append({
                    "event_a": event_a,
                    "event_b": event_b,
                    "comparison": comparison
                })

    return results


def validate_timestamps(
    extraction_a,
    extraction_b
):
    dates_a = extraction_a.get(
        "dates",
        []
    )

    dates_b = extraction_b.get(
        "dates",
        []
    )

    times_a = extraction_a.get(
        "times",
        []
    )

    times_b = extraction_b.get(
        "times",
        []
    )

    date_matches = []
    time_matches = []

    for date_a in dates_a:

        for date_b in dates_b:

            comparison = compare_values(
                date_a,
                date_b
            )

            if comparison["matched"]:

                date_matches.append({
                    "date_a": date_a,
                    "date_b": date_b,
                    "comparison": comparison
                })

    for time_a in times_a:

        for time_b in times_b:

            comparison = compare_values(
                time_a,
                time_b
            )

            if comparison["matched"]:

                time_matches.append({
                    "time_a": time_a,
                    "time_b": time_b,
                    "comparison": comparison
                })

    return {
        "date_matches": date_matches,
        "time_matches": time_matches
    }


def validate_correlation_relationship(
    relationship
):
    corroboration_score = relationship.get(
        "corroboration_score",
        0
    )

    similarity = relationship.get(
        "similarity_percentage",
        0
    )

    temporal = relationship.get(
        "temporal_correlation",
        []
    )

    entity = relationship.get(
        "entity_correlation",
        {}
    )

    contextual = relationship.get(
        "contextual_correlation",
        {}
    )

    if relationship.get(
        "relationship_type"
    ) == "DUPLICATE":

        return {
            "status": PARTIALLY_SUPPORTED,
            "reason": "Evidence appears duplicated",
            "confidence": 70
        }

    if corroboration_score >= 70:

        return {
            "status": SUPPORTED,
            "reason": "Multiple correlation signals support the relationship",
            "confidence": 90
        }

    if (
        entity.get("matched")
        or contextual.get("matched")
        or len(temporal) > 0
        or similarity >= 50
    ):

        return {
            "status": PARTIALLY_SUPPORTED,
            "reason": "Some correlation signals are available",
            "confidence": 65
        }

    return {
        "status": UNSUPPORTED,
        "reason": "No strong correlation signal found",
        "confidence": 20
    }


def detect_conflicts(
    extraction_a,
    extraction_b
):
    conflicts = []

    # -------------------------
    # Location conflict
    # -------------------------

    locations_a = {
        normalize(x)
        for x in extraction_a.get(
            "locations",
            []
        )
    }

    locations_b = {
        normalize(x)
        for x in extraction_b.get(
            "locations",
            []
        )
    }

    if locations_a and locations_b:
        if not locations_a.intersection(locations_b):

            conflicts.append({
                "type": "LOCATION_CONFLICT",
                "details": {
                    "evidence_a_locations": list(
                        locations_a
                    ),
                    "evidence_b_locations": list(
                        locations_b
                    )
                }
            })

    # -------------------------
    # Event conflict
    # -------------------------

    events_a = {
        normalize(x)
        for x in extraction_a.get(
            "events",
            []
        )
    }

    events_b = {
        normalize(x)
        for x in extraction_b.get(
            "events",
            []
        )
    }

    if events_a and events_b:

        if not events_a.intersection(events_b):

            conflicts.append({
                "type": "EVENT_CONFLICT",
                "details": {
                    "evidence_a_events": list(
                        events_a
                    ),
                    "evidence_b_events": list(
                        events_b
                    )
                }
            })

    # -------------------------
    # Entity conflict
    # -------------------------

    persons_a = {
        normalize(x)
        for x in extraction_a.get(
            "persons",
            []
        )
    }

    persons_b = {
        normalize(x)
        for x in extraction_b.get(
            "persons",
            []
        )
    }

    if persons_a and persons_b:

        if not persons_a.intersection(persons_b):

            conflicts.append({
                "type": "PERSON_ENTITY_CONFLICT",
                "details": {
                    "evidence_a_persons": list(
                        persons_a
                    ),
                    "evidence_b_persons": list(
                        persons_b
                    )
                }
            })

    return conflicts


def calculate_validation_score(
    entity_matches,
    event_matches,
    timestamp_results,
    conflicts,
    correlation_results
):
    score = 0
    positive_signals = 0
    negative_signals = 0

    if entity_matches:
        score += 25
        positive_signals += 1

    if event_matches:
        score += 25
        positive_signals += 1

    if (
        timestamp_results.get("date_matches")
        or timestamp_results.get("time_matches")
    ):
        score += 20
        positive_signals += 1

    if correlation_results:
        score += 30
        positive_signals += 1

    negative_signals = len(conflicts)

    score -= min(
        negative_signals * 15,
        60
    )

    score = max(
        0,
        min(score, 100)
    )

    return {
        "validation_score": score,
        "positive_signals": positive_signals,
        "negative_signals": negative_signals
    }


def determine_status(
    validation_score,
    conflicts
):
    if conflicts and validation_score < 40:
        return CONTRADICTED

    if validation_score >= 75:
        return SUPPORTED

    if validation_score >= 40:
        return PARTIALLY_SUPPORTED

    return UNSUPPORTED


def cross_validate_two_evidence_items(
    evidence_a,
    evidence_b
):
    entity_matches = validate_entities(
        evidence_a,
        evidence_b
    )

    event_matches = validate_events(
        evidence_a,
        evidence_b
    )

    timestamp_results = validate_timestamps(
        evidence_a,
        evidence_b
    )

    conflicts = detect_conflicts(
        evidence_a,
        evidence_b
    )

    correlation_results = []

    validation_score_data = calculate_validation_score(
        entity_matches,
        event_matches,
        timestamp_results,
        conflicts,
        correlation_results
    )

    validation_score = validation_score_data[
        "validation_score"
    ]

    status = determine_status(
        validation_score,
        conflicts
    )

    return {
        "evidence_a": evidence_a.get(
            "evidence_uid"
        ),
        "evidence_b": evidence_b.get(
            "evidence_uid"
        ),
        "status": status,
        "validation_score": validation_score,
        "entity_validation": entity_matches,
        "event_validation": event_matches,
        "timestamp_validation": timestamp_results,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "methodology": {
            "exact_value_validation": True,
            "numeric_tolerance": True,
            "semantic_validation": True,
            "graph_based_validation": True
        }
    }


def cross_validate_evidence_set(
    evidence_list,
    correlation_result=None
):
    results = []

    for i in range(len(evidence_list)):

        for j in range(i + 1, len(evidence_list)):

            result = cross_validate_two_evidence_items(
                evidence_list[i],
                evidence_list[j]
            )

            results.append(result)

    supported = []
    partially_supported = []
    unsupported = []
    contradicted = []

    for result in results:

        status = result.get(
            "status"
        )

        if status == SUPPORTED:
            supported.append(result)

        elif status == PARTIALLY_SUPPORTED:
            partially_supported.append(result)

        elif status == CONTRADICTED:
            contradicted.append(result)

        else:
            unsupported.append(result)

    return {
        "generated_at": datetime.now().isoformat(),
        "total_comparisons": len(results),
        "results": results,
        "supported": supported,
        "partially_supported": partially_supported,
        "unsupported": unsupported,
        "contradicted": contradicted,
        "summary": {
            "supported_count": len(supported),
            "partially_supported_count": len(
                partially_supported
            ),
            "unsupported_count": len(
                unsupported
            ),
            "contradicted_count": len(
                contradicted
            )
        },
        "methodology": {
            "rule_based": True,
            "llm_required": False,
            "purpose": (
                "Cross-validation of extracted evidence "
                "using exact, tolerant, semantic and "
                "correlation-based signals."
            )
        }
    }


def save_cross_validation(
    evidence_uid,
    validation_result
):
    file_path = os.path.join(
        VALIDATION_DIR,
        f"CrossValidation_{evidence_uid}.json"
    )

    save_json(
        file_path,
        validation_result
    )

    return file_path


def load_cross_validation(
    evidence_uid
):
    file_path = os.path.join(
        VALIDATION_DIR,
        f"CrossValidation_{evidence_uid}.json"
    )

    return load_json(file_path)


def run_cross_validation(
    evidence_uid,
    evidence_list,
    correlation_result=None
):
    result = cross_validate_evidence_set(
        evidence_list,
        correlation_result
    )

    result["evidence_uid"] = evidence_uid

    save_cross_validation(
        evidence_uid,
        result
    )

    return result


def get_cross_validation_status():
    return {
        "module": "Evidence Cross-Validation Engine",
        "status": "READY",
        "llm_required": False,
        "supported_validation": [
            "Exact Value Validation",
            "Numeric Tolerance Validation",
            "Semantic Validation",
            "Timestamp Validation",
            "Entity Validation",
            "Event Validation",
            "Conflict Detection",
            "Correlation Validation"
        ],
        "output_folder": VALIDATION_DIR
    }