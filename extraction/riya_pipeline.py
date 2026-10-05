import os
import json
from datetime import datetime

from extraction.evidence_preprocessor import preprocess_evidence
from extraction.evidence_extractor import extract_evidence_information
from extraction.claim_engine import create_claims_from_extraction
from extraction.evidence_correlation import build_evidence_correlation
from extraction.knowledge_graph import build_knowledge_graph
from extraction.cross_validation import cross_validate_evidence_set


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RIYA_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "riya_output"
)

os.makedirs(RIYA_DIR, exist_ok=True)


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


def run_riya_pipeline(
    evidence_path,
    evidence_uid,
    verified_hash="",
    metadata=None,
    integrity_result=None,
    evidence_items=None
):
    """
    Complete  Evidence Extraction and Correlation pipeline.

    Flow:

    Evidence
        ↓
    Pre-processing
        ↓
    Evidence Extraction
        ↓
    Claim Creation
        ↓
    Evidence Correlation
        ↓
    Knowledge Graph
        ↓
    Cross Validation
        ↓
 Output
    """

    metadata = metadata or {}
    evidence_items = evidence_items or []

    # ---------------------------------
    # STEP 1: PRE-PROCESSING
    # ---------------------------------

    preprocessing_result = preprocess_evidence(
        file_path=evidence_path,
        evidence_uid=evidence_uid,
        verified_hash=verified_hash,
        metadata=metadata,
        integrity_result=integrity_result
    )

    # ---------------------------------
    # STEP 2: EVIDENCE EXTRACTION
    # ---------------------------------

    extraction_result = extract_evidence_information(
        file_path=evidence_path,
        evidence_uid=evidence_uid,
        verified_hash=verified_hash,
        metadata=metadata,
        integrity_result=integrity_result
    )

    # ---------------------------------
    # STEP 3: CLAIM CREATION
    # ---------------------------------

    claim_result = create_claims_from_extraction(
        extraction_result
    )

    # ---------------------------------
    # CURRENT EVIDENCE OBJECT
    # ---------------------------------

    current_evidence = {
        "evidence_uid": evidence_uid,
        "verified_hash": verified_hash,
        "persons": extraction_result.get(
            "persons",
            []
        ),
        "devices": extraction_result.get(
            "devices",
            []
        ),
        "locations": extraction_result.get(
            "locations",
            []
        ),
        "objects": extraction_result.get(
            "objects",
            []
        ),
        "events": extraction_result.get(
            "events",
            []
        ),
        "dates": extraction_result.get(
            "dates",
            []
        ),
        "times": extraction_result.get(
            "times",
            []
        ),
        "claims": claim_result.get(
            "claims",
            []
        )
    }

    # Add current evidence to correlation set
    all_evidence = list(evidence_items)

    current_uid_exists = False

    for item in all_evidence:
        if item.get("evidence_uid") == evidence_uid:
            current_uid_exists = True
            break

    if not current_uid_exists:
        all_evidence.append(
            current_evidence
        )

    # ---------------------------------
    # STEP 4: EVIDENCE CORRELATION
    # ---------------------------------

    correlation_result = build_evidence_correlation(
        all_evidence
    )

    # ---------------------------------
    # STEP 5: KNOWLEDGE GRAPH
    # ---------------------------------

    graph_result = build_knowledge_graph(
        evidence_uid=evidence_uid,
        extraction_result=extraction_result,
        correlation_result=correlation_result
    )

    # ---------------------------------
    # STEP 6: CROSS VALIDATION
    # ---------------------------------

    validation_result = cross_validate_evidence_set(
        all_evidence,
        correlation_result
    )

    # ---------------------------------
    # CORROBORATION
    # ---------------------------------

    corroboration_results = (
        correlation_result.get(
            "corroboration_results",
            []
        )
    )

    # ---------------------------------
    # DEDUPLICATION
    # ---------------------------------

    deduplication_results = (
        correlation_result.get(
            "deduplication_results",
            []
        )
    )

    # ---------------------------------
    # TEMPORAL CORRELATION
    # ---------------------------------

    temporal_correlation = []

    for relationship in correlation_result.get(
        "relationships",
        []
    ):

        temporal_items = relationship.get(
            "temporal_correlation",
            []
        )

        for item in temporal_items:
            temporal_correlation.append(
                item
            )

    # ---------------------------------
    # CONTEXTUAL CORRELATION
    # ---------------------------------

    contextual_correlation = []

    for relationship in correlation_result.get(
        "relationships",
        []
    ):

        contextual = relationship.get(
            "contextual_correlation",
            {}
        )

        if contextual.get("matched"):
            contextual_correlation.append(
                contextual
            )

    # ---------------------------------
    # EVIDENCE RELATIONSHIPS
    # ---------------------------------

    evidence_relationships = (
        correlation_result.get(
            "relationships",
            []
        )
    )

    # ---------------------------------
    # FINAL OUTPUT
    # ---------------------------------

    riya_result = {

        "module": (
            "AI Evidence Extraction & Correlation"
        ),

        "module_owner": "Riya",

        "evidence_uid": evidence_uid,

        "generated_at": (
            datetime.now().isoformat()
        ),

        "input": {

            "evidence_path": evidence_path,

            "evidence_uid": evidence_uid,

            "verified_hash": verified_hash,

            "metadata": metadata,

            "integrity_result": (
                integrity_result or {}
            )
        },

        "preprocessing": preprocessing_result,

        "structured_entities": {

            "persons": extraction_result.get(
                "persons",
                []
            ),

            "devices": extraction_result.get(
                "devices",
                []
            ),

            "locations": extraction_result.get(
                "locations",
                []
            ),

            "objects": extraction_result.get(
                "objects",
                []
            )
        },

        "events": extraction_result.get(
            "events",
            []
        ),

        "dates": extraction_result.get(
            "dates",
            []
        ),

        "times": extraction_result.get(
            "times",
            []
        ),

        "claims": claim_result.get(
            "claims",
            []
        ),

        "ai_confidence": extraction_result.get(
            "ai_confidence",
            {
                "score": 0,
                "method": (
                    "Rule-Based Extraction Confidence"
                )
            }
        ),

        "knowledge_graph": graph_result,

        "evidence_relationships": (
            evidence_relationships
        ),

        "temporal_correlation": (
            temporal_correlation
        ),

        "contextual_correlation": (
            contextual_correlation
        ),

        "deduplication_results": (
            deduplication_results
        ),

        "cross_validation_results": (
            validation_result
        ),

        "corroboration_results": (
            corroboration_results
        ),

        "summary": {

            "entities_detected": (
                len(
                    extraction_result.get(
                        "persons",
                        []
                    )
                )
                +
                len(
                    extraction_result.get(
                        "devices",
                        []
                    )
                )
                +
                len(
                    extraction_result.get(
                        "locations",
                        []
                    )
                )
                +
                len(
                    extraction_result.get(
                        "objects",
                        []
                    )
                )
            ),

            "events_detected": len(
                extraction_result.get(
                    "events",
                    []
                )
            ),

            "claims_created": len(
                claim_result.get(
                    "claims",
                    []
                )
            ),

            "graph_nodes": graph_result.get(
                "node_count",
                0
            ),

            "graph_relationships": graph_result.get(
                "relationship_count",
                0
            ),

            "evidence_relationships": len(
                evidence_relationships
            ),

            "corroborating_relationships": len(
                corroboration_results
            ),

            "duplicate_relationships": len(
                deduplication_results
            ),

            "cross_validation_comparisons": (
                validation_result.get(
                    "total_comparisons",
                    0
                )
            )
        },

        "decision_scope": {

            "guilt_decision": False,

            "final_legal_decision": False,

            "purpose": (
                "Generate structured evidence "
                "signals, relationships and "
                "validation results for forensic "
                "investigation."
            )
        },

        "methodology": {

            "llm_required": False,

            "preprocessing": True,

            "rule_based_extraction": True,

            "claim_creation": True,

            "temporal_correlation": True,

            "contextual_correlation": True,

            "entity_correlation": True,

            "deduplication": True,

            "corroboration": True,

            "knowledge_graph": True,

            "cross_validation": True
        }
    }

    # ---------------------------------
    # SAVE FINAL RESULT
    # ---------------------------------

    output_file = os.path.join(
        RIYA_DIR,
        f"Riya_Result_{evidence_uid}.json"
    )

    save_json(
        output_file,
        riya_result
    )

    riya_result["output_file"] = output_file

    return riya_result


def load_riya_result(evidence_uid):
    file_path = os.path.join(
        RIYA_DIR,
        f"Riya_Result_{evidence_uid}.json"
    )

    return load_json(file_path)


def get_riya_status():
    return {

        "module": (
            "AI Evidence Extraction & Correlation"
        ),

        "owner": "Riya",

        "status": "READY",

        "llm_required": False,

        "pipeline": [

            "Evidence Pre-processing",

            "AI Evidence Extraction",

            "Claim Creation",

            "Evidence Correlation",

            "Knowledge Graph",

            "Cross Validation",

            " Output"
        ],

        "output_folder": RIYA_DIR
    }