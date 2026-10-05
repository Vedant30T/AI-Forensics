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







from extraction.riya_pipeline import run_riya_pipeline



from extraction.riya_report import (



    save_riya_report,



    save_text_report



)











class RiyaEvidencePage(QWidget):







    def __init__(self, parent=None):



        super().__init__(parent)







        self.selected_file = ""



        self.evidence_uid = ""







        self.build_ui()







    def build_ui(self):







        main_layout = QVBoxLayout()







        # ==========================================



        # TITLE



        # ==========================================







        title = QLabel(



            "AI Evidence Extraction & Correlation"



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



            " Module - Evidence Extraction, "



            "Claims, Correlation, Knowledge Graph "



            "and Cross-Validation"



        )







        subtitle.setStyleSheet(



            """



            QLabel {



                font-size: 13px;



                padding-bottom: 8px;



            }



            """



        )







        main_layout.addWidget(subtitle)







        # ==========================================



        # INPUT GROUP



        # ==========================================







        input_group = QGroupBox(



            "Evidence Input"



        )







        input_layout = QFormLayout()







        # Evidence file







        file_layout = QHBoxLayout()







        self.file_input = QLineEdit()



        self.file_input.setPlaceholderText(



            "Select evidence file"



        )







        browse_button = QPushButton(



            "Browse File"



        )







        browse_button.clicked.connect(



            self.browse_evidence



        )



        folder_button = QPushButton(



            "Browse Folder"



        )



        folder_button.clicked.connect(



            self.browse_evidence_folder



        )







        file_layout.addWidget(



            self.file_input



        )







        file_layout.addWidget(



            browse_button



        )




        file_layout.addWidget(



            folder_button



        )







        input_layout.addRow(



            "Evidence File:",



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







        # Verified hash







        self.hash_input = QLineEdit()







        self.hash_input.setPlaceholderText(



            "Enter verified SHA-256 hash"



        )







        input_layout.addRow(



            "Verified Hash:",



            self.hash_input



        )







        input_group.setLayout(



            input_layout



        )







        main_layout.addWidget(



            input_group



        )







        # ==========================================



        # BUTTONS



        # ==========================================







        button_layout = QHBoxLayout()







        self.run_button = QPushButton(



            "Run  Analysis"



        )







        self.run_button.clicked.connect(



            self.run_analysis



        )







        self.json_button = QPushButton(



            "Generate JSON Report"



        )







        self.json_button.clicked.connect(



            self.generate_json_report



        )







        self.text_button = QPushButton(



            "Save Text Report"



        )







        self.text_button.clicked.connect(



            self.generate_text_report



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



            self.json_button



        )







        button_layout.addWidget(



            self.text_button



        )







        button_layout.addWidget(



            self.clear_button



        )







        main_layout.addLayout(



            button_layout



        )







        # ==========================================



        # SUMMARY TABLE



        # ==========================================







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







        # ==========================================



        # OUTPUT



        # ==========================================







        output_group = QGroupBox(



            " Analysis Output"



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







        self.latest_result = None







    # ==========================================



    # BROWSE EVIDENCE



    # ==========================================







    def browse_evidence(self):







        file_path, _ = QFileDialog.getOpenFileName(



            self,



            "Select Evidence",



            "",



            (



                "All Evidence Files "



                "(*.*);;"



                "Images "



                "(*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp);;"



                "Videos "



                "(*.mp4 *.avi *.mov *.mkv *.wmv *.webm);;"



                "Audio "



                "(*.mp3 *.wav *.aac *.m4a *.ogg *.flac);;"



                "Documents "



                "(*.pdf *.txt *.docx *.doc);;"



                "Logs "



                "(*.log *.csv *.json *.xml)"



            )



        )







        if file_path:







            self.selected_file = file_path







            self.file_input.setText(



                file_path



            )







    def browse_evidence_folder(self):



        folder_path = QFileDialog.getExistingDirectory(



            self,



            "Select Evidence Backup Folder",



            ""



        )



        if folder_path:



            self.selected_file = folder_path



            self.file_input.setText(folder_path)




    # ==========================================



    # RUN ANALYSIS



    # ==========================================







    def run_analysis(self):



        evidence_path = self.file_input.text().strip()



        evidence_uid = self.uid_input.text().strip()



        verified_hash = self.hash_input.text().strip()



        if not evidence_path:



            QMessageBox.warning(



                self,



                "Missing Evidence",



                "Please select an evidence file or backup folder."



            )



            return



        if not os.path.exists(evidence_path):



            QMessageBox.warning(



                self,



                "Invalid Evidence",



                "Selected evidence file/folder does not exist."



            )



            return



        if not evidence_uid:



            QMessageBox.warning(



                self,



                "Missing UID",



                "Please enter Evidence UID."



            )



            return



        self.output_text.clear()



        self.output_text.append("Starting  Evidence Analysis...\n")



        try:



            if os.path.isdir(evidence_path):



                supported_extensions = {



                    ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp",



                    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm",



                    ".mp3", ".wav", ".aac", ".m4a", ".ogg", ".flac",



                    ".pdf", ".txt", ".docx", ".doc",



                    ".log", ".csv", ".json", ".xml"



                }



                evidence_files = []



                for root, _, files in os.walk(evidence_path):



                    for name in files:



                        full_path = os.path.join(root, name)



                        if os.path.splitext(name)[1].lower() in supported_extensions:



                            evidence_files.append(full_path)



                if not evidence_files:



                    QMessageBox.warning(



                        self,



                        "No Evidence Files",



                        "No supported evidence files were found inside the selected folder."



                    )



                    return



                results = []



                for index, file_path in enumerate(evidence_files, start=1):



                    self.output_text.append(



                        f"Analyzing {index}/{len(evidence_files)}: {os.path.basename(file_path)}"



                    )



                    results.append(



                        run_riya_pipeline(



                            evidence_path=file_path,



                            evidence_uid=f"{evidence_uid}-{index:03d}",



                            verified_hash="",



                            metadata={"source_folder": evidence_path},



                            integrity_result={}



                        )



                    )



                result = self.combine_folder_results(



                    results,



                    evidence_uid,



                    evidence_path



                )



            else:



                result = run_riya_pipeline(



                    evidence_path=evidence_path,



                    evidence_uid=evidence_uid,



                    verified_hash=verified_hash,



                    metadata={},



                    integrity_result={}



                )



            self.latest_result = result



            self.display_result(result)



            QMessageBox.information(



                self,



                "Analysis Complete",



                " evidence analysis completed successfully."



            )



        except Exception as error:



            self.output_text.append(



                "\nERROR:\n" + str(error) + "\n\n" + traceback.format_exc()



            )



            QMessageBox.critical(



                self,



                " Analysis Error",



                str(error)



            )




    def combine_folder_results(self, results, evidence_uid, folder_path):



        combined = {



            "evidence_uid": evidence_uid,



            "source_folder": folder_path,



            "summary": {},



            "structured_entities": {},



            "events": [],



            "claims": [],



            "evidence_relationships": [],



            "cross_validation_results": {"summary": {}},



            "knowledge_graph": {"node_count": 0, "relationship_count": 0}



        }



        summary_keys = [



            "entities_detected", "events_detected", "claims_created",



            "graph_nodes", "graph_relationships", "evidence_relationships",



            "corroborating_relationships", "duplicate_relationships",



            "cross_validation_comparisons"



        ]



        for key in summary_keys:



            combined["summary"][key] = sum(



                int(r.get("summary", {}).get(key, 0) or 0) for r in results



            )



        for result in results:



            entities = result.get("structured_entities", {}) or {}



            for entity_type, values in entities.items():



                combined["structured_entities"].setdefault(entity_type, [])



                for value in values or []:



                    if value not in combined["structured_entities"][entity_type]:



                        combined["structured_entities"][entity_type].append(value)



            combined["events"].extend(result.get("events", []) or [])



            combined["claims"].extend(result.get("claims", []) or [])



            combined["evidence_relationships"].extend(



                result.get("evidence_relationships", []) or []



            )



            graph = result.get("knowledge_graph", {}) or {}



            combined["knowledge_graph"]["node_count"] += int(graph.get("node_count", 0) or 0)



            combined["knowledge_graph"]["relationship_count"] += int(graph.get("relationship_count", 0) or 0)



            validation_summary = (result.get("cross_validation_results", {}) or {}).get("summary", {}) or {}



            for key, value in validation_summary.items():



                if isinstance(value, (int, float)):



                    combined["cross_validation_results"]["summary"][key] = (



                        combined["cross_validation_results"]["summary"].get(key, 0) + value



                    )



        return combined




    # ==========================================



    # DISPLAY RESULT



    # ==========================================







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



                "Entities Detected",



                summary.get(



                    "entities_detected",



                    0



                )



            ),







            (



                "Events Detected",



                summary.get(



                    "events_detected",



                    0



                )



            ),







            (



                "Claims Created",



                summary.get(



                    "claims_created",



                    0



                )



            ),







            (



                "Knowledge Graph Nodes",



                summary.get(



                    "graph_nodes",



                    0



                )



            ),







            (



                "Knowledge Graph Relationships",



                summary.get(



                    "graph_relationships",



                    0



                )



            ),







            (



                "Evidence Relationships",



                summary.get(



                    "evidence_relationships",



                    0



                )



            ),







            (



                "Corroborating Relationships",



                summary.get(



                    "corroborating_relationships",



                    0



                )



            ),







            (



                "Duplicate Relationships",



                summary.get(



                    "duplicate_relationships",



                    0



                )



            ),







            (



                "Cross-Validation Comparisons",



                summary.get(



                    "cross_validation_comparisons",



                    0



                )



            )



        ]







        for parameter, value in summary_values:







            row = self.summary_table.rowCount()







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







        # ======================================



        # OUTPUT TEXT



        # ======================================







        output = []







        output.append(



            "=====  EVIDENCE ANALYSIS =====\n"



        )







        output.append(



            f"Evidence UID: "



            f"{result.get('evidence_uid', '')}\n"



        )







        output.append(



            "--------------------------------------\n"



        )







        # Entities







        entities = result.get(



            "structured_entities",



            {}



        )







        output.append(



            "\nSTRUCTURED ENTITIES"



        )







        for entity_type, values in entities.items():







            output.append(



                f"\n{entity_type.upper()}:"



            )







            if values:







                for value in values:







                    output.append(



                        f"\n  - {value}"



                    )







            else:







                output.append(



                    "\n  - None detected"



                )







        # Events







        output.append(



            "\n\nEVENTS"



        )







        events = result.get(



            "events",



            []



        )







        if events:







            for event in events:







                output.append(



                    f"\n- {event}"



                )







        else:







            output.append(



                "\n- No events detected"



            )







        # Claims







        output.append(



            "\n\nCLAIMS"



        )







        claims = result.get(



            "claims",



            []



        )







        if claims:







            for claim in claims:







                if isinstance(



                    claim,



                    dict



                ):







                    text = claim.get(



                        "claim_text",



                        claim.get(



                            "text",



                            str(claim)



                        )



                    )







                    output.append(



                        f"\n- {text}"



                    )







                else:







                    output.append(



                        f"\n- {claim}"



                    )







        else:







            output.append(



                "\n- No claims generated"



            )







        # Correlation







        output.append(



            "\n\nEVIDENCE CORRELATION"



        )







        relationships = result.get(



            "evidence_relationships",



            []



        )







        if relationships:







            for relationship in relationships:







                output.append(



                    "\n"



                    + json.dumps(



                        relationship,



                        indent=2,



                        ensure_ascii=False



                    )



                )







        else:







            output.append(



                "\n- No evidence relationships found"



            )







        # Cross Validation







        output.append(



            "\n\nCROSS-VALIDATION"



        )







        validation = result.get(



            "cross_validation_results",



            {}



        )







        validation_summary = validation.get(



            "summary",



            {}



        )







        output.append(



            "\nSupported: "



            + str(



                validation_summary.get(



                    "supported_count",



                    0



                )



            )



        )







        output.append(



            "\nPartially Supported: "



            + str(



                validation_summary.get(



                    "partially_supported_count",



                    0



                )



            )



        )







        output.append(



            "\nUnsupported: "



            + str(



                validation_summary.get(



                    "unsupported_count",



                    0



                )



            )



        )







        output.append(



            "\nContradicted: "



            + str(



                validation_summary.get(



                    "contradicted_count",



                    0



                )



            )



        )







        # Knowledge graph







        graph = result.get(



            "knowledge_graph",



            {}



        )







        output.append(



            "\n\nKNOWLEDGE GRAPH"



        )







        output.append(



            f"\nNodes: "



            f"{graph.get('node_count', 0)}"



        )







        output.append(



            f"\nRelationships: "



            f"{graph.get('relationship_count', 0)}"



        )







        # Scope







        output.append(



            "\n\nFORENSIC SCOPE"



        )







        output.append(



            "\nThis module generates forensic "



            "analysis signals."



        )







        output.append(



            "\nIt does not decide guilt or innocence."



        )







        output.append(



            "\nIt does not make a final legal "



            "authenticity decision."



        )







        self.output_text.setPlainText(



            "".join(output)



        )







    # ==========================================



    # JSON REPORT



    # ==========================================







    def generate_json_report(self):







        if not self.latest_result:







            QMessageBox.warning(



                self,



                "No Result",



                "Run  analysis first."



            )







            return







        try:







            file_path = save_riya_report(



                self.latest_result



            )







            QMessageBox.information(



                self,



                "Report Generated",



                "JSON report saved successfully:\n"



                + file_path



            )







        except Exception as error:







            QMessageBox.critical(



                self,



                "Report Error",



                str(error)



            )







    # ==========================================



    # TEXT REPORT



    # ==========================================







    def generate_text_report(self):







        if not self.latest_result:







            QMessageBox.warning(



                self,



                "No Result",



                "Run  analysis first."



            )







            return







        try:







            file_path = save_text_report(



                self.latest_result



            )







            QMessageBox.information(



                self,



                "Report Generated",



                "Text report saved successfully:\n"



                + file_path



            )







        except Exception as error:







            QMessageBox.critical(



                self,



                "Report Error",



                str(error)



            )







    # ==========================================



    # CLEAR



    # ==========================================







    def clear_page(self):







        self.file_input.clear()







        self.uid_input.clear()







        self.hash_input.clear()







        self.output_text.clear()







        self.summary_table.setRowCount(



            0



        )







        self.selected_file = ""







        self.evidence_uid = ""







        self.latest_result = None
