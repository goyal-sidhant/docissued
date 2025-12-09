# GSTR-1 Table 13 Document Summary Generator

A standalone desktop application for GST practitioners in India to generate **Table 13 of GSTR-1** (Summary of Documents Issued during the tax period).

## Features

- **Flexible Pattern Matching**: Define invoice patterns using intuitive bracket notation
  - `[001]` marks the sequential number
  - `*` marks variable parts that define sub-series
- **Auto Series Detection**: Automatically groups invoices into separate series
- **Gap Detection**: Identifies cancelled/missing invoice numbers
- **Duplicate Handling**: Detects and reports duplicate entries
- **GSTR-1 Ready Output**: Generates output in exact Table 13 format
- **Copy to Clipboard**: Easy copying for portal entry

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd gstr1-table13-generator

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

### Pattern Notation

1. **Sequence Marker `[NNN]`**: Mark the incrementing number with square brackets
   - `GST/24-25/[0001]` → prefix "GST/24-25/", 4-digit sequence
   - `[001]-SAL` → 3-digit sequence, suffix "-SAL"

2. **Wildcard `*`**: Mark variable parts that define sub-series
   - `GST/*/[001]` → Groups by what's in `*` position
   - `*/INV/[0001]/*` → Multiple wildcards supported

### Examples

**Simple Series:**
```
Pattern: INV/[001]
Input: INV/001, INV/002, INV/003, INV/005
Result: From=001, To=005, Total=5, Cancelled=1 (004)
```

**Multiple Series (Same Pattern):**
```
Pattern: GST/*/[001]
Input: GST/A/001, GST/A/002, GST/B/001, GST/B/002
Result: 
  - Series GST/A/: 001-002
  - Series GST/B/: 001-002
```

## Project Structure

```
gstr1-table13-generator/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── core/              # Business logic
│   │   ├── models.py      # Data classes
│   │   ├── pattern_parser.py
│   │   ├── invoice_processor.py
│   │   └── series_analyzer.py
│   ├── ui/                # PyQt5 UI components
│   │   ├── main_window.py
│   │   ├── input_panel.py
│   │   ├── output_panel.py
│   │   └── styles.py
│   └── utils/             # Helper functions
│       ├── validators.py
│       └── formatters.py
└── tests/                 # Unit tests
```

## Legal Context

As per **Rule 46 of CGST Rules 2017**, invoice numbers must be:
- Consecutive serial numbers
- Unique for a financial year
- May contain alphabets, numerals, special characters like "-" and "/"
- No fixed format prescribed

This tool is designed to handle any invoice format compliant with Rule 46.

## License

MIT License
