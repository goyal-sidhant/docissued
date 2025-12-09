"""
GSTR-1 Table 13 Generator - Sahaj

A simple desktop tool for GST practitioners to generate Table 13 
(Summary of Documents Issued) for GSTR-1 returns.

Run: python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.ui.main_window import MainWindow


def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Sahaj - Table 13 Generator")
    app.setApplicationVersion("1.0.0")
    
    # Larger default font for readability
    font = QFont("Segoe UI", 11)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
