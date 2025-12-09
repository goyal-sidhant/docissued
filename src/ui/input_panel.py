"""
Input Panel - Clean and Spacious Design
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPlainTextEdit, QPushButton,
    QFrame, QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from ..core.models import DocumentNature
from ..utils.validators import validate_pattern_input, count_lines


class InputPanel(QWidget):
    """Clean step-by-step input panel."""
    
    process_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    input_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        
        content = QWidget()
        content.setStyleSheet("background: white;")
        layout = QVBoxLayout(content)
        layout.setSpacing(24)
        layout.setContentsMargins(28, 28, 28, 28)
        
        # ===== STEP 1 =====
        layout.addWidget(self._make_step_label("1", "Document Type"))
        
        self.nature_combo = QComboBox()
        self.nature_combo.setFixedHeight(42)
        self.nature_combo.setStyleSheet("""
            QComboBox {
                font-size: 13px;
                padding: 8px 14px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
            }
            QComboBox:hover { border-color: #9ca3af; }
            QComboBox:focus { border-color: #3b82f6; }
            QComboBox::drop-down { width: 32px; border: none; }
            QComboBox QAbstractItemView { padding: 4px; }
        """)
        self.nature_combo.addItems(DocumentNature.get_all_values())
        layout.addWidget(self.nature_combo)
        
        layout.addSpacing(16)
        
        # ===== STEP 2 =====
        layout.addWidget(self._make_step_label("2", "Invoice Format"))
        
        hint = QLabel("Mark the serial number with [ ] brackets")
        hint.setStyleSheet("font-size: 12px; color: #6b7280; margin-bottom: 8px;")
        layout.addWidget(hint)
        
        self.pattern_input = QLineEdit()
        self.pattern_input.setFixedHeight(44)
        self.pattern_input.setPlaceholderText("e.g.  GST/24-25/[0001]  or  INV-[001]-A")
        self.pattern_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 10px 14px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
            }
            QLineEdit:hover { border-color: #9ca3af; }
            QLineEdit:focus { border-color: #3b82f6; }
        """)
        layout.addWidget(self.pattern_input)
        
        # Examples - compact
        examples = QLabel(
            "<span style='color: #6b7280;'>Examples:</span> "
            "<code>GST/24-25/[0001]</code> · "
            "<code>INV-[001]-SAL</code> · "
            "<code>GST/*/[001]</code> <span style='color: #9ca3af;'>(* for multiple series)</span>"
        )
        examples.setStyleSheet("font-size: 11px; color: #9ca3af; margin-top: 6px;")
        examples.setWordWrap(True)
        layout.addWidget(examples)
        
        # Validation feedback
        self.pattern_feedback = QLabel("")
        self.pattern_feedback.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.pattern_feedback.hide()
        layout.addWidget(self.pattern_feedback)
        
        layout.addSpacing(16)
        
        # ===== STEP 3 =====
        layout.addWidget(self._make_step_label("3", "Invoice List"))
        
        paste_hint = QLabel("Paste from Excel or Tally — one invoice per line")
        paste_hint.setStyleSheet("font-size: 12px; color: #6b7280; margin-bottom: 8px;")
        layout.addWidget(paste_hint)
        
        self.invoice_input = QPlainTextEdit()
        self.invoice_input.setMinimumHeight(180)
        self.invoice_input.setPlaceholderText(
            "GST/24-25/0001\n"
            "GST/24-25/0002\n"
            "GST/24-25/0003\n"
            "..."
        )
        self.invoice_input.setStyleSheet("""
            QPlainTextEdit {
                font-size: 13px;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: #fafafa;
                line-height: 1.5;
            }
            QPlainTextEdit:focus { 
                border-color: #3b82f6; 
                background: white;
            }
        """)
        layout.addWidget(self.invoice_input)
        
        self.line_count_label = QLabel("0 invoices")
        self.line_count_label.setStyleSheet("font-size: 12px; color: #9ca3af;")
        layout.addWidget(self.line_count_label)
        
        layout.addSpacing(24)
        
        # ===== BUTTONS =====
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.process_btn = QPushButton("Generate Table 13")
        self.process_btn.setFixedHeight(46)
        self.process_btn.setCursor(Qt.PointingHandCursor)
        self.process_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 600;
                color: white;
                background: #2563eb;
                border: none;
                border-radius: 8px;
                padding: 12px 28px;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:pressed { background: #1e40af; }
            QPushButton:disabled { background: #9ca3af; }
        """)
        btn_layout.addWidget(self.process_btn, 2)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(46)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                color: #6b7280;
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px 20px;
            }
            QPushButton:hover { background: #e5e7eb; }
        """)
        btn_layout.addWidget(self.clear_btn, 1)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _make_step_label(self, num: str, text: str) -> QWidget:
        """Create a simple step label."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(10)
        
        num_label = QLabel(num)
        num_label.setFixedSize(26, 26)
        num_label.setAlignment(Qt.AlignCenter)
        num_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: white;
            background: #3b82f6;
            border-radius: 13px;
        """)
        layout.addWidget(num_label)
        
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1f2937;")
        layout.addWidget(text_label)
        
        layout.addStretch()
        return widget
    
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
                self.pattern_feedback.setText(f"✗ {error}")
                self.pattern_feedback.setStyleSheet("font-size: 12px; color: #dc2626; margin-top: 4px;")
                self.pattern_feedback.show()
            else:
                wildcard_count = text.count('*')
                msg = "✓ Format valid"
                if wildcard_count > 0:
                    msg += " — will detect multiple series"
                self.pattern_feedback.setText(msg)
                self.pattern_feedback.setStyleSheet("font-size: 12px; color: #16a34a; margin-top: 4px;")
                self.pattern_feedback.show()
        else:
            self.pattern_feedback.hide()
        self.input_changed.emit()
    
    def _on_invoice_changed(self):
        text = self.invoice_input.toPlainText()
        count = count_lines(text)
        self.line_count_label.setText(f"{count:,} invoice{'s' if count != 1 else ''}")
        if count > 0:
            self.line_count_label.setStyleSheet("font-size: 12px; color: #16a34a;")
        else:
            self.line_count_label.setStyleSheet("font-size: 12px; color: #9ca3af;")
        self.input_changed.emit()
    
    def validate_inputs(self) -> bool:
        pattern = self.pattern_input.text().strip()
        is_valid, error = validate_pattern_input(pattern)
        
        if not is_valid:
            self.pattern_feedback.setText(f"✗ {error}")
            self.pattern_feedback.setStyleSheet("font-size: 12px; color: #dc2626; margin-top: 4px;")
            self.pattern_feedback.show()
            self.pattern_input.setFocus()
            return False
        
        if not self.invoice_input.toPlainText().strip():
            self.pattern_feedback.setText("✗ Please paste invoice numbers")
            self.pattern_feedback.setStyleSheet("font-size: 12px; color: #dc2626; margin-top: 4px;")
            self.pattern_feedback.show()
            self.invoice_input.setFocus()
            return False
        
        return True
    
    def clear_inputs(self):
        self.nature_combo.setCurrentIndex(0)
        self.pattern_input.clear()
        self.invoice_input.clear()
        self.pattern_feedback.hide()
        self.line_count_label.setText("0 invoices")
        self.line_count_label.setStyleSheet("font-size: 12px; color: #9ca3af;")
    
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
        self.process_btn.setText("Processing..." if is_processing else "Generate Table 13")
        self.pattern_input.setEnabled(not is_processing)
        self.invoice_input.setEnabled(not is_processing)
        self.nature_combo.setEnabled(not is_processing)
