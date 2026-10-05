import os
import json

from extraction.timeline_reconstruction import (
    reconstruct_timeline
)

from extraction.behavior_correlation import (
    correlate_behavior
)

from extraction.conflict_detection import (
    detect_conflicts
)

from extraction.source_reputation import (
    calculate_source_reputation
)

from extraction.behavior_report import (
    save_json_report,
    save_text_report
)


# ============================================================
# MAIN ANALYSIS PIPELINE
# ============================================================

def run_analysis(
    riya_result,
    source_information=None,
    verification_information=None,
    history_information=None
):
    """
    Complete behavioural evidence analysis pipeline.

    Input:
        Structured and correlated evidence result.

    Output:
        Timeline
        Behaviour correlation
        Conflict analysis
        Source reputation
        Overall analysis result
    """

    if not isinstance(
        riya_result,
        dict
    ):
        raise ValueError(
            "Input evidence result must be a dictionary."
        )

    # --------------------------------------------------------
    # COLLECT RECORDS
    # --------------------------------------------------------

    records = []

    events = riya_result.get(
        "events",
        []
    )

    claims = riya_result.get(
        "claims",
        []
    )

    structured_entities = (
        riya_result.get(
            "structured_entities",
            {}
        )
    )

    if isinstance(events, list):
        records.extend(events)

    if isinstance(claims, list):
        records.extend(claims)

    # --------------------------------------------------------
    # ADD STRUCTURED ENTITIES
    # --------------------------------------------------------

    if isinstance(
        structured_entities,
        dict
    ):

        for entity_type, values in (
            structured_entities.items()
        ):

            if isinstance(
                values,
                list
            ):

                for value in values:

                    records.append({

                        "entity_type":
                            entity_type,

                        "entity":
                            value,

                        "description":
                            str(value)
                    })

    # --------------------------------------------------------
    # TIMELINE
    # --------------------------------------------------------

    timeline_result = (
        reconstruct_timeline(
            records
        )
    )

    # --------------------------------------------------------
    # BEHAVIOUR CORRELATION
    # --------------------------------------------------------

    correlation_result = (
        correlate_behavior(
            records
        )
    )

    # --------------------------------------------------------
    # CONFLICT DETECTION
    # --------------------------------------------------------

    conflict_result = (
        detect_conflicts(
            records
        )
    )

    # --------------------------------------------------------
    # SOURCE REPUTATION
    # --------------------------------------------------------

    if source_information is None:
        source_information = {}

    if verification_information is None:
        verification_information = {}

    if history_information is None:
        history_information = {}

    reputation_result = (
        calculate_source_reputation(

            source_information=
                source_information,

            verification_information=
                verification_information,

            conflict_result=
                conflict_result,

            correlation_information=
                correlation_result,

            history_information=
                history_information
        )
    )

    # --------------------------------------------------------
    # BEHAVIOUR SCORE
    # --------------------------------------------------------

    total_activities = (
        timeline_result.get(
            "total_activities",
            0
        )
    )

    total_irregularities = len(
        timeline_result.get(
            "irregularities",
            []
        )
    )

    if total_activities == 0:

        behaviour_score = 0.0

    else:

        behaviour_score = (
            100
            - (
                total_irregularities
                / total_activities
                * 100
            )
        )

        behaviour_score = max(
            0.0,
            min(
                100.0,
                behaviour_score
            )
        )

    behaviour_score = round(
        behaviour_score,
        2
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    result = {

        "module":
            "Behavioural Evidence Analysis",

        "evidence_uid":
            riya_result.get(
                "evidence_uid",
                ""
            ),

        "behaviour_score":
            behaviour_score,

        "timeline_reconstruction":
            timeline_result.get(
                "timeline",
                []
            ),

        "timeline_analysis":
            timeline_result,

        "behaviour_evidence_correlation":
            correlation_result,

        "conflict_analysis":
            conflict_result,

        "source_reputation":
            reputation_result,

        "summary": {

            "activities":
                total_activities,

            "timeline_irregularities":
                total_irregularities,

            "behaviour_correlations":
                correlation_result.get(
                    "total_correlations",
                    0
                ),

            "conflicts":
                conflict_result.get(
                    "total_conflicts",
                    0
                ),

            "conflict_score":
                conflict_result.get(
                    "conflict_score",
                    0
                ),

            "source_reputation_score":
                reputation_result.get(
                    "source_reputation_score",
                    0
                ),

            "reliability_level":
                reputation_result.get(
                    "source_reliability_level",
                    "UNKNOWN"
                )
        },

        "llm_used":
            False,

        "scope": (
            "The analysis provides "
            "forensic behavioural signals "
            "and evidence consistency factors. "
            "It does not determine guilt, "
            "innocence, fabrication or final "
            "legal authenticity."
        )
    }

    return result


# ============================================================
# SAVE COMPLETE RESULT
# ============================================================

def save_analysis_result(
    result
):

    evidence_uid = (
        result.get(
            "evidence_uid",
            "UNKNOWN"
        )
        or "UNKNOWN"
    )

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "_-"
        else "_"
        for character in str(
            evidence_uid
        )
    )

    output_dir = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "extraction",
        "analysis_output"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    json_path = os.path.join(
        output_dir,
        f"Analysis_Result_{safe_uid}.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    return json_path


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_reports(
    result
):

    evidence_uid = (
        result.get(
            "evidence_uid",
            "UNKNOWN"
        )
        or "UNKNOWN"
    )

    json_report = save_json_report(
        result,
        evidence_uid
    )

    text_report = save_text_report(
        result,
        evidence_uid
    )

    return {
        "json_report":
            json_report,

        "text_report":
            text_report
    }