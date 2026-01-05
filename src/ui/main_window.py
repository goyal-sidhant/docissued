"""
Main Window - Responsive with Resizable Panels
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStatusBar, QMessageBox, QFrame, QLabel, QApplication,
    QSplitter, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from .input_panel import InputPanel
from .output_panel import OutputPanel

from ..core.pattern_parser import PatternParser
from ..core.invoice_processor import InvoiceProcessor
from ..core.series_analyzer import SeriesAnalyzer
from ..core.continuity_checker import check_continuity


# Visible scrollbar style - not camouflaged
SCROLLBAR_STYLE = """
    QScrollBar:vertical {
        background: #e5e7eb;
        width: 14px;
        margin: 0;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical {
        background: #9ca3af;
        min-height: 30px;
        border-radius: 7px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background: #6b7280;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background: #e5e7eb;
        height: 14px;
        margin: 0;
        border-radius: 7px;
    }
    QScrollBar::handle:horizontal {
        background: #9ca3af;
        min-width: 30px;
        border-radius: 7px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #6b7280;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
"""


class MainWindow(QMainWindow):
    """Main application window with resizable panels."""
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_window(self):
        self.setWindowTitle("Sahaj — Table 13 Generator")
        
        # Minimum size for very small screens
        self.setMinimumSize(800, 500)
        
        # Default size based on screen
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            # Use 85% of screen but cap at reasonable max
            w = min(1400, max(900, int(geo.width() * 0.85)))
            h = min(900, max(600, int(geo.height() * 0.85)))
            self.resize(w, h)
            # Center on screen
            self.move((geo.width() - w) // 2, (geo.height() - h) // 2)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background: #f1f5f9; }}
            {SCROLLBAR_STYLE}
        """)
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("background: #1e293b;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Sahaj")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("— Table 13 Generator")
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8; margin-left: 8px;")
        header_layout.addWidget(subtitle)
        
        header_layout.addStretch()
        
        help_text = QLabel("Drag the divider to resize panels")
        help_text.setStyleSheet("font-size: 11px; color: #64748b;")
        header_layout.addWidget(help_text)
        
        main_layout.addWidget(header)
        
        # Content with splitter
        content = QWidget()
        content.setStyleSheet("background: #f1f5f9;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(0)
        
        # Splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background: #94a3b8;
                width: 5px;
                margin: 0 6px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background: #3b82f6;
            }
            QSplitter::handle:pressed {
                background: #1d4ed8;
            }
        """)
        self.splitter.setHandleWidth(5)
        # Set resize cursor for the splitter handle
        self.splitter.setChildrenCollapsible(False)
        
        # Input panel (left)
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }
        """)
        input_frame.setMinimumWidth(320)  # Minimum, not fixed
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_panel = InputPanel()
        input_layout.addWidget(self.input_panel)
        
        self.splitter.addWidget(input_frame)
        
        # Output panel (right)
        output_frame = QFrame()
        output_frame.setStyleSheet("""
            QFrame {
                background: #fafafa;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }
        """)
        output_frame.setMinimumWidth(350)  # Minimum, not fixed
        
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_panel = OutputPanel()
        output_layout.addWidget(self.output_panel)
        
        self.splitter.addWidget(output_frame)
        
        # Set stretch factors (input: 2, output: 3) for proportional sizing
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 3)
        
        # Set resize cursor on the splitter handle
        handle = self.splitter.handle(1)
        if handle:
            handle.setCursor(Qt.SplitHCursor)
        
        content_layout.addWidget(self.splitter)
        main_layout.addWidget(content, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: white;
                border-top: 1px solid #d1d5db;
                padding: 5px 14px;
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
            
            # Check continuity if previous GSTR-1 was loaded
            previous_series = self.input_panel.get_previous_series()
            if previous_series:
                continuity_results = check_continuity(previous_series, result)
                self.output_panel.display_continuity_results(continuity_results)
            else:
                self.output_panel.display_continuity_results(None)
            
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
