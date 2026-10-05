"""
Final Trust Assessment & Reporting Engine
-----------------------------------------

Final-stage forensic assessment module.

Purpose:
- Receive outputs from the previous evidence-processing modules.
- Verify AI-generated claims against available evidence/correlation results.
- Detect unsupported / contradicted AI findings.
- Calculate a preliminary hallucination-risk score.
- Calculate a preliminary final evidence trust score (0-100).
- Prioritize evidence items.
- Calculate relevance and investigative value.
- Produce an explainable final forensic assessment.
- Generate JSON and TXT reports.

Important:
The weights in this module are PROPOSED / PRELIMINARY and should be
validated experimentally. This module does not determine guilt,
innocence, or final legal authenticity.

No LLM is used.
"""

import os
import json
import re
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "report", "final_assessment")
OUTPUT_DIR = os.path.join(BASE_DIR, "extraction", "final_assessment")

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


SUPPORTED = "SUPPORTED"
PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
UNSUPPORTED = "UNSUPPORTED"
CONTRADICTED = "CONTRADICTED"
UNVALIDATED = "UNVALIDATED"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _number(value, default=0.0):
    try:
        if value is None:
            return float(default)
        if isinstance(value, bool):
            return float(int(value))
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, _number(value)))


def _first(data, keys, default=None):
    if not isinstance(data, dict):
        return default

    for key in keys:
        if key in data and data[key] is not None:
            return data[key]

    return default


def _list_value(data, keys):
    value = _first(data, keys, [])
    if isinstance(value, list):
        return value
    return []


def _normalize_status(value):
    if value is None:
        return UNVALIDATED

    text = str(value).strip().upper()
    text = text.replace(" ", "_").replace("-", "_")

    aliases = {
        "SUPPORTED": SUPPORTED,
        "PARTIALLY_SUPPORTED": PARTIALLY_SUPPORTED,
        "PARTIAL": PARTIALLY_SUPPORTED,
        "PARTIALLY": PARTIALLY_SUPPORTED,
        "UNSUPPORTED": UNSUPPORTED,
        "CONTRADICTED": CONTRADICTED,
        "CONTRADICTION": CONTRADICTED,
        "UNVALIDATED": UNVALIDATED,
        "UNKNOWN": UNVALIDATED,
    }

    return aliases.get(text, UNVALIDATED)


def _status_from_claim(claim):
    if not isinstance(claim, dict):
        return UNVALIDATED

    return _normalize_status(
        _first(
            claim,
            [
                "validation_status",
                "status",
                "claim_status",
                "verification_status",
                "classification",
            ],
            None,
        )
    )


def _claim_text(claim):
    if isinstance(claim, str):
        return claim

    if not isinstance(claim, dict):
        return str(claim)

    value = _first(
        claim,
        [
            "claim",
            "claim_text",
            "statement",
            "text",
            "description",
            "content",
        ],
        "",
    )

    return str(value)


def _extract_claims(riya_result):
    claims = _list_value(
        riya_result,
        [
            "claims",
            "ai_claims",
            "extracted_claims",
        ],
    )

    if claims:
        return claims

    validation = _first(
        riya_result,
        [
            "cross_validation_results",
            "validation_results",
            "claim_validation",
        ],
        [],
    )

    if isinstance(validation, list):
        return validation

    return []


def _extract_evidence_items(all_inputs):
    items = []

    for source_name, data in all_inputs.items():
        if not isinstance(data, dict):
            continue

        candidates = _list_value(
            data,
            [
                "evidence_items",
                "evidence",
                "evidence_list",
                "registered_evidence",
                "prioritized_evidence",
            ],
        )

        for item in candidates:
            if isinstance(item, dict):
                copied = dict(item)
                copied["_input_source"] = source_name
                items.append(copied)

    return items


def _extract_score(data, keys, default=0.0):
    value = _first(data, keys, None)
    if isinstance(value, dict):
        value = _first(
            value,
            [
                "score",
                "value",
                "percentage",
                "integrity_score",
                "trust_score",
                "source_reputation_score",
                "behaviour_score",
                "confidence",
            ],
            default,
        )

    return _clamp(value, 0, 100)


# ------------------------------------------------------------------
# AI claim verification / hallucination detection
# ------------------------------------------------------------------

