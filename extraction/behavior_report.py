import os
import json
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "report",
    "behavior"
)

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(value):
    if value is None:
        return ""

    return str(value)


def safe_int(value):
    try:
        return int(value)
    except Exception:
        return 0


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


# ============================================================
# JSON REPORT
# ============================================================

def save_json_report(
    result,
    evidence_uid="UNKNOWN"
):

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "_-"
        else "_"
        for character in safe_text(
            evidence_uid
        )
    )

    if not safe_uid:
        safe_uid = "UNKNOWN"

    file_path = os.path.join(
        REPORT_DIR,
        f"Behavior_Report_{safe_uid}.json"
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


# ============================================================
# TEXT REPORT
# ============================================================

def build_text_report(result):

    lines = []

    lines.append(
        "========================================"
    )

    lines.append(
        "DIGITAL EVIDENCE BEHAVIOUR ANALYSIS"
    )

    lines.append(
        "========================================"
    )

    lines.append("")

    evidence_uid = result.get(
        "evidence_uid",
        "UNKNOWN"
    )

    lines.append(
        f"Evidence UID: {evidence_uid}"
    )

    lines.append(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    lines.append("")

    # --------------------------------------------------------
    # BEHAVIOUR SCORE
    # --------------------------------------------------------

    lines.append(
        "----------------------------------------"
    )

    lines.append(
        "BEHAVIOUR ANALYSIS"
    )

    lines.append(
        "----------------------------------------"
    )

    behaviour_score = safe_float(
        result.get(
            "behaviour_score",
            result.get(
                "behavior_score",
                0
            )
        )
    )

    lines.append(
        f"Behaviour Score: {behaviour_score}/100"
    )

    # --------------------------------------------------------
    # ACTIVITY SUMMARY
    # --------------------------------------------------------

    pattern = result.get(
        "activity_pattern_analysis",
        {}
    )

    lines.append("")

    lines.append(
        f"Total Activities: "
        f"{safe_int(pattern.get('total_activities', 0))}"
    )

    dominant = pattern.get(
        "dominant_activity"
    )

    lines.append(
        f"Dominant Activity: "
        f"{safe_text(dominant) if dominant else 'None'}"
    )

    lines.append("")

    lines.append(
        "Activity Categories:"
    )

    category_counts = pattern.get(
        "category_counts",
        {}
    )

    if category_counts:

        for category, count in category_counts.items():

            lines.append(
                f"  - {category}: {count}"
            )

    else:

        lines.append(
            "  - None detected"
        )

    # --------------------------------------------------------
    # TIMELINE
    # --------------------------------------------------------

    lines.append("")

    lines.append(
        "----------------------------------------"
    )

    lines.append(
        "TIMELINE RECONSTRUCTION"
    )

    lines.append(
        "----------------------------------------"
    )

    timeline = result.get(
        "timeline_reconstruction",
        []
    )

    if timeline:

        for item in timeline:

            timeline_id = item.get(
                "activity_id",
                item.get(
                    "timeline_id",
                    ""
                )
            )

            timestamp = item.get(
                "timestamp",
                "Unknown"
            )

            description = item.get(
                "description",
                ""
            )

            categories = item.get(
                "categories",
                item.get(
                    "category",
                    []
                )
            )

            if isinstance(
                categories,
                list
            ):

                category_text = ", ".join(
                    str(value)
                    for value in categories
                )

            else:

                category_text = str(
                    categories
                )

            lines.append("")

            lines.append(
                f"[{timeline_id}]"
            )

            lines.append(
                f"Time: {timestamp}"
            )

            lines.append(
                f"Category: {category_text}"
            )

            lines.append(
                f"Description: {description}"
            )

    else:

        lines.append(
            "No timeline activities detected."
        )

    # --------------------------------------------------------
    # BEHAVIOURAL ANOMALIES
    # --------------------------------------------------------

    lines.append("")

    lines.append(
        "----------------------------------------"
    )

    lines.append(
        "BEHAVIOURAL ANOMALIES"
    )

    lines.append(
        "----------------------------------------"
    )

    anomalies = result.get(
        "behavioural_anomalies",
        result.get(
            "behavioral_anomalies",
            []
        )
    )

    if anomalies:

        for index, anomaly in enumerate(
            anomalies,
            start=1
        ):

            lines.append(
                f"\n{index}. "
                f"{anomaly.get('type', 'UNKNOWN')}"
            )

            lines.append(
                f"Severity: "
                f"{anomaly.get('severity', 'UNKNOWN')}"
            )

            lines.append(
                f"Description: "
                f"{anomaly.get('description', '')}"
            )

    else:

        lines.append(
            "No behavioural anomalies detected."
        )

    # --------------------------------------------------------
    # BEHAVIOUR CORRELATION
    # --------------------------------------------------------

    correlation = result.get(
        "behaviour_evidence_correlation",
        result.get(
            "behavior_evidence_correlation",
            {}
        )
    )

    if correlation:

        lines.append("")

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            "BEHAVIOUR-EVIDENCE CORRELATION"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"Total Correlations: "
            f"{correlation.get('total_correlations', 0)}"
        )

        lines.append(
            f"Correlation Score: "
            f"{correlation.get('correlation_score', 0)}/100"
        )

    # --------------------------------------------------------
    # CONFLICT ANALYSIS
    # --------------------------------------------------------

    conflict = result.get(
        "conflict_analysis",
        {}
    )

    if conflict:

        lines.append("")

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            "CONFLICT ANALYSIS"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"Total Conflicts: "
            f"{conflict.get('total_conflicts', 0)}"
        )

        lines.append(
            f"Conflict Score: "
            f"{conflict.get('conflict_score', 0)}/100"
        )

        lines.append(
            f"High Severity: "
            f"{conflict.get('high_severity', 0)}"
        )

        lines.append(
            f"Medium Severity: "
            f"{conflict.get('medium_severity', 0)}"
        )

        lines.append(
            f"Low Severity: "
            f"{conflict.get('low_severity', 0)}"
        )

    # --------------------------------------------------------
    # SOURCE REPUTATION
    # --------------------------------------------------------

    reputation = result.get(
        "source_reputation",
        {}
    )

    if reputation:

        lines.append("")

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            "SOURCE REPUTATION"
        )

        lines.append(
            "----------------------------------------"
        )

        lines.append(
            f"Source Type: "
            f"{reputation.get('source_type', 'unknown')}"
        )

        lines.append(
            f"Source Reputation Score: "
            f"{reputation.get('source_reputation_score', 0)}/100"
        )

        lines.append(
            f"Reliability Level: "
            f"{reputation.get('source_reliability_level', 'UNKNOWN')}"
        )

        factors = reputation.get(
            "source_reliability_factors",
            {}
        )

        if factors:

            lines.append(
                "\nReliability Factors:"
            )

            for factor, score in factors.items():

                lines.append(
                    f"  - {factor}: {score}"
                )

    # --------------------------------------------------------
    # SCOPE
    # --------------------------------------------------------

    lines.append("")

    lines.append(
        "----------------------------------------"
    )

    lines.append(
        "FORENSIC SCOPE"
    )

    lines.append(
        "----------------------------------------"
    )

    lines.append(
        "This analysis generates forensic "
        "behavioural signals."
    )

    lines.append(
        "An anomaly does not automatically "
        "mean that evidence is false."
    )

    lines.append(
        "A conflict does not automatically "
        "mean that evidence is fabricated."
    )

    lines.append(
        "Source reputation is a reliability "
        "factor and not absolute truth."
    )

    lines.append(
        "The system does not determine guilt "
        "or innocence."
    )

    lines.append(
        "The system does not make a final "
        "legal authenticity decision."
    )

    lines.append("")

    return "\n".join(
        lines
    )


# ============================================================
# SAVE TEXT REPORT
# ============================================================

def save_text_report(
    result,
    evidence_uid="UNKNOWN"
):

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "_-"
        else "_"
        for character in safe_text(
            evidence_uid
        )
    )

    if not safe_uid:
        safe_uid = "UNKNOWN"

    file_path = os.path.join(
        REPORT_DIR,
        f"Behavior_Report_{safe_uid}.txt"
    )

    report_text = build_text_report(
        result
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            report_text
        )

    return file_path