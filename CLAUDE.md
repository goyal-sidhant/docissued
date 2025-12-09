# CLAUDE.md - Build Instructions for GSTR-1 Table 13 Generator

## Project Overview

Build a **standalone desktop application** for GST practitioners in India to generate **Table 13 of GSTR-1** (Summary of Documents Issued during the tax period).

### What is Table 13?

Table 13 requires taxpayers to report a summary of all documents issued during the return period. For each document type/series, they must report:

| Column | Description |
|--------|-------------|
| Nature of Document | Type of document (Invoice, Credit Note, etc.) |
| Sr. No. From | First invoice number in series |
| Sr. No. To | Last invoice number in series |
| Total Number | Calculated as (To - From + 1) |
| Cancelled | How many were cancelled/not issued |
| Net Issued | Total minus Cancelled |

### The Problem This Solves

Taxpayers maintain invoice registers in Excel/Tally. At month-end, they manually:
1. Identify invoice series used
2. Find start and end numbers
3. Count gaps (cancelled invoices)
4. Fill into Table 13

This is tedious and error-prone. This tool automates it.

### Legal Context (Rule 46, CGST Rules 2017)

Invoice numbers must be:
- Consecutive serial numbers
- Unique for a financial year
- May contain alphabets, numerals, special characters like `-` and `/`
- **No fixed format prescribed** — businesses use wildly varying patterns

---

## Core Functional Requirements

### 1. Pattern Input System

Users define patterns using intuitive notation:

#### Sequence Marker `[NNN]`
- Marks the incrementing sequence number
- Content defines expected padding: `[001]` = 3 digits, `[0001]` = 4 digits
- **Exactly ONE sequence marker required per pattern**

#### Wildcard Marker `*`
- Marks variable parts that define **sub-series**
- Zero or more wildcards allowed
- Used when same pattern structure has multiple series

#### Examples

| Pattern | Description |
|---------|-------------|
| `GST/24-25/[0001]` | Simple: prefix "GST/24-25/", 4-digit sequence |
| `[001]-SAL-2024` | Sequence first, then suffix |
| `INV/[00001]/A` | Sequence sandwiched between prefix and suffix |
| `GST/*/[001]` | **CRITICAL**: Wildcard for sub-series grouping |
| `*/INV/[0001]/*` | Multiple wildcards |

### 2. Multi-Series Auto-Detection (CRITICAL FEATURE)

When pattern contains wildcards, the tool must **auto-detect and group** different series.

**Example:**
```
Pattern: GST/*/[001]

Input:
GST/A/001
GST/A/002
GST/A/003
GST/B/001
GST/B/002

Output:
Series GST/A/: From 001, To 003, Total 3, Cancelled 0, Net 3
Series GST/B/: From 001, To 002, Total 2, Cancelled 0, Net 2
```

The wildcard `*` captures "A" and "B", creating two separate series in the output.

**Implementation approach:**
1. Parse pattern to identify fixed parts, wildcards, and sequence position
2. Build regex with named capture groups for wildcards and sequence
3. For each invoice, extract wildcard values
4. Group invoices by `(fixed_parts + wildcard_values)` = **series_key**
5. Analyze each group independently

### 3. Processing Logic

#### Step 1: Parse Pattern
From `GST/*/[001]`, extract:
- Parts: `[('fixed', 'GST/'), ('wildcard', '*'), ('fixed', '/'), ('sequence', '001')]`
- Regex: `^GST/(?P<wc0>.+?)/(?P<seq>\d+)$`
- Sequence length: 3

#### Step 2: Process Each Invoice
For each pasted invoice:
1. Match against regex
2. Extract sequence number and wildcard values
3. Build series_key from fixed parts + wildcards
4. Categorize: Matched / Unmatched / Duplicate / Invalid

#### Step 3: Analyze Each Series
For each series group:
1. Collect unique sequence numbers
2. Find MIN (start) and MAX (end)
3. Calculate TOTAL = MAX - MIN + 1
4. Find MISSING = all integers in range not present
5. Calculate CANCELLED = count of missing
6. Calculate NET_ISSUED = actual unique invoices

