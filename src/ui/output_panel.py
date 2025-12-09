"""
Output Panel - Clear Results Display

Shows Table 13 output in a format that's easy to understand
and copy to GST portal.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QTextEdit, QHeaderView, QScrollArea,
    QApplication, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from typing import List, Optional
from ..core.models import ProcessingResult, SeriesAnalysis, Table13Row
from ..utils.formatters import format_missing_invoices, format_table13_tsv


class ResultCard(QFrame):
    """A card showing key statistics."""
    
    def __init__(self, title: str, value: str, color: str = "#0284c7", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(15, 12, 15, 12)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; border: none;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #64748b; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        self.value_label = value_label
    
    def set_value(self, value: str, color: str = None):
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; border: none;")


class OutputPanel(QWidget):
    """Panel displaying processing results in a clear, readable format."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_result: Optional[ProcessingResult] = None
        self._current_rows: List[Table13Row] = []
        self._setup_ui()
    
    def _setup_ui(self):
        # Scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f8fafc; }")
        
        content = QWidget()
        content.setStyleSheet("background: #f8fafc;")
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_layout = QHBoxLayout()
        title = QLabel("📋 Results - Table 13 Summary")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Stats cards
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background: transparent;")
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setSpacing(15)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.card_total = ResultCard("Total Invoices", "-", "#0284c7")
        self.card_matched = ResultCard("Matched", "-", "#16a34a")
        self.card_cancelled = ResultCard("Cancelled", "-", "#dc2626")
        self.card_series = ResultCard("Series Found", "-", "#7c3aed")
        
        stats_layout.addWidget(self.card_total)
        stats_layout.addWidget(self.card_matched)
        stats_layout.addWidget(self.card_cancelled)
        stats_layout.addWidget(self.card_series)
        
        self.stats_frame.hide()
        layout.addWidget(self.stats_frame)
        
        # Placeholder when no results
        self.placeholder = QLabel("👆 Fill in the details on the left and click 'Generate Table 13' to see results here")
        self.placeholder.setStyleSheet("""
            font-size: 15px;
            color: #94a3b8;
            padding: 60px 40px;
            background-color: white;
            border: 2px dashed #e2e8f0;
            border-radius: 12px;
        """)
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setWordWrap(True)
        layout.addWidget(self.placeholder)
        
        # Main table
        self.table_frame = QFrame()
        self.table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        table_layout = QVBoxLayout(self.table_frame)
        table_layout.setSpacing(12)
        
        table_title = QLabel("📊 Table 13 Output (Ready to copy to GST Portal)")
        table_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e293b; border: none; background: transparent;")
        table_layout.addWidget(table_title)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Document Type",
            "From (Sr. No.)",
            "To (Sr. No.)",
            "Total",
            "Cancelled",
            "Net Issued"
        ])
        
        # Style the table
        self.results_table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #e0f2fe;
                color: #0c4a6e;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                font-weight: bold;
                font-size: 12px;
                padding: 12px 10px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
            }
        """)
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setMinimumHeight(150)
        self.results_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.results_table)
        
        # Copy button
        copy_btn_layout = QHBoxLayout()
        
        self.copy_table_btn = QPushButton("📋  Copy Table for Excel / GST Portal")
        self.copy_table_btn.setMinimumHeight(45)
        self.copy_table_btn.setCursor(Qt.PointingHandCursor)
        self.copy_table_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 500;
                color: white;
                background-color: #16a34a;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
            }
            QPushButton:hover {
                background-color: #15803d;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.copy_table_btn.clicked.connect(self._copy_table)
        copy_btn_layout.addWidget(self.copy_table_btn)
        copy_btn_layout.addStretch()
        
        table_layout.addLayout(copy_btn_layout)
        
        self.table_frame.hide()
        layout.addWidget(self.table_frame)
        
        # Warnings section
        self.warnings_frame = QFrame()
        self.warnings_frame.setStyleSheet("""
            QFrame {
                background-color: #fefce8;
                border: 1px solid #fde047;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        warnings_layout = QVBoxLayout(self.warnings_frame)
        
        warnings_title = QLabel("⚠️ Warnings")
        warnings_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #854d0e; border: none; background: transparent;")
        warnings_layout.addWidget(warnings_title)
        
        self.warnings_text = QLabel()
        self.warnings_text.setStyleSheet("font-size: 13px; color: #713f12; border: none; background: transparent;")
        self.warnings_text.setWordWrap(True)
        warnings_layout.addWidget(self.warnings_text)
        
        self.warnings_frame.hide()
        layout.addWidget(self.warnings_frame)
        
        # Missing invoices section
        self.missing_frame = QFrame()
        self.missing_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        missing_layout = QVBoxLayout(self.missing_frame)
        
        missing_header = QHBoxLayout()
        missing_title = QLabel("❌ Cancelled / Missing Invoice Numbers")
        missing_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc2626; border: none; background: transparent;")
        missing_header.addWidget(missing_title)
        
        self.copy_missing_btn = QPushButton("📋 Copy List")
        self.copy_missing_btn.setCursor(Qt.PointingHandCursor)
        self.copy_missing_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                color: #64748b;
                background-color: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.copy_missing_btn.clicked.connect(self._copy_missing)
        missing_header.addWidget(self.copy_missing_btn)
        missing_header.addStretch()
        
        missing_layout.addLayout(missing_header)
        
        self.missing_text = QTextEdit()
        self.missing_text.setReadOnly(True)
        self.missing_text.setMaximumHeight(120)
        self.missing_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                font-family: Consolas, monospace;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        missing_layout.addWidget(self.missing_text)
        
        self.missing_frame.hide()
        layout.addWidget(self.missing_frame)
        
        # Unmatched invoices section
        self.unmatched_frame = QFrame()
        self.unmatched_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        unmatched_layout = QVBoxLayout(self.unmatched_frame)
        
        unmatched_title = QLabel("🔍 Unmatched Invoices (Different format?)")
        unmatched_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #64748b; border: none; background: transparent;")
        unmatched_layout.addWidget(unmatched_title)
        
        unmatched_hint = QLabel("These invoices didn't match your format - they might belong to a different series")
        unmatched_hint.setStyleSheet("font-size: 12px; color: #94a3b8; border: none; background: transparent;")
        unmatched_layout.addWidget(unmatched_hint)
        
        self.unmatched_text = QTextEdit()
        self.unmatched_text.setReadOnly(True)
        self.unmatched_text.setMaximumHeight(100)
        self.unmatched_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                font-family: Consolas, monospace;
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        unmatched_layout.addWidget(self.unmatched_text)
        
        self.unmatched_frame.hide()
        layout.addWidget(self.unmatched_frame)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def display_result(self, result: ProcessingResult, rows: List[Table13Row]):
        """Display processing results."""
        self._current_result = result
        self._current_rows = rows
        
        # Hide placeholder, show results
        self.placeholder.hide()
        self.stats_frame.show()
        self.table_frame.show()
        
        # Update stat cards
        total_cancelled = sum(s.cancelled_count for s in result.series_results)
        
        self.card_total.set_value(f"{result.total_input_lines:,}")
        self.card_matched.set_value(f"{result.total_matched:,}", "#16a34a")
        self.card_cancelled.set_value(f"{total_cancelled:,}", "#dc2626" if total_cancelled > 0 else "#16a34a")
        self.card_series.set_value(f"{len(result.series_results):,}")
        
        # Update table
        self._populate_table(rows)
        
        # Update warnings
        self._update_warnings(result)
        
        # Update missing invoices
        self._update_missing_section(result)
        
        # Update unmatched invoices
        self._update_unmatched_section(result)
    
    def _populate_table(self, rows: List[Table13Row]):
        """Fill the results table."""
        self.results_table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            # Shorten document type for display
            doc_type = row.nature_of_document
            if len(doc_type) > 35:
                doc_type = doc_type[:32] + "..."
            
            items = [
                QTableWidgetItem(doc_type),
                QTableWidgetItem(row.sr_no_from),
                QTableWidgetItem(row.sr_no_to),
                QTableWidgetItem(str(row.total_number)),
                QTableWidgetItem(str(row.cancelled)),
                QTableWidgetItem(str(row.net_issued)),
            ]
            
            for col_idx, item in enumerate(items):
                if col_idx >= 3:
                    item.setTextAlignment(Qt.AlignCenter)
                    # Highlight cancelled column if non-zero
                    if col_idx == 4 and row.cancelled > 0:
                        item.setForeground(QColor("#dc2626"))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                self.results_table.setItem(row_idx, col_idx, item)
        
        self.results_table.resizeRowsToContents()
    
    def _update_warnings(self, result: ProcessingResult):
        """Update warnings section."""
        all_warnings = list(result.warnings)
        for series in result.series_results:
            all_warnings.extend(series.warnings)
        
        if all_warnings:
            self.warnings_text.setText("\n\n".join(all_warnings))
            self.warnings_frame.show()
        else:
            self.warnings_frame.hide()
    
    def _update_missing_section(self, result: ProcessingResult):
        """Update missing invoices section."""
        missing_parts = []
        
        for series in result.series_results:
            if series.missing_invoices:
                series_name = series.series_display_name.replace('<seq>', '___')
                missing_list = ", ".join(series.missing_invoices[:30])
                if len(series.missing_invoices) > 30:
                    missing_list += f"\n... and {len(series.missing_invoices) - 30} more"
                missing_parts.append(f"Series {series_name}:\n{missing_list}")
        
        if missing_parts:
            self.missing_text.setText("\n\n".join(missing_parts))
            self.missing_frame.show()
        else:
            self.missing_frame.hide()
    
    def _update_unmatched_section(self, result: ProcessingResult):
        """Update unmatched invoices section."""
        if result.unmatched_invoices:
            display_list = result.unmatched_invoices[:20]
            text = "\n".join(display_list)
            if len(result.unmatched_invoices) > 20:
                text += f"\n\n... and {len(result.unmatched_invoices) - 20} more"
            
            self.unmatched_text.setText(text)
            self.unmatched_frame.show()
        else:
            self.unmatched_frame.hide()
    
    def _copy_table(self):
        """Copy table data to clipboard."""
        if not self._current_rows:
            return
        
        tsv_data = format_table13_tsv(self._current_rows)
        clipboard = QApplication.clipboard()
        clipboard.setText(tsv_data)
        
        QMessageBox.information(
            self,
            "Copied! ✅",
            "Table copied to clipboard.\n\nYou can now paste it directly into Excel or the GST Portal."
        )
    
    def _copy_missing(self):
        """Copy missing invoice numbers to clipboard."""
        if not self._current_result:
            return
        
        missing_parts = []
        for series in self._current_result.series_results:
            if series.missing_invoices:
                missing_parts.extend(series.missing_invoices)
        
        if missing_parts:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(missing_parts))
            
            QMessageBox.information(
                self,
                "Copied! ✅",
                f"{len(missing_parts)} cancelled invoice numbers copied to clipboard."
            )
    
    def clear_results(self):
        """Clear all displayed results."""
        self._current_result = None
        self._current_rows = []
        
        self.placeholder.show()
        self.stats_frame.hide()
        self.table_frame.hide()
        self.warnings_frame.hide()
        self.missing_frame.hide()
        self.unmatched_frame.hide()
        
        self.results_table.setRowCount(0)
        
        self.card_total.set_value("-")
        self.card_matched.set_value("-")
        self.card_cancelled.set_value("-")
        self.card_series.set_value("-")
