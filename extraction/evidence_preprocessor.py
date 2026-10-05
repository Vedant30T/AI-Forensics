import os
import json
import mimetypes
from datetime import datetime


# ============================================================
# AI Evidence Extraction - Preprocessor
# Riya Module
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "extraction",
    "preprocessed_data"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# SUPPORTED FILE TYPES
# ============================================================

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tiff",
    ".webp"
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".webm"
}

AUDIO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".aac",
    ".m4a",
    ".ogg",
    ".flac"
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".doc"
}

LOG_EXTENSIONS = {
    ".log",
    ".csv",
    ".json",
    ".xml"
}


# ============================================================
# BASIC FILE INFORMATION
# ============================================================

def get_basic_file_information(file_path):

    if not os.path.exists(file_path):

        return {
            "success": False,
            "message": "Evidence file not found.",
            "file_path": file_path
        }

    file_size = os.path.getsize(
        file_path
    )

    created_time = os.path.getctime(
        file_path
    )

    modified_time = os.path.getmtime(
        file_path
    )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    mime_type, _ = mimetypes.guess_type(
        file_path
    )

    return {
        "success": True,
        "file_name": os.path.basename(file_path),
        "file_path": os.path.abspath(file_path),
        "file_size_bytes": file_size,
        "file_extension": extension,
        "mime_type": mime_type or "unknown",
        "created_time": datetime.fromtimestamp(
            created_time
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "modified_time": datetime.fromtimestamp(
            modified_time
        ).strftime("%Y-%m-%d %H:%M:%S")
    }


# ============================================================
# DETECT EVIDENCE TYPE
# ============================================================

def detect_evidence_type(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension in IMAGE_EXTENSIONS:
        return "IMAGE"

    if extension in VIDEO_EXTENSIONS:
        return "VIDEO"

    if extension in AUDIO_EXTENSIONS:
        return "AUDIO"

    if extension in DOCUMENT_EXTENSIONS:
        return "DOCUMENT"

    if extension in LOG_EXTENSIONS:
        return "LOG"

    return "UNKNOWN"


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(file_path):

    information = get_basic_file_information(
        file_path
    )

    if not information["success"]:
        return information

    result = {
        "evidence_type": "IMAGE",
        "preprocessing_status": "COMPLETED",
        "file_information": information,
        "image_analysis_ready": True,
        "object_detection_ready": True,
        "person_detection_ready": True,
        "metadata_analysis_ready": True
    }

    # Optional PIL processing
    try:

        from PIL import Image

        image = Image.open(
            file_path
        )

        result["image_information"] = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode
        }

        # EXIF information
        try:

            exif_data = image.getexif()

            exif = {}

            for key, value in exif_data.items():

                exif[str(key)] = str(value)

            result["exif_available"] = bool(
                exif
            )

            result["exif"] = exif

        except Exception:

            result["exif_available"] = False
            result["exif"] = {}

        image.close()

    except ImportError:

        result["image_information"] = {}
        result["exif_available"] = False
        result["exif"] = {}

    except Exception as error:

        result["image_processing_note"] = str(
            error
        )

    return result


# ============================================================
# VIDEO PREPROCESSING
# ============================================================

def preprocess_video(file_path):

    information = get_basic_file_information(
        file_path
    )

    if not information["success"]:
        return information

    result = {
        "evidence_type": "VIDEO",
        "preprocessing_status": "COMPLETED",
        "file_information": information,
        "frame_extraction_ready": True,
        "person_detection_ready": True,
        "object_detection_ready": True,
        "event_analysis_ready": True
    }

    try:

        import cv2

        video = cv2.VideoCapture(
            file_path
        )

        if video.isOpened():

            frame_count = int(
                video.get(
                    cv2.CAP_PROP_FRAME_COUNT
                )
            )

            fps = float(
                video.get(
                    cv2.CAP_PROP_FPS
                )
            )

            width = int(
                video.get(
                    cv2.CAP_PROP_FRAME_WIDTH
                )
            )

            height = int(
                video.get(
                    cv2.CAP_PROP_FRAME_HEIGHT
                )
            )

            duration = 0

            if fps > 0:
                duration = frame_count / fps

            result["video_information"] = {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration_seconds": round(
                    duration,
                    2
                )
            }

            video.release()

        else:

            result["video_information"] = {}

    except ImportError:

        result["video_information"] = {}

        result["processing_note"] = (
            "OpenCV is not installed. "
            "Basic video preprocessing is available."
        )

    except Exception as error:

        result["video_information"] = {}

        result["processing_note"] = str(
            error
        )

    return result


