import os

import json



from PySide6.QtWidgets import (

    QWidget,

    QVBoxLayout,

    QHBoxLayout,

    QLabel,

    QPushButton,

    QFileDialog,

    QMessageBox,

    QLineEdit,

    QTextEdit,

    QTableWidget,

    QTableWidgetItem,

    QGroupBox,

    QFormLayout,

)

from PySide6.QtCore import Qt



from extraction.final_trust_assessment import (

    run_final_assessment,

    generate_final_reports,

)





class FinalTrustAssessmentPage(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)



        self.parent_window = parent

        self.security_result = {}

        self.integrity_result = {}

        self.riya_result = {}

        self.behaviour_result = {}

        self.correlation_result = {}

        self.evidence_items = []

        self.result = {}



        self.build_ui()



    def build_ui(self):

        main_layout = QVBoxLayout(self)



        title = QLabel("Final Trust Assessment & Reporting")

        title.setStyleSheet(

            "font-size: 24px; font-weight: bold; padding: 10px;"

        )

        main_layout.addWidget(title)



        info = QLabel(

            "Final forensic decision-support stage: "

            "AI claim verification, hallucination-risk analysis, "

            "trust scoring, evidence prioritization and reporting."

        )

        info.setWordWrap(True)

        main_layout.addWidget(info)



        input_group = QGroupBox("Previous Module Outputs")

        input_layout = QFormLayout()



        self.security_path = QLineEdit()

        self.integrity_path = QLineEdit()

        self.riya_path = QLineEdit()

        self.behaviour_path = QLineEdit()

        self.correlation_path = QLineEdit()

        self.evidence_path = QLineEdit()



        input_layout.addRow(

            "Security & Provenance:",

            self.file_row(self.security_path, "security")

        )

        input_layout.addRow(

            "Integrity & Dynamic Trust:",

            self.file_row(self.integrity_path, "integrity")

        )

        input_layout.addRow(

            "AI / Extraction / Validation:",

            self.file_row(self.riya_path, "riya")

        )

        input_layout.addRow(

            "Behaviour Analysis:",

            self.file_row(self.behaviour_path, "behaviour")

        )

        input_layout.addRow(

            "Correlation:",

            self.file_row(self.correlation_path, "correlation")

        )

        input_layout.addRow(

            "Evidence Items:",

            self.file_row(self.evidence_path, "evidence")

        )



        input_group.setLayout(input_layout)

        main_layout.addWidget(input_group)



        uid_layout = QHBoxLayout()

        uid_layout.addWidget(QLabel("Evidence UID:"))



        self.uid_input = QLineEdit()

        self.uid_input.setPlaceholderText("Optional - e.g. EVD-001")

        uid_layout.addWidget(self.uid_input)



        main_layout.addLayout(uid_layout)



        button_layout = QHBoxLayout()



        run_button = QPushButton("Run Final Assessment")

        run_button.clicked.connect(self.run_assessment)

        button_layout.addWidget(run_button)



        report_button = QPushButton("Generate Reports")

        report_button.clicked.connect(self.generate_reports)

        button_layout.addWidget(report_button)



        clear_button = QPushButton("Clear")

        clear_button.clicked.connect(self.clear_page)

        button_layout.addWidget(clear_button)



        main_layout.addLayout(button_layout)



        summary_group = QGroupBox("Final Assessment Summary")

        summary_layout = QVBoxLayout()



        self.summary_table = QTableWidget(7, 2)

        self.summary_table.setHorizontalHeaderLabels(["Parameter", "Result"])

        self.summary_table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.summary_table.horizontalHeader().setStretchLastSection(True)



        summary_layout.addWidget(self.summary_table)

        summary_group.setLayout(summary_layout)

        main_layout.addWidget(summary_group)



        self.output_box = QTextEdit()

        self.output_box.setReadOnly(True)

        self.output_box.setPlaceholderText(

            "Final assessment details will appear here..."

        )

        main_layout.addWidget(self.output_box)



    def file_row(self, line_edit, folder_key):

        widget = QWidget()

        layout = QHBoxLayout(widget)

        layout.setContentsMargins(0, 0, 0, 0)



        layout.addWidget(line_edit)



        button = QPushButton("Browse")

        button.clicked.connect(

            lambda checked=False, target=line_edit, key=folder_key:

                self.browse_json(target, key)

        )

        layout.addWidget(button)



        return widget



    def default_browse_folder(self, folder_key):
        """Return the exact project output folder for each Final Trust input."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        candidates = {
            "security": [
                os.path.join(base_dir, "reports"),
            ],
            "integrity": [
                os.path.join(base_dir, "report"),
            ],
            "riya": [
                os.path.join(base_dir, "extraction", "riya_output"),
            ],
            "behaviour": [
                os.path.join(base_dir, "report", "behavior"),
            ],
            "correlation": [
                os.path.join(base_dir, "report", "riya"),
            ],
            "evidence": [
                base_dir,
                os.path.join(base_dir, "evidence"),
            ],
        }

        for folder in candidates.get(folder_key, [base_dir]):
            if os.path.isdir(folder):
                return folder

        return base_dir

    def browse_json(self, target, folder_key):
        start_folder = self.default_browse_folder(folder_key)

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select JSON File",
            start_folder,
            "JSON Files (*.json);;All Files (*)",
        )

        if path:
            target.setText(path)

    def load_json(self, path):

        if not path:

            return {}



        if not os.path.isfile(path):

            return {}



        try:

            with open(path, "r", encoding="utf-8") as file:

                data = json.load(file)



            return data if isinstance(data, dict) else {}



        except Exception as error:

            QMessageBox.warning(

                self,

                "JSON Error",

                f"Could not read:\n{path}\n\n{error}",

            )

            return {}



    def load_evidence_items(self, path):

        if not path:

            return []



        if not os.path.isfile(path):

            return []



        try:

            with open(path, "r", encoding="utf-8") as file:

                data = json.load(file)



            if isinstance(data, list):

                return data



            if isinstance(data, dict):

                for key in (

                    "evidence_items",

                    "evidence",

                    "evidence_list",

                    "registered_evidence",

                    "prioritized_evidence",

                ):

                    value = data.get(key)

                    if isinstance(value, list):

                        return value



            return []



        except Exception as error:

            QMessageBox.warning(

                self,

                "Evidence JSON Error",

                f"Could not read evidence file:\n{path}\n\n{error}",

            )

            return []



    def run_assessment(self):

        self.security_result = self.load_json(

            self.security_path.text().strip()

        )



        self.integrity_result = self.load_json(

            self.integrity_path.text().strip()

        )



        self.riya_result = self.load_json(

            self.riya_path.text().strip()

        )



        self.behaviour_result = self.load_json(

            self.behaviour_path.text().strip()

        )



        self.correlation_result = self.load_json(

            self.correlation_path.text().strip()

        )



        self.evidence_items = self.load_evidence_items(

            self.evidence_path.text().strip()

        )



        if not self.riya_result:

            QMessageBox.warning(

                self,

                "Missing AI Output",

                "Please select the AI / Extraction / Validation JSON file.",

            )

            return



        try:

            self.result = run_final_assessment(

                security_result=self.security_result,

                integrity_result=self.integrity_result,

                riya_result=self.riya_result,

                behaviour_result=self.behaviour_result,

                correlation_result=self.correlation_result,

                evidence_items=(

                    self.evidence_items

                    if self.evidence_items

                    else None

                ),

            )



            self.update_summary()

            self.display_result()



            QMessageBox.information(

                self,

                "Assessment Complete",

                "Final Trust Assessment completed successfully.",

            )



        except Exception as error:

            QMessageBox.critical(

                self,

                "Assessment Error",

                f"Final assessment failed:\n\n{error}",

            )



    def update_summary(self):

        trust = self.result.get(

            "final_trust_assessment",

            {}

        )



        hallucination = self.result.get(

            "hallucination_analysis",

            {}

        )



        claims = self.result.get(

            "ai_output_verification",

            {}

        ).get(

            "claim_verification",

            {}

        )



        prioritization = self.result.get(

            "evidence_prioritization",

            []

        )



        rows = [

            ("Evidence UID", self.result.get("evidence_uid", "UNKNOWN")),

            (

                "Final Trust Score",

                f"{trust.get('final_score', 0)}/100",

            ),

            (

                "Trust Level",

                trust.get("trust_level", "UNKNOWN"),

            ),

            (

                "Hallucination Risk",

                f"{hallucination.get('risk_score', 0)}/100",

            ),

            (

                "Hallucination Level",

                hallucination.get("risk_level", "UNKNOWN"),

            ),

            (

                "Total Claims",

                claims.get("total_claims", 0),

            ),

            (

                "Evidence Items",

                len(prioritization),

            ),

        ]



        self.summary_table.setRowCount(len(rows))



        for row, (parameter, value) in enumerate(rows):

            self.summary_table.setItem(

                row,

                0,

                QTableWidgetItem(str(parameter)),

            )

            self.summary_table.setItem(

                row,

                1,

                QTableWidgetItem(str(value)),

            )



    def display_result(self):

        trust = self.result.get("final_trust_assessment", {})

        claims = self.result.get(

            "ai_output_verification",

            {}

        ).get(

            "claim_verification",

            {}

        )

        hallucination = self.result.get(

            "hallucination_analysis",

            {}

        )

        factors = self.result.get(

            "trust_factors",

            {}

        )

        explanation = self.result.get(

            "explainable_assessment",

            {}

        )



        lines = []



        lines.append("FINAL TRUST ASSESSMENT")

        lines.append("=" * 60)

        lines.append(

            f"Evidence UID: {self.result.get('evidence_uid', 'UNKNOWN')}"

        )

        lines.append("")



        lines.append("AI OUTPUT VERIFICATION")

        lines.append("-" * 40)

        lines.append(

            f"Total Claims: {claims.get('total_claims', 0)}"

        )

        lines.append(

            f"Supported: {claims.get('supported', 0)}"

        )

        lines.append(

            f"Partially Supported: "

            f"{claims.get('partially_supported', 0)}"

        )

        lines.append(

            f"Unsupported: {claims.get('unsupported', 0)}"

        )

        lines.append(

            f"Contradicted: {claims.get('contradicted', 0)}"

        )

        lines.append("")



        lines.append("HALLUCINATION ANALYSIS")

        lines.append("-" * 40)

        lines.append(

            f"Risk Score: {hallucination.get('risk_score', 0)}/100"

        )

        lines.append(

            f"Risk Level: {hallucination.get('risk_level', 'UNKNOWN')}"

        )

        lines.append("")



        lines.append("TRUST FACTORS")

        lines.append("-" * 40)



        for key, value in factors.items():

            lines.append(f"{key}: {value}/100")



        lines.append("")

        lines.append("FINAL TRUST SCORE")

        lines.append("-" * 40)

        lines.append(

            f"Positive Score: {trust.get('positive_score', 0)}"

        )

        lines.append(

            f"Total Penalty: {trust.get('total_penalty', 0)}"

        )

        lines.append(

            f"Final Score: {trust.get('final_score', 0)}/100"

        )

        lines.append(

            f"Trust Level: {trust.get('trust_level', 'UNKNOWN')}"

        )



        lines.append("")

        lines.append("EXPLAINABLE ASSESSMENT")

        lines.append("-" * 40)

        lines.append(

            explanation.get(

                "human_readable_explanation",

                "No explanation available.",

            )

        )



        lines.append("")

        lines.append("EVIDENCE PRIORITIZATION")

        lines.append("-" * 40)



        for item in self.result.get(

            "evidence_prioritization",

            []

        ):

            lines.append(

                f"{item.get('rank', '-')}. "

                f"{item.get('evidence_uid', 'UNKNOWN')} | "

                f"Trust={item.get('trust_score', 0)} | "

                f"Relevance={item.get('relevance_score', 0)} | "

                f"Investigative Value="

                f"{item.get('investigative_value_score', 0)} | "

                f"Priority={item.get('priority_score', 0)} "

                f"({item.get('priority_level', 'UNKNOWN')})"

            )



        lines.append("")

        lines.append("FORENSIC SCOPE")

        lines.append("-" * 40)

        lines.append(self.result.get("scope", ""))



        lines.append("")

        lines.append(self.result.get("methodology_note", ""))



        self.output_box.setPlainText("\n".join(lines))



    def generate_reports(self):

        if not self.result:

            QMessageBox.warning(

                self,

                "No Assessment",

                "Run Final Trust Assessment first.",

            )

            return



        try:

            reports = generate_final_reports(self.result)



            message = (

                "Reports generated successfully.\n\n"

                f"JSON Report:\n{reports.get('json_report', '')}\n\n"

                f"Text Report:\n{reports.get('text_report', '')}\n\n"

                f"Assessment Output:\n"

                f"{reports.get('assessment_output', '')}"

            )



            QMessageBox.information(

                self,

                "Reports Generated",

                message,

            )



        except Exception as error:

            QMessageBox.critical(

                self,

                "Report Error",

                f"Report generation failed:\n\n{error}",

            )



    def clear_page(self):

        self.security_path.clear()

        self.integrity_path.clear()

        self.riya_path.clear()

        self.behaviour_path.clear()

        self.correlation_path.clear()

        self.evidence_path.clear()

        self.uid_input.clear()

        self.summary_table.clearContents()

        self.output_box.clear()



        self.security_result = {}

        self.integrity_result = {}

        self.riya_result = {}

        self.behaviour_result = {}

        self.correlation_result = {}

        self.evidence_items = []

        self.result = {}