def verify_ai_claims(riya_result, correlation_result=None, integrity_result=None):
    """
    Verify claim statuses using the statuses produced by the previous
    validation/correlation stages.

    This is deterministic verification. It does not invent evidence
    when a claim is not supported.
    """
    claims = _extract_claims(riya_result)

    correlation_result = correlation_result or {}
    integrity_result = integrity_result or {}

    verified_claims = []

    correlation_text = json.dumps(
        correlation_result,
        ensure_ascii=False,
    ).lower()

    integrity_text = json.dumps(
        integrity_result,
        ensure_ascii=False,
    ).lower()

    for index, claim in enumerate(claims, start=1):
        status = _status_from_claim(claim)

        claim_text = _claim_text(claim)

        # If the claim is explicitly validated, preserve that result.
        # We only use surrounding correlation/integrity data as supporting
        # context and never upgrade an unsupported claim automatically.
        evidence_support = []
        evidence_conflicts = []

        if isinstance(claim, dict):
            evidence_support = _list_value(
                claim,
                [
                    "supporting_evidence",
                    "supporting_evidence_ids",
                    "corroborating_evidence",
                    "evidence_references",
                ],
            )

            evidence_conflicts = _list_value(
                claim,
                [
                    "contradicting_evidence",
                    "contradicting_evidence_ids",
                    "conflicting_evidence",
                ],
            )

        if evidence_conflicts and status == UNVALIDATED:
            status = CONTRADICTED
        elif evidence_support and status == UNVALIDATED:
            status = PARTIALLY_SUPPORTED

        # Keep these fields informational; they are not used to fabricate
        # support.
        context_match = bool(
            claim_text
            and claim_text.lower() in correlation_text
        )

        integrity_context_available = bool(
            integrity_text
        )

        verified_claims.append(
            {
                "claim_id": f"CLM-{index:03d}",
                "claim": claim_text,
                "status": status,
                "supporting_evidence": evidence_support,
                "contradicting_evidence": evidence_conflicts,
                "correlation_context_match": context_match,
                "integrity_context_available": integrity_context_available,
            }
        )

    counts = {
        SUPPORTED: 0,
        PARTIALLY_SUPPORTED: 0,
        UNSUPPORTED: 0,
        CONTRADICTED: 0,
        UNVALIDATED: 0,
    }

    for item in verified_claims:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    total = len(verified_claims)

    return {
        "total_claims": total,
        "supported": counts[SUPPORTED],
        "partially_supported": counts[PARTIALLY_SUPPORTED],
        "unsupported": counts[UNSUPPORTED],
        "contradicted": counts[CONTRADICTED],
        "unvalidated": counts[UNVALIDATED],
        "claims": verified_claims,
    }


def calculate_hallucination_risk(claim_verification):
    """
    Preliminary risk model.

    Penalties:
    - Supported: 0
    - Partially supported: 0.5
    - Unsupported: 1
    - Contradicted: 1.5

    Risk = weighted unsupported/contradicted/partial claims / total claims * 100

    The contradiction penalty is intentionally higher, as proposed by the
    methodology. Thresholds are preliminary.
    """
    total = _number(
        claim_verification.get("total_claims", 0)
    )

    if total <= 0:
        return {
            "risk_score": 0.0,
            "risk_level": "UNKNOWN",
            "formula": "No claims available for hallucination-risk calculation.",
        }

    partial = _number(
        claim_verification.get("partially_supported", 0)
    )
    unsupported = _number(
        claim_verification.get("unsupported", 0)
    )
    contradicted = _number(
        claim_verification.get("contradicted", 0)
    )

    weighted_penalty = (
        partial * 0.5
        + unsupported * 1.0
        + contradicted * 1.5
    )

    risk = _clamp(
        (weighted_penalty / total) * 100.0
    )

    if risk < 15:
        level = "LOW"
    elif risk < 35:
        level = "MEDIUM"
    elif risk < 60:
        level = "HIGH"
    else:
        level = "VERY_HIGH"

    return {
        "risk_score": round(risk, 2),
        "risk_level": level,
        "weighted_penalty": round(weighted_penalty, 2),
        "formula": (
            "(Partial × 0.5 + Unsupported × 1.0 + "
            "Contradicted × 1.5) / Total Claims × 100"
        ),
        "thresholds": {
            "LOW": "< 15",
            "MEDIUM": "15-34.99",
            "HIGH": "35-59.99",
            "VERY_HIGH": ">= 60",
        },
        "preliminary": True,
    }


# ------------------------------------------------------------------
# Trust factors
# ------------------------------------------------------------------

