import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QMessageBox,
    QStackedWidget,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QFrame,
    QScrollArea,
    QButtonGroup,
    QSizePolicy,
    QHeaderView,
)

from detection.android import detect_android_devices
from acquisition.android_acquisition import (
    get_device_info,
    create_backup_folder,
    backup_android_storage,
    start_android_sms_acquisition,
    finish_android_sms_acquisition,
)

from evidence.usb_detector import get_pen_drive_options
from evidence.pen_drive import copy_pen_drive_evidence
from evidence.file_manager import (
    select_evidence_file,
    select_evidence_folder
)
from evidence.evidence_validator import validate_evidence_file
from evidence.provenance_service import create_provenance_record
from evidence.report_generator import generate_provenance_report
from evidence.registry_search import (
    get_all_registered_evidence,
    find_by_uid,
)
from evidence.chain_of_custody import get_custody_history
from evidence.blockchain_registry import get_blockchain_record
from evidence.system_initializer import initialize_project

from ui.integrity_engine_page import IntegrityEnginePage
from ui.riya_page import RiyaEvidencePage
from ui.analysis_page import AnalysisPage
from ui.final_trust_page import FinalTrustAssessmentPage


# =============================================================
# PROJECT PATH
# =============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

APK_PATH = os.path.join(
    BASE_DIR,
    "apk",
    "EvidenceAcquisition.apk"
)


# =============================================================
# DARK THEME (DESIGN ONLY)
# =============================================================

