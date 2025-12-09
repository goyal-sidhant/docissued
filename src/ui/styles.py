"""
Styles and theming for GSTR-1 Table 13 Generator.

Contains color schemes, fonts, and Qt stylesheets.
"""

# Color Palette
COLORS = {
    # Primary colors
    'primary': '#2563eb',        # Blue
    'primary_dark': '#1d4ed8',
    'primary_light': '#3b82f6',
    
    # Secondary colors
    'secondary': '#64748b',      # Slate
    'secondary_dark': '#475569',
    'secondary_light': '#94a3b8',
    
    # Accent colors
    'success': '#16a34a',        # Green
    'warning': '#ca8a04',        # Yellow/Amber
    'error': '#dc2626',          # Red
    'info': '#0891b2',           # Cyan
    
    # Background colors
    'bg_primary': '#ffffff',
    'bg_secondary': '#f8fafc',
    'bg_tertiary': '#f1f5f9',
    'bg_input': '#ffffff',
    
    # Border colors
    'border': '#e2e8f0',
    'border_focus': '#2563eb',
    
    # Text colors
    'text_primary': '#1e293b',
    'text_secondary': '#64748b',
    'text_muted': '#94a3b8',
    'text_on_primary': '#ffffff',
}

# Font settings
FONTS = {
    'family': 'Segoe UI, Arial, sans-serif',
    'family_mono': 'Consolas, Monaco, monospace',
    'size_small': '11px',
    'size_normal': '13px',
    'size_large': '15px',
    'size_title': '18px',
    'size_header': '24px',
}

# Spacing
SPACING = {
    'xs': '4px',
    'sm': '8px',
    'md': '12px',
    'lg': '16px',
    'xl': '24px',
    'xxl': '32px',
}

# Main application stylesheet
MAIN_STYLESHEET = f"""
/* Global styles */
QWidget {{
    font-family: {FONTS['family']};
    font-size: {FONTS['size_normal']};
    color: {COLORS['text_primary']};
}}

QMainWindow {{
    background-color: {COLORS['bg_secondary']};
}}

/* Labels */
QLabel {{
    color: {COLORS['text_primary']};
    padding: 2px;
}}

QLabel[class="header"] {{
    font-size: {FONTS['size_header']};
    font-weight: bold;
    color: {COLORS['primary']};
    padding: {SPACING['md']};
}}

QLabel[class="section-title"] {{
    font-size: {FONTS['size_large']};
    font-weight: 600;
    color: {COLORS['text_primary']};
    padding: {SPACING['sm']} 0;
}}

QLabel[class="hint"] {{
    font-size: {FONTS['size_small']};
    color: {COLORS['text_secondary']};
    font-style: italic;
}}

QLabel[class="error"] {{
    color: {COLORS['error']};
    font-weight: 500;
}}

QLabel[class="success"] {{
    color: {COLORS['success']};
    font-weight: 500;
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_on_primary']};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-weight: 500;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_light']};
}}

QPushButton:disabled {{
    background-color: {COLORS['secondary_light']};
    color: {COLORS['text_muted']};
}}

QPushButton[class="secondary"] {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['border']};
}}

QPushButton[class="success"] {{
    background-color: {COLORS['success']};
}}

QPushButton[class="danger"] {{
    background-color: {COLORS['error']};
}}

/* Input fields */
QLineEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 12px;
    font-size: {FONTS['size_normal']};
    selection-background-color: {COLORS['primary_light']};
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
    padding: 9px 11px;
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_muted']};
}}

/* Text areas */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px;
    font-family: {FONTS['family_mono']};
    font-size: {FONTS['size_normal']};
    selection-background-color: {COLORS['primary_light']};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

/* Combo boxes */
QComboBox {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 10px 12px;
    min-width: 200px;
}}

QComboBox:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['text_primary']};
    padding: 4px;
}}

/* Tables */
QTableWidget {{
    background-color: {COLORS['bg_input']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    gridline-color: {COLORS['border']};
    selection-background-color: {COLORS['primary_light']};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {COLORS['bg_tertiary']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary_light']};
    color: {COLORS['text_primary']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    font-weight: 600;
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid {COLORS['border']};
}}

/* Scroll bars */
QScrollBar:vertical {{
    background-color: {COLORS['bg_tertiary']};
    width: 12px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['secondary_light']};
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['secondary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_tertiary']};
    height: 12px;
    border-radius: 6px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['secondary_light']};
    border-radius: 5px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['secondary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* Group boxes */
QGroupBox {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px;
    padding-top: 24px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

/* Checkboxes */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['bg_input']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['primary_light']};
}}

/* Tooltips */
QToolTip {{
    background-color: {COLORS['text_primary']};
    color: {COLORS['bg_primary']};
    border: none;
    padding: 8px 12px;
    border-radius: 4px;
    font-size: {FONTS['size_small']};
}}

/* Status bar */
QStatusBar {{
    background-color: {COLORS['bg_tertiary']};
    border-top: 1px solid {COLORS['border']};
    padding: 4px;
}}

/* Splitter */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}
"""

# Card-style container
CARD_STYLE = f"""
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 16px;
"""

# Warning box style
WARNING_BOX_STYLE = f"""
    background-color: #fef3c7;
    border: 1px solid #f59e0b;
    border-radius: 6px;
    padding: 12px;
    color: #92400e;
"""

# Error box style
ERROR_BOX_STYLE = f"""
    background-color: #fee2e2;
    border: 1px solid #ef4444;
    border-radius: 6px;
    padding: 12px;
    color: #991b1b;
"""

# Success box style
SUCCESS_BOX_STYLE = f"""
    background-color: #dcfce7;
    border: 1px solid #22c55e;
    border-radius: 6px;
    padding: 12px;
    color: #166534;
"""

# Info box style
INFO_BOX_STYLE = f"""
    background-color: #e0f2fe;
    border: 1px solid #0ea5e9;
    border-radius: 6px;
    padding: 12px;
    color: #075985;
"""
