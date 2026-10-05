import os
import string
import platform
import subprocess


def get_windows_drives():
    """
    Detect available Windows drive letters.
    """

    drives = []

    if platform.system() != "Windows":
        return drives

    for letter in string.ascii_uppercase:

        drive = f"{letter}:\\"

        if os.path.exists(drive):
            drives.append(drive)

    return drives


def get_drive_label(drive):
    """
    Get the volume label of a drive.
    """

    if not drive:
        return ""

    try:

        result = subprocess.run(
            [
                "cmd",
                "/c",
                "vol",
                drive
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout.strip()

        if "Volume in drive" in output:

            lines = output.splitlines()

            for line in lines:

                if "Volume Serial Number" not in line:
                    continue

                break

            if lines:
                first_line = lines[0]

                if "is" in first_line:
                    return first_line.split(
                        "is",
                        1
                    )[1].strip()

    except Exception:
        pass

    return ""


def get_drive_type(drive):
    """
    Identify the Windows drive type.
    """

    if not drive:
        return "Unknown"

    try:

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    f"(Get-CimInstance Win32_LogicalDisk "
                    f"-Filter \"DeviceID='{drive[:2]}'\").DriveType"
                )
            ],
            capture_output=True,
            text=True,
            timeout=5
        )

        drive_type = result.stdout.strip()

        drive_types = {
            "2": "Removable",
            "3": "Fixed",
            "4": "Network",
            "5": "CD/DVD",
            "6": "RAM Disk"
        }

        return drive_types.get(
            drive_type,
            "Unknown"
        )

    except Exception:
        return "Unknown"


def detect_pen_drives():
    """
    Detect removable drives currently connected.

    Returns a list of drive information.
    """

    drives = []

    for drive in get_windows_drives():

        drive_type = get_drive_type(drive)

        if drive_type != "Removable":
            continue

        drives.append({
            "drive": drive,
            "label": get_drive_label(drive),
            "type": drive_type
        })

    return drives


def get_pen_drive_options():
    """
    Return drives that can be displayed in the GUI.

    The GUI can show the selection option even when
    no Pen Drive is currently connected.
    """

    drives = detect_pen_drives()

    options = [
        {
            "display": (
                f"{item['drive']} "
                f"{item['label'] or 'Removable Drive'}"
            ),
            "path": item["drive"],
            "connected": True
        }
        for item in drives
    ]

    if not options:

        options.append({
            "display": "No Pen Drive Connected",
            "path": "",
            "connected": False
        })

    return options