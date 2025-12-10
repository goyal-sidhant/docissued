"""
Output Panel - With Resizable Table and Expandable Sections
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QTextEdit, QHeaderView, QScrollArea,
    QApplication, QMessageBox, QSizePolicy, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from typing import List, Optional
from ..core.models import ProcessingResult, Table13Row
from ..utils.formatters import format_table13_tsv


# Visible scrollbar and splitter styles
PANEL_STYLES = """
    QScrollArea { 
        border: none; 
        background: #fafafa; 
    }
    QSplitter::handle:vertical {
        background: #d1d5db;
        height: 5px;
        margin: 4px 0;
        border-radius: 2px;
    }
    QSplitter::handle:vertical:hover {
        background: #3b82f6;
    }
"""


class OutputPanel(QWidget):
    """Results panel with resizable table and expandable sections."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_result: Optional[ProcessingResult] = None
        self._current_rows: List[Table13Row] = []
        self._setup_ui()
    
    def _setup_ui(self):
        # Main scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(PANEL_STYLES)
        
        content = QWidget()
        content.setStyleSheet("background: #fafafa;")
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Results")
        header.setStyleSheet("font-size: 16px; font-weight: 600; color: #1f2937;")
        layout.addWidget(header)
        
        # Placeholder (shown when no results)
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
        
        # ========================================
        # VERTICAL SPLITTER for table vs details
        # ========================================
        self.results_splitter = QSplitter(Qt.Vertical)
        self.results_splitter.setStyleSheet(PANEL_STYLES)
        self.results_splitter.setChildrenCollapsible(False)
        
        # --- TOP: Table section ---
        self.table_section = QWidget()
        self.table_section.setStyleSheet("background: transparent;")
        table_layout = QVBoxLayout(self.table_section)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(8)
        
        # Table header with copy button
        table_header = QHBoxLayout()
        table_title = QLabel("Table 13 Output")
        table_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #374151;")
        table_header.addWidget(table_title)
        
        resize_hint = QLabel("(drag column edges to resize)")
        resize_hint.setStyleSheet("font-size: 10px; color: #9ca3af;")
        table_header.addWidget(resize_hint)
        
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
        
        # Results table with resizable columns
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Document Type", "From", "To", "Total", "Cancelled", "Net"
        ])
        self.results_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.results_table.setMinimumHeight(80)
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
                border-right: 1px solid #e5e7eb;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
        
        # Make columns resizable by user
        header = self.results_table.horizontalHeader()
        header.setSectionsMovable(False)
        header.setStretchLastSection(False)
        
        # Document Type stretches, others are interactive (resizable)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set reasonable default widths
        self.results_table.setColumnWidth(1, 130)  # From
        self.results_table.setColumnWidth(2, 130)  # To
        self.results_table.setColumnWidth(3, 55)   # Total
        self.results_table.setColumnWidth(4, 70)   # Cancelled
        self.results_table.setColumnWidth(5, 45)   # Net
        
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.results_table, 1)
        
        self.results_splitter.addWidget(self.table_section)
        
        # --- BOTTOM: Details section (warnings, missing, unmatched) ---
        self.details_section = QWidget()
        self.details_section.setStyleSheet("background: transparent;")
        details_layout = QVBoxLayout(self.details_section)
        details_layout.setContentsMargins(0, 8, 0, 0)
        details_layout.setSpacing(12)
        
        # Resize hint for splitter
        splitter_hint = QLabel("↕ Drag above line to resize table area")
        splitter_hint.setStyleSheet("font-size: 10px; color: #9ca3af; font-style: italic;")
        splitter_hint.setAlignment(Qt.AlignCenter)
        details_layout.addWidget(splitter_hint)
        
        # Warnings section
        self.warnings_widget = QWidget()
        self.warnings_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        warnings_layout = QVBoxLayout(self.warnings_widget)
        warnings_layout.setContentsMargins(0, 0, 0, 0)
        warnings_layout.setSpacing(4)
        
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
        details_layout.addWidget(self.warnings_widget)
        
        # Missing invoices section
        self.missing_widget = QWidget()
        self.missing_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        missing_layout = QVBoxLayout(self.missing_widget)
        missing_layout.setContentsMargins(0, 0, 0, 0)
        missing_layout.setSpacing(4)
        
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
        self.missing_text.setMinimumHeight(50)
        self.missing_text.setMaximumHeight(150)
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
        details_layout.addWidget(self.missing_widget)
        
        # Unmatched section
        self.unmatched_widget = QWidget()
        self.unmatched_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        unmatched_layout = QVBoxLayout(self.unmatched_widget)
        unmatched_layout.setContentsMargins(0, 0, 0, 0)
        unmatched_layout.setSpacing(4)
        
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
        details_layout.addWidget(self.unmatched_widget)
        
        details_layout.addStretch()
        
        self.results_splitter.addWidget(self.details_section)
        
        # Set splitter initial sizes (table gets more space)
        self.results_splitter.setSizes([300, 150])
        self.results_splitter.setStretchFactor(0, 2)  # Table expands more
        self.results_splitter.setStretchFactor(1, 1)
        
        # Set cursor for splitter handle
        handle = self.results_splitter.handle(1)
        if handle:
            handle.setCursor(Qt.SplitVCursor)
        
        self.results_splitter.hide()
        layout.addWidget(self.results_splitter, 1)
        
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
        self.results_splitter.show()
        
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
                series_name = series.series_display_name.replace('<seq>', '___')
                inv_list = ", ".join(series.missing_invoices[:20])
                if len(series.missing_invoices) > 20:
                    inv_list += f" ...+{len(series.missing_invoices) - 20} more"
                missing_parts.append(f"Series: {series_name}\nMissing: {inv_list}")
        
        if missing_parts:
            self.missing_text.setText("\n\n".join(missing_parts))
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
        lines = []
        for series in self._current_result.series_results:
            if series.missing_invoices:
                series_name = series.series_display_name.replace('<seq>', '___')
                lines.append(f"Series: {series_name}")
                lines.append(f"Missing: {', '.join(series.missing_invoices)}")
                lines.append("")
        if lines:
            QApplication.clipboard().setText("\n".join(lines).strip())
            total = sum(len(s.missing_invoices) for s in self._current_result.series_results)
            QMessageBox.information(self, "Copied", f"{total} missing invoice numbers copied")
    
    def clear_results(self):
        self._current_result = None
        self._current_rows = []
        
        self.placeholder.show()
        self.stats_widget.hide()
        self.results_splitter.hide()
        self.warnings_widget.hide()
        self.missing_widget.hide()
        self.unmatched_widget.hide()
        
        self.results_table.setRowCount(0)
