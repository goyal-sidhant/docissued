# Sahaj — GSTR-1 Table 13 Generator

A desktop application for Indian GST practitioners to automate GSTR-1 Table 13 (HSN Summary of Documents) generation. Detects invoice series, finds gaps, and outputs ready-to-paste Table 13 data.

## What It Does

Table 13 of GSTR-1 requires a summary of all document series issued during a tax period — invoice ranges, totals, and cancelled counts. Doing this manually is tedious and error-prone.

**Sahaj automates this:**
1. Paste your invoice numbers from Tally/Excel
2. Enter your invoice format pattern
3. Get Table 13 output with one click

The app automatically:
- Detects multiple invoice series (branches, years, document types)
- Identifies gaps in sequence (cancelled/missing invoices)
- Calculates From, To, Total, Cancelled, and Net for each series
- Outputs in a format ready to paste into the GST Portal

## Who Is This For

- Chartered Accountants
- GST Practitioners
- Tax Consultants
- Accountants handling GST compliance

No coding knowledge required. The interface is designed for accounting professionals familiar with Tally and Excel.

## Features

- **Multi-series detection**: Automatically groups invoices by branch, year, or any variable part
- **Gap analysis**: Finds missing invoice numbers in each series
- **Pattern-based matching**: Flexible format specification using simple notation
- **One-click copy**: Output formatted for direct paste into Excel or GST Portal
- **Resizable interface**: Drag to resize panels, columns, and sections
- **Duplicate detection**: Warns about duplicate invoice entries
- **Validation warnings**: Alerts for high cancellation ratios or mixed series

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/sahaj-table13-generator.git
cd sahaj-table13-generator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies
- PyQt5 (GUI framework)

## Usage

### Step 1: Select Document Type

Choose the type of document from the dropdown:
- Invoices for outward supply
- Credit Note
- Debit Note
- Delivery Challan
- etc.

### Step 2: Enter Invoice Format

Specify your invoice numbering pattern using this notation:

| Symbol | Meaning | Example |
|--------|---------|---------|
| `[NNN]` | Serial number (put in brackets) | `[001]`, `[0001]` |
| `*` | Variable part (branch code, etc.) | `GST/*/[001]` |
| Everything else | Fixed text that appears in all invoices | `GST/24-25/` |

**Examples:**

| Your Invoices | Pattern to Enter |
|---------------|------------------|
| `GST/24-25/0001`, `GST/24-25/0002` | `GST/24-25/[0001]` |
| `INV-001-SAL`, `INV-002-SAL` | `INV-[001]-SAL` |
| `GST/A/001`, `GST/B/001` (multiple branches) | `GST/*/[001]` |
| `GST/MUM/001/24-25`, `GST/DEL/001/24-25` | `GST/*/[001]/*` |

### Step 3: Paste Invoice Numbers

Copy your invoice numbers from Tally or Excel and paste them into the text area. One invoice per line.

```
GST/24-25/0001
GST/24-25/0002
GST/24-25/0005
GST/24-25/0006
```

### Step 4: Generate

Click **"Generate Table 13"** to see:

- **Summary stats**: Total invoices, matched, cancelled, series count
- **Table 13 output**: Ready-to-use table with From, To, Total, Cancelled, Net
- **Cancelled/Missing list**: Which invoice numbers are missing in each series
- **Warnings**: Any issues detected (duplicates, high cancellation ratio, etc.)

### Step 5: Copy and Paste

Click **"Copy for Excel"** to copy the table. Paste directly into:
- Excel spreadsheet
- GST Portal Table 13 input
- Any other application

## Pattern Syntax Details

### The Sequence Marker `[NNN]`

The number inside brackets tells the app where your serial number is. The number of digits doesn't need to match exactly — the app detects actual padding from your data.

```
Pattern: GST/[1]/*
Matches: GST/001/24-25, GST/002/24-25, GST/100/24-25
```

### The Wildcard `*`

Use `*` for parts that vary between series but should be grouped separately.

**Example — Multiple Branches:**
```
Pattern: GST/*/[001]/*
Input:
  GST/MUM/001/24-25
  GST/MUM/002/24-25
  GST/DEL/001/24-25
  GST/DEL/002/24-25

Output:
  Series 1: GST/MUM/001/24-25 to GST/MUM/002/24-25 (2 total)
  Series 2: GST/DEL/001/24-25 to GST/DEL/002/24-25 (2 total)
```

### Multiple Wildcards

You can use multiple `*` for complex patterns:

```
Pattern: */[001]/*-*
Matches: GST/001/24-25, INV/001/23-24, etc.
```

## Interface Guide

### Resizing

- **Left/Right panels**: Drag the vertical divider between input and output
- **Table height**: Drag the horizontal divider below the table
- **Table columns**: Drag column header edges to resize

### Keyboard Shortcuts

- `Ctrl+V`: Paste invoice list
- `Ctrl+C`: Copy selected text

## Output Format

The Table 13 output includes:

| Column | Description |
|--------|-------------|
| Document Type | Selected document nature |
| From | First invoice number in series |
| To | Last invoice number in series |
| Total | Count of invoices from first to last |
| Cancelled | Count of missing/cancelled in range |
| Net | Actual invoices issued (Total - Cancelled) |

## Warnings Explained

| Warning | Meaning |
|---------|---------|
| Multiple series detected | Your invoices belong to different series (branches, years, etc.) |
| High cancellation ratio | More than 20% of invoices in range are missing — verify if correct |
| Duplicate invoices found | Same invoice number appears multiple times |

## Project Structure

```
sahaj-table13-generator/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── core/              # Business logic
│   │   ├── models.py      # Data structures
│   │   ├── pattern_parser.py    # Pattern syntax parsing
│   │   ├── invoice_processor.py # Invoice matching & grouping
│   │   └── series_analyzer.py   # Gap detection & statistics
│   ├── ui/                # User interface
│   │   ├── main_window.py # Main application window
│   │   ├── input_panel.py # Left panel (inputs)
│   │   └── output_panel.py # Right panel (results)
│   └── utils/             # Utilities
│       ├── validators.py  # Input validation
│       └── formatters.py  # Output formatting
└── tests/                 # Unit tests
    ├── test_pattern_parser.py
    ├── test_invoice_processor.py
    └── test_series_analyzer.py
```

## Running Tests

```bash
pytest tests/ -v
```

## Technical Notes

- Built with PyQt5 for cross-platform desktop support
- Pattern matching uses regex with named capture groups
- Zero-width wildcards supported (wildcard can match empty string)
- Actual padding detected from input data, not pattern specification

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License — free for personal and commercial use.

## Support

For issues, feature requests, or questions:
- Open an issue on GitHub
- Contact: [your email]

---

**Sahaj** (साहज) — Sanskrit for "simple" or "natural". Because GST compliance shouldn't be complicated.
