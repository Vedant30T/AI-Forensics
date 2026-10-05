# AI Digital Evidence Security & Provenance

## Project Overview

This project provides a secure digital evidence lifecycle for collecting,
registering, storing, tracking, and verifying digital evidence.

The system supports:

- Android Evidence Acquisition
- Pen Drive Evidence Acquisition
- Evidence Registration
- Evidence UID Generation
- SHA-256 Hash Generation
- Secure Evidence Storage
- Chain of Custody
- Blockchain Reference Registration
- Evidence Access Logging
- Audit Logging
- Provenance Report Generation
- Evidence Registry

## Evidence Lifecycle

Evidence Collection
        ↓
Evidence Registration
        ↓
Evidence UID Generation
        ↓
SHA-256 Hash Generation
        ↓
Secure Storage
        ↓
Chain of Custody
        ↓
Blockchain Reference
        ↓
Provenance Report

## Supported Evidence Types

- Mobile Phone Data
- Pen Drive Data
- CCTV Video
- Images
- Audio
- PDF / Documents
- System Logs
- Digital Forensic Images
- Other Digital Evidence

## Important Security Principle

The actual evidence file is stored in secure storage.

The complete evidence file is NOT stored on the blockchain.

The blockchain reference contains information such as:

- Evidence UID
- Case ID
- SHA-256 Hash
- Timestamp
- Storage Reference
- Collector
- Provenance Information

## Android Evidence

The project uses ADB for Android device detection and evidence acquisition.

The existing:

`apk/EvidenceAcquisition.apk`

is retained for Android SMS acquisition.

## Project Structure

```text
AI_Digital_Evidence/
│
├── main.py
├── requirements.txt
├── README.md
│
├── apk/
│   └── EvidenceAcquisition.apk
│
├── acquisition/
│   ├── __init__.py
│   └── android_acquisition.py
│
├── detection/
│   ├── __init__.py
│   └── android.py
│
├── extraction/
│   ├── __init__.py
│   └── android_extractor.py
│
├── evidence/
│   ├── __init__.py
│   ├── evidence_registry.py
│   ├── chain_of_custody.py
│   ├── blockchain_registry.py
│   ├── provenance_service.py
│   ├── hash_utils.py
│   ├── metadata.py
│   ├── pen_drive.py
│   ├── file_manager.py
│   ├── security.py
│   ├── evidence_access.py
│   ├── evidence_validator.py
│   ├── lifecycle.py
│   ├── audit_logger.py
│   ├── registry_search.py
│   ├── dashboard_data.py
│   ├── report_generator.py
│   ├── case_manager.py
│   ├── usb_detector.py
│   └── system_initializer.py
│
└── utils/
    ├── __init__.py
    └── paths.py