def apply_dark_palette(app):
    """Dark palette so file dialogs / message boxes also look dark."""

    app.setStyle("Fusion")

    palette = QPalette()

    palette.setColor(QPalette.Window, QColor("#0d1117"))
    palette.setColor(QPalette.WindowText, QColor("#e6edf3"))
    palette.setColor(QPalette.Base, QColor("#0d1117"))
    palette.setColor(QPalette.AlternateBase, QColor("#161b22"))
    palette.setColor(QPalette.Text, QColor("#e6edf3"))
    palette.setColor(QPalette.Button, QColor("#21262d"))
    palette.setColor(QPalette.ButtonText, QColor("#e6edf3"))
    palette.setColor(QPalette.ToolTipBase, QColor("#161b22"))
    palette.setColor(QPalette.ToolTipText, QColor("#e6edf3"))
    palette.setColor(QPalette.Highlight, QColor("#2f81f7"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.PlaceholderText, QColor("#6e7681"))
    palette.setColor(QPalette.Link, QColor("#58a6ff"))

    app.setPalette(palette)


DARK_STYLE = """
QWidget {
    font-family: "Segoe UI", "Inter", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    color: #e6edf3;
}

QMainWindow, QDialog, QMessageBox {
    background: #0d1117;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

QLabel {
    color: #e6edf3;
    background: transparent;
}

/* ---------- Header ---------- */

QFrame#header {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}

QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #f0f6fc;
    letter-spacing: 1px;
}

QLabel#subtitle {
    font-size: 12px;
    color: #8b949e;
}

QLabel#pageTitle {
    font-size: 20px;
    font-weight: 700;
    color: #f0f6fc;
    padding: 4px 2px 8px 2px;
}

/* ---------- Sidebar ---------- */

QFrame#sidebar {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
}

QLabel#brand {
    font-size: 15px;
    font-weight: 800;
    color: #58a6ff;
    padding: 10px 6px 14px 6px;
}

QPushButton#nav {
    background: transparent;
    color: #c9d1d9;
    text-align: left;
    padding: 11px 14px;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}

QPushButton#nav:hover {
    background: #21262d;
    color: #ffffff;
}

QPushButton#nav:checked {
    background: #1f6feb;
    color: #ffffff;
}

/* ---------- Status ---------- */

QLabel#status {
    padding: 10px 12px;
    background: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-left: 4px solid #2f81f7;
    border-radius: 6px;
}

/* ---------- Cards ---------- */

QGroupBox {
    font-weight: 700;
    color: #f0f6fc;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-top: 14px;
    padding: 18px 12px 12px 12px;
    background: #161b22;
}

QGroupBox::title {
    color: #58a6ff;
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
}

/* ---------- Buttons ---------- */

QPushButton {
    padding: 9px 16px;
    min-height: 20px;
    border-radius: 6px;
    background: #238636;
    color: #ffffff;
    font-weight: 600;
    border: 1px solid rgba(240, 246, 252, 0.10);
}

QPushButton:hover {
    background: #2ea043;
}

QPushButton:pressed {
    background: #1a7f37;
}

QPushButton:disabled {
    background: #21262d;
    color: #6e7681;
}

/* ---------- Inputs ---------- */

QLineEdit, QTextEdit, QComboBox {
    padding: 8px 10px;
    border: 1px solid #30363d;
    border-radius: 6px;
    background: #0d1117;
    color: #e6edf3;
    selection-background-color: #2f81f7;
    selection-color: #ffffff;
}

QLineEdit:read-only {
    background: #11161d;
    color: #9da7b3;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #2f81f7;
}

QTextEdit {
    font-family: Consolas, "Cascadia Mono", "Courier New", monospace;
    font-size: 13px;
}

QComboBox {
    min-height: 20px;
}

QComboBox::drop-down {
    border: none;
    width: 26px;
}

QComboBox QAbstractItemView {
    background: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    selection-background-color: #1f6feb;
    selection-color: #ffffff;
    outline: none;
}

/* ---------- Progress ---------- */

QProgressBar {
    background: #0d1117;
    color: #e6edf3;
    border: 1px solid #30363d;
    border-radius: 6px;
    text-align: center;
    min-height: 20px;
}

QProgressBar::chunk {
    background: #2f81f7;
    border-radius: 5px;
}

/* ---------- Table ---------- */

QTableWidget {
    background: #0d1117;
    alternate-background-color: #131920;
    color: #e6edf3;
    gridline-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    selection-background-color: #1f3a5f;
    selection-color: #ffffff;
}

QTableWidget::item {
    color: #e6edf3;
    padding: 6px;
}

QTableWidget::item:selected {
    background: #1f3a5f;
    color: #ffffff;
}

QHeaderView::section {
    background: #1c2330;
    color: #f0f6fc;
    padding: 8px;
    font-weight: 700;
    border: none;
    border-right: 1px solid #30363d;
    border-bottom: 1px solid #30363d;
}

QTableCornerButton::section {
    background: #1c2330;
    border: none;
}

/* ---------- Scrollbars ---------- */

QScrollBar:vertical {
    background: transparent;
    width: 12px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #484f58;
}

QScrollBar:horizontal {
    background: transparent;
    height: 12px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #30363d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #484f58;
}

QScrollBar::add-line, QScrollBar::sub-line {
    width: 0px;
    height: 0px;
}

QScrollBar::add-page, QScrollBar::sub-page {
    background: transparent;
}

QToolTip {
    background: #161b22;
    color: #e6edf3;
    border: 1px solid #30363d;
    padding: 4px;
}

QMessageBox QLabel {
    color: #e6edf3;
    min-width: 280px;
}

QMessageBox QPushButton {
    min-width: 80px;
    background: #1f6feb;
}

QMessageBox QPushButton:hover {
    background: #388bfd;
}
"""


# =============================================================
# MAIN WINDOW
# =============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Create required folders automatically
        initialize_project()

        self.android_device = None
        self.selected_evidence_file = ""
        self.selected_pen_drive = ""

        self.compact_mode = False

        self.setWindowTitle(
            "AI Digital Evidence Security & Provenance"
        )

        self.resize(1250, 780)
        self.setMinimumSize(360, 520)

        self.apply_styles()

        self.build_ui()

    # =========================================================
    # STYLE
    # =========================================================

    def apply_styles(self):
        self.setStyleSheet(DARK_STYLE)

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # -----------------------------------------------------
        # STACKED PAGES (created first, navigation uses them)
        # -----------------------------------------------------

        self.pages = QStackedWidget()

        self.android_page = self.create_android_page()
        self.pen_drive_page = self.create_pen_drive_page()
        self.provenance_page = self.create_provenance_page()
        self.registry_page = self.create_registry_page()
        self.integrity_page = IntegrityEnginePage(self)
        self.riya_page = RiyaEvidencePage(self)
        self.analysis_page = AnalysisPage(self)
        self.final_trust_page = FinalTrustAssessmentPage(self)

        self.pages.addWidget(self.android_page)
        self.pages.addWidget(self.pen_drive_page)
        self.pages.addWidget(self.provenance_page)
        self.pages.addWidget(self.registry_page)
        self.pages.addWidget(self.integrity_page)
        self.pages.addWidget(self.riya_page)
        self.pages.addWidget(self.analysis_page)
        self.pages.addWidget(self.final_trust_page)

        # -----------------------------------------------------
        # SIDEBAR NAVIGATION
        # -----------------------------------------------------

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(270)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(6)

        self.brand_label = QLabel("DIGITAL EVIDENCE\nSECURITY SUITE")
        self.brand_label.setObjectName("brand")
        self.brand_label.setAlignment(Qt.AlignCenter)

        sidebar_layout.addWidget(self.brand_label)

        # (full text, short text, page, click handler)
        nav_items = [
            ("Android Evidence", "AND", self.android_page, None),
            ("Pen Drive Evidence", "USB", self.pen_drive_page, None),
            ("Evidence Security & Provenance", "PRV", self.provenance_page, None),
            ("Evidence Registry", "REG", self.registry_page, self.load_registry),
            ("Integrity & Dynamic Trust", "INT", self.integrity_page, None),
            ("AI Evidence Extraction & Correlation", "AI", self.riya_page, None),
            ("Behavioural Evidence Analysis", "BEH", self.analysis_page, None),
            ("Final Trust Assessment", "TRU", self.final_trust_page, None),
        ]

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_buttons = []
        self.nav_texts = []

        for full_text, short_text, page, handler in nav_items:

            button = QPushButton(full_text)
            button.setObjectName("nav")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(full_text)
            button.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed
            )

            if handler:
                button.clicked.connect(handler)
            else:
                button.clicked.connect(
                    lambda checked=False, p=page:
                    self.pages.setCurrentWidget(p)
                )

            self.nav_group.addButton(button)
            self.nav_buttons.append(button)
            self.nav_texts.append((full_text, short_text))

            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        # keep sidebar highlight in sync with the visible page
        self.pages.currentChanged.connect(
            self.sync_navigation
        )

        self.nav_buttons[0].setChecked(True)

        # -----------------------------------------------------
        # RIGHT SIDE (HEADER + SCROLLABLE CONTENT)
        # -----------------------------------------------------

        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)

        self.header = QFrame()
        self.header.setObjectName("header")

        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(14, 10, 14, 10)
        header_layout.setSpacing(2)

        title = QLabel(
            "AI DIGITAL EVIDENCE SECURITY & PROVENANCE"
        )
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)

        self.subtitle = QLabel(
            "Secure Evidence Lifecycle • Hash • Chain of Custody • Blockchain Reference"
        )
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        header_layout.addWidget(title)
        header_layout.addWidget(self.subtitle)

        right_layout.addWidget(self.header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setWidget(self.pages)

        right_layout.addWidget(self.scroll, 1)

        root_layout.addWidget(self.sidebar)
        root_layout.addLayout(right_layout, 1)

    # =========================================================
    # NAVIGATION HELPERS (DESIGN ONLY)
    # =========================================================

    def sync_navigation(self, index):

        if 0 <= index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)

    def set_compact_mode(self, compact):

        if compact == self.compact_mode:
            return

        self.compact_mode = compact

        if compact:
            self.sidebar.setFixedWidth(70)
            self.brand_label.setText("DES")
            self.subtitle.setVisible(False)
        else:
            self.sidebar.setFixedWidth(270)
            self.brand_label.setText("DIGITAL EVIDENCE\nSECURITY SUITE")
            self.subtitle.setVisible(True)

        for button, (full_text, short_text) in zip(
            self.nav_buttons,
            self.nav_texts
        ):
            button.setText(
                short_text if compact else full_text
            )

            if compact:
                button.setStyleSheet(
                    "text-align:center;padding:11px 4px;"
                )
            else:
                button.setStyleSheet("")

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.set_compact_mode(
            self.width() < 900
        )

    # =========================================================
    # SMALL UI HELPER (DESIGN ONLY)
    # =========================================================

    def make_page_title(self, text):

        label = QLabel(text)
        label.setObjectName("pageTitle")
        label.setWordWrap(True)

        return label

    def style_form(self, form):

        form.setFieldGrowthPolicy(
            QFormLayout.ExpandingFieldsGrow
        )
        form.setRowWrapPolicy(
            QFormLayout.WrapLongRows
        )
        form.setLabelAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

    # =========================================================
    # ANDROID PAGE
    # =========================================================

    def create_android_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(
            self.make_page_title(
                "Android Evidence Acquisition"
            )
        )

        device_group = QGroupBox(
            "Android Device"
        )

        device_layout = QVBoxLayout(device_group)
        device_layout.setSpacing(10)

        self.android_status = QLabel(
            "Status: Device not detected"
        )
        self.android_status.setObjectName("status")
        self.android_status.setWordWrap(True)

        self.device_info = QTextEdit()
        self.device_info.setReadOnly(True)
        self.device_info.setMaximumHeight(150)
        self.device_info.setMinimumHeight(110)

        detect_button = QPushButton(
            "Detect Android Device"
        )
        detect_button.clicked.connect(
            self.detect_android
        )

        backup_button = QPushButton(
            "Backup Android Evidence"
        )
        backup_button.clicked.connect(
            self.backup_android
        )

        sms_button = QPushButton(
            "Start SMS Extraction"
        )
        sms_button.clicked.connect(
            self.start_sms
        )

        device_layout.addWidget(self.android_status)
        device_layout.addWidget(detect_button)
        device_layout.addWidget(backup_button)
        device_layout.addWidget(sms_button)
        device_layout.addWidget(self.device_info)

        layout.addWidget(device_group)

        self.android_progress = QProgressBar()
        self.android_progress.setValue(0)

        layout.addWidget(self.android_progress)

        layout.addStretch()

        return page

    # =========================================================
    # DETECT ANDROID
    # =========================================================

    def detect_android(self):

        try:

            devices = detect_android_devices()

            if not devices:

                self.android_device = None

                self.android_status.setText(
                    "Status: No authorized Android device detected."
                )

                self.device_info.setText(
                    "Please connect the Android phone and enable USB Debugging."
                )

                return

            # First authorized device
            self.android_device = devices[0]

            info = get_device_info(
                self.android_device
            )

            self.android_status.setText(
                "Status: Android Device Connected"
            )

            device_text = (
                f"Serial Number : {self.android_device}\n"
                f"Manufacturer  : {info.get('manufacturer', 'Unknown')}\n"
                f"Model         : {info.get('model', 'Unknown')}\n"
                f"Android       : {info.get('android_version', 'Unknown')}\n"
                f"SDK Version   : {info.get('sdk_version', 'Unknown')}\n"
                f"Device        : {info.get('device', 'Unknown')}\n"
                "\n"
                "ADB Status    : AUTHORIZED"
            )

            self.device_info.setText(
                device_text
            )

            self.android_progress.setValue(
                20
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Android Detection Error",
                str(error)
            )

    # =========================================================
    # ANDROID BACKUP
    # =========================================================

    def backup_android(self):

        if not self.android_device:
            self.detect_android()

        if not self.android_device:

            QMessageBox.warning(
                self,
                "Android Device",
                "Please connect and authorize an Android device first."
            )

            return

        try:

            backup_folder = create_backup_folder(
                os.path.join(
                    BASE_DIR,
                    "android_backups"
                )
            )

            self.android_progress.setValue(
                30
            )

            result = backup_android_storage(
                self.android_device,
                backup_folder
            )

            if result["success"]:

                self.android_progress.setValue(
                    100
                )

                self.android_status.setText(
                    "Status: Android Evidence Backup Completed"
                )

                QMessageBox.information(
                    self,
                    "Backup Complete",
                    (
                        "Android evidence backup completed.\n\n"
                        f"Backup Location:\n"
                        f"{result['destination']}"
                    )
                )

            else:

                QMessageBox.warning(
                    self,
                    "Backup Failed",
                    result["message"]
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Backup Error",
                str(error)
            )

    # =========================================================
    # SMS ACQUISITION
    # =========================================================

    def start_sms(self):

        if not self.android_device:
            self.detect_android()

        if not self.android_device:

            QMessageBox.warning(
                self,
                "Android Device",
                "Connect and authorize the Android device first."
            )

            return

        if not os.path.exists(
            APK_PATH
        ):

            QMessageBox.critical(
                self,
                "APK Missing",
                (
                    "EvidenceAcquisition.apk was not found.\n\n"
                    f"Expected location:\n{APK_PATH}"
                )
            )

            return

        try:

            output_folder = os.path.join(
                BASE_DIR,
                "android_backups"
            )

            os.makedirs(
                output_folder,
                exist_ok=True
            )

            output_json = os.path.join(
                output_folder,
                "sms_data.json"
            )

            result = start_android_sms_acquisition(
                APK_PATH,
                output_json
            )

            if not result["success"]:

                QMessageBox.warning(
                    self,
                    "SMS Acquisition",
                    result["message"]
                )

                return

            QMessageBox.information(
                self,
                "SMS Acquisition",
                (
                    "EvidenceAcquisition APK started "
                    "on the Android device.\n\n"
                    "Complete SMS extraction on the phone."
                )
            )

            remote_json = (
                "/sdcard/sms_data.json"
            )

            finish = finish_android_sms_acquisition(
                self.android_device,
                remote_json,
                output_json
            )

            if finish["success"]:

                QMessageBox.information(
                    self,
                    "SMS Complete",
                    (
                        "SMS evidence acquired successfully.\n\n"
                        f"Saved at:\n{finish['path']}"
                    )
                )

            else:

                QMessageBox.warning(
                    self,
                    "SMS Acquisition",
                    finish["message"]
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "SMS Error",
                str(error)
            )

    # =========================================================
    # PEN DRIVE PAGE
    # =========================================================

    def create_pen_drive_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(
            self.make_page_title(
                "Pen Drive / Removable Evidence"
            )
        )

        group = QGroupBox(
            "Evidence Source"
        )

        form = QFormLayout(group)
        self.style_form(form)

        self.pen_drive_combo = QComboBox()

        refresh_button = QPushButton(
            "Refresh Pen Drives"
        )
        refresh_button.clicked.connect(
            self.refresh_pen_drives
        )

        select_folder_button = QPushButton(
            "Select Evidence Folder"
        )
        select_folder_button.clicked.connect(
            self.select_pen_folder
        )

        self.pen_drive_path = QLineEdit()
        self.pen_drive_path.setReadOnly(True)

        backup_button = QPushButton(
            "Create Evidence Backup"
        )
        backup_button.clicked.connect(
            self.backup_pen_drive
        )

        self.pen_drive_status = QLabel(
            "No Pen Drive selected."
        )
        self.pen_drive_status.setObjectName("status")
        self.pen_drive_status.setWordWrap(True)

        form.addRow(
            "Pen Drive:",
            self.pen_drive_combo
        )

        form.addRow(
            "",
            refresh_button
        )

        form.addRow(
            "Evidence Path:",
            self.pen_drive_path
        )

        form.addRow(
            "",
            select_folder_button
        )

        form.addRow(
            "",
            backup_button
        )

        layout.addWidget(group)

        layout.addWidget(
            self.pen_drive_status
        )

        layout.addStretch()

        self.refresh_pen_drives()

        return page

    # =========================================================
    # REFRESH PEN DRIVE
    # =========================================================

    def refresh_pen_drives(self):

        self.pen_drive_combo.clear()

        options = get_pen_drive_options()

        for option in options:

            self.pen_drive_combo.addItem(
                option["display"],
                option["path"]
            )

        if options:

            first_path = options[0]["path"]

            if first_path:

                self.selected_pen_drive = (
                    first_path
                )

                self.pen_drive_path.setText(
                    first_path
                )

                self.pen_drive_status.setText(
                    f"Pen Drive detected: {first_path}"
                )

            else:

                self.selected_pen_drive = ""

                self.pen_drive_path.clear()

                self.pen_drive_status.setText(
                    "No Pen Drive connected. You can select an evidence folder manually."
                )

    # =========================================================
    # SELECT PEN DRIVE FOLDER
    # =========================================================

    def select_pen_folder(self):

        folder = select_evidence_folder(
            self
        )

        if not folder:
            return

        self.selected_pen_drive = (
            folder
        )

        self.pen_drive_path.setText(
            folder
        )

        self.pen_drive_status.setText(
            f"Selected Evidence Folder: {folder}"
        )

    # =========================================================
    # BACKUP PEN DRIVE
    # =========================================================

    def backup_pen_drive(self):

        source = (
            self.pen_drive_path.text().strip()
        )

        if not source:

            QMessageBox.warning(
                self,
                "Pen Drive Evidence",
                "Please select a Pen Drive or evidence folder."
            )

            return

        try:

            result = copy_pen_drive_evidence(
                source
            )

            if result["success"]:

                self.pen_drive_status.setText(
                    (
                        "Evidence backup completed.\n"
                        f"Backup: {result['backup_path']}"
                    )
                )

                QMessageBox.information(
                    self,
                    "Backup Complete",
                    (
                        "Pen Drive evidence backup completed.\n\n"
                        f"{result['backup_path']}"
                    )
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Backup Error",
                str(error)
            )

    # =========================================================
    # PROVENANCE PAGE
    # =========================================================

    def create_provenance_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(
            self.make_page_title(
                "Evidence Security & Provenance"
            )
        )

        group = QGroupBox(
            "Evidence Registration"
        )

        form = QFormLayout(group)
        self.style_form(form)

        self.case_id = QLineEdit()

        self.evidence_type = QComboBox()

        self.evidence_type.addItems([
            "Mobile Phone Data",
            "Pen Drive Data",
            "CCTV Video",
            "Image",
            "Audio",
            "PDF / Document",
            "System Logs",
            "Digital Forensic Image",
            "Other Evidence"
        ])

        self.description = QTextEdit()
        self.description.setMaximumHeight(70)

        self.source = QLineEdit()

        self.collector = QLineEdit()

        self.collection_location = QLineEdit()

        self.acquisition_method = QComboBox()

        self.acquisition_method.addItems([
            "Android ADB Acquisition",
            "Pen Drive Acquisition",
            "File Upload",
            "Forensic Image Acquisition",
            "Manual Collection",
            "Other"
        ])

        self.evidence_path = QLineEdit()
        self.evidence_path.setReadOnly(True)

        select_button = QPushButton(
            "Select Evidence Folder / File"
        )
        select_button.clicked.connect(
            self.select_provenance_file
        )

        register_button = QPushButton(
            "Register Evidence & Create Provenance"
        )
        register_button.clicked.connect(
            self.register_provenance
        )

        form.addRow(
            "Case ID:",
            self.case_id
        )

        form.addRow(
            "Evidence Type:",
            self.evidence_type
        )

        form.addRow(
            "Description:",
            self.description
        )

        form.addRow(
            "Source / Device:",
            self.source
        )

        form.addRow(
            "Collector / Investigator:",
            self.collector
        )

        form.addRow(
            "Collection Location:",
            self.collection_location
        )

        form.addRow(
            "Acquisition Method:",
            self.acquisition_method
        )

        form.addRow(
            "Evidence Folder / File:",
            self.evidence_path
        )

        form.addRow(
            "",
            select_button
        )

        form.addRow(
            "",
            register_button
        )

        layout.addWidget(group)

        result_group = QGroupBox(
            "Provenance Result"
        )

        result_layout = QVBoxLayout(result_group)

        self.provenance_result = QTextEdit()
        self.provenance_result.setReadOnly(True)
        self.provenance_result.setMinimumHeight(200)

        result_layout.addWidget(
            self.provenance_result
        )

        layout.addWidget(result_group)

        return page

    # =========================================================
    # SELECT EVIDENCE FILE
    # =========================================================

    def select_provenance_file(self):
        """
        Select a complete evidence folder or a single evidence file.

        Android / Pen Drive acquisition should normally use the
        complete evidence backup folder. Individual files are also
        supported for CCTV, image, audio, PDF and other evidence.
        """

        # First try selecting the complete evidence folder.
        folder_path = select_evidence_folder(self)

        if folder_path:
            self.selected_evidence_file = folder_path
            self.evidence_path.setText(folder_path)
            return

        # If folder selection is cancelled, allow single-file selection.
        file_path = select_evidence_file(self)

        if not file_path:
            return

        self.selected_evidence_file = file_path
        self.evidence_path.setText(file_path)

    # =========================================================
    # REGISTER PROVENANCE
    # =========================================================

    def register_provenance(self):

        evidence_file = (
            self.evidence_path.text().strip()
        )

        case_id = (
            self.case_id.text().strip()
        )

        description = (
            self.description.toPlainText().strip()
        )

        source = (
            self.source.text().strip()
        )

        collector = (
            self.collector.text().strip()
        )

        location = (
            self.collection_location.text().strip()
        )

        acquisition_method = (
            self.acquisition_method.currentText()
        )

        evidence_type = (
            self.evidence_type.currentText()
        )

        # -----------------------------------------------------
        # Required fields
        # -----------------------------------------------------

        if not case_id:

            QMessageBox.warning(
                self,
                "Registration",
                "Case ID is required."
            )

            return

        if not collector:

            QMessageBox.warning(
                self,
                "Registration",
                "Collector / Investigator is required."
            )

            return

        if not evidence_file:

            QMessageBox.warning(
                self,
                "Registration",
                "Please select an evidence folder or file."
            )

            return

        # -----------------------------------------------------
        # Validate Evidence
        # -----------------------------------------------------

        if not os.path.exists(evidence_file):

            QMessageBox.warning(
                self,
                "Evidence Validation Failed",
                "Selected evidence folder/file does not exist."
            )

            return

        if not (
            os.path.isdir(evidence_file)
            or os.path.isfile(evidence_file)
        ):

            QMessageBox.warning(
                self,
                "Evidence Validation Failed",
                "Selected evidence path is not a valid folder or file."
            )

            return

        # Existing validator is used only for individual files.
        # Complete folders are handled by the provenance service.
        if os.path.isfile(evidence_file):

            validation = validate_evidence_file(
                evidence_file
            )

            if not validation["valid"]:

                QMessageBox.warning(
                    self,
                    "Evidence Validation Failed",
                    "\n".join(
                        validation["errors"]
                    )
                )

                return

        try:

            # -------------------------------------------------
            # Complete Provenance
            # -------------------------------------------------

            provenance = create_provenance_record(
                evidence_file=evidence_file,
                case_id=case_id,
                evidence_type=evidence_type,
                description=description,
                source=source,
                collector=collector,
                collection_location=location,
                acquisition_method=acquisition_method
            )

            # -------------------------------------------------
            # Generate Report
            # -------------------------------------------------

            report = generate_provenance_report(
                provenance
            )

            uid = provenance[
                "evidence_uid"
            ]

            registration = provenance[
                "registration"
            ]

            blockchain = provenance[
                "blockchain"
            ]

            result_text = (
                "EVIDENCE REGISTRATION SUCCESSFUL\n"
                "\n"
                "========================================\n"
                f"Evidence UID : {uid}\n"
                f"Case ID      : {case_id}\n"
                f"Evidence Type: {evidence_type}\n"
                f"File Name    : "
                f"{registration.get('evidence_name', registration.get('file_name', ''))}\n"
                f"File Size    : "
                f"{registration.get('file_size_bytes', 0)} bytes\n"
                "\n"
                "SHA-256 HASH\n"
                "========================================\n"
                f"{registration.get('sha256_hash', '')}\n"
                "\n"
                "SECURE STORAGE\n"
                "========================================\n"
                f"{registration.get('storage_reference', '')}\n"
                "\n"
                "CHAIN OF CUSTODY\n"
                "========================================\n"
                f"Events: "
                f"{len(provenance.get('chain_of_custody', []))}\n"
                "\n"
                "BLOCKCHAIN REFERENCE\n"
                "========================================\n"
                f"Status: "
                f"{blockchain.get('blockchain_status', '')}\n"
                f"Timestamp: "
                f"{blockchain.get('registration_timestamp', '')}\n"
                "\n"
                "FINAL PROVENANCE REPORT\n"
                "========================================\n"
                f"{report.get('report_path', '')}\n"
                "\n"
                "PROVENANCE STATUS: COMPLETE"
            )

            self.provenance_result.setText(
                result_text
            )

            QMessageBox.information(
                self,
                "Evidence Registered",
                (
                    "Evidence Security & Provenance "
                    "registration completed successfully.\n\n"
                    f"Evidence UID:\n{uid}"
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Registration Error",
                str(error)
            )

    # =========================================================
    # REGISTRY PAGE
    # =========================================================

    def create_registry_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        layout.addWidget(
            self.make_page_title(
                "Evidence Registry"
            )
        )

        self.registry_table = QTableWidget()

        self.registry_table.setColumnCount(7)

        self.registry_table.setHorizontalHeaderLabels([
            "Evidence UID",
            "Case ID",
            "Type",
            "File",
            "SHA-256",
            "Storage Reference",
            "Status"
        ])

        self.registry_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.registry_table.setAlternatingRowColors(True)
        self.registry_table.verticalHeader().setVisible(False)
        self.registry_table.horizontalHeader().setStretchLastSection(True)
        self.registry_table.setMinimumHeight(260)
        self.registry_table.setHorizontalScrollMode(
            QTableWidget.ScrollPerPixel
        )

        layout.addWidget(
            self.registry_table,
            1
        )

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        refresh_button = QPushButton(
            "Refresh Registry"
        )
        refresh_button.clicked.connect(
            self.load_registry
        )

        view_button = QPushButton(
            "View Selected Provenance"
        )
        view_button.clicked.connect(
            self.view_selected_provenance
        )

        buttons.addWidget(refresh_button)
        buttons.addWidget(view_button)

        layout.addLayout(buttons)

        return page

    # =========================================================
    # LOAD REGISTRY
    # =========================================================

    def load_registry(self):

        self.pages.setCurrentWidget(
            self.registry_page
        )

        records = get_all_registered_evidence()

        self.registry_table.setRowCount(
            len(records)
        )

        for row, record in enumerate(
            records
        ):

            values = [
                record.get(
                    "evidence_uid",
                    ""
                ),
                record.get(
                    "case_id",
                    ""
                ),
                record.get(
                    "evidence_type",
                    ""
                ),
                record.get(
                    "evidence_name",
                    record.get(
                        "file_name",
                        ""
                    )
                ),
                record.get(
                    "sha256_hash",
                    ""
                ),
                record.get(
                    "storage_reference",
                    ""
                ),
                record.get(
                    "registration_status",
                    ""
                )
            ]

            for column, value in enumerate(
                values
            ):

                self.registry_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(value)
                    )
                )

        self.registry_table.resizeColumnsToContents()

    # =========================================================
    # VIEW PROVENANCE
    # =========================================================

    def view_selected_provenance(self):

        row = (
            self.registry_table.currentRow()
        )

        if row < 0:

            QMessageBox.warning(
                self,
                "Registry",
                "Please select an evidence record first."
            )

            return

        uid_item = (
            self.registry_table.item(
                row,
                0
            )
        )

        if not uid_item:
            return

        uid = uid_item.text()

        record = find_by_uid(
            uid
        )

        if not record:

            QMessageBox.warning(
                self,
                "Registry",
                "Evidence record not found."
            )

            return

        custody = get_custody_history(
            uid
        )

        blockchain = get_blockchain_record(
            uid
        )

        text = (
            "EVIDENCE PROVENANCE\n"
            "\n"
            "========================================\n"
            f"Evidence UID       : {uid}\n"
            f"Case ID            : "
            f"{record.get('case_id', '')}\n"
            f"Evidence Type      : "
            f"{record.get('evidence_type', '')}\n"
            f"Description        : "
            f"{record.get('description', '')}\n"
            f"Source / Device    : "
            f"{record.get('source', '')}\n"
            f"Collector          : "
            f"{record.get('collector', '')}\n"
            f"Collection Time    : "
            f"{record.get('collection_datetime', '')}\n"
            f"Collection Location: "
            f"{record.get('collection_location', '')}\n"
            f"Acquisition Method : "
            f"{record.get('acquisition_method', '')}\n"
            "\n"
            "SHA-256 HASH\n"
            "========================================\n"
            f"{record.get('sha256_hash', '')}\n"
            "\n"
            "SECURE STORAGE\n"
            "========================================\n"
            f"{record.get('storage_reference', '')}\n"
            "\n"
            "CHAIN OF CUSTODY\n"
            "========================================\n"
        )

        for event in custody:

            text += (
                f"\nAction        : "
                f"{event.get('action', '')}\n"
                f"Person        : "
                f"{event.get('person', '')}\n"
                f"Timestamp     : "
                f"{event.get('timestamp', '')}\n"
                f"Location      : "
                f"{event.get('location', '')}\n"
                f"Reason        : "
                f"{event.get('reason', '')}\n"
                f"Authorization : "
                f"{event.get('authorization_status', '')}\n"
                f"Details       : "
                f"{event.get('access_details', '')}\n"
                "----------------------------------------\n"
            )

        text += (
            "\nBLOCKCHAIN REFERENCE\n"
            "========================================\n"
        )

        if blockchain:

            text += (
                f"Status       : "
                f"{blockchain.get('blockchain_status', '')}\n"
                f"Timestamp    : "
                f"{blockchain.get('registration_timestamp', '')}\n"
                f"Storage Ref. : "
                f"{blockchain.get('storage_reference', '')}\n"
                f"Hash         : "
                f"{blockchain.get('sha256_hash', '')}\n"
            )

        else:

            text += (
                "No blockchain reference found.\n"
            )

        dialog = QMessageBox(
            self
        )

        dialog.setWindowTitle(
            "Evidence Provenance"
        )

        dialog.setText(
            "Complete Evidence Provenance Details"
        )

        dialog.setDetailedText(
            text
        )

        dialog.setStandardButtons(
            QMessageBox.Ok
        )

        dialog.exec()


# =============================================================
# APPLICATION START
# =============================================================

def main():

    app = QApplication(
        sys.argv
    )

    apply_dark_palette(app)

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()