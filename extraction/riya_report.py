import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REPORT_DIR = os.path.join(
    BASE_DIR,
    "report",
    "riya"
)

os.makedirs(REPORT_DIR, exist_ok=True)


def clean(value):
    if value is None:
        return ""

    return str(value).strip()


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


def generate_riya_report(riya_result):
    """
    Creates a structured forensic report from
    the Riya Evidence Extraction & Correlation
    pipeline.

    This report contains verification signals
    and does not make a guilt or legal decision.
    """

    evidence_uid = clean(
        riya_result.get(
            "evidence_uid",
            "UNKNOWN"
        )
    )

    summary = riya_result.get(
        "summary",
        {}
    )

    report = {

        "report_title": (
            "AI Evidence Extraction & "
            "Correlation Report"
        ),

        "module_owner": "Riya",

        "evidence_uid": evidence_uid,

        "generated_at": (
            datetime.now().isoformat()
        ),

        "executive_summary": {

            "entities_detected": summary.get(
                "entities_detected",
                0
            ),

            "events_detected": summary.get(
                "events_detected",
                0
            ),

            "claims_created": summary.get(
                "claims_created",
                0
            ),

            "graph_nodes": summary.get(
                "graph_nodes",
                0
            ),

            "graph_relationships": summary.get(
                "graph_relationships",
                0
            ),

            "evidence_relationships": summary.get(
                "evidence_relationships",
                0
            ),

            "corroborating_relationships": summary.get(
                "corroborating_relationships",
                0
            ),

            "duplicate_relationships": summary.get(
                "duplicate_relationships",
                0
            ),

            "cross_validation_comparisons": (
                summary.get(
                    "cross_validation_comparisons",
                    0
                )
            )
        },

        "structured_entities": (
            riya_result.get(
                "structured_entities",
                {}
            )
        ),

        "events": riya_result.get(
            "events",
            []
        ),

        "dates": riya_result.get(
            "dates",
            []
        ),

        "times": riya_result.get(
            "times",
            []
        ),

        "claims": riya_result.get(
            "claims",
            []
        ),

        "ai_confidence": (
            riya_result.get(
                "ai_confidence",
                {}
            )
        ),

        "temporal_correlation": (
            riya_result.get(
                "temporal_correlation",
                []
            )
        ),

        "contextual_correlation": (
            riya_result.get(
                "contextual_correlation",
                []
            )
        ),

        "evidence_relationships": (
            riya_result.get(
                "evidence_relationships",
                []
            )
        ),

        "deduplication_results": (
            riya_result.get(
                "deduplication_results",
                []
            )
        ),

        "corroboration_results": (
            riya_result.get(
                "corroboration_results",
                []
            )
        ),

        "cross_validation_results": (
            riya_result.get(
                "cross_validation_results",
                {}
            )
        ),

        "knowledge_graph": (
            riya_result.get(
                "knowledge_graph",
                {}
            )
        ),

        "decision_scope": {

            "guilt_decision": False,

            "legal_decision": False,

            "evidence_authenticity_final_decision": False,

            "note": (
                "The generated results are forensic "
                "analysis signals. They support "
                "investigation and cross-validation "
                "and do not independently establish "
                "guilt, innocence, or final legal "
                "authenticity."
            )
        },

        "methodology": (
            riya_result.get(
                "methodology",
                {}
            )
        )
    }

    return report


def save_riya_report(
    riya_result
):
    report = generate_riya_report(
        riya_result
    )

    evidence_uid = clean(
        riya_result.get(
            "evidence_uid",
            "UNKNOWN"
        )
    )

    file_path = os.path.join(
        REPORT_DIR,
        f"Riya_Report_{evidence_uid}.json"
    )

    save_json(
        file_path,
        report
    )

    return file_path


def read_riya_report(
    evidence_uid
):
    file_path = os.path.join(
        REPORT_DIR,
        f"Riya_Report_{evidence_uid}.json"
    )

    return load_json(file_path)


