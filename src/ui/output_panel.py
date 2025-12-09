"""
Output Panel for GSTR-1 Table 13 Generator.

Contains output display widgets for Table 13 results, missing invoices,
and warnings.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QTextEdit, QFrame, QHeaderView,
    QSizePolicy, QScrollArea, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from typing import List, Optional
from ..core.models import ProcessingResult, SeriesAnalysis, Table13Row
from ..utils.formatters import format_missing_invoices, format_table13_tsv
from .styles import (
    COLORS, CARD_STYLE, WARNING_BOX_STYLE, 
    ERROR_BOX_STYLE, SUCCESS_BOX_STYLE, INFO_BOX_STYLE
)


class OutputPanel(QWidget):
    """Panel displaying processing results."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_result: Optional[ProcessingResult] = None
        self._current_rows: List[Table13Row] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("Output - Table 13 Format")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Results summary
        self.summary_label = QLabel("Process invoices to see results")
        self.summary_label.setProperty("class", "hint")
        layout.addWidget(self.summary_label)
        
        # Main table
        layout.addWidget(self._create_table_section())
        
        # Copy buttons
        layout.addWidget(self._create_copy_buttons())
        
        # Warnings section
        self.warnings_section = self._create_warnings_section()
        self.warnings_section.hide()
        layout.addWidget(self.warnings_section)
        
        # Missing invoices section
        self.missing_section = self._create_missing_section()
        self.missing_section.hide()
        layout.addWidget(self.missing_section)
        
        # Unmatched invoices section
        self.unmatched_section = self._create_unmatched_section()
        self.unmatched_section.hide()
        layout.addWidget(self.unmatched_section)
        
        # Add stretch
        layout.addStretch()
    
    def _create_table_section(self) -> QWidget:
        """Create the main results table."""
        group = QGroupBox("Document Summary")
        layout = QVBoxLayout(group)
        
        # Table widget
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Nature of Document",
            "Sr. No. From",
            "Sr. No. To",
            "Total Number",
            "Cancelled",
            "Net Issued"
        ])
        
        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setMinimumHeight(150)
        
        layout.addWidget(self.results_table)
        
        return group
    
    def _create_copy_buttons(self) -> QWidget:
        """Create copy action buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.copy_table_btn = QPushButton("Copy Table (TSV)")
        self.copy_table_btn.setProperty("class", "secondary")
        self.copy_table_btn.setToolTip("Copy table data as tab-separated values for Excel/GST Portal")
        self.copy_table_btn.clicked.connect(self._copy_table)
        self.copy_table_btn.setEnabled(False)
        layout.addWidget(self.copy_table_btn)
        
        self.copy_missing_btn = QPushButton("Copy Missing List")
        self.copy_missing_btn.setProperty("class", "secondary")
        self.copy_missing_btn.setToolTip("Copy list of cancelled/missing invoice numbers")
        self.copy_missing_btn.clicked.connect(self._copy_missing)
        self.copy_missing_btn.setEnabled(False)
        layout.addWidget(self.copy_missing_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_warnings_section(self) -> QWidget:
        """Create the warnings display section."""
        group = QGroupBox("Warnings")
        layout = QVBoxLayout(group)
        
        self.warnings_text = QLabel()
        self.warnings_text.setWordWrap(True)
        self.warnings_text.setStyleSheet(WARNING_BOX_STYLE)
        layout.addWidget(self.warnings_text)
        
        return group
    
    def _create_missing_section(self) -> QWidget:
        """Create the missing invoices display section."""
        group = QGroupBox("Missing/Cancelled Invoices")
        layout = QVBoxLayout(group)
        
        self.missing_text = QTextEdit()
        self.missing_text.setReadOnly(True)
        self.missing_text.setMaximumHeight(150)
        layout.addWidget(self.missing_text)
        
        return group
    
    def _create_unmatched_section(self) -> QWidget:
        """Create the unmatched invoices display section."""
        group = QGroupBox("Unmatched Invoices (Different Series?)")
        layout = QVBoxLayout(group)
        
        self.unmatched_text = QTextEdit()
        self.unmatched_text.setReadOnly(True)
        self.unmatched_text.setMaximumHeight(120)
        self.unmatched_text.setStyleSheet(f"background-color: {COLORS['bg_tertiary']};")
        layout.addWidget(self.unmatched_text)
        
        return group
    
    def display_result(self, result: ProcessingResult, rows: List[Table13Row]):
        """
        Display processing results.
        
        Args:
            result: The ProcessingResult object
            rows: List of Table13Row for display
        """
        self._current_result = result
        self._current_rows = rows
        
        # Update summary
        self.summary_label.setText(
            f"Processed {result.total_input_lines} invoices | "
            f"{result.total_matched} matched | "
            f"{result.total_unmatched} unmatched | "
            f"{len(result.series_results)} series found"
        )
        self.summary_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: 500;")
        
        # Update table
        self._populate_table(rows)
        
        # Enable copy buttons
        self.copy_table_btn.setEnabled(True)
        self.copy_missing_btn.setEnabled(self._has_missing_invoices())
        
        # Update warnings
        self._update_warnings(result)
        
        # Update missing invoices
        self._update_missing_section(result)
        
        # Update unmatched invoices
        self._update_unmatched_section(result)
    
    def _populate_table(self, rows: List[Table13Row]):
        """Populate the results table with data."""
        self.results_table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            items = [
                QTableWidgetItem(row.nature_of_document),
                QTableWidgetItem(row.sr_no_from),
                QTableWidgetItem(row.sr_no_to),
                QTableWidgetItem(str(row.total_number)),
                QTableWidgetItem(str(row.cancelled)),
                QTableWidgetItem(str(row.net_issued)),
            ]
            
            for col_idx, item in enumerate(items):
                # Right-align numeric columns
                if col_idx >= 3:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Adjust row heights
        self.results_table.resizeRowsToContents()
    
    def _update_warnings(self, result: ProcessingResult):
        """Update warnings section."""
        all_warnings = list(result.warnings)
        
        for series in result.series_results:
            all_warnings.extend(series.warnings)
        
        if all_warnings:
            self.warnings_text.setText("\n\n".join(all_warnings))
            self.warnings_section.show()
        else:
            self.warnings_section.hide()
    
    def _update_missing_section(self, result: ProcessingResult):
        """Update missing invoices section."""
        missing_parts = []
        
        for series in result.series_results:
            if series.missing_invoices:
                series_name = series.series_display_name
                missing_list = format_missing_invoices(series.missing_invoices, max_display=50)
                missing_parts.append(
                    f"Series {series_name}:\n{missing_list}\n({series.cancelled_count} missing)"
                )
        
        if missing_parts:
            self.missing_text.setText("\n\n".join(missing_parts))
            self.missing_section.show()
        else:
            self.missing_section.hide()
    
    def _update_unmatched_section(self, result: ProcessingResult):
        """Update unmatched invoices section."""
        if result.unmatched_invoices:
            unmatched_display = "\n".join(result.unmatched_invoices[:50])
            if len(result.unmatched_invoices) > 50:
                unmatched_display += f"\n... and {len(result.unmatched_invoices) - 50} more"
            
            self.unmatched_text.setText(unmatched_display)
            self.unmatched_section.show()
        else:
            self.unmatched_section.hide()
    
    def _has_missing_invoices(self) -> bool:
        """Check if there are any missing invoices."""
        if not self._current_result:
            return False
        
        return any(
            series.missing_invoices 
            for series in self._current_result.series_results
        )
    
    def _copy_table(self):
        """Copy table data to clipboard."""
        if not self._current_rows:
            return
        
        tsv_data = format_table13_tsv(self._current_rows)
        clipboard = QApplication.clipboard()
        clipboard.setText(tsv_data)
        
        QMessageBox.information(
            self,
            "Copied",
            "Table data copied to clipboard.\nYou can paste it in Excel or GST Portal."
        )
    
    def _copy_missing(self):
        """Copy missing invoice numbers to clipboard."""
        if not self._current_result:
            return
        
        missing_parts = []
        for series in self._current_result.series_results:
            if series.missing_invoices:
                missing_parts.append(f"Series: {series.series_display_name}")
                missing_parts.extend(series.missing_invoices)
                missing_parts.append("")
        
        if missing_parts:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(missing_parts))
            
            QMessageBox.information(
                self,
                "Copied",
                "Missing invoice numbers copied to clipboard."
            )
    
    def clear_results(self):
        """Clear all displayed results."""
        self._current_result = None
        self._current_rows = []
        
        self.summary_label.setText("Process invoices to see results")
        self.summary_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        self.results_table.setRowCount(0)
        
        self.copy_table_btn.setEnabled(False)
        self.copy_missing_btn.setEnabled(False)
        
        self.warnings_section.hide()
        self.missing_section.hide()
        self.unmatched_section.hide()