def calculate_trust_factors(
    security_result=None,
    integrity_result=None,
    riya_result=None,
    behaviour_result=None,
    correlation_result=None,
    hallucination_result=None,
):
    """
    Convert previous-module outputs into normalized 0-100 trust factors.

    The weights are preliminary and are intended for experimental
    validation, not as universally correct forensic weights.
    """
    security_result = security_result or {}
    integrity_result = integrity_result or {}
    riya_result = riya_result or {}
    behaviour_result = behaviour_result or {}
    correlation_result = correlation_result or {}
    hallucination_result = hallucination_result or {}

    hash_score = _extract_score(
        integrity_result,
        [
            "hash_verification_score",
            "hash_score",
            "hash_integrity_score",
        ],
        0,
    )

    integrity_score = _extract_score(
        integrity_result,
        [
            "integrity_score",
            "score",
        ],
        hash_score,
    )

    metadata_score = _extract_score(
        integrity_result,
        [
            "metadata_score",
            "metadata_verification_score",
        ],
        0,
    )

    provenance_score = _extract_score(
        security_result,
        [
            "provenance_score",
            "provenance_trust_score",
            "trust_score",
        ],
        0,
    )

    custody_score = _extract_score(
        security_result,
        [
            "chain_of_custody_score",
            "custody_score",
        ],
        0,
    )

    blockchain_score = _extract_score(
        security_result,
        [
            "blockchain_score",
            "blockchain_verification_score",
        ],
        0,
    )

    kg_score = _extract_score(
        riya_result,
        [
            "knowledge_graph_score",
            "kg_score",
        ],
        0,
    )

    cross_validation = _extract_score(
        riya_result,
        [
            "cross_validation_score",
            "validation_score",
        ],
        0,
    )

    behaviour_score = _extract_score(
        behaviour_result,
        [
            "behaviour_score",
        ],
        0,
    )

    source_score = _extract_score(
        behaviour_result,
        [
            "source_reputation_score",
            "source_reliability_score",
        ],
        0,
    )

    correlation_score = _extract_score(
        behaviour_result,
        [
            "correlation_score",
        ],
        _extract_score(
            correlation_result,
            [
                "correlation_score",
            ],
            0,
        ),
    )

    # AI reliability is driven primarily by hallucination risk.
    hallucination_risk = _number(
        hallucination_result.get("risk_score", 100)
    )
    ai_reliability = _clamp(100 - hallucination_risk)

    factors = {
        "integrity": round(integrity_score, 2),
        "hash_integrity": round(hash_score, 2),
        "metadata_consistency": round(metadata_score, 2),
        "provenance": round(provenance_score, 2),
        "chain_of_custody": round(custody_score, 2),
        "blockchain_verification": round(blockchain_score, 2),
        "knowledge_graph_validation": round(kg_score, 2),
        "cross_validation": round(cross_validation, 2),
        "behaviour_consistency": round(behaviour_score, 2),
        "source_reliability": round(source_score, 2),
        "correlation": round(correlation_score, 2),
        "ai_reliability": round(ai_reliability, 2),
    }

    return factors


def calculate_final_trust_score(
    factors,
    conflict_score=0,
    hallucination_risk=0,
    manipulation_penalty=0,
    metadata_inconsistency_penalty=0,
):
    """
    Preliminary weighted trust model.

    Positive weights:
        Integrity 20
        Provenance 15
        Cross-validation 15
        Behaviour 10
        Source reliability 10
        AI reliability 10
        Knowledge graph 5
        Chain of custody 5
        Blockchain verification 5
        Metadata consistency 5

    Negative penalties:
        Conflict score
        Hallucination risk
        Manipulation indicators
        Metadata inconsistency

    The positive weights sum to 100 before penalties.
    Penalties are capped so the final score remains 0-100.
    """
    positive = (
        factors.get("integrity", 0) * 0.20
        + factors.get("provenance", 0) * 0.15
        + factors.get("cross_validation", 0) * 0.15
        + factors.get("behaviour_consistency", 0) * 0.10
        + factors.get("source_reliability", 0) * 0.10
        + factors.get("ai_reliability", 0) * 0.10
        + factors.get("knowledge_graph_validation", 0) * 0.05
        + factors.get("chain_of_custody", 0) * 0.05
        + factors.get("blockchain_verification", 0) * 0.05
        + factors.get("metadata_consistency", 0) * 0.05
    )

    total_penalty = (
        _clamp(conflict_score)
        + _clamp(hallucination_risk)
        + _clamp(manipulation_penalty)
        + _clamp(metadata_inconsistency_penalty)
    )

    final_score = _clamp(
        positive - (total_penalty * 0.25)
    )

    if final_score >= 80:
        level = "HIGH"
    elif final_score >= 60:
        level = "MEDIUM"
    elif final_score >= 40:
        level = "LOW"
    else:
        level = "VERY_LOW"

    return {
        "positive_score": round(positive, 2),
        "conflict_penalty": round(_clamp(conflict_score), 2),
        "hallucination_penalty": round(_clamp(hallucination_risk), 2),
        "manipulation_penalty": round(_clamp(manipulation_penalty), 2),
        "metadata_inconsistency_penalty": round(
            _clamp(metadata_inconsistency_penalty), 2
        ),
        "total_penalty": round(total_penalty, 2),
        "final_score": round(final_score, 2),
        "trust_level": level,
        "preliminary": True,
    }


