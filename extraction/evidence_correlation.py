import os
import json
import math
import hashlib
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXTRACTION_DIR = os.path.join(BASE_DIR, "extraction", "extracted_data")
CORRELATION_DIR = os.path.join(BASE_DIR, "extraction", "correlation")

os.makedirs(CORRELATION_DIR, exist_ok=True)


def clean_text(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize_text(value):
    value = clean_text(value).lower()

    return " ".join(value.split())


def unique_list(values):
    result = []

    for value in values:
        value = clean_text(value)

        if value and value not in result:
            result.append(value)

    return result


def safe_load_json(file_path):
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_extraction_result(evidence_uid):
    file_path = os.path.join(
        EXTRACTION_DIR,
        f"Extraction_{evidence_uid}.json"
    )

    return safe_load_json(file_path)


def normalize_timestamp(value):
    if not value:
        return None

    value = clean_text(value)

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def temporal_correlation(current_event, other_event):
    current_time = (
        current_event.get("timestamp")
        or current_event.get("time")
        or current_event.get("date")
    )

    other_time = (
        other_event.get("timestamp")
        or other_event.get("time")
        or other_event.get("date")
    )

    first = normalize_timestamp(current_time)
    second = normalize_timestamp(other_time)

    if not first or not second:
        return {
            "matched": False,
            "reason": "Timestamp information unavailable"
        }

    difference = abs((first - second).total_seconds())

    if difference <= 60:
        level = "VERY_CLOSE"
    elif difference <= 300:
        level = "CLOSE"
    elif difference <= 3600:
        level = "RELATED"
    else:
        level = "DISTANT"

    return {
        "matched": difference <= 3600,
        "time_difference_seconds": difference,
        "correlation_level": level
    }


def entity_correlation(current_data, other_data):
    current_entities = []

    current_entities.extend(current_data.get("persons", []))
    current_entities.extend(current_data.get("devices", []))
    current_entities.extend(current_data.get("locations", []))
    current_entities.extend(current_data.get("objects", []))

    other_entities = []

    other_entities.extend(other_data.get("persons", []))
    other_entities.extend(other_data.get("devices", []))
    other_entities.extend(other_data.get("locations", []))
    other_entities.extend(other_data.get("objects", []))

    current_normalized = {
        normalize_text(item)
        for item in current_entities
        if clean_text(item)
    }

    other_normalized = {
        normalize_text(item)
        for item in other_entities
        if clean_text(item)
    }

    common = sorted(current_normalized.intersection(other_normalized))

    return {
        "matched": len(common) > 0,
        "common_entities": common,
        "entity_match_count": len(common)
    }


def text_similarity(text1, text2):
    first = set(normalize_text(text1).split())
    second = set(normalize_text(text2).split())

    if not first or not second:
        return 0.0

    intersection = len(first.intersection(second))
    union = len(first.union(second))

    if union == 0:
        return 0.0

    return round((intersection / union) * 100, 2)


def calculate_similarity(current_data, other_data):
    current_text = " ".join(
        map(
            str,
            current_data.get("claims", [])
        )
    )

    other_text = " ".join(
        map(
            str,
            other_data.get("claims", [])
        )
    )

    return text_similarity(current_text, other_text)


def create_evidence_fingerprint(data):
    important_data = {
        "persons": data.get("persons", []),
        "devices": data.get("devices", []),
        "locations": data.get("locations", []),
        "objects": data.get("objects", []),
        "events": data.get("events", []),
        "dates": data.get("dates", []),
        "times": data.get("times", [])
    }

    raw = json.dumps(
        important_data,
        sort_keys=True,
        ensure_ascii=False
    )

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def deduplication_check(evidence_a, evidence_b):
    hash_a = clean_text(evidence_a.get("verified_hash"))
    hash_b = clean_text(evidence_b.get("verified_hash"))

    if hash_a and hash_b and hash_a == hash_b:
        return {
            "duplicate": True,
            "method": "Verified SHA-256 Hash",
            "similarity": 100.0
        }

    similarity = calculate_similarity(evidence_a, evidence_b)

    if similarity >= 90:
        return {
            "duplicate": True,
            "method": "High Content Similarity",
            "similarity": similarity
        }

    return {
        "duplicate": False,
        "method": "No duplicate detected",
        "similarity": similarity
    }


def contextual_correlation(current_data, other_data):
    current_locations = {
        normalize_text(x)
        for x in current_data.get("locations", [])
        if clean_text(x)
    }

    other_locations = {
        normalize_text(x)
        for x in other_data.get("locations", [])
        if clean_text(x)
    }

    common_locations = sorted(
        current_locations.intersection(other_locations)
    )

    current_events = {
        normalize_text(x)
        for x in current_data.get("events", [])
        if clean_text(x)
    }

    other_events = {
        normalize_text(x)
        for x in other_data.get("events", [])
        if clean_text(x)
    }

    common_events = sorted(
        current_events.intersection(other_events)
    )

    score = 0

    if common_locations:
        score += 50

    if common_events:
        score += 50

    return {
        "matched": score > 0,
        "common_locations": common_locations,
        "common_events": common_events,
        "context_score": score
    }


def calculate_corroboration_score(
    temporal_result,
    entity_result,
    contextual_result,
    similarity
):
    score = 0

    if temporal_result.get("matched"):
        score += 25

    if entity_result.get("matched"):
        score += 30

    if contextual_result.get("matched"):
        score += 25

    if similarity >= 50:
        score += 20
    elif similarity >= 25:
        score += 10

    return min(score, 100)


def correlate_two_evidence_items(evidence_a, evidence_b):
    temporal_results = []

    events_a = evidence_a.get("events", [])
    events_b = evidence_b.get("events", [])

    for event_a in events_a:
        for event_b in events_b:
            result = temporal_correlation(event_a, event_b)

            if result.get("matched"):
                temporal_results.append({
                    "event_a": event_a,
                    "event_b": event_b,
                    "result": result
                })

    entity_result = entity_correlation(
        evidence_a,
        evidence_b
    )

    contextual_result = contextual_correlation(
        evidence_a,
        evidence_b
    )

    similarity = calculate_similarity(
        evidence_a,
        evidence_b
    )

    duplicate_result = deduplication_check(
        evidence_a,
        evidence_b
    )

    corroboration_score = calculate_corroboration_score(
        {
            "matched": len(temporal_results) > 0
        },
        entity_result,
        contextual_result,
        similarity
    )

    relationship_type = "RELATED"

    if duplicate_result.get("duplicate"):
        relationship_type = "DUPLICATE"

    elif corroboration_score >= 70:
        relationship_type = "CORROBORATING"

    elif corroboration_score >= 40:
        relationship_type = "PARTIALLY_RELATED"

    return {
        "evidence_a": evidence_a.get("evidence_uid"),
        "evidence_b": evidence_b.get("evidence_uid"),
        "relationship_type": relationship_type,
        "temporal_correlation": temporal_results,
        "entity_correlation": entity_result,
        "contextual_correlation": contextual_result,
        "similarity_percentage": similarity,
        "deduplication": duplicate_result,
        "corroboration_score": corroboration_score
    }


def build_evidence_correlation(
    evidence_list
):
    relationships = []

    for i in range(len(evidence_list)):
        for j in range(i + 1, len(evidence_list)):

            result = correlate_two_evidence_items(
                evidence_list[i],
                evidence_list[j]
            )

            relationships.append(result)

    corroborating = []
    duplicates = []
    related = []

    for relationship in relationships:

        relationship_type = relationship.get(
            "relationship_type"
        )

        if relationship_type == "CORROBORATING":
            corroborating.append(relationship)

        elif relationship_type == "DUPLICATE":
            duplicates.append(relationship)

        else:
            related.append(relationship)

    return {
        "total_evidence_items": len(evidence_list),
        "total_relationships": len(relationships),
        "relationships": relationships,
        "corroboration_results": corroborating,
        "deduplication_results": duplicates,
        "related_evidence": related,
        "methodology": {
            "temporal": "Timestamp and event-time comparison",
            "contextual": "Location and event comparison",
            "entity": "Person, device, object and location comparison",
            "similarity": "Rule-based text similarity",
            "deduplication": "Hash and content similarity",
            "corroboration": "Combined correlation score"
        }
    }


def save_correlation_result(
    evidence_uid,
    correlation_result
):
    file_path = os.path.join(
        CORRELATION_DIR,
        f"Correlation_{evidence_uid}.json"
    )

    save_json(
        file_path,
        correlation_result
    )

    return file_path


def load_correlation_result(evidence_uid):
    file_path = os.path.join(
        CORRELATION_DIR,
        f"Correlation_{evidence_uid}.json"
    )

    return safe_load_json(file_path)


def run_correlation_for_evidence(
    evidence_uid,
    evidence_items
):
    correlation_result = build_evidence_correlation(
        evidence_items
    )

    correlation_result["evidence_uid"] = evidence_uid

    correlation_result["generated_at"] = (
        datetime.now().isoformat()
    )

    save_correlation_result(
        evidence_uid,
        correlation_result
    )

    return correlation_result


def get_correlation_status():
    return {
        "module": "Evidence Correlation Engine",
        "status": "READY",
        "llm_required": False,
        "supported_features": [
            "Temporal Correlation",
            "Contextual Correlation",
            "Entity Correlation",
            "Similarity Analysis",
            "Deduplication",
            "Corroboration"
        ],
        "output_folder": CORRELATION_DIR
    }