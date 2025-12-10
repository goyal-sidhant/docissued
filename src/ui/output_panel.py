"""
Output Panel - Responsive with Visible Scrollbars
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QTextEdit, QHeaderView, QScrollArea,
    QApplication, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from typing import List, Optional
from ..core.models import ProcessingResult, Table13Row
from ..utils.formatters import format_table13_tsv


class OutputPanel(QWidget):
    """Responsive results panel with scrolling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_result: Optional[ProcessingResult] = None
        self._current_rows: List[Table13Row] = []
        self._setup_ui()
    
    def _setup_ui(self):
        # Scroll area with VISIBLE scrollbars
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: #fafafa; 
            }
        """)
        
        content = QWidget()
        content.setStyleSheet("background: #fafafa;")
        content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Results")
        header.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        layout.addWidget(header)
        
        # Placeholder
        self.placeholder = QLabel("Fill in details on the left and click\n'Generate Table 13' to see results")
        self.placeholder.setStyleSheet("""
            font-size: 13px;
            color: #9ca3af;
            padding: 40px 20px;
            background: white;
            border: 1px dashed #d1d5db;
            border-radius: 6px;
        """)
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)
        
        # Stats row
        self.stats_widget = QWidget()
        self.stats_widget.setStyleSheet("background: transparent;")
        self.stats_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        stats_layout = QHBoxLayout(self.stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)
        
        self.stat_total = self._make_stat("0", "Total")
        self.stat_matched = self._make_stat("0", "Matched", "#16a34a")
        self.stat_cancelled = self._make_stat("0", "Cancelled", "#dc2626")
        self.stat_series = self._make_stat("0", "Series")
        
        stats_layout.addWidget(self.stat_total)
        stats_layout.addWidget(self.stat_matched)
        stats_layout.addWidget(self.stat_cancelled)
        stats_layout.addWidget(self.stat_series)
        stats_layout.addStretch()
        
        self.stats_widget.hide()
        layout.addWidget(self.stats_widget)
        
        # Table section
        self.table_section = QWidget()
        self.table_section.setStyleSheet("background: transparent;")
        self.table_section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table_layout = QVBoxLayout(self.table_section)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(10)
        
        # Table header with copy button
        table_header = QHBoxLayout()
        table_title = QLabel("Table 13 Output")
        table_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #374151;")
        table_header.addWidget(table_title)
        table_header.addStretch()
        
        self.copy_btn = QPushButton("Copy for Excel")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                color: white;
                background: #16a34a;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover { background: #15803d; }
        """)
        self.copy_btn.clicked.connect(self._copy_table)
        table_header.addWidget(self.copy_btn)
        
        table_layout.addLayout(table_header)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Document Type", "From", "To", "Total", "Cancelled", "Net"
        ])
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.results_table.setMinimumHeight(100)
        self.results_table.setStyleSheet("""
            QTableWidget {
                font-size: 12px;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                gridline-color: #e5e7eb;
            }
            QTableWidget::item {
                padding: 8px 6px;
            }
            QTableWidget::item:selected {
                background: #eff6ff;
                color: #1f2937;
            }
            QHeaderView::section {
                background: #f3f4f6;
                color: #6b7280;
                font-weight: 600;
                font-size: 11px;
                padding: 8px 6px;
                border: none;
                border-bottom: 1px solid #d1d5db;
            }
        """)
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.results_table, 1)
        
        self.table_section.hide()
        layout.addWidget(self.table_section, 1)
        
        # Warnings section
        self.warnings_widget = QWidget()
        self.warnings_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        warnings_layout = QVBoxLayout(self.warnings_widget)
        warnings_layout.setContentsMargins(0, 0, 0, 0)
        warnings_layout.setSpacing(6)
        
        warnings_title = QLabel("⚠ Warnings")
        warnings_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #b45309;")
        warnings_layout.addWidget(warnings_title)
        
        self.warnings_text = QLabel()
        self.warnings_text.setStyleSheet("""
            font-size: 11px;
            color: #92400e;
            background: #fef3c7;
            padding: 10px;
            border-radius: 5px;
        """)
        self.warnings_text.setWordWrap(True)
        warnings_layout.addWidget(self.warnings_text)
        
        self.warnings_widget.hide()
        layout.addWidget(self.warnings_widget)
        
        # Missing invoices section
        self.missing_widget = QWidget()
        self.missing_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        missing_layout = QVBoxLayout(self.missing_widget)
        missing_layout.setContentsMargins(0, 0, 0, 0)
        missing_layout.setSpacing(6)
        
        missing_header = QHBoxLayout()
        missing_title = QLabel("Cancelled/Missing")
        missing_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #dc2626;")
        missing_header.addWidget(missing_title)
        missing_header.addStretch()
        
        self.copy_missing_btn = QPushButton("Copy")
        self.copy_missing_btn.setCursor(Qt.PointingHandCursor)
        self.copy_missing_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                color: #6b7280;
                background: #f3f4f6;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
            }
            QPushButton:hover { background: #e5e7eb; }
        """)
        self.copy_missing_btn.clicked.connect(self._copy_missing)
        missing_header.addWidget(self.copy_missing_btn)
        
        missing_layout.addLayout(missing_header)
        
        self.missing_text = QTextEdit()
        self.missing_text.setReadOnly(True)
        self.missing_text.setMaximumHeight(80)
        self.missing_text.setStyleSheet("""
            QTextEdit {
                font-size: 11px;
                font-family: Consolas, monospace;
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        missing_layout.addWidget(self.missing_text)
        
        self.missing_widget.hide()
        layout.addWidget(self.missing_widget)
        
        # Unmatched section
        self.unmatched_widget = QWidget()
        self.unmatched_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        unmatched_layout = QVBoxLayout(self.unmatched_widget)
        unmatched_layout.setContentsMargins(0, 0, 0, 0)
        unmatched_layout.setSpacing(6)
        
        unmatched_title = QLabel("Unmatched (different format?)")
        unmatched_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #6b7280;")
        unmatched_layout.addWidget(unmatched_title)
        
        self.unmatched_text = QTextEdit()
        self.unmatched_text.setReadOnly(True)
        self.unmatched_text.setMaximumHeight(70)
        self.unmatched_text.setStyleSheet("""
            QTextEdit {
                font-size: 11px;
                font-family: Consolas, monospace;
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        unmatched_layout.addWidget(self.unmatched_text)
        
        self.unmatched_widget.hide()
        layout.addWidget(self.unmatched_widget)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _make_stat(self, value: str, label: str, color: str = "#1f2937") -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("""
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
        """)
        widget.setMinimumWidth(70)
        widget.setMaximumWidth(100)
        widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(1)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {color}; background: transparent; border: none;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        name_label = QLabel(label)
        name_label.setStyleSheet("font-size: 10px; color: #9ca3af; background: transparent; border: none;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        widget.value_label = value_label
        return widget
    
    def display_result(self, result: ProcessingResult, rows: List[Table13Row]):
        self._current_result = result
        self._current_rows = rows
        
        self.placeholder.hide()
        self.stats_widget.show()
        self.table_section.show()
        
        # Update stats
        total_cancelled = sum(s.cancelled_count for s in result.series_results)
        
        self.stat_total.value_label.setText(f"{result.total_input_lines:,}")
        self.stat_matched.value_label.setText(f"{result.total_matched:,}")
        self.stat_cancelled.value_label.setText(f"{total_cancelled:,}")
        self.stat_series.value_label.setText(f"{len(result.series_results):,}")
        
        # Update table
        self._populate_table(rows)
        
        # Warnings
        all_warnings = list(result.warnings)
        for series in result.series_results:
            all_warnings.extend(series.warnings)
        
        if all_warnings:
            self.warnings_text.setText("\n".join(all_warnings))
            self.warnings_widget.show()
        else:
            self.warnings_widget.hide()
        
        # Missing
        missing_parts = []
        for series in result.series_results:
            if series.missing_invoices:
                inv_list = ", ".join(series.missing_invoices[:15])
                if len(series.missing_invoices) > 15:
                    inv_list += f" ...+{len(series.missing_invoices) - 15} more"
                missing_parts.append(inv_list)
        
        if missing_parts:
            self.missing_text.setText("\n".join(missing_parts))
            self.missing_widget.show()
        else:
            self.missing_widget.hide()
        
        # Unmatched
        if result.unmatched_invoices:
            display = result.unmatched_invoices[:10]
            text = "\n".join(display)
            if len(result.unmatched_invoices) > 10:
                text += f"\n...+{len(result.unmatched_invoices) - 10} more"
            self.unmatched_text.setText(text)
            self.unmatched_widget.show()
        else:
            self.unmatched_widget.hide()
    
    def _populate_table(self, rows: List[Table13Row]):
        self.results_table.setRowCount(len(rows))
        
        for row_idx, row in enumerate(rows):
            doc_type = row.nature_of_document
            if len(doc_type) > 25:
                doc_type = doc_type[:22] + "..."
            
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
                    if col_idx == 4 and row.cancelled > 0:
                        item.setForeground(QColor("#dc2626"))
                        f = item.font()
                        f.setBold(True)
                        item.setFont(f)
                
                self.results_table.setItem(row_idx, col_idx, item)
        
        self.results_table.resizeRowsToContents()
    
    def _copy_table(self):
        if not self._current_rows:
            return
        tsv = format_table13_tsv(self._current_rows)
        QApplication.clipboard().setText(tsv)
        QMessageBox.information(self, "Copied", "Table copied — paste into Excel or GST Portal")
    
    def _copy_missing(self):
        if not self._current_result:
            return
        missing = []
        for series in self._current_result.series_results:
            missing.extend(series.missing_invoices)
        if missing:
            QApplication.clipboard().setText("\n".join(missing))
            QMessageBox.information(self, "Copied", f"{len(missing)} invoice numbers copied")
    
    def clear_results(self):
        self._current_result = None
        self._current_rows = []
        
        self.placeholder.show()
        self.stats_widget.hide()
        self.table_section.hide()
        self.warnings_widget.hide()
        self.missing_widget.hide()
        self.unmatched_widget.hide()
        
        self.results_table.setRowCount(0)
