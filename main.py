#!/usr/bin/env python3
"""
GSTR-1 Table 13 Generator

A desktop application for GST practitioners to generate Table 13 
(Summary of Documents Issued) for GSTR-1 returns.

Usage:
    python main.py

Author: GST Practitioner Tools
License: MIT
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui.main_window import MainWindow


def main():
    """Application entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("GSTR-1 Table 13 Generator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GST Tools")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