#### Step 4: Generate Warnings

| Condition | Warning |
|-----------|---------|
| Cancellation ratio > 20% | "⚠️ High cancellation ratio: X% missing. Verify data or check for mixed series." |
| Gap of 50+ consecutive numbers | "⚠️ Large gap detected: X numbers missing from Y to Z." |
| Duplicates found | "ℹ️ X duplicate entries ignored." |
| Unmatched invoices | "ℹ️ X invoices didn't match pattern — possibly different series." |

### 4. Input Section

#### Document Nature Dropdown
```
- Invoices for outward supply
- Invoices for inward supply from unregistered person (RCM)
- Revised Invoice
- Debit Note
- Credit Note
- Receipt Voucher
- Payment Voucher
- Refund Voucher
- Delivery Challan for job work
- Delivery Challan for supply on approval
- Delivery Challan in case of liquid gas
- Delivery Challan in other cases
```

#### Pattern Input Field
- Placeholder: `Example: GST/24-25/[0001] or GST/*/[001]`
- Real-time validation with error display
- Info box explaining notation

#### Invoice List Textarea
- Accepts one invoice per line
- Handles Windows (CRLF) and Unix (LF) line endings
- Shows live line count
- Ignores empty lines and whitespace

#### Options
- Checkbox: "Ignore leading zero differences" (treats `01` and `001` as same)

### 5. Output Section

#### Main Table (Table 13 Format)

| Nature of Document | Sr. No. From | Sr. No. To | Total Number | Cancelled | Net Issued |
|--------------------|--------------|------------|--------------|-----------|------------|
| Invoices for outward supply | GST/A/001 | GST/A/003 | 3 | 0 | 3 |
| Invoices for outward supply | GST/B/001 | GST/B/005 | 5 | 2 | 3 |

#### Missing/Cancelled Invoices Section
Collapsible section showing:
```
Series GST/A/:
(None)

Series GST/B/:
GST/B/003, GST/B/004
(2 numbers missing)
```

#### Warnings Section
Display all warnings with appropriate styling (yellow background).

#### Unmatched Invoices Section
Show invoices that didn't match the pattern — these likely belong to a different series.

#### Copy Buttons
- **Copy Table (TSV)**: Tab-separated for Excel/GST Portal paste
- **Copy Missing List**: List of cancelled invoice numbers

---

## Technical Specifications

### Platform
- **PyQt5** desktop application
- Works on Windows (primary), Mac/Linux (secondary)
- Fully offline — no network required

### Project Structure
```
gstr1-table13-generator/
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                      # Entry point
├── src/
│   ├── __init__.py
│   ├── core/                    # Business logic
│   │   ├── __init__.py
│   │   ├── models.py            # Data classes
│   │   ├── pattern_parser.py    # Pattern parsing
│   │   ├── invoice_processor.py # Invoice matching
│   │   └── series_analyzer.py   # Series analysis
│   ├── ui/                      # PyQt5 components
│   │   ├── __init__.py
│   │   ├── main_window.py       # Main application window
│   │   ├── input_panel.py       # Input widgets
│   │   ├── output_panel.py      # Output display
│   │   └── styles.py            # Qt stylesheets
│   └── utils/                   # Helpers
│       ├── __init__.py
│       ├── validators.py        # Input validation
│       └── formatters.py        # Output formatting
└── tests/
    ├── __init__.py
    ├── test_pattern_parser.py
    ├── test_invoice_processor.py
    └── test_series_analyzer.py
```

### Key Classes

#### `ParsedPattern` (dataclass)
```python
parts: List[Tuple[str, str]]  # [('fixed', 'GST/'), ('wildcard', '*'), ('sequence', '001')]
wildcard_count: int
sequence_length: int
regex_pattern: str
is_valid: bool
error_message: str
```

