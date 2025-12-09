"""
Input Panel for GSTR-1 Table 13 Generator.

Contains input widgets for document nature, pattern, and invoice list.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QLineEdit, QPlainTextEdit, QPushButton,
    QGroupBox, QCheckBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from ..core.models import DocumentNature
from ..utils.validators import validate_pattern_input, count_lines
from .styles import COLORS, CARD_STYLE, INFO_BOX_STYLE


class InputPanel(QWidget):
    """Panel containing all input controls."""
    
    # Signals
    process_requested = pyqtSignal()  # Emitted when user clicks Process
    clear_requested = pyqtSignal()    # Emitted when user clicks Clear
    input_changed = pyqtSignal()      # Emitted when any input changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("Input")
        title.setProperty("class", "section-title")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Document Nature Section
        layout.addWidget(self._create_nature_section())
        
        # Pattern Section
        layout.addWidget(self._create_pattern_section())
        
        # Invoice List Section
        layout.addWidget(self._create_invoice_section())
        
        # Options Section
        layout.addWidget(self._create_options_section())
        
        # Buttons
        layout.addWidget(self._create_buttons_section())
        
        # Add stretch to push everything up
        layout.addStretch()
    
    def _create_nature_section(self) -> QWidget:
        """Create the document nature selection section."""
        group = QGroupBox("Document Nature")
        layout = QVBoxLayout(group)
        
        self.nature_combo = QComboBox()
        self.nature_combo.addItems(DocumentNature.get_all_values())
        self.nature_combo.setCurrentIndex(0)
        layout.addWidget(self.nature_combo)
        
        return group
    
    def _create_pattern_section(self) -> QWidget:
        """Create the pattern input section."""
        group = QGroupBox("Invoice Pattern")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Help text
        help_frame = QFrame()
        help_frame.setStyleSheet(INFO_BOX_STYLE)
        help_layout = QVBoxLayout(help_frame)
        help_layout.setContentsMargins(8, 8, 8, 8)
        
        help_text = QLabel(
            "<b>Pattern Notation:</b><br>"
            "• Use <code>[NNN]</code> to mark the sequence number (e.g., <code>[001]</code>, <code>[0001]</code>)<br>"
            "• Use <code>*</code> to mark variable parts that define sub-series<br>"
            "<br>"
            "<b>Examples:</b><br>"
            "• <code>GST/24-25/[0001]</code> — Simple 4-digit sequence<br>"
            "• <code>GST/*/[001]</code> — Multiple series with wildcard<br>"
            "• <code>[001]-SAL-2024</code> — Sequence at start"
        )
        help_text.setWordWrap(True)
        help_text.setTextFormat(Qt.RichText)
        help_layout.addWidget(help_text)
        layout.addWidget(help_frame)
        
        # Pattern input
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("Enter pattern, e.g., GST/24-25/[0001]")
        layout.addWidget(self.pattern_input)
        
        # Validation message
        self.pattern_error = QLabel("")
        self.pattern_error.setProperty("class", "error")
        self.pattern_error.setWordWrap(True)
        self.pattern_error.hide()
        layout.addWidget(self.pattern_error)
        
        return group
    
    def _create_invoice_section(self) -> QWidget:
        """Create the invoice list input section."""
        group = QGroupBox("Invoice List")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Instructions
        instructions = QLabel("Paste invoice numbers below, one per line:")
        instructions.setProperty("class", "hint")
        layout.addWidget(instructions)
        
        # Text area
        self.invoice_input = QPlainTextEdit()
        self.invoice_input.setPlaceholderText(
            "GST/24-25/0001\n"
            "GST/24-25/0002\n"
            "GST/24-25/0003\n"
            "..."
        )
        self.invoice_input.setMinimumHeight(200)
        layout.addWidget(self.invoice_input)
        
        # Line count
        count_layout = QHBoxLayout()
        self.line_count_label = QLabel("0 lines")
        self.line_count_label.setProperty("class", "hint")
        count_layout.addWidget(self.line_count_label)
        count_layout.addStretch()
        layout.addLayout(count_layout)
        
        return group
    
    def _create_options_section(self) -> QWidget:
        """Create the options section."""
        group = QGroupBox("Options")
        layout = QVBoxLayout(group)
        
        self.ignore_zeros_checkbox = QCheckBox("Ignore leading zero differences (treat 01 and 001 as same)")
        self.ignore_zeros_checkbox.setToolTip(
            "When checked, invoice numbers with different zero padding "
            "will be treated as the same sequence number."
        )
        layout.addWidget(self.ignore_zeros_checkbox)
        
        return group
    
    def _create_buttons_section(self) -> QWidget:
        """Create the action buttons section."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 0)
        
        # Process button
        self.process_btn = QPushButton("Process")
        self.process_btn.setMinimumWidth(120)
        self.process_btn.setMinimumHeight(40)
        layout.addWidget(self.process_btn)
        
        # Clear button
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setProperty("class", "secondary")
        self.clear_btn.setMinimumHeight(40)
        layout.addWidget(self.clear_btn)
        
        layout.addStretch()
        
        return widget
    
    def _connect_signals(self):
        """Connect internal signals."""
        self.process_btn.clicked.connect(self._on_process_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.pattern_input.textChanged.connect(self._on_pattern_changed)
        self.invoice_input.textChanged.connect(self._on_invoice_changed)
    
    def _on_process_clicked(self):
        """Handle process button click."""
        if self.validate_inputs():
            self.process_requested.emit()
    
    def _on_clear_clicked(self):
        """Handle clear button click."""
        self.clear_inputs()
        self.clear_requested.emit()
    
    def _on_pattern_changed(self, text: str):
        """Handle pattern input changes."""
        if text.strip():
            is_valid, error = validate_pattern_input(text)
            if not is_valid:
                self.pattern_error.setText(error)
                self.pattern_error.show()
            else:
                self.pattern_error.hide()
        else:
            self.pattern_error.hide()
        
        self.input_changed.emit()
    
    def _on_invoice_changed(self):
        """Handle invoice list changes."""
        text = self.invoice_input.toPlainText()
        line_count = count_lines(text)
        self.line_count_label.setText(f"{line_count} line{'s' if line_count != 1 else ''}")
        self.input_changed.emit()
    
    def validate_inputs(self) -> bool:
        """
        Validate all inputs.
        
        Returns:
            True if all inputs are valid
        """
        # Validate pattern
        pattern = self.pattern_input.text().strip()
        is_valid, error = validate_pattern_input(pattern)
        
        if not is_valid:
            self.pattern_error.setText(error)
            self.pattern_error.show()
            self.pattern_input.setFocus()
            return False
        
        # Validate invoice list
        invoices = self.invoice_input.toPlainText().strip()
        if not invoices:
            self.pattern_error.setText("Please enter invoice numbers")
            self.pattern_error.show()
            self.invoice_input.setFocus()
            return False
        
        self.pattern_error.hide()
        return True
    
    def clear_inputs(self):
        """Clear all inputs to default state."""
        self.nature_combo.setCurrentIndex(0)
        self.pattern_input.clear()
        self.invoice_input.clear()
        self.ignore_zeros_checkbox.setChecked(False)
        self.pattern_error.hide()
        self.line_count_label.setText("0 lines")
    
    def get_document_nature(self) -> str:
        """Get selected document nature."""
        return self.nature_combo.currentText()
    
    def get_pattern(self) -> str:
        """Get entered pattern."""
        return self.pattern_input.text().strip()
    
    def get_invoice_text(self) -> str:
        """Get invoice list text."""
        return self.invoice_input.toPlainText()
    
    def get_ignore_leading_zeros(self) -> bool:
        """Get ignore leading zeros option."""
        return self.ignore_zeros_checkbox.isChecked()
    
    def set_processing_state(self, is_processing: bool):
        """Enable/disable inputs during processing."""
        self.process_btn.setEnabled(not is_processing)
        self.process_btn.setText("Processing..." if is_processing else "Process")
        self.pattern_input.setEnabled(not is_processing)
        self.invoice_input.setEnabled(not is_processing)
        self.nature_combo.setEnabled(not is_processing)
