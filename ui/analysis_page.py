import os

import json

import traceback



from PySide6.QtWidgets import (

    QWidget,

    QVBoxLayout,

    QHBoxLayout,

    QLabel,

    QPushButton,

    QLineEdit,

    QTextEdit,

    QFileDialog,

    QMessageBox,

    QTableWidget,

    QTableWidgetItem,

    QGroupBox,

    QFormLayout,

    QHeaderView

)



from extraction.analysis_pipeline import (

    run_analysis,

    generate_reports

)





class AnalysisPage(QWidget):



    def __init__(self, parent=None):

        super().__init__(parent)



        self.parent_window = parent

        self.selected_folder = ""

        self.latest_result = None



        self.build_ui()



    # ========================================================

    # UI

    # ========================================================



    def build_ui(self):



        main_layout = QVBoxLayout()



        title = QLabel(

            "Behavioural Evidence Analysis"

        )



        title.setStyleSheet(

            """

            QLabel {

                font-size: 24px;

                font-weight: bold;

                padding: 10px;

            }

            """

        )



        main_layout.addWidget(title)



        subtitle = QLabel(

            "Timeline Reconstruction, Behaviour Correlation, "

            "Conflict Detection and Source Reliability"

        )



        subtitle.setStyleSheet(

            """

            QLabel {

                font-size: 13px;

                padding-bottom: 8px;

            }

            """

        )



        main_layout.addWidget(

            subtitle

        )



        # ====================================================

        # INPUT

        # ====================================================



        input_group = QGroupBox(

            "Analysis Input"

        )



        input_layout = QFormLayout()



        # Evidence Folder



        file_layout = QHBoxLayout()



        self.file_input = QLineEdit()



        self.file_input.setPlaceholderText(

            "Select evidence folder"

        )



        browse_button = QPushButton(

            "Browse Evidence Folder"

        )



        browse_button.clicked.connect(

            self.browse_folder

        )



        file_layout.addWidget(

            self.file_input

        )



        file_layout.addWidget(

            browse_button

        )



        input_layout.addRow(

            "Evidence Folder:",

            file_layout

        )



        # UID



        self.uid_input = QLineEdit()



        self.uid_input.setPlaceholderText(

            "Enter Evidence UID"

        )



        input_layout.addRow(

            "Evidence UID:",

            self.uid_input

        )



        input_group.setLayout(

            input_layout

        )



        main_layout.addWidget(

            input_group

        )



        # ====================================================

        # BUTTONS

        # ====================================================



        button_layout = QHBoxLayout()



        self.run_button = QPushButton(

            "Run Analysis"

        )



        self.run_button.clicked.connect(

            self.run_analysis

        )



        self.report_button = QPushButton(

            "Generate Reports"

        )



        self.report_button.clicked.connect(

            self.generate_reports

        )



        self.clear_button = QPushButton(

            "Clear"

        )



        self.clear_button.clicked.connect(

            self.clear_page

        )



        button_layout.addWidget(

            self.run_button

        )



        button_layout.addWidget(

            self.report_button

        )



        button_layout.addWidget(

            self.clear_button

        )



        main_layout.addLayout(

            button_layout

        )



        # ====================================================

        # SUMMARY

        # ====================================================



        summary_group = QGroupBox(

            "Analysis Summary"

        )



        summary_layout = QVBoxLayout()



        self.summary_table = QTableWidget(

            0,

            2

        )



        self.summary_table.setHorizontalHeaderLabels(

            [

                "Parameter",

                "Result"

            ]

        )



        self.summary_table.horizontalHeader().setSectionResizeMode(

            0,

            QHeaderView.Stretch

        )



        self.summary_table.horizontalHeader().setSectionResizeMode(

            1,

            QHeaderView.Stretch

        )



        summary_layout.addWidget(

            self.summary_table

        )



        summary_group.setLayout(

            summary_layout

        )



        main_layout.addWidget(

            summary_group

        )



        # ====================================================

        # OUTPUT

        # ====================================================



        output_group = QGroupBox(

            "Detailed Analysis Output"

        )



        output_layout = QVBoxLayout()



        self.output_text = QTextEdit()



        self.output_text.setReadOnly(

            True

        )



        output_layout.addWidget(

            self.output_text

        )



        output_group.setLayout(

            output_layout

        )



        main_layout.addWidget(

            output_group

        )



        self.setLayout(

            main_layout

        )



    # ========================================================

    # BROWSE

    # ========================================================



    def browse_folder(self):



        folder_path = QFileDialog.getExistingDirectory(



            self,

            "Select Evidence Folder",

            ""



        )



        if folder_path:



            self.selected_folder = folder_path



            self.file_input.setText(



                folder_path



            )