#### `ParsedInvoice` (dataclass)
```python
raw: str
sequence_number: int
sequence_str: str
wildcard_values: List[str]
series_key: str
is_valid: bool
```

#### `SeriesAnalysis` (dataclass)
```python
series_key: str
start_number: int
end_number: int
start_invoice: str
end_invoice: str
total_in_range: int
cancelled_count: int
net_issued: int
missing_numbers: List[int]
missing_invoices: List[str]
duplicate_invoices: List[str]
warnings: List[str]
```

#### `Table13Row` (dataclass)
```python
nature_of_document: str
sr_no_from: str
sr_no_to: str
total_number: int
cancelled: int
net_issued: int
```

---

## Test Cases

### Test Case 1: Simple Series
```
Pattern: GST/24-25/[0001]
Input:
GST/24-25/0001
GST/24-25/0002
GST/24-25/0003
GST/24-25/0005

Expected:
From: GST/24-25/0001
To: GST/24-25/0005
Total: 5
Cancelled: 1 (0004)
Net: 4
```

### Test Case 2: Multiple Series via Wildcard
```
Pattern: GST/*/[001]
Input:
GST/A/001
GST/A/002
GST/B/001
GST/B/002
GST/B/003

Expected:
Series 1 (GST/A/): From 001, To 002, Total 2, Cancelled 0, Net 2
Series 2 (GST/B/): From 001, To 003, Total 3, Cancelled 0, Net 3
```

### Test Case 3: Duplicates
```
Pattern: INV-[001]
Input:
INV-001
INV-002
INV-002
INV-003

Expected:
Total: 3, Cancelled: 0, Net: 3
Duplicates Ignored: 1 (INV-002)
```

### Test Case 4: High Gap Warning
```
Pattern: [0001]
Input:
0001
0002
0500
0501

Expected:
Warning: High cancellation ratio (99%)
Warning: Large gap from 3 to 499
```

### Test Case 5: Mixed Matched/Unmatched
```
Pattern: GST/[001]
Input:
GST/001
GST/002
SAL/001
OTHER/001

Expected:
Matched: GST/001, GST/002
Unmatched: SAL/001, OTHER/001 (reported separately)
```

---

## UI/UX Requirements

### Layout
- Split view: Input (left/top) | Output (right/bottom)
- Splitter for resizing
- Minimum window size: 1200x800
- Works well on 1366x768 (common in India)

### Design
- Professional, clean — this is an accounting tool
- Good use of whitespace
- Clear visual hierarchy
- Blue primary color (#2563eb)
- Readable fonts (Segoe UI)

### Helpful Elements
- Placeholder text with examples
- Tooltips on options
- Real-time validation feedback
- Line count display
- Clear All button
- Status bar messages

### Copy Functionality
- TSV format for Excel paste
- Clear confirmation messages

---

## Performance

- Handle 10,000+ invoices without freezing
- Process and display in 2-3 seconds
- Use QTimer.singleShot for UI responsiveness during processing

---

## Edge Cases to Handle

1. **Empty input**: Show validation error
2. **Pattern without sequence**: Show clear error message
3. **Multiple sequence markers**: Reject with error
4. **Non-numeric sequence content**: Reject
5. **Single invoice**: Should work (Total=1, From=To)
6. **All duplicates**: Handle gracefully
7. **Windows line endings**: Convert to Unix internally
8. **Leading/trailing whitespace**: Trim automatically
9. **Sequence starting at non-1**: Handle (start from actual MIN)
10. **Very large gaps**: Warn but don't break

---

## What's Already Built

The project structure and core logic modules have been created. You need to:

1. **Test the existing code** — run `pytest tests/`
2. **Fix any issues** found during testing
3. **Ensure PyQt5 UI works** — run `python main.py`
4. **Polish the UI** — improve any rough edges
5. **Add any missing features** based on this spec

---

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run application
python main.py
```

---

## Future Enhancements (Not for v1)

- Import from Excel directly
- Export to Excel
- Save/load sessions
- Multiple financial years
- Tally export format integration