# ------------------------------------------------------------------
# Evidence relevance / investigative value / prioritization
# ------------------------------------------------------------------

def calculate_evidence_priority(evidence_items):
    """
    Rank evidence items using:
    - trust score
    - relevance
    - investigative value

    High trust is deliberately kept separate from relevance and
    investigative value.
    """
    ranked = []

    for index, item in enumerate(evidence_items, start=1):
        uid = str(
            _first(
                item,
                [
                    "evidence_uid",
                    "uid",
                    "id",
                    "evidence_id",
                ],
                f"EVD-{index:03d}",
            )
        )

        trust = _extract_score(
            item,
            [
                "trust_score",
                "final_trust_score",
                "score",
            ],
            0,
        )

        relevance = _extract_score(
            item,
            [
                "relevance_score",
                "evidence_relevance",
                "relevance",
            ],
            0,
        )

        investigative_value = _extract_score(
            item,
            [
                "investigative_value_score",
                "investigative_value",
                "forensic_value",
            ],
            0,
        )

        priority = (
            trust * 0.50
            + relevance * 0.25
            + investigative_value * 0.25
        )

        if priority >= 80:
            priority_level = "HIGH"
        elif priority >= 60:
            priority_level = "MEDIUM"
        else:
            priority_level = "LOW"

        ranked.append(
            {
                "evidence_uid": uid,
                "trust_score": round(trust, 2),
                "relevance_score": round(relevance, 2),
                "investigative_value_score": round(
                    investigative_value, 2
                ),
                "priority_score": round(
                    _clamp(priority), 2
                ),
                "priority_level": priority_level,
            }
        )

    ranked.sort(
        key=lambda x: x["priority_score"],
        reverse=True,
    )

    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank

    return ranked


# ------------------------------------------------------------------
# Explainability
# ------------------------------------------------------------------

def build_explanation(
    final_trust,
    factors,
    claim_verification,
    hallucination,
    conflict_score,
):
    positive_reasons = []
    negative_reasons = []

    if factors.get("hash_integrity", 0) >= 80:
        positive_reasons.append("Hash integrity was strongly verified.")
    elif factors.get("hash_integrity", 0) > 0:
        negative_reasons.append("Hash verification was not fully strong.")

    if factors.get("provenance", 0) >= 80:
        positive_reasons.append("Evidence provenance is strong.")
    elif factors.get("provenance", 0) > 0:
        negative_reasons.append("Provenance contains limitations.")

    if factors.get("cross_validation", 0) >= 80:
        positive_reasons.append(
            "Cross-validation provides strong supporting consistency."
        )
    elif factors.get("cross_validation", 0) > 0:
        negative_reasons.append(
            "Cross-validation is not fully conclusive."
        )

    if factors.get("behaviour_consistency", 0) >= 80:
        positive_reasons.append(
            "Behavioural evidence shows strong consistency."
        )
    elif factors.get("behaviour_consistency", 0) > 0:
        negative_reasons.append(
            "Behavioural analysis contains consistency limitations."
        )

    if factors.get("source_reliability", 0) >= 80:
        positive_reasons.append(
            "Source reliability is rated strongly."
        )
    elif factors.get("source_reliability", 0) > 0:
        negative_reasons.append(
            "Source reliability is not strongly established."
        )

    if conflict_score > 0:
        negative_reasons.append(
            f"Evidence conflict score contributed a {conflict_score:.2f} penalty."
        )

    if hallucination["risk_score"] > 0:
        negative_reasons.append(
            "AI claim verification identified "
            f"{claim_verification['unsupported']} unsupported, "
            f"{claim_verification['contradicted']} contradicted and "
            f"{claim_verification['partially_supported']} partially supported claims."
        )

    score = final_trust["final_score"]
    level = final_trust["trust_level"]

    sentence = (
        f"The evidence received a {level.lower()} trust assessment "
        f"with a final trust score of {score:.2f}/100. "
    )

    if positive_reasons:
        sentence += "Positive factors: " + " ".join(positive_reasons) + " "

    if negative_reasons:
        sentence += "Negative factors: " + " ".join(negative_reasons)

    return {
        "positive_factors": positive_reasons,
        "negative_factors": negative_reasons,
        "human_readable_explanation": sentence.strip(),
    }