def create_text_report(
    riya_result
):
    evidence_uid = clean(
        riya_result.get(
            "evidence_uid",
            "UNKNOWN"
        )
    )

    summary = riya_result.get(
        "summary",
        {}
    )

    entities = riya_result.get(
        "structured_entities",
        {}
    )

    lines = []

    lines.append(
        "=============================================="
    )

    lines.append(
        "AI EVIDENCE EXTRACTION & CORRELATION REPORT"
    )

    lines.append(
        "=============================================="
    )

    lines.append(
        f"Evidence UID: {evidence_uid}"
    )

    lines.append(
        f"Generated At: {datetime.now().isoformat()}"
    )

    lines.append("")

    # --------------------------------
    # SUMMARY
    # --------------------------------

    lines.append(
        "SUMMARY"
    )

    lines.append(
        "----------------------------------------------"
    )

    lines.append(
        f"Entities Detected: "
        f"{summary.get('entities_detected', 0)}"
    )

    lines.append(
        f"Events Detected: "
        f"{summary.get('events_detected', 0)}"
    )

    lines.append(
        f"Claims Created: "
        f"{summary.get('claims_created', 0)}"
    )

    lines.append(
        f"Graph Nodes: "
        f"{summary.get('graph_nodes', 0)}"
    )

    lines.append(
        f"Graph Relationships: "
        f"{summary.get('graph_relationships', 0)}"
    )

    lines.append(
        f"Evidence Relationships: "
        f"{summary.get('evidence_relationships', 0)}"
    )

    lines.append("")

    # --------------------------------
    # ENTITIES
    # --------------------------------

    lines.append(
        "STRUCTURED ENTITIES"
    )

    lines.append(
        "----------------------------------------------"
    )

    for entity_type, values in entities.items():

        lines.append(
            f"{entity_type.upper()}:"
        )

        if values:

            for value in values:

                lines.append(
                    f"  - {value}"
                )

        else:

            lines.append(
                "  - None detected"
            )

    lines.append("")

    # --------------------------------
    # EVENTS
    # --------------------------------

    lines.append(
        "EVENTS"
    )

    lines.append(
        "----------------------------------------------"
    )

    events = riya_result.get(
        "events",
        []
    )

    if events:

        for event in events:

            lines.append(
                f"- {event}"
            )

    else:

        lines.append(
            "- No events detected"
        )

    lines.append("")

    # --------------------------------
    # CLAIMS
    # --------------------------------

    lines.append(
        "CLAIMS"
    )

    lines.append(
        "----------------------------------------------"
    )

    claims = riya_result.get(
        "claims",
        []
    )

    if claims:

        for claim in claims:

            if isinstance(claim, dict):

                claim_text = (
                    claim.get(
                        "claim_text",
                        claim.get(
                            "text",
                            str(claim)
                        )
                    )
                )

                lines.append(
                    f"- {claim_text}"
                )

            else:

                lines.append(
                    f"- {claim}"
                )

    else:

        lines.append(
            "- No claims generated"
        )

    lines.append("")

    # --------------------------------
    # CORROBORATION
    # --------------------------------

    lines.append(
        "CORROBORATION RESULTS"
    )

    lines.append(
        "----------------------------------------------"
    )

    corroboration = riya_result.get(
        "corroboration_results",
        []
    )

    if corroboration:

        for item in corroboration:

            lines.append(
                f"- {item}"
            )

    else:

        lines.append(
            "- No corroboration relationship detected"
        )

    lines.append("")

    # --------------------------------
    # DEDUPLICATION
    # --------------------------------

    lines.append(
        "DEDUPLICATION RESULTS"
    )

    lines.append(
        "----------------------------------------------"
    )

    duplicates = riya_result.get(
        "deduplication_results",
        []
    )

    if duplicates:

        for item in duplicates:

            lines.append(
                f"- {item}"
            )

    else:

        lines.append(
            "- No duplicate relationship detected"
        )

    lines.append("")

    # --------------------------------
    # CROSS VALIDATION
    # --------------------------------

    lines.append(
        "CROSS-VALIDATION"
    )

    lines.append(
        "----------------------------------------------"
    )

    validation = riya_result.get(
        "cross_validation_results",
        {}
    )

    validation_summary = validation.get(
        "summary",
        {}
    )

    lines.append(
        f"Supported: "
        f"{validation_summary.get('supported_count', 0)}"
    )

    lines.append(
        f"Partially Supported: "
        f"{validation_summary.get('partially_supported_count', 0)}"
    )

    lines.append(
        f"Unsupported: "
        f"{validation_summary.get('unsupported_count', 0)}"
    )

    lines.append(
        f"Contradicted: "
        f"{validation_summary.get('contradicted_count', 0)}"
    )

    lines.append("")

    # --------------------------------
    # KNOWLEDGE GRAPH
    # --------------------------------

    graph = riya_result.get(
        "knowledge_graph",
        {}
    )

    lines.append(
        "KNOWLEDGE GRAPH"
    )

    lines.append(
        "----------------------------------------------"
    )

    lines.append(
        f"Nodes: "
        f"{graph.get('node_count', 0)}"
    )

    lines.append(
        f"Relationships: "
        f"{graph.get('relationship_count', 0)}"
    )

    lines.append("")

    # --------------------------------
    # FINAL NOTE
    # --------------------------------

    lines.append(
        "FORENSIC SCOPE"
    )

    lines.append(
        "----------------------------------------------"
    )

    lines.append(
        "These results are forensic analysis signals."
    )

    lines.append(
        "They do not independently determine guilt,"
    )

    lines.append(
        "innocence, or final legal authenticity."
    )

    lines.append("")

    lines.append(
        "=============================================="
    )

    return "\n".join(lines)


def save_text_report(
    riya_result
):
    evidence_uid = clean(
        riya_result.get(
            "evidence_uid",
            "UNKNOWN"
        )
    )

    text = create_text_report(
        riya_result
    )

    file_path = os.path.join(
        REPORT_DIR,
        f"Riya_Report_{evidence_uid}.txt"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)

    return file_path


def get_riya_report_status():
    return {

        "module": (
            "Riya Evidence Extraction "
            "and Correlation Report"
        ),

        "status": "READY",

        "formats": [
            "JSON",
            "TXT"
        ],

        "output_folder": REPORT_DIR
    }