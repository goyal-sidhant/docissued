"""
Main Window - Sahaj Table 13 Generator
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStatusBar, QMessageBox, QFrame, QLabel, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .input_panel import InputPanel
from .output_panel import OutputPanel

from ..core.pattern_parser import PatternParser
from ..core.invoice_processor import InvoiceProcessor
from ..core.series_analyzer import SeriesAnalyzer


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_window(self):
        self.setWindowTitle("Sahaj — Table 13 Generator")
        self.setMinimumSize(1000, 650)
        
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            w = min(1300, int(geo.width() * 0.8))
            h = min(850, int(geo.height() * 0.8))
            self.resize(w, h)
            self.move((geo.width() - w) // 2, (geo.height() - h) // 2)
        
        self.setStyleSheet("QMainWindow { background: #f1f5f9; }")
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background: #1e293b;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        title = QLabel("Sahaj")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Table 13 Generator")
        subtitle.setStyleSheet("font-size: 13px; color: #94a3b8; margin-left: 12px;")
        header_layout.addWidget(subtitle)
        
        header_layout.addStretch()
        
        main_layout.addWidget(header)
        
        # Content
        content = QWidget()
        content.setStyleSheet("background: #f1f5f9;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)
        
        # Input (left)
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        input_frame.setFixedWidth(420)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_panel = InputPanel()
        input_layout.addWidget(self.input_panel)
        
        content_layout.addWidget(input_frame)
        
        # Output (right)
        output_frame = QFrame()
        output_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }
        """)
        
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_panel = OutputPanel()
        output_layout.addWidget(self.output_panel)
        
        content_layout.addWidget(output_frame, 1)
        
        main_layout.addWidget(content, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: white;
                border-top: 1px solid #e2e8f0;
                padding: 6px 16px;
                font-size: 12px;
                color: #6b7280;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _connect_signals(self):
        self.input_panel.process_requested.connect(self._on_process)
        self.input_panel.clear_requested.connect(self._on_clear)
    
    def _on_process(self):
        pattern_text = self.input_panel.get_pattern()
        invoice_text = self.input_panel.get_invoice_text()
        doc_nature = self.input_panel.get_document_nature()
        
        self.input_panel.set_processing_state(True)
        self.status_bar.showMessage("Processing...")
        
        QTimer.singleShot(30, lambda: self._do_process(pattern_text, invoice_text, doc_nature))
    
    def _do_process(self, pattern_text: str, invoice_text: str, doc_nature: str):
        try:
            parser = PatternParser()
            pattern = parser.parse(pattern_text)
            
            if not pattern.is_valid:
                raise ValueError(pattern.error_message)
            
            processor = InvoiceProcessor(pattern, False)
            series_groups, unmatched, invalid = processor.process_text_input(invoice_text)
            
            analyzer = SeriesAnalyzer(pattern, processor)
            result = analyzer.analyze_all_series(series_groups, unmatched, invalid, doc_nature)
            rows = analyzer.to_table13_rows(result)
            
            self.output_panel.display_result(result, rows)
            
            cancelled = sum(s.cancelled_count for s in result.series_results)
            self.status_bar.showMessage(
                f"Done — {result.total_matched:,} invoices, {len(result.series_results)} series, {cancelled} cancelled"
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not process:\n\n{str(e)}")
            self.status_bar.showMessage("Error — check inputs")
        
        finally:
            self.input_panel.set_processing_state(False)
    
    def _on_clear(self):
        self.output_panel.clear_results()
        self.status_bar.showMessage("Cleared")