# LOAD JSON

    # ========================================================



    def load_json(self, file_path):



        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as file:



            return json.load(file)



    # ========================================================

    # RUN ANALYSIS

    # ========================================================



    def run_analysis(self):



        folder_path = (



            self.file_input



            .text()



            .strip()



        )



        evidence_uid = (



            self.uid_input



            .text()



            .strip()



        )



        if not folder_path:



            QMessageBox.warning(



                self,

                "Missing Folder",



                "Please select the evidence folder."



            )



            return



        if not os.path.isdir(



            folder_path



        ):



            QMessageBox.warning(



                self,

                "Invalid Folder",



                "Selected evidence folder does not exist."



            )



            return



        self.output_text.clear()



        self.output_text.append(



            "Starting behavioural evidence analysis..."



        )



        try:



            json_candidates = []



            for root, dirs, files in os.walk(folder_path):



                for name in files:



                    if name.lower().endswith(".json"):



                        json_candidates.append(



                            os.path.join(root, name)



                        )



            preferred_names = [



                "riya_result.json",

                "riya_output.json",

                "evidence_result.json",

                "analysis_result.json",

                "sms_data.json"



            ]



            preferred_path = None



            for preferred in preferred_names:



                for candidate in json_candidates:



                    if os.path.basename(candidate).lower() == preferred:



                        preferred_path = candidate



                        break



                if preferred_path:



                    break



            if preferred_path is None and len(json_candidates) == 1:



                preferred_path = json_candidates[0]



            if preferred_path is None:



                QMessageBox.warning(



                    self,

                    "Structured JSON Not Found",



                    "Evidence folder selected, but no suitable JSON file "

                    "was found for behavioural analysis."



                )



                return



            self.output_text.append(



                "\nEvidence Folder:\n" + folder_path +

                "\n\nUsing JSON:\n" + preferred_path



            )



            riya_result = self.load_json(



                preferred_path



            )



            if not evidence_uid:



                evidence_uid = (

                    riya_result.get(

                        "evidence_uid",

                        ""

                    )

                )



            result = run_analysis(

                riya_result

            )



            result[

                "evidence_uid"

            ] = evidence_uid



            self.latest_result = result



            self.display_result(

                result

            )



            QMessageBox.information(

                self,

                "Analysis Complete",

                "Behavioural evidence analysis completed successfully."

            )



        except Exception as error:



            self.output_text.append(

                "\nERROR:\n"

                + str(error)

                + "\n\n"

                + traceback.format_exc()

            )



            QMessageBox.critical(

                self,

                "Analysis Error",

                str(error)

            )



    # ========================================================

    # DISPLAY RESULT

    # ========================================================



    def display_result(

        self,

        result

    ):



        self.summary_table.setRowCount(

            0

        )



        summary = result.get(

            "summary",

            {}

        )



        summary_values = [



            (

                "Activities",

                summary.get(

                    "activities",

                    0

                )

            ),



            (

                "Timeline Irregularities",

                summary.get(

                    "timeline_irregularities",

                    0

                )

            ),



            (

                "Behaviour Correlations",

                summary.get(

                    "behaviour_correlations",

                    0

                )

            ),



            (

                "Conflicts",

                summary.get(

                    "conflicts",

                    0

                )

            ),



            (

                "Conflict Score",

                summary.get(

                    "conflict_score",

                    0

                )

            ),



            (

                "Source Reputation Score",

                summary.get(

                    "source_reputation_score",

                    0

                )

            ),



            (

                "Reliability Level",

                summary.get(

                    "reliability_level",

                    "UNKNOWN"

                )

            ),



            (

                "Behaviour Score",

                result.get(

                    "behaviour_score",

                    0

                )

            )

        ]



        for parameter, value in summary_values:



            row = (

                self.summary_table

                .rowCount()

            )



            self.summary_table.insertRow(

                row

            )



            self.summary_table.setItem(

                row,

                0,

                QTableWidgetItem(

                    str(parameter)

                )

            )



            self.summary_table.setItem(

                row,

                1,

                QTableWidgetItem(

                    str(value)

                )

            )



        # ====================================================

        # DETAILED OUTPUT

        # ====================================================



        output = []



        output.append(

            "===== BEHAVIOURAL EVIDENCE ANALYSIS =====\n"

        )



        output.append(

            f"\nEvidence UID: "

            f"{result.get('evidence_uid', '')}\n"

        )



        output.append(

            "\n----------------------------------------"

        )



        output.append(

            "\nBEHAVIOUR SCORE"

        )



        output.append(

            f"\nScore: "

            f"{result.get('behaviour_score', 0)}/100\n"

        )



        # Timeline



        output.append(

            "\n\nTIMELINE RECONSTRUCTION"

        )



        timeline = result.get(

            "timeline_reconstruction",

            []

        )



        if timeline:



            for item in timeline:



                output.append(

                    "\n\n"

                    + json.dumps(

                        item,

                        indent=2,

                        ensure_ascii=False

                    )

                )



        else:



            output.append(

                "\n- No timeline activities found"

            )



        # Correlation



        output.append(

            "\n\nBEHAVIOUR-EVIDENCE CORRELATION"

        )



        correlation = result.get(

            "behaviour_evidence_correlation",

            {}

        )



        output.append(

            "\nTotal Correlations: "

            + str(

                correlation.get(

                    "total_correlations",

                    0

                )

            )

        )



        output.append(

            "\nCorrelation Score: "

            + str(

                correlation.get(

                    "correlation_score",

                    0

                )

            )

            + "/100"

        )



        # Conflicts



        output.append(

            "\n\nCONFLICT ANALYSIS"

        )



        conflict = result.get(

            "conflict_analysis",

            {}

        )



        output.append(

            "\nTotal Conflicts: "

            + str(

                conflict.get(

                    "total_conflicts",

                    0

                )

            )

        )



        output.append(

            "\nConflict Score: "

            + str(

                conflict.get(

                    "conflict_score",

                    0

                )

            )

            + "/100"

        )



        # Source reputation



        output.append(

            "\n\nSOURCE REPUTATION"

        )



        reputation = result.get(

            "source_reputation",

            {}

        )



        output.append(

            "\nSource Type: "

            + str(

                reputation.get(

                    "source_type",

                    "unknown"

                )

            )

        )



        output.append(

            "\nReputation Score: "

            + str(

                reputation.get(

                    "source_reputation_score",

                    0

                )

            )

            + "/100"

        )



        output.append(

            "\nReliability Level: "

            + str(

                reputation.get(

                    "source_reliability_level",

                    "UNKNOWN"

                )

            )

        )



        output.append(

            "\n\nFORENSIC SCOPE"

        )



        output.append(

            "\nThis analysis generates "

            "forensic behavioural signals."

        )



        output.append(

            "\nIt does not determine guilt "

            "or innocence."

        )



        output.append(

            "\nIt does not make a final legal "

            "authenticity decision."

        )



        self.output_text.setPlainText(

            "".join(output)

        )



    # ========================================================

    # REPORTS

    # ========================================================



    def generate_reports(self):



        if not self.latest_result:



            QMessageBox.warning(

                self,

                "No Result",

                "Run analysis first."

            )



            return



        try:



            reports = generate_reports(

                self.latest_result

            )



            QMessageBox.information(

                self,

                "Reports Generated",

                "Reports generated successfully.\n\n"

                "JSON:\n"

                + reports["json_report"]

                + "\n\n"

                "Text:\n"

                + reports["text_report"]

            )



        except Exception as error:



            QMessageBox.critical(

                self,

                "Report Error",

                str(error)

            )



    # ========================================================

    # CLEAR

    # ========================================================



    def clear_page(self):



        self.file_input.clear()



        self.uid_input.clear()



        self.output_text.clear()



        self.summary_table.setRowCount(

            0

        )



        self.selected_folder = ""



        self.latest_result = None