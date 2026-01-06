"""
Output Panel - Table expands and pushes content down, panel scrolls
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QFrame, QTextEdit, QHeaderView, QScrollArea,
    QApplication, QMessageBox, QSizePolicy, QMenu
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor, QKeySequence

from typing import List, Optional
from ..core.models import ProcessingResult, Table13Row
from ..utils.formatters import format_table13_tsv


class OutputPanel(QWidget):
    """Results panel - table expands, content flows, panel scrolls."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_result: Optional[ProcessingResult] = None
        self._current_rows: List[Table13Row] = []
        self._table_expanded = False
        self._ui_scale = 1.0  # Default 100%
        self._setup_ui()
    
    def _setup_ui(self):
        # Scroll area for the ENTIRE panel
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
            QScrollBar:vertical {
                background: #e5e7eb;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #9ca3af;
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6b7280;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)
        
        # Content widget - everything flows vertically
        content = QWidget()
        content.setStyleSheet("background: #fafafa;")
        
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
        
        # ========== TABLE SECTION ==========
        self.table_section = QWidget()
        self.table_section.setStyleSheet("background: transparent;")
        table_layout = QVBoxLayout(self.table_section)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(8)
        
        # Table header row
        table_header = QHBoxLayout()
        table_title = QLabel("Table 13 Output")
        table_title.setStyleSheet("font-size: 13px; font-weight: 600; color: #374151;")
        table_header.addWidget(table_title)
        
        resize_hint = QLabel("(drag columns to resize • Ctrl+C to copy selection)")
        resize_hint.setStyleSheet("font-size: 10px; color: #9ca3af;")
        table_header.addWidget(resize_hint)
        
        table_header.addStretch()
        
        # Expand/Collapse button
        self.expand_btn = QPushButton("▼ Show All Rows")
        self.expand_btn.setCursor(Qt.PointingHandCursor)
        self.expand_btn.setStyleSheet("""
            QPushButton {
                font-size: 10px;
                color: #6b7280;
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:hover { background: #e5e7eb; }
        """)
        self.expand_btn.clicked.connect(self._toggle_table_expand)
        table_header.addWidget(self.expand_btn)
        
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
        
        # Resizable columns
        header = self.results_table.horizontalHeader()
        header.setSectionsMovable(False)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        self.results_table.setColumnWidth(1, 130)
        self.results_table.setColumnWidth(2, 130)
        self.results_table.setColumnWidth(3, 55)
        self.results_table.setColumnWidth(4, 70)
        self.results_table.setColumnWidth(5, 45)
        
        # Allow selecting individual cells, rows, or ranges
        self.results_table.setSelectionBehavior(QTableWidget.SelectItems)
        self.results_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        
        # Enable Ctrl+C for copying selected cells
        self.results_table.installEventFilter(self)
        
        # Right-click context menu
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_table_context_menu)
        
        # Default: compact mode with max height
        self.results_table.setMinimumHeight(80)
        self.results_table.setMaximumHeight(200)
        
        table_layout.addWidget(self.results_table)
        
        self.table_section.hide()
        layout.addWidget(self.table_section)
        
        # ========== WARNINGS SECTION ==========
        self.warnings_widget = QWidget()
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
        layout.addWidget(self.warnings_widget)
        
        # ========== MISSING SECTION ==========
        self.missing_widget = QWidget()
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
        self.missing_text.setMinimumHeight(60)
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
        layout.addWidget(self.missing_widget)
        
        # ========== UNMATCHED SECTION ==========
        self.unmatched_widget = QWidget()
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
        layout.addWidget(self.unmatched_widget)
        
        # ========== CONTINUITY CHECK SECTION ==========
        self.continuity_widget = QWidget()
        continuity_layout = QVBoxLayout(self.continuity_widget)
        continuity_layout.setContentsMargins(0, 0, 0, 0)
        continuity_layout.setSpacing(4)
        
        continuity_title = QLabel("📋 Continuity Check (vs Previous GSTR-1)")
        continuity_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #1e40af;")
        continuity_layout.addWidget(continuity_title)
        
        self.continuity_text = QTextEdit()
        self.continuity_text.setReadOnly(True)
        self.continuity_text.setMinimumHeight(80)
        self.continuity_text.setMaximumHeight(200)
        self.continuity_text.setStyleSheet("""
            QTextEdit {
                font-size: 11px;
                font-family: Consolas, monospace;
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        continuity_layout.addWidget(self.continuity_text)
        
        self.continuity_widget.hide()
        layout.addWidget(self.continuity_widget)
        
        # Spacer at bottom
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _toggle_table_expand(self):
        """Toggle between compact and expanded table view."""
        self._table_expanded = not self._table_expanded
        
        if self._table_expanded:
            # Calculate ACTUAL needed height from table
            header_height = self.results_table.horizontalHeader().height()
            rows_height = 0
            for i in range(self.results_table.rowCount()):
                rows_height += self.results_table.rowHeight(i)
            
            # Add buffer for borders, padding, and horizontal scrollbar if needed
            needed_height = header_height + rows_height + 10
            
            self.results_table.setMinimumHeight(needed_height)
            self.results_table.setMaximumHeight(16777215)  # Remove max constraint
            self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.expand_btn.setText("▲ Collapse")
        else:
            # Compact: limited height with scrolling
            self.results_table.setMinimumHeight(80)
            self.results_table.setMaximumHeight(200)
            self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.expand_btn.setText("▼ Show All Rows")
    
    def eventFilter(self, obj, event):
        """Handle Ctrl+C for copying selected cells."""
        if obj == self.results_table and event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.Copy):
                self._copy_selected()
                return True
        return super().eventFilter(obj, event)
    
    def _copy_selected(self):
        """Copy selected cells to clipboard (Tab-separated for Excel)."""
        selection = self.results_table.selectedRanges()
        if not selection:
            return
        
        # Get bounds of selection
        rows = set()
        cols = set()
        for sel_range in selection:
            for r in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                rows.add(r)
            for c in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                cols.add(c)
        
        rows = sorted(rows)
        cols = sorted(cols)
        
        # Build TSV from selected cells
        lines = []
        for r in rows:
            row_data = []
            for c in cols:
                item = self.results_table.item(r, c)
                row_data.append(item.text() if item else "")
            lines.append("\t".join(row_data))
        
        text = "\n".join(lines)
        QApplication.clipboard().setText(text)
    
    def _show_table_context_menu(self, pos):
        """Show right-click context menu for table."""
        menu = QMenu(self)
        
        copy_selected = menu.addAction("Copy Selected (Ctrl+C)")
        copy_selected.triggered.connect(self._copy_selected)
        
        copy_all = menu.addAction("Copy All Rows")
        copy_all.triggered.connect(self._copy_table)
        
        menu.exec_(self.results_table.mapToGlobal(pos))
    
    def _make_stat(self, value: str, label: str, color: str = "#1f2937") -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("""
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
        """)
        widget.setMinimumWidth(70)
        widget.setMaximumWidth(100)
        
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
        self._table_expanded = False
        
        self.placeholder.hide()
        self.stats_widget.show()
        self.table_section.show()
        
        # Reset table to compact mode
        self.results_table.setMinimumHeight(80)
        self.results_table.setMaximumHeight(200)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.expand_btn.setText("▼ Show All Rows")
        
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
        self._table_expanded = False
        
        self.placeholder.show()
        self.stats_widget.hide()
        self.table_section.hide()
        self.warnings_widget.hide()
        self.missing_widget.hide()
        self.unmatched_widget.hide()
        self.continuity_widget.hide()
        
        self.results_table.setRowCount(0)
        self.results_table.setMinimumHeight(80)
        self.results_table.setMaximumHeight(200)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.expand_btn.setText("▼ Show All Rows")
    
    def display_continuity_results(self, continuity_results):
        """Display continuity check results."""
        if not continuity_results:
            self.continuity_widget.hide()
            return

        lines = []
        ok_count = 0
        gap_count = 0
        new_count = 0

        for result in continuity_results:
            if result.previous_to is None:
                new_count += 1
                status_icon = "ℹ️"
            elif result.is_continuous:
                ok_count += 1
                status_icon = "✓"
            else:
                gap_count += 1
                status_icon = "⚠️"

            lines.append(f"{status_icon} {result.series_display_name}")
            lines.append(f"   Current: {result.current_from} → {result.current_to}")
            if result.previous_to:
                lines.append(f"   Previous ended: {result.previous_to}")
            if result.message:
                # Shorten message for display
                msg = result.message
                if msg.startswith("✓ "):
                    msg = msg[2:]
                elif msg.startswith("⚠️ "):
                    msg = msg[3:]
                elif msg.startswith("ℹ️ "):
                    msg = msg[3:]
                lines.append(f"   → {msg}")
            lines.append("")

        # Summary at top
        summary = f"Summary: {ok_count} OK"
        if gap_count > 0:
            summary += f", {gap_count} with gaps"
        if new_count > 0:
            summary += f", {new_count} new series"

        full_text = summary + "\n" + "─" * 40 + "\n\n" + "\n".join(lines)

        self.continuity_text.setText(full_text)
        self.continuity_widget.show()

    def apply_scale(self, scale: float):
        """Apply UI scale to all elements."""
        self._ui_scale = scale
        s = scale

        # Results table
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                font-size: {int(12*s)}px;
                background: white;
                border: 1px solid #d1d5db;
                border-radius: {int(5*s)}px;
                gridline-color: #e5e7eb;
            }}
            QTableWidget::item {{
                padding: {int(8*s)}px {int(6*s)}px;
            }}
            QTableWidget::item:selected {{
                background: #eff6ff;
                color: #1f2937;
            }}
            QHeaderView::section {{
                background: #f3f4f6;
                color: #6b7280;
                font-weight: 600;
                font-size: {int(11*s)}px;
                padding: {int(8*s)}px {int(6*s)}px;
                border: none;
                border-bottom: 1px solid #d1d5db;
                border-right: 1px solid #e5e7eb;
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)

        # Update column widths
        self.results_table.setColumnWidth(1, int(130 * s))
        self.results_table.setColumnWidth(2, int(130 * s))
        self.results_table.setColumnWidth(3, int(55 * s))
        self.results_table.setColumnWidth(4, int(70 * s))
        self.results_table.setColumnWidth(5, int(45 * s))

        # Table height constraints
        if self._table_expanded:
            # Recalculate expanded height with new scale
            header_height = self.results_table.horizontalHeader().height()
            rows_height = sum(self.results_table.rowHeight(i) for i in range(self.results_table.rowCount()))
            needed_height = header_height + rows_height + int(10 * s)
            self.results_table.setMinimumHeight(needed_height)
        else:
            self.results_table.setMinimumHeight(int(80 * s))
            self.results_table.setMaximumHeight(int(200 * s))

        # Expand/Collapse button
        self.expand_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {int(10*s)}px;
                color: #6b7280;
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: {int(4*s)}px;
                padding: {int(4*s)}px {int(10*s)}px;
            }}
            QPushButton:hover {{ background: #e5e7eb; }}
        """)

        # Copy button
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {int(11*s)}px;
                color: white;
                background: #16a34a;
                border: none;
                border-radius: {int(4*s)}px;
                padding: {int(6*s)}px {int(12*s)}px;
            }}
            QPushButton:hover {{ background: #15803d; }}
        """)

        # Copy missing button
        self.copy_missing_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: {int(10*s)}px;
                color: #6b7280;
                background: #f3f4f6;
                border: none;
                border-radius: {int(3*s)}px;
                padding: {int(4*s)}px {int(8*s)}px;
            }}
            QPushButton:hover {{ background: #e5e7eb; }}
        """)

        # Text areas
        self.missing_text.setMinimumHeight(int(60 * s))
        self.missing_text.setMaximumHeight(int(150 * s))
        self.missing_text.setStyleSheet(f"""
            QTextEdit {{
                font-size: {int(11*s)}px;
                font-family: Consolas, monospace;
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: {int(5*s)}px;
                padding: {int(8*s)}px;
            }}
        """)

        self.unmatched_text.setMaximumHeight(int(70 * s))
        self.unmatched_text.setStyleSheet(f"""
            QTextEdit {{
                font-size: {int(11*s)}px;
                font-family: Consolas, monospace;
                background: #f3f4f6;
                border: 1px solid #d1d5db;
                border-radius: {int(5*s)}px;
                padding: {int(8*s)}px;
            }}
        """)

        self.continuity_text.setMinimumHeight(int(80 * s))
        self.continuity_text.setMaximumHeight(int(200 * s))
        self.continuity_text.setStyleSheet(f"""
            QTextEdit {{
                font-size: {int(11*s)}px;
                font-family: Consolas, monospace;
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: {int(5*s)}px;
                padding: {int(8*s)}px;
            }}
        """)

        # Warnings text
        self.warnings_text.setStyleSheet(f"""
            font-size: {int(11*s)}px;
            color: #92400e;
            background: #fef3c7;
            padding: {int(10*s)}px;
            border-radius: {int(5*s)}px;
        """)

        # Placeholder
        self.placeholder.setStyleSheet(f"""
            font-size: {int(13*s)}px;
            color: #9ca3af;
            padding: {int(40*s)}px {int(20*s)}px;
            background: white;
            border: 1px dashed #d1d5db;
            border-radius: {int(6*s)}px;
        """)

        # Update stat boxes
        self._update_stat_box_scale(self.stat_total, s)
        self._update_stat_box_scale(self.stat_matched, s)
        self._update_stat_box_scale(self.stat_cancelled, s)
        self._update_stat_box_scale(self.stat_series, s)

        # Force layout recalculation
        self.results_table.resizeRowsToContents()

    def _update_stat_box_scale(self, widget: QWidget, s: float):
        """Update a stat box with scaled values."""
        widget.setMinimumWidth(int(70 * s))
        widget.setMaximumWidth(int(100 * s))
        widget.setStyleSheet(f"""
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: {int(6*s)}px;
        """)

        layout = widget.layout()
        layout.setContentsMargins(int(10*s), int(8*s), int(10*s), int(8*s))

        # Update value label
        value_label = widget.value_label
        current_color = value_label.styleSheet().split('color: ')[1].split(';')[0] if 'color:' in value_label.styleSheet() else '#1f2937'
        value_label.setStyleSheet(f"font-size: {int(18*s)}px; font-weight: 700; color: {current_color}; background: transparent; border: none;")

        # Update name label
        name_label = layout.itemAt(1).widget()
        if isinstance(name_label, QLabel):
            name_label.setStyleSheet(f"font-size: {int(10*s)}px; color: #9ca3af; background: transparent; border: none;")
