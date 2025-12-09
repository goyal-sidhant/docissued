"""
Input Panel - Redesigned for GST Practitioners

Simple, step-by-step interface that any accountant can use.
No technical jargon - just plain language.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPlainTextEdit, QPushButton,
    QFrame, QSizePolicy, QSpacerItem, QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from ..core.models import DocumentNature
from ..utils.validators import validate_pattern_input, count_lines


class StepHeader(QFrame):
    """A styled step header with number and title."""
    
    def __init__(self, step_num: int, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Step number circle
        num_label = QLabel(str(step_num))
        num_label.setFixedSize(36, 36)
        num_label.setAlignment(Qt.AlignCenter)
        num_label.setStyleSheet("""
            QLabel {
                background-color: #0284c7;
                color: white;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(num_label)
        
        # Title and subtitle
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #0c4a6e; background: transparent; border: none;")
        text_layout.addWidget(title_label)
        
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet("font-size: 12px; color: #64748b; background: transparent; border: none;")
            sub_label.setWordWrap(True)
            text_layout.addWidget(sub_label)
        
        layout.addLayout(text_layout, 1)


class InputPanel(QWidget):
    """Step-by-step input panel for GST practitioners."""
    
    process_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    input_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        # Scroll area for smaller screens
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== STEP 1: Document Type =====
        layout.addWidget(StepHeader(1, "Document Type", "What type of documents are you summarizing?"))
        
        self.nature_combo = QComboBox()
        self.nature_combo.setMinimumHeight(45)
        self.nature_combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 10px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QComboBox:focus {
                border-color: #0284c7;
            }
            QComboBox::drop-down {
                width: 40px;
                border: none;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                padding: 5px;
            }
        """)
        self.nature_combo.addItems(DocumentNature.get_all_values())
        layout.addWidget(self.nature_combo)
        
        layout.addSpacing(10)
        
        # ===== STEP 2: Invoice Format =====
        layout.addWidget(StepHeader(
            2, 
            "Invoice Number Format", 
            "Show us one example invoice number. Mark the SERIAL NUMBER part with [ ] brackets."
        ))
        
        # Example box
        example_frame = QFrame()
        example_frame.setStyleSheet("""
            QFrame {
                background-color: #fefce8;
                border: 1px solid #fde047;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        example_layout = QVBoxLayout(example_frame)
        example_layout.setSpacing(10)
        
        example_title = QLabel("📝 Examples - How to write the format:")
        example_title.setStyleSheet("font-weight: bold; font-size: 13px; color: #854d0e; background: transparent; border: none;")
        example_layout.addWidget(example_title)
        
        examples_text = QLabel(
            "If your invoices are: <b>GST/24-25/0001</b>, <b>GST/24-25/0002</b>, <b>GST/24-25/0003</b>...\n"
            "Write format as: <b>GST/24-25/[0001]</b>\n\n"
            "If your invoices are: <b>INV-001-A</b>, <b>INV-002-A</b>, <b>INV-003-A</b>...\n"
            "Write format as: <b>INV-[001]-A</b>\n\n"
            "If you have multiple series like <b>GST/A/001</b> and <b>GST/B/001</b>:\n"
            "Write format as: <b>GST/*/[001]</b>  (use * for the changing letter)"
        )
        examples_text.setStyleSheet("font-size: 13px; color: #713f12; background: transparent; border: none; line-height: 1.5;")
        examples_text.setWordWrap(True)
        examples_text.setTextFormat(Qt.RichText)
        example_layout.addWidget(examples_text)
        
        layout.addWidget(example_frame)
        
        # Format input
        format_label = QLabel("Enter your invoice format:")
        format_label.setStyleSheet("font-size: 13px; font-weight: 500; margin-top: 10px;")
        layout.addWidget(format_label)
        
        self.pattern_input = QLineEdit()
        self.pattern_input.setMinimumHeight(50)
        self.pattern_input.setPlaceholderText("Example: GST/24-25/[0001]  or  INV-[001]-A  or  GST/*/[001]")
        self.pattern_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                font-family: Consolas, monospace;
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #0284c7;
            }
        """)
        layout.addWidget(self.pattern_input)
        
        # Validation message
        self.pattern_error = QLabel("")
        self.pattern_error.setStyleSheet("""
            font-size: 13px;
            color: #dc2626;
            padding: 8px 12px;
            background-color: #fef2f2;
            border-radius: 6px;
        """)
        self.pattern_error.setWordWrap(True)
        self.pattern_error.hide()
        layout.addWidget(self.pattern_error)
        
        # Pattern preview/validation success
        self.pattern_success = QLabel("")
        self.pattern_success.setStyleSheet("""
            font-size: 13px;
            color: #16a34a;
            padding: 8px 12px;
            background-color: #f0fdf4;
            border-radius: 6px;
        """)
        self.pattern_success.hide()
        layout.addWidget(self.pattern_success)
        
        layout.addSpacing(10)
        
        # ===== STEP 3: Invoice List =====
        layout.addWidget(StepHeader(
            3, 
            "Paste Invoice Numbers", 
            "Copy invoice numbers from Excel/Tally and paste below (one per line)"
        ))
        
        self.invoice_input = QPlainTextEdit()
        self.invoice_input.setMinimumHeight(200)
        self.invoice_input.setPlaceholderText(
            "Paste your invoice numbers here...\n\n"
            "Example:\n"
            "GST/24-25/0001\n"
            "GST/24-25/0002\n"
            "GST/24-25/0003\n"
            "GST/24-25/0005\n"
            "..."
        )
        self.invoice_input.setStyleSheet("""
            QPlainTextEdit {
                font-size: 14px;
                font-family: Consolas, monospace;
                padding: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                line-height: 1.4;
            }
            QPlainTextEdit:focus {
                border-color: #0284c7;
            }
        """)
        layout.addWidget(self.invoice_input)
        
        # Line count
        self.line_count_label = QLabel("📊 0 invoice numbers entered")
        self.line_count_label.setStyleSheet("font-size: 13px; color: #64748b;")
        layout.addWidget(self.line_count_label)
        
        layout.addSpacing(20)
        
        # ===== ACTION BUTTONS =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.process_btn = QPushButton("🚀  Generate Table 13")
        self.process_btn.setMinimumHeight(55)
        self.process_btn.setCursor(Qt.PointingHandCursor)
        self.process_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #0284c7;
                border: none;
                border-radius: 10px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
            QPushButton:pressed {
                background-color: #075985;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        btn_layout.addWidget(self.process_btn, 2)
        
        self.clear_btn = QPushButton("🗑️  Clear All")
        self.clear_btn.setMinimumHeight(55)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 500;
                color: #64748b;
                background-color: #f1f5f9;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
                color: #475569;
            }
        """)
        btn_layout.addWidget(self.clear_btn, 1)
        
        layout.addLayout(btn_layout)
        
        # Add stretch at the end
        layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(content)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _connect_signals(self):
        self.process_btn.clicked.connect(self._on_process_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.pattern_input.textChanged.connect(self._on_pattern_changed)
        self.invoice_input.textChanged.connect(self._on_invoice_changed)
    
    def _on_process_clicked(self):
        if self.validate_inputs():
            self.process_requested.emit()
    
    def _on_clear_clicked(self):
        self.clear_inputs()
        self.clear_requested.emit()
    
    def _on_pattern_changed(self, text: str):
        if text.strip():
            is_valid, error = validate_pattern_input(text)
            if not is_valid:
                self.pattern_error.setText("❌ " + error)
                self.pattern_error.show()
                self.pattern_success.hide()
            else:
                self.pattern_error.hide()
                # Show success preview
                wildcard_count = text.count('*')
                
                msg = "✅ Format looks good!"
                if wildcard_count > 0:
                    msg += " Will auto-detect multiple series."
                
                self.pattern_success.setText(msg)
                self.pattern_success.show()
        else:
            self.pattern_error.hide()
            self.pattern_success.hide()
        
        self.input_changed.emit()
    
    def _on_invoice_changed(self):
        text = self.invoice_input.toPlainText()
        line_count = count_lines(text)
        
        if line_count == 0:
            self.line_count_label.setText("📊 0 invoice numbers entered")
            self.line_count_label.setStyleSheet("font-size: 13px; color: #64748b;")
        elif line_count == 1:
            self.line_count_label.setText("📊 1 invoice number entered")
            self.line_count_label.setStyleSheet("font-size: 13px; color: #16a34a;")
        else:
            self.line_count_label.setText(f"📊 {line_count:,} invoice numbers entered")
            self.line_count_label.setStyleSheet("font-size: 13px; color: #16a34a;")
        
        self.input_changed.emit()
    
    def validate_inputs(self) -> bool:
        pattern = self.pattern_input.text().strip()
        is_valid, error = validate_pattern_input(pattern)
        
        if not is_valid:
            self.pattern_error.setText("❌ " + error)
            self.pattern_error.show()
            self.pattern_success.hide()
            self.pattern_input.setFocus()
            return False
        
        invoices = self.invoice_input.toPlainText().strip()
        if not invoices:
            self.pattern_error.setText("❌ Please paste invoice numbers in Step 3")
            self.pattern_error.show()
            self.invoice_input.setFocus()
            return False
        
        self.pattern_error.hide()
        return True
    
    def clear_inputs(self):
        self.nature_combo.setCurrentIndex(0)
        self.pattern_input.clear()
        self.invoice_input.clear()
        self.pattern_error.hide()
        self.pattern_success.hide()
        self.line_count_label.setText("📊 0 invoice numbers entered")
        self.line_count_label.setStyleSheet("font-size: 13px; color: #64748b;")
    
    def get_document_nature(self) -> str:
        return self.nature_combo.currentText()
    
    def get_pattern(self) -> str:
        return self.pattern_input.text().strip()
    
    def get_invoice_text(self) -> str:
        return self.invoice_input.toPlainText()
    
    def get_ignore_leading_zeros(self) -> bool:
        return False
    
    def set_processing_state(self, is_processing: bool):
        self.process_btn.setEnabled(not is_processing)
        self.process_btn.setText("⏳  Processing..." if is_processing else "🚀  Generate Table 13")
        self.pattern_input.setEnabled(not is_processing)
        self.invoice_input.setEnabled(not is_processing)
        self.nature_combo.setEnabled(not is_processing)