# ------------------------------------------------------------------
# Main final assessment
# ------------------------------------------------------------------

def run_final_assessment(
    security_result=None,
    integrity_result=None,
    riya_result=None,
    behaviour_result=None,
    correlation_result=None,
    evidence_items=None,
):
    """
    Main entry point for the final module.

    All previous module outputs are optional dictionaries so the
    function remains usable while the project is being integrated.
    """
    security_result = security_result or {}
    integrity_result = integrity_result or {}
    riya_result = riya_result or {}
    behaviour_result = behaviour_result or {}
    correlation_result = correlation_result or {}

    claim_verification = verify_ai_claims(
        riya_result=riya_result,
        correlation_result=correlation_result,
        integrity_result=integrity_result,
    )

    hallucination = calculate_hallucination_risk(
        claim_verification
    )

    factors = calculate_trust_factors(
        security_result=security_result,
        integrity_result=integrity_result,
        riya_result=riya_result,
        behaviour_result=behaviour_result,
        correlation_result=correlation_result,
        hallucination_result=hallucination,
    )

    conflict_score = _extract_score(
        behaviour_result,
        [
            "conflict_score",
        ],
        _extract_score(
            behaviour_result.get("conflict_analysis", {}),
            [
                "conflict_score",
            ],
            0,
        ),
    )

    manipulation_penalty = _extract_score(
        integrity_result,
        [
            "manipulation_penalty",
            "manipulation_indicator_score",
        ],
        0,
    )

    metadata_inconsistency_penalty = _extract_score(
        integrity_result,
        [
            "metadata_inconsistency_penalty",
        ],
        0,
    )

    final_trust = calculate_final_trust_score(
        factors=factors,
        conflict_score=conflict_score,
        hallucination_risk=hallucination["risk_score"],
        manipulation_penalty=manipulation_penalty,
        metadata_inconsistency_penalty=metadata_inconsistency_penalty,
    )

    if evidence_items is None:
        evidence_items = _extract_evidence_items(
            {
                "security": security_result,
                "integrity": integrity_result,
                "riya": riya_result,
                "behaviour": behaviour_result,
            }
        )

    prioritization = calculate_evidence_priority(
        evidence_items
    )

    explanation = build_explanation(
        final_trust=final_trust,
        factors=factors,
        claim_verification=claim_verification,
        hallucination=hallucination,
        conflict_score=conflict_score,
    )

    evidence_uid = _first(
        integrity_result,
        ["evidence_uid", "uid"],
        _first(
            riya_result,
            ["evidence_uid", "uid"],
            "UNKNOWN",
        ),
    )

    result = {
        "module": "Final Trust Assessment & Reporting",
        "evidence_uid": evidence_uid,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_modules": [
            "Security & Provenance",
            "Integrity + Metadata + Dynamic Trust",
            "AI Extraction + Knowledge Graph + Validation",
            "Behaviour + Conflict + Source Reliability",
        ],
        "ai_output_verification": {
            "method": "Deterministic claim-to-evidence verification",
            "llm_used": False,
            "claim_verification": claim_verification,
        },
        "hallucination_analysis": hallucination,
        "trust_factors": factors,
        "final_trust_assessment": final_trust,
        "evidence_prioritization": prioritization,
        "explainable_assessment": explanation,
        "scope": (
            "This is a forensic decision-support assessment. "
            "It does not determine guilt or innocence and does not "
            "make a final legal authenticity decision."
        ),
        "methodology_note": (
            "Trust weights, hallucination thresholds and penalty "
            "coefficients are preliminary/proposed and should be "
            "validated experimentally."
        ),
    }

    return result


# ------------------------------------------------------------------
# Reports
# ------------------------------------------------------------------

