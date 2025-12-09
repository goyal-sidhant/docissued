"""
Main Window for GSTR-1 Table 13 Generator.

The primary application window containing input and output panels.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QFrame,
    QLabel, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from .input_panel import InputPanel
from .output_panel import OutputPanel
from .styles import MAIN_STYLESHEET, COLORS

from ..core.pattern_parser import PatternParser
from ..core.invoice_processor import InvoiceProcessor
from ..core.series_analyzer import SeriesAnalyzer
from ..core.models import ProcessingResult


class MainWindow(QMainWindow):
    """Main application window."""
    
    APP_NAME = "GSTR-1 Table 13 Generator"
    APP_VERSION = "1.0.0"
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.setMinimumSize(1200, 800)
        
        # Try to set a reasonable default size
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
        
        # Apply stylesheet
        self.setStyleSheet(MAIN_STYLESHEET)
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        main_layout.addWidget(self._create_header())
        
        # Content area with splitter
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Input panel (left)
        input_container = QFrame()
        input_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_panel = InputPanel()
        input_layout.addWidget(self.input_panel)
        
        splitter.addWidget(input_container)
        
        # Output panel (right)
        output_container = QFrame()
        output_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        output_layout = QVBoxLayout(output_container)
        output_layout.setContentsMargins(0, 0, 0, 0)
        
        self.output_panel = OutputPanel()
        output_layout.addWidget(self.output_panel)
        
        splitter.addWidget(output_container)
        
        # Set splitter proportions (40% input, 60% output)
        splitter.setSizes([400, 600])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        content_layout.addWidget(splitter)
        main_layout.addWidget(content)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_header(self) -> QWidget:
        """Create the application header."""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                padding: 16px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)
        
        # Title
        title = QLabel(self.APP_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['text_on_primary']};")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Subtitle
        subtitle = QLabel("Generate Table 13 summary from invoice lists")
        subtitle.setStyleSheet(f"color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(subtitle)
        
        return header
    
    def _connect_signals(self):
        """Connect signals between components."""
        self.input_panel.process_requested.connect(self._on_process)
        self.input_panel.clear_requested.connect(self._on_clear)
    
    def _on_process(self):
        """Handle process request from input panel."""
        # Get inputs
        pattern_text = self.input_panel.get_pattern()
        invoice_text = self.input_panel.get_invoice_text()
        document_nature = self.input_panel.get_document_nature()
        ignore_zeros = self.input_panel.get_ignore_leading_zeros()
        
        # Set processing state
        self.input_panel.set_processing_state(True)
        self.status_bar.showMessage("Processing...")
        
        # Use QTimer to allow UI to update before processing
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
                raise ValueError(f"Invalid pattern: {pattern.error_message}")
            
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
            self.status_bar.showMessage(
                f"Processed {result.total_input_lines} invoices successfully"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Processing Error",
                f"An error occurred while processing:\n\n{str(e)}"
            )
            self.status_bar.showMessage("Processing failed")
        
        finally:
            self.input_panel.set_processing_state(False)
    
    def _on_clear(self):
        """Handle clear request."""
        self.output_panel.clear_results()
        self.status_bar.showMessage("Cleared")
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Could add confirmation dialog here if needed
        event.accept()
