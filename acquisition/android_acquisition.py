import os
import subprocess
from datetime import datetime


# =========================================================
# CONSTANTS
# =========================================================

APK_PACKAGE = "com.example.evidenceacquisition"
SMS_FILE_NAME = "evidence_sms.json"


# =========================================================
# ADB COMMAND
# =========================================================

def run_adb_command(command, timeout=300):
    """
    Execute an ADB command.
    """

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }

    except FileNotFoundError:

        return {
            "success": False,
            "output": "",
            "error": (
                "ADB is not installed or not available in PATH."
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "output": "",
            "error": (
                "ADB command timed out."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "output": "",
            "error": str(error)
        }


# =========================================================
# GET CONNECTED ANDROID DEVICES
# =========================================================

def get_android_device_serials():

    result = run_adb_command(
        [
            "adb",
            "devices"
        ],
        timeout=30
    )

    if not result["success"]:
        return []

    devices = []

    for line in result["output"].splitlines():

        parts = line.split()

        if (
            len(parts) >= 2
            and parts[1] == "device"
        ):

            devices.append(
                parts[0]
            )

    return devices


# =========================================================
# DEVICE INFORMATION
# =========================================================

def get_device_info(device_id):

    info = {}

    properties = {
        "model": "ro.product.model",
        "manufacturer": "ro.product.manufacturer",
        "android_version": "ro.build.version.release",
        "sdk_version": "ro.build.version.sdk",
        "device": "ro.product.device"
    }

    for key, prop in properties.items():

        result = run_adb_command(
            [
                "adb",
                "-s",
                device_id,
                "shell",
                "getprop",
                prop
            ],
            timeout=30
        )

        if result["success"]:
            info[key] = result["output"]
        else:
            info[key] = "Unknown"

    return info


# =========================================================
# CREATE BACKUP FOLDER
# =========================================================

def create_backup_folder(
    base_folder="evidence"
):

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_folder = os.path.join(
        base_folder,
        "android_backup_" + timestamp
    )

    os.makedirs(
        backup_folder,
        exist_ok=True
    )

    return backup_folder


# =========================================================
# CHECK ANDROID FOLDER
# =========================================================

def android_folder_exists(
    device_id,
    remote_path
):
    """
    Check Android folder without using shell if/then syntax.
    """

    result = run_adb_command(
        [
            "adb",
            "-s",
            device_id,
            "shell",
            "test",
            "-d",
            remote_path
        ],
        timeout=20
    )

    return result["success"]


# =========================================================
# BACKUP SINGLE ANDROID FOLDER
# =========================================================

def backup_android_folder(
    device_id,
    remote_path,
    local_folder
):

    os.makedirs(
        local_folder,
        exist_ok=True
    )

    folder_name = os.path.basename(
        remote_path.rstrip("/")
    )

    destination = os.path.join(
        local_folder,
        folder_name
    )

    if not android_folder_exists(
        device_id,
        remote_path
    ):

        return {
            "success": True,
            "skipped": True,
            "folder": folder_name,
            "message": (
                f"{folder_name} not available on device."
            )
        }

    result = run_adb_command(
        [
            "adb",
            "-s",
            device_id,
            "pull",
            remote_path,
            destination
        ],
        timeout=600
    )

    if result["success"]:

        return {
            "success": True,
            "skipped": False,
            "folder": folder_name,
            "destination": destination,
            "message": (
                f"{folder_name} backup completed."
            )
        }

    return {
        "success": False,
        "skipped": False,
        "folder": folder_name,
        "destination": destination,
        "message": (
            result["error"]
            or f"{folder_name} backup failed."
        )
    }


# =========================================================
# FAST ANDROID BACKUP
# =========================================================

def backup_android_storage(
    device_id,
    destination_folder
):
    """
    Backup important user-accessible Android evidence folders.

    The phone data is not modified.
    """

    if not device_id:

        return {
            "success": False,
            "destination": destination_folder,
            "message": (
                "Android device ID is required."
            )
        }

    os.makedirs(
        destination_folder,
        exist_ok=True
    )

    evidence_folders = [
        "/sdcard/DCIM",
        "/sdcard/Pictures",
        "/sdcard/Movies",
        "/sdcard/Music",
        "/sdcard/Download",
        "/sdcard/Documents"
    ]

    results = []

    successful = 0
    failed = 0
    skipped = 0

    for remote_path in evidence_folders:

        result = backup_android_folder(
            device_id,
            remote_path,
            destination_folder
        )

        results.append(
            result
        )

        if result["success"]:

            if result.get("skipped"):
                skipped += 1
            else:
                successful += 1

        else:

            failed += 1

    # -----------------------------------------------------
    # Backup information
    # -----------------------------------------------------

    info_file = os.path.join(
        destination_folder,
        "backup_info.txt"
    )

    with open(
        info_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "ANDROID EVIDENCE BACKUP\n"
        )

        file.write(
            "========================\n\n"
        )

        file.write(
            f"Device ID: {device_id}\n"
        )

        file.write(
            "Backup Time: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        for result in results:

            file.write(
                f"{result.get('folder', '')}: "
                f"{result.get('message', '')}\n"
            )

    if (
        successful > 0
        or skipped == len(evidence_folders)
    ):

        return {
            "success": True,
            "destination": os.path.abspath(
                destination_folder
            ),
            "successful_folders": successful,
            "skipped_folders": skipped,
            "failed_folders": failed,
            "results": results,
            "message": (
                "Android evidence backup completed."
            )
        }

    return {
        "success": False,
        "destination": os.path.abspath(
            destination_folder
        ),
        "successful_folders": successful,
        "skipped_folders": skipped,
        "failed_folders": failed,
        "results": results,
        "message": (
            "Android backup failed."
        )
    }


# =========================================================
# INSTALL APK
# =========================================================

def install_acquisition_apk(
    device_id,
    apk_path
):

    if not os.path.exists(
        apk_path
    ):

        return {
            "success": False,
            "message": (
                "EvidenceAcquisition.apk not found."
            )
        }

    result = run_adb_command(
        [
            "adb",
            "-s",
            device_id,
            "install",
            "-r",
            apk_path
        ],
        timeout=120
    )

    if result["success"]:

        return {
            "success": True,
            "message": (
                "EvidenceAcquisition APK "
                "installed successfully."
            )
        }

    return {
        "success": False,
        "message": (
            result["error"]
            or "APK installation failed."
        )
    }


# =========================================================
# START SMS ACQUISITION
# =========================================================

def start_android_sms_acquisition(
    apk_path,
    output_json
):

    if not os.path.exists(
        apk_path
    ):

        return {
            "success": False,
            "message": (
                "EvidenceAcquisition.apk not found."
            )
        }

    try:

        devices = get_android_device_serials()

        if not devices:

            return {
                "success": False,
                "message": (
                    "No authorized Android device detected."
                )
            }

        device_id = devices[0]

        # -------------------------------------------------
        # Install APK
        # -------------------------------------------------

        install_result = install_acquisition_apk(
            device_id,
            apk_path
        )

        if not install_result["success"]:
            return install_result

        # -------------------------------------------------
        # Start APK
        # -------------------------------------------------

        launch_result = run_adb_command(
            [
                "adb",
                "-s",
                device_id,
                "shell",
                "monkey",
                "-p",
                APK_PACKAGE,
                "1"
            ],
            timeout=30
        )

        if not launch_result["success"]:

            return {
                "success": False,
                "message": (
                    launch_result["error"]
                    or (
                        "EvidenceAcquisition APK "
                        "could not be started."
                    )
                )
            }

        return {
            "success": True,
            "device_id": device_id,
            "package_name": APK_PACKAGE,
            "output_json": output_json,
            "message": (
                "EvidenceAcquisition application started."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error)
        }


# =========================================================
# CHECK PRIVATE SMS FILE
# =========================================================

def check_private_sms_file(
    device_id
):
    """
    Check the actual SMS JSON created by the APK.

    APK package:
        com.example.evidenceacquisition

    File:
        files/evidence_sms.json
    """

    remote_path = (
        f"files/{SMS_FILE_NAME}"
    )

    # No shell if/then.
    # Directly use run-as + ls.
    result = run_adb_command(
        [
            "adb",
            "-s",
            device_id,
            "shell",
            "run-as",
            APK_PACKAGE,
            "ls",
            "-l",
            remote_path
        ],
        timeout=30
    )

    if (
        result["success"]
        and result["output"]
    ):

        return {
            "success": True,
            "path": remote_path,
            "message": (
                "SMS JSON found inside APK private storage."
            )
        }

    return {
        "success": False,
        "path": remote_path,
        "message": (
            result["error"]
            or (
                "evidence_sms.json was not found "
                "inside APK private storage."
            )
        )
    }


# =========================================================
# COPY PRIVATE SMS JSON
# =========================================================

def copy_private_sms_json(
    device_id,
    local_json
):
    """
    Copy evidence_sms.json from APK private storage
    to the computer.

    Android source:

    /data/data/com.example.evidenceacquisition/files/
    evidence_sms.json
    """

    try:

        parent = os.path.dirname(
            local_json
        )

        if parent:

            os.makedirs(
                parent,
                exist_ok=True
            )

        # -------------------------------------------------
        # Check file
        # -------------------------------------------------

        check = check_private_sms_file(
            device_id
        )

        if not check["success"]:

            return {
                "success": False,
                "path": local_json,
                "message": check["message"]
            }

        remote_file = (
            f"files/{SMS_FILE_NAME}"
        )

        # -------------------------------------------------
        # Read private file using run-as
        # -------------------------------------------------

        result = subprocess.run(
            [
                "adb",
                "-s",
                device_id,
                "exec-out",
                "run-as",
                APK_PACKAGE,
                "cat",
                remote_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120
        )

        if result.returncode != 0:

            error_text = (
                result.stderr
                .decode(
                    "utf-8",
                    errors="replace"
                )
                .strip()
            )

            return {
                "success": False,
                "path": local_json,
                "message": (
                    error_text
                    or (
                        "Unable to read SMS JSON "
                        "from APK private storage."
                    )
                )
            }

        if not result.stdout:

            return {
                "success": False,
                "path": local_json,
                "message": (
                    "SMS JSON file is empty."
                )
            }

        # -------------------------------------------------
        # Save JSON on PC
        # -------------------------------------------------

        with open(
            local_json,
            "wb"
        ) as file:

            file.write(
                result.stdout
            )

        if not os.path.exists(
            local_json
        ):

            return {
                "success": False,
                "path": local_json,
                "message": (
                    "SMS JSON could not be saved."
                )
            }

        if os.path.getsize(
            local_json
        ) == 0:

            return {
                "success": False,
                "path": local_json,
                "message": (
                    "SMS JSON file is empty."
                )
            }

        return {
            "success": True,
            "path": local_json,
            "remote_path": (
                f"/data/data/"
                f"{APK_PACKAGE}/files/"
                f"{SMS_FILE_NAME}"
            ),
            "message": (
                "SMS evidence copied successfully."
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "path": local_json,
            "message": (
                "Timed out while copying SMS evidence."
            )
        }

    except Exception as error:

        return {
            "success": False,
            "path": local_json,
            "message": str(error)
        }


# =========================================================
# FINISH SMS ACQUISITION
# =========================================================

def finish_android_sms_acquisition(
    device_id,
    remote_json,
    local_json
):
    """
    Complete SMS acquisition.

    The APK stores:

        files/evidence_sms.json

    inside its private application storage.

    This function does not use /sdcard.
    """

    try:

        return copy_private_sms_json(
            device_id,
            local_json
        )

    except Exception as error:

        return {
            "success": False,
            "path": local_json,
            "message": str(error)
        }