# ============================================================
# PDF / DOCUMENT PREPROCESSING
# ============================================================

def preprocess_document(file_path):

    information = get_basic_file_information(
        file_path
    )

    if not information["success"]:
        return information

    extension = information[
        "file_extension"
    ]

    result = {
        "evidence_type": "DOCUMENT",
        "preprocessing_status": "COMPLETED",
        "file_information": information,
        "text_extraction_ready": True,
        "ocr_ready": True
    }

    extracted_text = ""

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if extension == ".pdf":

        try:

            import fitz

            document = fitz.open(
                file_path
            )

            pages = []

            for page_number in range(
                len(document)
            ):

                page = document[
                    page_number
                ]

                text = page.get_text(
                    "text"
                )

                pages.append({
                    "page_number": page_number + 1,
                    "text": text
                })

                extracted_text += text + "\n"

            document.close()

            result["page_count"] = len(
                pages
            )

            result["pages"] = pages

        except ImportError:

            result["page_count"] = 0
            result["pages"] = []

            result["processing_note"] = (
                "PyMuPDF is not installed."
            )

        except Exception as error:

            result["processing_note"] = str(
                error
            )

    # --------------------------------------------------------
    # TXT
    # --------------------------------------------------------

    elif extension == ".txt":

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                extracted_text = file.read()

        except Exception as error:

            result["processing_note"] = str(
                error
            )

    # --------------------------------------------------------
    # DOCX
    # --------------------------------------------------------

    elif extension == ".docx":

        try:

            from docx import Document

            document = Document(
                file_path
            )

            paragraphs = []

            for paragraph in document.paragraphs:

                if paragraph.text.strip():

                    paragraphs.append(
                        paragraph.text
                    )

            extracted_text = "\n".join(
                paragraphs
            )

            result["paragraph_count"] = len(
                paragraphs
            )

        except ImportError:

            result["processing_note"] = (
                "python-docx is not installed."
            )

        except Exception as error:

            result["processing_note"] = str(
                error
            )

    else:

        result["processing_note"] = (
            "Basic document preprocessing completed."
        )

    result["extracted_text"] = extracted_text

    result["text_length"] = len(
        extracted_text
    )

    return result


# ============================================================
# LOG PREPROCESSING
# ============================================================

def preprocess_log(file_path):

    information = get_basic_file_information(
        file_path
    )

    if not information["success"]:
        return information

    extension = information[
        "file_extension"
    ]

    result = {
        "evidence_type": "LOG",
        "preprocessing_status": "COMPLETED",
        "file_information": information,
        "structured_records": [],
        "timestamp_normalization_ready": True
    }

    # --------------------------------------------------------
    # JSON LOG
    # --------------------------------------------------------

    if extension == ".json":

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                data = json.load(file)

            if isinstance(
                data,
                list
            ):

                records = data

            elif isinstance(
                data,
                dict
            ):

                records = [data]

            else:

                records = []

            result[
                "structured_records"
            ] = records

        except Exception as error:

            result["processing_note"] = str(
                error
            )

    # --------------------------------------------------------
    # CSV LOG
    # --------------------------------------------------------

    elif extension == ".csv":

        try:

            import csv

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore",
                newline=""
            ) as file:

                reader = csv.DictReader(
                    file
                )

                result[
                    "structured_records"
                ] = list(reader)

        except Exception as error:

            result["processing_note"] = str(
                error
            )

    # --------------------------------------------------------
    # TEXT / LOG FILE
    # --------------------------------------------------------

    else:

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                lines = file.readlines()

            records = []

            for line_number, line in enumerate(
                lines,
                start=1
            ):

                clean_line = line.strip()

                if clean_line:

                    records.append({
                        "line_number": line_number,
                        "raw_text": clean_line
                    })

            result[
                "structured_records"
            ] = records

        except Exception as error:

            result["processing_note"] = str(
                error
            )

    result["record_count"] = len(
        result["structured_records"]
    )

    return result


# ============================================================
# AUDIO PREPROCESSING
# ============================================================

