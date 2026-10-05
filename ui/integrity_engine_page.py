import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTextEdit,
    QGroupBox,
    QMessageBox
)

from evidence.integrity_engine import (
    verify_evidence_by_uid,
    rehash_verify,
    get_evidence_by_uid,
    get_blockchain_record,
    get_chain_of_custody
)

from evidence.integrity_report import (
    save_integrity_report,
    save_text_report
)


class IntegrityEnginePage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent
        self.current_result = None

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        title = QLabel(
            "Evidence Integrity & Dynamic Trust Engine"
        )

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 12px;
            }
            """
        )

        main_layout.addWidget(title)

        subtitle = QLabel(
            "UID Retrieval • SHA-256 • Metadata Verification • "
            "Integrity Score • Dynamic Trust"
        )

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding-bottom: 10px;
            }
            """
        )

        main_layout.addWidget(subtitle)

        # =================================================
        # UID SECTION
        # =================================================

        uid_group = QGroupBox("Evidence Retrieval")

        uid_layout = QHBoxLayout()

        self.uid_input = QLineEdit()

        self.uid_input.setPlaceholderText(
            "Enter Evidence UID e.g. EVD-CASE001-0001"
        )

        retrieve_button = QPushButton(
            "Retrieve Evidence"
        )

        retrieve_button.clicked.connect(
            self.retrieve_evidence
        )

        uid_layout.addWidget(
            self.uid_input
        )

        uid_layout.addWidget(
            retrieve_button
        )

        uid_group.setLayout(
            uid_layout
        )

        main_layout.addWidget(
            uid_group
        )

        # =================================================
        # REGISTRATION INFORMATION
        # =================================================

        registration_group = QGroupBox(
            "Registration Information"
        )

        registration_layout = QFormLayout()

        self.case_id = QLineEdit()
        self.evidence_type = QLineEdit()
        self.source = QLineEdit()
        self.collector = QLineEdit()
        self.storage_reference = QLineEdit()

        self.case_id.setReadOnly(True)
        self.evidence_type.setReadOnly(True)
        self.source.setReadOnly(True)
        self.collector.setReadOnly(True)
        self.storage_reference.setReadOnly(True)

        registration_layout.addRow(
            "Case ID:",
            self.case_id
        )

        registration_layout.addRow(
            "Evidence Type:",
            self.evidence_type
        )

        registration_layout.addRow(
            "Source / Device:",
            self.source
        )

        registration_layout.addRow(
            "Collector:",
            self.collector
        )

        registration_layout.addRow(
            "Storage Reference:",
            self.storage_reference
        )

        registration_group.setLayout(
            registration_layout
        )

        main_layout.addWidget(
            registration_group
        )

        # =================================================
        # VERIFICATION BUTTONS
        # =================================================

        button_layout = QHBoxLayout()

        verify_button = QPushButton(
            "Verify Evidence"
        )

        verify_button.clicked.connect(
            self.verify_evidence
        )

        rehash_button = QPushButton(
            "Re-Hash Verification"
        )

        rehash_button.clicked.connect(
            self.rehash_evidence
        )

        report_button = QPushButton(
            "Generate JSON Report"
        )

        report_button.clicked.connect(
            self.generate_json_report
        )

        text_report_button = QPushButton(
            "Save Text Report"
        )

        text_report_button.clicked.connect(
            self.generate_text_report
        )

        clear_button = QPushButton(
            "Clear"
        )

        clear_button.clicked.connect(
            self.clear_page
        )

        button_layout.addWidget(
            verify_button
        )

        button_layout.addWidget(
            rehash_button
        )

        button_layout.addWidget(
            report_button
        )

        button_layout.addWidget(
            text_report_button
        )

        button_layout.addWidget(
            clear_button
        )

        main_layout.addLayout(
            button_layout
        )

        # =================================================
        # SCORE SECTION
        # =================================================

        score_group = QGroupBox(
            "Integrity & Dynamic Trust"
        )

        score_layout = QFormLayout()

        self.integrity_score = QLabel(
            "Not Verified"
        )

        self.dynamic_trust_score = QLabel(
            "Not Verified"
        )

        self.hash_status = QLabel(
            "Not Verified"
        )

        self.metadata_status = QLabel(
            "Not Verified"
        )

        self.blockchain_status = QLabel(
            "Not Verified"
        )

        self.custody_status = QLabel(
            "Not Verified"
        )

        score_layout.addRow(
            "Hash Verification:",
            self.hash_status
        )

        score_layout.addRow(
            "Metadata Verification:",
            self.metadata_status
        )

        score_layout.addRow(
            "Blockchain Verification:",
            self.blockchain_status
        )

        score_layout.addRow(
            "Chain of Custody:",
            self.custody_status
        )

        score_layout.addRow(
            "Integrity Score:",
            self.integrity_score
        )

        score_layout.addRow(
            "Dynamic Trust Score:",
            self.dynamic_trust_score
        )

        score_group.setLayout(
            score_layout
        )

        main_layout.addWidget(
            score_group
        )

        # =================================================
        # HASH
        # =================================================

        hash_group = QGroupBox(
            "SHA-256 Hash"
        )

        hash_layout = QVBoxLayout()

        self.hash_output = QTextEdit()

        self.hash_output.setReadOnly(True)

        self.hash_output.setMaximumHeight(120)

        hash_layout.addWidget(
            self.hash_output
        )

        hash_group.setLayout(
            hash_layout
        )

        main_layout.addWidget(
            hash_group
        )

        # =================================================
        # METADATA
        # =================================================

        metadata_group = QGroupBox(
            "Metadata"
        )

        metadata_layout = QVBoxLayout()

        self.metadata_output = QTextEdit()

        self.metadata_output.setReadOnly(True)

        metadata_layout.addWidget(
            self.metadata_output
        )

        metadata_group.setLayout(
            metadata_layout
        )

        main_layout.addWidget(
            metadata_group
        )

        # =================================================
        # DYNAMIC TRUST
        # =================================================

        trust_group = QGroupBox(
            "Dynamic Trust Information"
        )

        trust_layout = QVBoxLayout()

        self.trust_output = QTextEdit()

        self.trust_output.setReadOnly(True)

        trust_layout.addWidget(
            self.trust_output
        )

        trust_group.setLayout(
            trust_layout
        )

        main_layout.addWidget(
            trust_group
        )

        # =================================================
        # VERIFICATION HISTORY
        # =================================================

        history_group = QGroupBox(
            "Verification History"
        )

        history_layout = QVBoxLayout()

        self.history_output = QTextEdit()

        self.history_output.setReadOnly(True)

        history_layout.addWidget(
            self.history_output
        )

        history_group.setLayout(
            history_layout
        )

        main_layout.addWidget(
            history_group
        )

    # =====================================================
    # RETRIEVE EVIDENCE
    # =====================================================

    def retrieve_evidence(self):

        evidence_uid = self.uid_input.text().strip()

        if not evidence_uid:

            QMessageBox.warning(
                self,
                "Evidence UID Required",
                "Please enter an Evidence UID."
            )

            return

        try:

            registration = get_evidence_by_uid(
                evidence_uid
            )

            if not registration:

                QMessageBox.warning(
                    self,
                    "Evidence Not Found",
                    (
                        f"No evidence was found for UID:\n"
                        f"{evidence_uid}"
                    )
                )

                return

            self.case_id.setText(
                str(
                    registration.get(
                        "case_id",
                        ""
                    )
                )
            )

            self.evidence_type.setText(
                str(
                    registration.get(
                        "evidence_type",
                        ""
                    )
                )
            )

            self.source.setText(
                str(
                    registration.get(
                        "source",
                        ""
                    )
                )
            )

            self.collector.setText(
                str(
                    registration.get(
                        "collector",
                        ""
                    )
                )
            )

            self.storage_reference.setText(
                str(
                    registration.get(
                        "storage_reference",
                        ""
                    )
                )
            )

            blockchain = get_blockchain_record(
                evidence_uid
            )

            custody = get_chain_of_custody(
                evidence_uid
            )

            self.hash_output.setPlainText(
                "Reference SHA-256:\n"
                + str(
                    registration.get(
                        "sha256_hash",
                        "Not available"
                    )
                )
                + "\n\nBlockchain Reference:\n"
                + (
                    json.dumps(
                        blockchain,
                        indent=4,
                        default=str
                    )
                    if blockchain
                    else "Not registered"
                )
            )

            self.history_output.setPlainText(
                "\n".join(
                    str(event)
                    for event in custody
                )
                if custody
                else
                "No Chain of Custody events found."
            )

            QMessageBox.information(
                self,
                "Evidence Retrieved",
                "Evidence registration, blockchain and custody information loaded."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Retrieval Error",
                str(error)
            )

    # =====================================================
    # VERIFY
    # =====================================================

    def verify_evidence(self):

        evidence_uid = self.uid_input.text().strip()

        if not evidence_uid:

            QMessageBox.warning(
                self,
                "Evidence UID Required",
                "Please enter an Evidence UID."
            )

            return

        try:

            result = verify_evidence_by_uid(
                evidence_uid
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Verification Error",
                str(error)
            )

            return

        if not result.get(
            "success",
            False
        ):

            QMessageBox.critical(
                self,
                "Verification Error",
                result.get(
                    "message",
                    "Evidence verification failed."
                )
            )

            return

        self.current_result = result

        self.display_result(result)

        QMessageBox.information(
            self,
            "Verification Completed",
            "Evidence integrity and dynamic trust verification completed."
        )

    # =====================================================
    # RE-HASH
    # =====================================================

    def rehash_evidence(self):

        evidence_uid = self.uid_input.text().strip()

        if not evidence_uid:

            QMessageBox.warning(
                self,
                "Evidence UID Required",
                "Please enter an Evidence UID."
            )

            return

        try:

            result = rehash_verify(
                evidence_uid
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Re-Hash Error",
                str(error)
            )

            return

        if not result.get(
            "success",
            False
        ):

            QMessageBox.critical(
                self,
                "Re-Hash Error",
                result.get(
                    "message",
                    "Re-hash verification failed."
                )
            )

            return

        self.current_result = result

        self.display_result(result)

        QMessageBox.information(
            self,
            "Re-Hash Completed",
            "Evidence hash was recalculated and verification history was updated."
        )

    # =====================================================
    # GENERATE JSON REPORT
    # =====================================================

    def generate_json_report(self):

        if not self.current_result:

            QMessageBox.warning(
                self,
                "No Verification Data",
                "Please verify or re-hash the evidence first."
            )

            return

        try:

            report_path = save_integrity_report(
                self.current_result
            )

            QMessageBox.information(
                self,
                "Report Generated",
                (
                    "Integrity JSON report generated successfully.\n\n"
                    f"Location:\n{report_path}"
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Report Error",
                str(error)
            )

    # =====================================================
    # GENERATE TEXT REPORT
    # =====================================================

    def generate_text_report(self):

        if not self.current_result:

            QMessageBox.warning(
                self,
                "No Verification Data",
                "Please verify or re-hash the evidence first."
            )

            return

        try:

            report_path = save_text_report(
                self.current_result
            )

            QMessageBox.information(
                self,
                "Text Report Generated",
                (
                    "Readable text report generated successfully.\n\n"
                    f"Location:\n{report_path}"
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Report Error",
                str(error)
            )

    # =====================================================
    # DISPLAY RESULT
    # =====================================================

    def display_result(self, result):

        hash_result = result.get(
            "hash_verification",
            {}
        )

        metadata_result = result.get(
            "metadata_verification",
            {}
        )

        blockchain_result = result.get(
            "blockchain_verification",
            {}
        )

        custody_history = result.get(
            "chain_of_custody",
            []
        )

        # -------------------------------------------------
        # HASH
        # -------------------------------------------------

        self.hash_output.setPlainText(
            "Reference SHA-256:\n"
            + str(
                hash_result.get(
                    "reference_hash",
                    "N/A"
                )
            )
            + "\n\nCurrent SHA-256:\n"
            + str(
                hash_result.get(
                    "current_hash",
                    "N/A"
                )
            )
            + "\n\nResult:\n"
            + str(
                hash_result.get(
                    "integrity_status",
                    "UNKNOWN"
                )
            )
        )

        self.hash_status.setText(
            str(
                hash_result.get(
                    "integrity_status",
                    "UNKNOWN"
                )
            )
        )

        # -------------------------------------------------
        # METADATA
        # -------------------------------------------------

        metadata = result.get(
            "metadata",
            {}
        )

        metadata_lines = []

        for key, value in metadata.items():

            metadata_lines.append(
                f"{key}: {value}"
            )

        self.metadata_output.setPlainText(
            "\n".join(metadata_lines)
        )

        metadata_score = metadata_result.get(
            "metadata_consistency_score",
            0
        )

        self.metadata_status.setText(
            f"{metadata_score}%"
        )

        # -------------------------------------------------
        # BLOCKCHAIN
        # -------------------------------------------------

        blockchain_verified = blockchain_result.get(
            "verified",
            False
        )

        self.blockchain_status.setText(
            "VERIFIED"
            if blockchain_verified
            else "NOT VERIFIED"
        )

        # -------------------------------------------------
        # CHAIN OF CUSTODY
        # -------------------------------------------------

        custody_count = len(
            custody_history
        )

        self.custody_status.setText(
            f"{custody_count} event(s)"
        )

        # -------------------------------------------------
        # INTEGRITY SCORE
        # -------------------------------------------------

        integrity_data = result.get(
            "integrity_score",
            0
        )

        if isinstance(
            integrity_data,
            dict
        ):

            integrity_score = integrity_data.get(
                "integrity_score",
                integrity_data.get(
                    "score",
                    0
                )
            )

        else:

            integrity_score = integrity_data

        self.integrity_score.setText(
            f"{integrity_score}/100"
        )

        # -------------------------------------------------
        # DYNAMIC TRUST
        # -------------------------------------------------

        dynamic_trust = result.get(
            "dynamic_trust",
            {}
        )

        if isinstance(
            dynamic_trust,
            dict
        ):

            trust_score = dynamic_trust.get(
                "dynamic_trust_score",
                dynamic_trust.get(
                    "score",
                    0
                )
            )

            trust_status = dynamic_trust.get(
                "trust_status",
                "UNKNOWN"
            )

            decision_note = dynamic_trust.get(
                "decision_note",
                ""
            )

        else:

            trust_score = dynamic_trust
            trust_status = "UNKNOWN"
            decision_note = ""

        self.dynamic_trust_score.setText(
            f"{trust_score}/100 - {trust_status}"
        )

        signals = {}

        if isinstance(
            dynamic_trust,
            dict
        ):

            signals = dynamic_trust.get(
                "signals",
                {}
            )

        trust_text = (
            f"Evidence UID: "
            f"{result.get('evidence_uid', '')}\n\n"

            f"Integrity Score: "
            f"{integrity_score}/100\n"

            f"Hash Integrity: "
            f"{signals.get('hash_integrity', 0)}/100\n"

            f"Metadata Consistency: "
            f"{signals.get('metadata_consistency', 0)}/100\n"

            f"Blockchain Verification: "
            f"{signals.get('blockchain_verification', 0)}/100\n"

            f"Chain of Custody: "
            f"{signals.get('chain_of_custody', 0)}/100\n\n"

            f"Dynamic Trust Score: "
            f"{trust_score}/100\n"

            f"Trust Status: "
            f"{trust_status}\n\n"

            f"{decision_note}"
        )

        self.trust_output.setPlainText(
            trust_text
        )

        # -------------------------------------------------
        # VERIFICATION HISTORY
        # -------------------------------------------------

        history = result.get(
            "verification_history",
            []
        )

        if not history:

            history = result.get(
                "chain_of_custody",
                []
            )

        self.history_output.setPlainText(
            "\n".join(
                str(event)
                for event in history
            )
            if history
            else
            "No Verification History found."
        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_page(self):

        self.uid_input.clear()

        self.case_id.clear()
        self.evidence_type.clear()
        self.source.clear()
        self.collector.clear()
        self.storage_reference.clear()

        self.hash_output.clear()
        self.metadata_output.clear()
        self.trust_output.clear()
        self.history_output.clear()

        self.hash_status.setText(
            "Not Verified"
        )

        self.metadata_status.setText(
            "Not Verified"
        )

        self.blockchain_status.setText(
            "Not Verified"
        )

        self.custody_status.setText(
            "Not Verified"
        )

        self.integrity_score.setText(
            "Not Verified"
        )

        self.dynamic_trust_score.setText(
            "Not Verified"
        )

        self.current_result = None