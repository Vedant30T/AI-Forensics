import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CASES_FILE = os.path.join(
    BASE_DIR,
    "cases.json"
)


def load_cases():
    """
    Load all created cases.
    """

    if not os.path.exists(CASES_FILE):
        return []

    try:
        with open(
            CASES_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    return []


def save_cases(cases):
    """
    Save case records.
    """

    with open(
        CASES_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            cases,
            file,
            indent=4,
            ensure_ascii=False
        )


def create_case(
    case_id,
    investigator,
    description="",
    location="",
):
    """
    Create a new digital-forensics case.
    """

    if not case_id:
        raise ValueError(
            "Case ID is required."
        )

    if not investigator:
        raise ValueError(
            "Investigator is required."
        )

    cases = load_cases()

    for case in cases:

        if case.get("case_id") == case_id:
            raise ValueError(
                "Case ID already exists."
            )

    case = {
        "case_id": case_id,
        "investigator": investigator,
        "description": description,
        "location": location,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "status": "OPEN",
        "evidence_count": 0
    }

    cases.append(case)

    save_cases(cases)

    return case


def get_case(case_id):
    """
    Retrieve a case using Case ID.
    """

    if not case_id:
        return None

    cases = load_cases()

    for case in cases:

        if case.get("case_id") == case_id:
            return case

    return None


def case_exists(case_id):
    """
    Check whether a Case ID already exists.
    """

    return get_case(case_id) is not None


def update_evidence_count(case_id):
    """
    Increase the evidence count of a case.
    """

    cases = load_cases()

    for case in cases:

        if case.get("case_id") == case_id:

            case["evidence_count"] = (
                int(case.get("evidence_count", 0))
                + 1
            )

            save_cases(cases)

            return case

    return None


def close_case(case_id):
    """
    Close an investigation case.
    """

    cases = load_cases()

    for case in cases:

        if case.get("case_id") == case_id:

            case["status"] = "CLOSED"

            case["closed_at"] = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            save_cases(cases)

            return case

    return None