def preprocess_audio(file_path):

    information = get_basic_file_information(
        file_path
    )

    if not information["success"]:
        return information

    result = {
        "evidence_type": "AUDIO",
        "preprocessing_status": "COMPLETED",
        "file_information": information,
        "speech_processing_ready": True,
        "audio_analysis_ready": True,
        "transcription_ready": True
    }

    try:

        import wave

        if information[
            "file_extension"
        ] == ".wav":

            audio = wave.open(
                file_path,
                "rb"
            )

            result["audio_information"] = {
                "channels": audio.getnchannels(),
                "sample_width": audio.getsampwidth(),
                "sample_rate": audio.getframerate(),
                "frame_count": audio.getnframes(),
                "duration_seconds": round(
                    audio.getnframes()
                    / audio.getframerate(),
                    2
                )
                if audio.getframerate() > 0
                else 0
            }

            audio.close()

        else:

            result["audio_information"] = {}

    except Exception:

        result["audio_information"] = {}

    return result


# ============================================================
# MAIN PREPROCESSOR
# ============================================================

def preprocess_evidence(
    file_path,
    evidence_uid=None,
    verified_hash=None,
    metadata=None,
    integrity_result=None
):

    if not file_path:

        return {
            "success": False,
            "message": "Evidence file path is required."
        }

    if not os.path.exists(file_path):

        return {
            "success": False,
            "message": "Evidence file does not exist.",
            "file_path": file_path
        }

    file_information = get_basic_file_information(
        file_path
    )

    evidence_type = detect_evidence_type(
        file_path
    )

    # --------------------------------------------------------
    # TYPE-SPECIFIC PREPROCESSING
    # --------------------------------------------------------

    if evidence_type == "IMAGE":

        analysis = preprocess_image(
            file_path
        )

    elif evidence_type == "VIDEO":

        analysis = preprocess_video(
            file_path
        )

    elif evidence_type == "DOCUMENT":

        analysis = preprocess_document(
            file_path
        )

    elif evidence_type == "LOG":

        analysis = preprocess_log(
            file_path
        )

    elif evidence_type == "AUDIO":

        analysis = preprocess_audio(
            file_path
        )

    else:

        analysis = {
            "evidence_type": "UNKNOWN",
            "preprocessing_status": "LIMITED",
            "message": (
                "Unsupported evidence type. "
                "Basic file information is available."
            )
        }

    # --------------------------------------------------------
    # RIYA INPUT PACKAGE
    # --------------------------------------------------------

    result = {
        "success": True,

        "module": (
            "AI Evidence Extraction & Correlation"
        ),

        "stage": (
            "Evidence Pre-processing"
        ),

        "evidence_uid": evidence_uid,

        "verified_hash": verified_hash,

        "integrity_result": integrity_result or {},

        "verified_metadata": metadata or {},

        "file_information": file_information,

        "evidence_type": evidence_type,

        "preprocessing_result": analysis,

        "next_stage": (
            "AI-Based Evidence Extraction"
        )
    }

    return result


# ============================================================
# SAVE PREPROCESSED RESULT
# ============================================================

def save_preprocessed_result(result):

    if not result:

        return None

    evidence_uid = result.get(
        "evidence_uid"
    )

    if not evidence_uid:

        evidence_uid = "UNKNOWN_EVIDENCE"

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in str(evidence_uid)
    )

    filename = (
        f"preprocessed_{safe_uid}.json"
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
            default=str
        )

    return output_path


# ============================================================
# LOAD PREPROCESSED RESULT
# ============================================================

def load_preprocessed_result(
    evidence_uid
):

    safe_uid = "".join(
        character
        if character.isalnum()
        or character in "-_"
        else "_"
        for character in str(evidence_uid)
    )

    filename = (
        f"preprocessed_{safe_uid}.json"
    )

    file_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    if not os.path.exists(
        file_path
    ):

        return None

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return None


# ============================================================
# SIMPLE STATUS
# ============================================================

def get_preprocessor_status():

    return {
        "module": (
            "AI Evidence Extraction & Correlation"
        ),
        "component": (
            "Evidence Pre-processing"
        ),
        "status": "READY",
        "supported_types": [
            "IMAGE",
            "VIDEO",
            "DOCUMENT",
            "LOG",
            "AUDIO"
        ],
        "llm_required": False
    }