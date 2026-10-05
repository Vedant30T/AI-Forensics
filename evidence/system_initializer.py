import os

from utils.paths import create_evidence_folders


def initialize_project():
    """
    Initialize the AI Digital Evidence project structure.

    Creates all required folders without deleting or
    modifying existing evidence.
    """

    folders = create_evidence_folders()

    # Additional folders used by the project
    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    additional_folders = [
        os.path.join(base_dir, "reports"),
        os.path.join(base_dir, "logs"),
        os.path.join(base_dir, "cases"),
    ]

    for folder in additional_folders:
        os.makedirs(folder, exist_ok=True)

    return {
        "success": True,
        "folders": {
            **folders,
            "reports": os.path.join(
                base_dir,
                "reports"
            ),
            "logs": os.path.join(
                base_dir,
                "logs"
            ),
            "cases": os.path.join(
                base_dir,
                "cases"
            )
        }
    }


def get_project_root():
    """
    Return the root directory of the project.
    """

    return os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )


def get_project_status():
    """
    Return the current project storage status.
    """

    base_dir = get_project_root()

    required_paths = {
        "evidence": os.path.join(
            base_dir,
            "evidence"
        ),
        "secure_storage": os.path.join(
            base_dir,
            "secure_storage"
        ),
        "android_backups": os.path.join(
            base_dir,
            "android_backups"
        ),
        "pen_drive_backups": os.path.join(
            base_dir,
            "pen_drive_backups"
        ),
        "reports": os.path.join(
            base_dir,
            "reports"
        )
    }

    status = {}

    for name, path in required_paths.items():
        status[name] = {
            "path": path,
            "exists": os.path.exists(path)
        }

    return status