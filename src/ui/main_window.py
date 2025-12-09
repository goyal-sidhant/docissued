"""
Main Window - Sahaj Table 13 Generator

Clean, professional layout for GST practitioners.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QFrame,
    QLabel, QApplication
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
    
    APP_NAME = "Sahaj - Table 13 Generator"
    APP_VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle(self.APP_NAME)
        self.setMinimumSize(1100, 700)
        
        # Set reasonable default size
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            width = min(1400, int(geometry.width() * 0.85))
            height = min(900, int(geometry.height() * 0.85))
            self.resize(width, height)
            
            # Center on screen
            x = (geometry.width() - width) // 2
            y = (geometry.height() - height) // 2
            self.move(x, y)
        
        # Clean background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f1f5f9;
            }
            QSplitter::handle {
                background-color: #e2e8f0;
                width: 1px;
            }
        """)
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        main_layout.addWidget(self._create_header())
        
        # Content area
        content = QWidget()
        content.setStyleSheet("background-color: #f1f5f9;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Input panel (left)
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        input_container.setMinimumWidth(450)
        input_container.setMaximumWidth(550)
        
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_panel = InputPanel()
        input_layout.addWidget(self.input_panel)
        
        content_layout.addWidget(input_container)
        
        # Output panel (right)
        output_container = QFrame()
        output_container.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
            }
        """)
        
        output_layout = QVBoxLayout(output_container)
        output_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_panel = OutputPanel()
        output_layout.addWidget(self.output_panel)
        
        content_layout.addWidget(output_container, 1)
        
        main_layout.addWidget(content, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: white;
                border-top: 1px solid #e2e8f0;
                padding: 8px 15px;
                font-size: 12px;
                color: #64748b;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Enter invoice details to generate Table 13")
    
    def _create_header(self) -> QWidget:
        """Create the application header."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: none;
            }
        """)
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 0, 25, 0)
        
        # Logo / Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title = QLabel("📋 Sahaj")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("GSTR-1 Table 13 Generator")
        subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Help text
        help_text = QLabel("Generate document summary for GST returns in seconds")
        help_text.setStyleSheet("font-size: 13px; color: #94a3b8;")
        layout.addWidget(help_text)
        
        return header
    
    def _connect_signals(self):
        """Connect signals between components."""
        self.input_panel.process_requested.connect(self._on_process)
        self.input_panel.clear_requested.connect(self._on_clear)
    
    def _on_process(self):
        """Handle process request."""
        pattern_text = self.input_panel.get_pattern()
        invoice_text = self.input_panel.get_invoice_text()
        document_nature = self.input_panel.get_document_nature()
        ignore_zeros = self.input_panel.get_ignore_leading_zeros()
        
        self.input_panel.set_processing_state(True)
        self.status_bar.showMessage("Processing invoices...")
        
        # Process after UI updates
        QTimer.singleShot(50, lambda: self._do_process(
            pattern_text, invoice_text, document_nature, ignore_zeros
        ))
    
    def _do_process(self, pattern_text: str, invoice_text: str, 
                    document_nature: str, ignore_zeros: bool):
        """Perform the actual processing."""
        try:
            # Parse pattern
            parser = PatternParser()
            pattern = parser.parse(pattern_text)
            
            if not pattern.is_valid:
                raise ValueError(f"Invalid format: {pattern.error_message}")
            
            # Process invoices
            processor = InvoiceProcessor(pattern, ignore_zeros)
            series_groups, unmatched, invalid = processor.process_text_input(invoice_text)
            
            # Analyze series
            analyzer = SeriesAnalyzer(pattern, processor)
            result = analyzer.analyze_all_series(
                series_groups, unmatched, invalid, document_nature
            )
            
            # Convert to Table 13 rows
            rows = analyzer.to_table13_rows(result)
            
            # Display results
            self.output_panel.display_result(result, rows)
            
            # Update status
            total_cancelled = sum(s.cancelled_count for s in result.series_results)
            self.status_bar.showMessage(
                f"✅ Done! {result.total_matched:,} invoices processed | "
                f"{len(result.series_results)} series | "
                f"{total_cancelled} cancelled"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not process invoices:\n\n{str(e)}\n\n"
                "Please check your invoice format and try again."
            )
            self.status_bar.showMessage("❌ Processing failed - check your inputs")
        
        finally:
            self.input_panel.set_processing_state(False)
    
    def _on_clear(self):
        """Handle clear request."""
        self.output_panel.clear_results()
        self.status_bar.showMessage("Cleared - Ready for new data")