def save_json_report(result, evidence_uid="UNKNOWN"):
    safe_uid = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        str(evidence_uid),
    )

    path = os.path.join(
        REPORT_DIR,
        f"Final_Assessment_{safe_uid}.json",
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return path


def build_text_report(result):
    trust = result.get(
        "final_trust_assessment",
        {},
    )

    claims = result.get(
        "ai_output_verification",
        {},
    ).get(
        "claim_verification",
        {},
    )

    hallucination = result.get(
        "hallucination_analysis",
        {},
    )

    factors = result.get(
        "trust_factors",
        {},
    )

    explanation = result.get(
        "explainable_assessment",
        {},
    )

    lines = [
        "FINAL FORENSIC TRUST ASSESSMENT REPORT",
        "=" * 55,
        "",
        f"Evidence UID: {result.get('evidence_uid', 'UNKNOWN')}",
        f"Generated: {result.get('generated_at', '')}",
        "",
        "AI OUTPUT VERIFICATION",
        "-" * 30,
        f"Total Claims: {claims.get('total_claims', 0)}",
        f"Supported: {claims.get('supported', 0)}",
        f"Partially Supported: {claims.get('partially_supported', 0)}",
        f"Unsupported: {claims.get('unsupported', 0)}",
        f"Contradicted: {claims.get('contradicted', 0)}",
        "",
        "HALLUCINATION ANALYSIS",
        "-" * 30,
        f"Risk Score: {hallucination.get('risk_score', 0)}/100",
        f"Risk Level: {hallucination.get('risk_level', 'UNKNOWN')}",
        "",
        "TRUST FACTORS",
        "-" * 30,
    ]

    for key, value in factors.items():
        lines.append(
            f"{key}: {value}/100"
        )

    lines.extend(
        [
            "",
            "FINAL TRUST ASSESSMENT",
            "-" * 30,
            f"Positive Score: {trust.get('positive_score', 0)}",
            f"Total Penalty: {trust.get('total_penalty', 0)}",
            f"Final Trust Score: {trust.get('final_score', 0)}/100",
            f"Trust Level: {trust.get('trust_level', 'UNKNOWN')}",
            "",
            "EXPLAINABLE ASSESSMENT",
            "-" * 30,
            "",
            explanation.get(
                "human_readable_explanation",
                "No explanation available.",
            ),
            "",
            "EVIDENCE PRIORITIZATION",
            "-" * 30,
        ]
    )

    for item in result.get(
        "evidence_prioritization",
        [],
    ):
        lines.append(
            f"{item.get('rank', '-')}. "
            f"{item.get('evidence_uid', 'UNKNOWN')} | "
            f"Trust={item.get('trust_score', 0)} | "
            f"Relevance={item.get('relevance_score', 0)} | "
            f"Investigative Value={item.get('investigative_value_score', 0)} | "
            f"Priority={item.get('priority_score', 0)} "
            f"({item.get('priority_level', 'UNKNOWN')})"
        )

    lines.extend(
        [
            "",
            "FORENSIC SCOPE",
            "-" * 30,
            result.get("scope", ""),
            "",
            result.get("methodology_note", ""),
        ]
    )

    return "\n".join(lines)


def save_text_report(result, evidence_uid="UNKNOWN"):
    safe_uid = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        str(evidence_uid),
    )

    path = os.path.join(
        REPORT_DIR,
        f"Final_Assessment_{safe_uid}.txt",
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(
            build_text_report(result)
        )

    return path


def save_assessment_output(result, evidence_uid="UNKNOWN"):
    safe_uid = re.sub(
        r"[^A-Za-z0-9_.-]+",
        "_",
        str(evidence_uid),
    )

    path = os.path.join(
        OUTPUT_DIR,
        f"Final_Assessment_{safe_uid}.json",
    )

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
        )

    return path


def generate_final_reports(result):
    evidence_uid = result.get(
        "evidence_uid",
        "UNKNOWN",
    )

    json_report = save_json_report(
        result,
        evidence_uid,
    )

    text_report = save_text_report(
        result,
        evidence_uid,
    )

    output_json = save_assessment_output(
        result,
        evidence_uid,
    )

    return {
        "json_report": json_report,
        "text_report": text_report,
        "assessment_output": output_json,
    }


if __name__ == "__main__":
    print(
        "Final Trust Assessment & Reporting Engine loaded successfully."
    )
    print(
        "Use run_final_assessment(...) from the project GUI/pipeline."
    )
