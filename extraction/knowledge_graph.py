import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRAPH_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "knowledge_graph"
)

os.makedirs(GRAPH_DIR, exist_ok=True)


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def normalize(value):
    return " ".join(
        clean(value).lower().split()
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


def create_node(
    node_id,
    node_type,
    label,
    evidence_uid,
    properties=None
):
    return {
        "node_id": clean(node_id),
        "node_type": clean(node_type),
        "label": clean(label),
        "evidence_uid": clean(evidence_uid),
        "properties": properties or {}
    }


def create_relationship(
    source,
    relationship,
    target,
    evidence_uid,
    provenance=None
):
    return {
        "source": clean(source),
        "relationship": clean(relationship),
        "target": clean(target),
        "evidence_uid": clean(evidence_uid),
        "provenance": provenance or {
            "source": "Evidence Extraction & Correlation",
            "verification": "Rule-Based"
        }
    }


def add_node(nodes, node):
    for existing in nodes:

        if existing["node_id"] == node["node_id"]:
            return

    nodes.append(node)


def add_relationship(
    relationships,
    relationship
):
    for existing in relationships:

        if (
            existing["source"]
            == relationship["source"]
            and existing["relationship"]
            == relationship["relationship"]
            and existing["target"]
            == relationship["target"]
        ):
            return

    relationships.append(relationship)


def build_knowledge_graph(
    evidence_uid,
    extraction_result,
    correlation_result=None
):
    nodes = []
    relationships = []

    evidence_node_id = f"EVIDENCE:{evidence_uid}"

    add_node(
        nodes,
        create_node(
            evidence_node_id,
            "Evidence",
            evidence_uid,
            evidence_uid,
            {
                "evidence_uid": evidence_uid
            }
        )
    )

    persons = extraction_result.get(
        "persons",
        []
    )

    devices = extraction_result.get(
        "devices",
        []
    )

    locations = extraction_result.get(
        "locations",
        []
    )

    objects = extraction_result.get(
        "objects",
        []
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

    # -----------------------------
    # PERSON NODES
    # -----------------------------

    for index, person in enumerate(
        persons,
        start=1
    ):

        person_id = (
            f"PERSON:{normalize(person)}"
        )

        add_node(
            nodes,
            create_node(
                person_id,
                "Person",
                person,
                evidence_uid
            )
        )

        add_relationship(
            relationships,
            create_relationship(
                evidence_node_id,
                "contains_person",
                person_id,
                evidence_uid
            )
        )

    # -----------------------------
    # DEVICE NODES
    # -----------------------------

    for index, device in enumerate(
        devices,
        start=1
    ):

        device_id = (
            f"DEVICE:{normalize(device)}"
        )

        add_node(
            nodes,
            create_node(
                device_id,
                "Device",
                device,
                evidence_uid
            )
        )

        add_relationship(
            relationships,
            create_relationship(
                evidence_node_id,
                "contains_device",
                device_id,
                evidence_uid
            )
        )

    # -----------------------------
    # LOCATION NODES
    # -----------------------------

    for location in locations:

        location_id = (
            f"LOCATION:{normalize(location)}"
        )

        add_node(
            nodes,
            create_node(
                location_id,
                "Location",
                location,
                evidence_uid
            )
        )

        add_relationship(
            relationships,
            create_relationship(
                evidence_node_id,
                "contains_location",
                location_id,
                evidence_uid
            )
        )

    # -----------------------------
    # OBJECT NODES
    # -----------------------------

    for obj in objects:

        object_id = (
            f"OBJECT:{normalize(obj)}"
        )

        add_node(
            nodes,
            create_node(
                object_id,
                "Object",
                obj,
                evidence_uid
            )
        )

        add_relationship(
            relationships,
            create_relationship(
                evidence_node_id,
                "contains_object",
                object_id,
                evidence_uid
            )
        )

    # -----------------------------
    # EVENT NODES
    # -----------------------------

    for index, event in enumerate(
        events,
        start=1
    ):

        event_id = (
            f"EVENT:{evidence_uid}:{index}"
        )

        add_node(
            nodes,
            create_node(
                event_id,
                "Event",
                event,
                evidence_uid
            )
        )

        add_relationship(
            relationships,
            create_relationship(
                evidence_node_id,
                "supports_event",
                event_id,
                evidence_uid
            )
        )

    # -----------------------------
    # TIMESTAMP NODES
    # -----------------------------

    time_values = []

    time_values.extend(dates)
    time_values.extend(times)

    for index, time_value in enumerate(
        time_values,
        start=1
    ):

        timestamp_id = (
            f"TIMESTAMP:{evidence_uid}:{index}"
        )

        add_node(
            nodes,
            create_node(
                timestamp_id,
                "Timestamp",
                time_value,
                evidence_uid
            )
        )

    # -----------------------------
    # PERSON -> DEVICE
    # -----------------------------

    for person in persons:

        person_id = (
            f"PERSON:{normalize(person)}"
        )

        for device in devices:

            device_id = (
                f"DEVICE:{normalize(device)}"
            )

            add_relationship(
                relationships,
                create_relationship(
                    person_id,
                    "used",
                    device_id,
                    evidence_uid
                )
            )

    # -----------------------------
    # PERSON -> LOCATION
    # -----------------------------

    for person in persons:

        person_id = (
            f"PERSON:{normalize(person)}"
        )

        for location in locations:

            location_id = (
                f"LOCATION:{normalize(location)}"
            )

            add_relationship(
                relationships,
                create_relationship(
                    person_id,
                    "associated_with",
                    location_id,
                    evidence_uid
                )
            )

    # -----------------------------
    # DEVICE -> LOCATION
    # -----------------------------

    for device in devices:

        device_id = (
            f"DEVICE:{normalize(device)}"
        )

        for location in locations:

            location_id = (
                f"LOCATION:{normalize(location)}"
            )

            add_relationship(
                relationships,
                create_relationship(
                    device_id,
                    "located_at",
                    location_id,
                    evidence_uid
                )
            )

    # -----------------------------
    # PERSON -> OBJECT
    # -----------------------------

    for person in persons:

        person_id = (
            f"PERSON:{normalize(person)}"
        )

        for obj in objects:

            object_id = (
                f"OBJECT:{normalize(obj)}"
            )

            add_relationship(
                relationships,
                create_relationship(
                    person_id,
                    "associated_with",
                    object_id,
                    evidence_uid
                )
            )

    # -----------------------------
    # EVENT -> TIMESTAMP
    # -----------------------------

    event_index = 1

    for event in events:

        event_id = (
            f"EVENT:{evidence_uid}:{event_index}"
        )

        for index, time_value in enumerate(
            time_values,
            start=1
        ):

            timestamp_id = (
                f"TIMESTAMP:{evidence_uid}:{index}"
            )

            add_relationship(
                relationships,
                create_relationship(
                    event_id,
                    "occurred_at",
                    timestamp_id,
                    evidence_uid
                )
            )

        event_index += 1

    # -----------------------------
    # EVIDENCE CORRELATION
    # -----------------------------

    if correlation_result:

        correlation_relationships = (
            correlation_result.get(
                "relationships",
                []
            )
        )

        for item in correlation_relationships:

            evidence_a = clean(
                item.get("evidence_a")
            )

            evidence_b = clean(
                item.get("evidence_b")
            )

            relationship_type = clean(
                item.get("relationship_type")
            )

            if not evidence_a or not evidence_b:
                continue

            source_id = f"EVIDENCE:{evidence_a}"
            target_id = f"EVIDENCE:{evidence_b}"

            if relationship_type == "CORROBORATING":

                relation = "corroborates"

            elif relationship_type == "DUPLICATE":

                relation = "duplicate_of"

            elif relationship_type == "PARTIALLY_RELATED":

                relation = "partially_supports"

            else:

                relation = "related_to"

            provenance = {
                "source": "Evidence Correlation Engine",
                "relationship_type": relationship_type,
                "corroboration_score": item.get(
                    "corroboration_score",
                    0
                ),
                "similarity_percentage": item.get(
                    "similarity_percentage",
                    0
                )
            }

            add_relationship(
                relationships,
                create_relationship(
                    source_id,
                    relation,
                    target_id,
                    evidence_uid,
                    provenance
                )
            )

    return {
        "evidence_uid": evidence_uid,
        "generated_at": datetime.now().isoformat(),
        "nodes": nodes,
        "relationships": relationships,
        "node_count": len(nodes),
        "relationship_count": len(relationships),
        "graph_type": "Digital Forensic Knowledge Graph",
        "methodology": {
            "nodes": [
                "Person",
                "Device",
                "Evidence",
                "Event",
                "Location",
                "Timestamp",
                "Object"
            ],
            "relationships": [
                "used",
                "associated_with",
                "located_at",
                "supports_event",
                "occurred_at",
                "corroborates",
                "duplicate_of",
                "related_to"
            ],
            "provenance_tracking": True
        }
    }


def save_knowledge_graph(
    evidence_uid,
    graph_result
):
    file_path = os.path.join(
        GRAPH_DIR,
        f"KnowledgeGraph_{evidence_uid}.json"
    )

    save_json(
        file_path,
        graph_result
    )

    return file_path


def load_knowledge_graph(evidence_uid):
    file_path = os.path.join(
        GRAPH_DIR,
        f"KnowledgeGraph_{evidence_uid}.json"
    )

    return load_json(file_path)


def run_knowledge_graph(
    evidence_uid,
    extraction_result,
    correlation_result=None
):
    graph_result = build_knowledge_graph(
        evidence_uid,
        extraction_result,
        correlation_result
    )

    save_knowledge_graph(
        evidence_uid,
        graph_result
    )

    return graph_result


def get_graph_status():
    return {
        "module": "Digital Forensic Knowledge Graph",
        "status": "READY",
        "llm_required": False,
        "provenance_tracking": True,
        "supported_nodes": [
            "Person",
            "Device",
            "Evidence",
            "Event",
            "Location",
            "Timestamp",
            "Object"
        ],
        "output_folder": GRAPH_DIR
    }