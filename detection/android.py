import subprocess


def detect_android_devices():
    """
    Detect connected Android devices using ADB.

    Returns:
        list: List of authorized Android device serial numbers.
    """

    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return []

        devices = []

        for line in result.stdout.splitlines():
            line = line.strip()

            if not line or line.startswith("List of devices"):
                continue

            parts = line.split()

            if len(parts) >= 2:
                serial = parts[0]
                status = parts[1]

                if status == "device":
                    devices.append(serial)

        return devices

    except FileNotFoundError:
        return []

    except subprocess.TimeoutExpired:
        return []

    except Exception:
        return []


def get_first_android_device():
    """
    Return the first authorized Android device.
    """

    devices = detect_android_devices()

    if devices:
        return devices[0]

    return None


def is_android_connected():
    """
    Check whether at least one authorized Android device is connected.
    """

    return len(detect_android_devices()) > 0