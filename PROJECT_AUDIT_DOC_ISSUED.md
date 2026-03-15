# PROJECT_AUDIT_DOC_ISSUED.md — Complete Project Archaeology

**Audit Date:** 2026-03-15
**Auditor:** Claude Opus 4.6 (AI-assisted reverse engineering)
**Project:** Sahaj — GSTR-1 Table 13 Generator
**Codebase Snapshot:** Commit `e650cc5` (latest on `main`)

---

## SECTION 1: EXECUTIVE SUMMARY

Sahaj is a desktop application built for Indian GST (Goods and Services Tax) practitioners — Chartered Accountants, tax consultants, and accountants — to automate the generation of **Table 13 of GSTR-1**, which is a summary of all documents (invoices, credit notes, debit notes, etc.) issued during a tax period. The tool takes a list of invoice numbers (pasted from Tally or Excel), matches them against a user-defined pattern, groups them into series, finds gaps (cancelled/missing invoices), and outputs a ready-to-paste Table 13 with From, To, Total, Cancelled, and Net columns. It also supports auto-detecting invoice patterns and checking continuity against a previous month's GSTR-1 Excel file. The application is built with **Python 3.8+**, using **PyQt5** for the desktop GUI and **openpyxl** for reading Excel files. The project is **feature-complete for v1** — all core functionality works, the UI is polished with scaling support, and there are 43 unit tests covering the business logic. Development occurred in two intense sessions (December 10, 2025 and January 5–6, 2026) and the code is clean and well-structured, though it contains some dead code and a few minor bugs that don't affect primary functionality.

---

## SECTION 2: PROJECT STRUCTURE MAP

```
d:\OneDrive 2\OneDrive\Python\Doc Issued\Code\
│
├── main.py                              [CORE] Entry point — run this to start the app
├── requirements.txt                     [CONFIG] Python dependencies (PyQt5, openpyxl)
├── README.md                            [DOCS] User-facing documentation
├── CLAUDE.md                            [DOCS] Developer spec / build instructions
├── HANDOVER.md                          [DOCS] Knowledge transfer from original dev session
├── FILE_INDEX.md                        [DOCS] File-by-file status index
├── .gitignore                           [CONFIG] Standard Python + IDE ignores
│
├── .claude/                             [TOOLING] Claude Code AI assistant config
│   └── settings.local.json              [TOOLING] Permission: allows `python main.py`
│
├── src/                                 [CORE] Main source package
│   ├── __init__.py                      [CORE] Package marker (1 line)
│   │
│   ├── core/                            [CORE] Business logic layer
│   │   ├── __init__.py                  [CORE] Re-exports all public APIs (14 symbols)
│   │   ├── models.py                    [CORE] Data classes: DocumentNature, ParsedPattern, etc.
│   │   ├── pattern_parser.py            [CORE] Converts [NNN]/* notation to regex
│   │   ├── invoice_processor.py         [CORE] Matches invoices, groups by series
│   │   ├── series_analyzer.py           [CORE] Gap detection, statistics, Table 13 rows
│   │   ├── pattern_detector.py          [CORE] Auto-detect pattern from invoice list
│   │   ├── excel_reader.py              [CORE] Read GSTR1-Portal-*.xlsx files
│   │   └── continuity_checker.py        [CORE] Compare previous vs current period
│   │
│   ├── ui/                              [UI] PyQt5 interface layer
│   │   ├── __init__.py                  [UI] Package marker (1 line)
│   │   ├── main_window.py              [UI] QMainWindow with splitter, header, status bar
│   │   ├── input_panel.py              [UI] Left panel: 4-step input wizard
│   │   ├── output_panel.py             [UI] Right panel: results, table, warnings
│   │   └── styles.py                    [UI] **DEAD CODE** — COLORS dict, never imported
│   │
│   └── utils/                           [UTIL] Helper functions
│       ├── __init__.py                  [UTIL] Package marker (1 line)
│       ├── validators.py               [UTIL] Pattern validation, line counting
│       ├── formatters.py               [UTIL] TSV/CSV formatting for output
│       └── fy_utils.py                 [UTIL] Financial year calculations
│
├── tests/                               [TEST] Unit tests (pytest)
│   ├── __init__.py                      [TEST] Package marker
│   ├── test_pattern_parser.py           [TEST] 17 tests for pattern parsing
│   ├── test_invoice_processor.py        [TEST] 13 tests for invoice processing
│   └── test_series_analyzer.py          [TEST] 13 tests for series analysis
│
└── run_template.bat                     [CONFIG] **MISSING FROM DISK** — tracked in git but deleted
                                                  (uses `pythonw` to run main.py silently)
```

**Entry Point:** `python main.py`

### Dead Code Inventory

| Level | Item | Location | Evidence |
|-------|------|----------|----------|
| **Dead File** | `src/ui/styles.py` | Entire file | Defines `COLORS` dict; never imported by any file. `SCROLLBAR_STYLE` is defined inline in `main_window.py:23` instead. |
| **Dead Functions** | `validate_invoice_list()` | `validators.py:57` | Defined but never called anywhere. |
| **Dead Functions** | `validate_document_nature()` | `validators.py:82` | Defined but never called anywhere. |
| **Dead Functions** | `sanitize_input()` | `validators.py:102` | Defined but never called anywhere. |
| **Dead Functions** | `format_result_summary()` | `formatters.py:69` | Defined but never called anywhere. |
| **Dead Functions** | `format_series_summary()` | `formatters.py:35` | Only called from `format_result_summary()` which is itself dead. |
| **Dead Functions** | `format_table13_csv()` | `formatters.py:145` | Defined but never called anywhere. |
| **Dead Functions** | `format_number_with_commas()` | `formatters.py:186` | Defined but never called anywhere. |
| **Dead Functions** | `parse_display_to_tax_period()` | `fy_utils.py:108` | Defined but never called anywhere. |
| **Dead Functions** | `is_fy_boundary()` | `fy_utils.py:185` | Defined but never called anywhere. |
| **Dead Functions** | `get_pattern_description()` | `pattern_parser.py:199` | Method defined but never called anywhere. |
| **Dead Functions** | `process_invoice_list()` | `invoice_processor.py:106` | Method defined but never called (only `process_text_input()` is used). |
| **Dead Functions** | `format_continuity_report()` | `continuity_checker.py:147` | Exported in `__init__.py` but never called anywhere. |
| **Unused Import** | `Counter` from `collections` | `pattern_detector.py:12` | Imported but never used. |
| **Unused Import** | `Optional` | `fy_utils.py:9` | Imported but never used. |
| **Unused Import** | `Dict` | `continuity_checker.py:8` | Imported but never used. |
| **Unused Parameter** | `current_series_key` | `excel_reader.py:266` | Accepted by `match_series()` but never read in function body. |
| **Stubbed Feature** | `ignore_leading_zeros` | `invoice_processor.py:16,28` | Parameter accepted and stored but never used in processing logic. `get_ignore_leading_zeros()` in `input_panel.py:571` always returns `False`. |
| **Missing File** | `run_template.bat` | Root directory | Tracked in git (commit `1ff5d7b`) but deleted from disk without staging the deletion. |

---

## SECTION 3: FEATURE INVENTORY

### F1: Pattern Parsing

- **What it does:** Converts a user-friendly invoice format notation (like `GST/24-25/[0001]` or `GST/*/[001]`) into a regular expression (a text-matching formula) that the computer can use to match real invoice numbers.
- **Where it lives:** `src/core/pattern_parser.py` — `PatternParser` class, `parse()` method (line 42)
- **Input → Output:** String pattern → `ParsedPattern` dataclass with parts list, regex, wildcard count, sequence length
- **User interaction:** User types a pattern into the "Invoice Format" text field (Step 2 in input panel)
- **Concrete trace:** Pattern `GST/*/[001]` → `_build_parts()` produces `[('fixed','GST/'), ('wildcard','*'), ('fixed','/'), ('sequence','001')]` → `_build_regex()` produces `^GST/(?P<wc0>.*?)/(?P<seq>\d+)$` → `ParsedPattern` with `is_valid=True`, `wildcard_count=1`, `sequence_length=3`. Verified correct.

### F2: Invoice Processing & Series Grouping

- **What it does:** Takes a list of invoice numbers (pasted text), matches each against the pattern's regex, extracts the sequence number and any wildcard values, then groups invoices into series based on their fixed+wildcard combination.
- **Where it lives:** `src/core/invoice_processor.py` — `InvoiceProcessor` class, `process_text_input()` (line 129)
- **Input → Output:** Raw text → tuple of (series_groups dict, unmatched list, invalid list)
- **User interaction:** User pastes invoices into the text area (Step 3) then clicks "Generate Table 13"
- **Concrete trace:** Pattern `GST/*/[001]`, input `"GST/A/001\nGST/A/002\nGST/B/001\nSAL/001"` → line splitting produces 4 lines → `GST/A/001` matches regex, seq=1, wc0="A", series_key=`"GST/A/{SEQ}"` → `GST/A/002` matches, seq=2, same key → `GST/B/001` matches, seq=1, wc0="B", series_key=`"GST/B/{SEQ}"` → `SAL/001` fails regex match → unmatched. Result: 2 series groups (A with 2 invoices, B with 1), 1 unmatched. Verified correct.

### F3: Series Analysis (Gap Detection & Table 13 Generation)

- **What it does:** For each series group, finds the min and max sequence numbers, calculates Total = max−min+1, finds missing numbers in the range (cancelled invoices), counts duplicates, and generates warnings.
- **Where it lives:** `src/core/series_analyzer.py` — `SeriesAnalyzer` class, `analyze_series()` (line 41), `analyze_all_series()` (line 190), `to_table13_rows()` (line 244)
- **Input → Output:** Series groups → `ProcessingResult` with `SeriesAnalysis` per series → `Table13Row` list
- **User interaction:** Triggered automatically when user clicks "Generate Table 13"
- **Concrete trace:** Series `"INV/{SEQ}"` with invoices INV/001 (seq 1), INV/002 (seq 2), INV/005 (seq 5) → `start_number=1`, `end_number=5`, `total_in_range=5`, `unique_sequences={1,2,5}`, `missing_numbers=[3,4]`, `cancelled_count=2`, `net_issued=3`. Uses ORIGINAL strings for From/To display. Padding detection: INV/001 starts with '0' and len > 1, so `is_padded=True` → missing displayed as `["003","004"]`. Warning check: `cancelled_ratio = 2/5 = 0.40 > 0.20` → generates "High cancellation ratio: 40%". Verified correct.

### F4: Pattern Auto-Detection

- **What it does:** Analyzes a list of pasted invoice numbers to automatically guess the pattern, without the user having to type it manually. Splits each invoice into text/numeric parts, finds which numeric part varies (the sequence), and builds a pattern string.
- **Where it lives:** `src/core/pattern_detector.py` — `detect_pattern()` (line 15), `_analyze_invoices()` (line 52)
- **Input → Output:** List of invoice strings → tuple of (pattern string or None, message string)
- **User interaction:** User pastes invoices, then clicks the yellow "🔍 Auto-Detect" button
- **Concrete trace:** Input `["GST/24-25/0001", "GST/24-25/0002", "GST/24-25/0003"]` → `_split_into_parts()` produces `[('text','GST/'), ('num','24'), ('text','-'), ('num','25'), ('text','/'), ('num','0001')]` for each → numeric indices are [1,3,5] → checking which varies: index 1 has values {24,24,24} (same), index 3 has {25,25,25} (same), index 5 has {"0001","0002","0003"} (varies) → `varying_index=5` → is_padded check: "0001" starts with '0', so True → `max_len=4` → pattern `"GST/24-25/[0000]"` → confidence `min(95, 50+3*5)=65`. Note: the pattern content `[0000]` uses all zeros of max length, which differs from the CLAUDE.md spec's `[0001]` example but is functionally equivalent since the content only determines padding length. Verified functionally correct.

### F5: Previous GSTR-1 Excel Reader

- **What it does:** Reads a GSTR-1 Excel file downloaded from the GST Portal (filename must start with "GSTR1-Portal-") and extracts document series information from the "DocIssued" sheet, including invoice ranges, totals, and cancelled counts.
- **Where it lives:** `src/core/excel_reader.py` — `read_gstr1_excel()` (line 29)
- **Input → Output:** Excel file path → tuple of (list of `PreviousSeriesInfo`, message string)
- **User interaction:** User clicks "Browse..." in Step 4, selects an Excel file
- **Concrete trace:** File `GSTR1-Portal-April2024.xlsx` → validates filename prefix ✓ → validates `.xlsx` extension ✓ → opens with openpyxl → searches for "DocIssued" sheet (tries 5 name variants) → if not found, uses active sheet → searches first 15 rows for header containing "doc type" → finds column indices for doc_type, from, to, total, cancelled, tax_period → reads data rows, skipping empties and repeated headers → for each row, calls `_extract_pattern_info()` to find prefix/suffix/end_sequence from the "to" invoice → returns list. The sequence-finding logic skips numbers 1900–2100 (likely years) and 2-digit numbers 00–50 (likely year codes like "24", "25"). Verified correct for standard GST Portal formats.

### F6: Continuity Checking

- **What it does:** Compares the previous GSTR-1's ending invoice numbers with the current month's starting numbers to detect gaps between filing periods. Respects Indian Financial Year (April–March) boundaries.
- **Where it lives:** `src/core/continuity_checker.py` — `check_continuity()` (line 28)
- **Input → Output:** Previous series list + current ProcessingResult + tax period → list of `ContinuityResult`
- **User interaction:** Automatic — runs after "Generate Table 13" if a previous GSTR-1 file was loaded
- **Concrete trace:** Previous series has prefix="GST/24-25/", suffix="", end_sequence=500. Current series starts at "GST/24-25/0501". → `match_series()` extracts current_prefix="GST/24-25/", current_suffix="", current_start_seq=501 → exact prefix/suffix match found → expected_next = 500+1 = 501 → `is_continuous = (501 == 501) = True` → message "✓ Continuity OK". If current started at 503 instead → `gap = 503 - 500 - 1 = 2` → message "⚠️ Gap detected: Missing 2 invoice(s): 501 to 502". Verified correct.

### F7: Financial Year Utilities

- **What it does:** Handles Indian Financial Year calculations — parsing tax periods (MMYYYY format), determining which FY a period belongs to (April starts new FY), checking if two periods are in the same FY, and generating recent period lists for dropdowns.
- **Where it lives:** `src/utils/fy_utils.py` — `parse_tax_period()` (line 12), `get_fy_from_tax_period()` (line 43), etc.
- **Input → Output:** Tax period strings → FY strings, boolean comparisons, period lists
- **User interaction:** Powers the "Current Tax Period" dropdown in Step 4 and filters continuity checks to same-FY series only.
- **Concrete trace:** Tax period "042024" → `parse_tax_period()` → month=4, year=2024 → `get_fy_from_tax_period()` → month >= 4 so fy_start=2024, fy_end=2025 → returns "2024-25". Tax period "032025" → month=3, year=2025 → month < 4 so fy_start=2024, fy_end=2025 → returns "2024-25". Both are same FY. Verified correct.

### F8: UI Scaling

- **What it does:** Allows users to scale the entire UI from 75% to 110% using a dropdown in the header bar. Scales fonts, padding, border radii, widget sizes, and table dimensions proportionally.
- **Where it lives:** `main_window.py:285` (`_on_scale_changed`), `input_panel.py:583` (`apply_scale`), `output_panel.py:714` (`apply_scale`)
- **Input → Output:** Scale percentage → all widget stylesheets updated with scaled values
- **User interaction:** User selects a percentage from the "UI Scale" dropdown in the dark header bar
- **Concrete trace:** User selects "80%" → `_on_scale_changed("80%")` → scale_value=80, `_ui_scale=0.8` → calls `_apply_header_scale()` (title becomes 14px instead of 18px), `input_panel.apply_scale(0.8)` (all widget heights, font sizes, padding multiplied by 0.8), `output_panel.apply_scale(0.8)` (table columns, text areas, stat boxes scaled). Verified correct.

### F9: Copy Functionality

- **What it does:** Copies Table 13 data to clipboard in tab-separated format (TSV) for pasting into Excel or the GST Portal. Also supports copying selected cells (Ctrl+C) and copying missing invoice lists.
- **Where it lives:** `output_panel.py` — `_copy_table()` (line 570), `_copy_selected()` (line 407), `_copy_missing()` (line 577)
- **Input → Output:** Table13Row list → TSV string on clipboard
- **User interaction:** "Copy for Excel" button, Ctrl+C on selected cells, right-click context menu, or "Copy" button next to missing invoices
- **Concrete trace:** Two rows: "Invoices\tGST/001\tGST/003\t3\t1\t2" → `format_table13_tsv()` adds header row → clipboard gets "Nature of Document\tSr. No. From\t..." + data rows. Verified correct.

---

## SECTION 4: DATA FLOW

```
USER INPUT                    PROCESSING PIPELINE                         OUTPUT
─────────                    ────────────────────                         ──────

Step 1: Document Type ──┐
                        │
Step 2: Pattern ────────┤
    (or Auto-Detect) ───┤    ┌──────────────┐     ┌───────────────┐     ┌──────────────┐
                        ├───→│PatternParser  │────→│InvoiceProcessor│───→│SeriesAnalyzer │
Step 3: Invoice List ───┤    │parse()        │     │process_text_  │     │analyze_all_  │
    (pasted text)       │    │               │     │input()        │     │series()      │
                        │    │Pattern string │     │               │     │              │
                        │    │→ ParsedPattern│     │Text + Pattern │     │Series groups │
                        │    │  (with regex) │     │→ series_groups│     │→ Processing  │
                        │    └──────────────┘     │  unmatched    │     │  Result      │
                        │                         │  invalid      │     │              │
                        │                         └───────────────┘     │→ Table13Rows │
                        │                                               └──────┬───────┘
                        │                                                      │
Step 4: Previous ───────┤    ┌──────────────┐     ┌───────────────┐            │
  GSTR-1 (optional)     ├───→│ExcelReader   │────→│Continuity     │            │
    (.xlsx file)        │    │read_gstr1_   │     │Checker        │            │
                        │    │excel()       │     │check_         │            │
Tax Period dropdown ────┘    │              │     │continuity()   │            │
                             │File → List of│     │               │            │
                             │PreviousSeries│     │Prev + Current │            │
                             │Info          │     │→ Continuity   │            │
                             └──────────────┘     │  Results      │            │
                                                  └───────┬───────┘            │
                                                          │                    │
                                                          ▼                    ▼
                                                  ┌────────────────────────────────┐
                                                  │         OutputPanel            │
                                                  │                                │
                                                  │  • Stats cards (Total,         │
                                                  │    Matched, Cancelled, Series) │
                                                  │  • Table 13 table              │
                                                  │  • Warnings section            │
                                                  │  • Missing invoices section    │
                                                  │  • Unmatched section           │
                                                  │  • Continuity check section    │
                                                  │                                │
                                                  │  EXPORT: Copy for Excel (TSV)  │
                                                  │          Copy Missing list     │
                                                  │          Ctrl+C selection      │
                                                  └────────────────────────────────┘
```

**Data entry points:**
1. User typing/pasting text (pattern field, invoice text area)
2. File selection dialog (Previous GSTR-1 Excel file)
3. Dropdown selections (document type, tax period, UI scale)

**Data exit points:**
1. Screen display (table, stats, warnings, continuity results)
2. System clipboard (TSV copy, selected cells copy, missing invoices copy)

**No data is saved to disk, sent over network, or persisted between sessions.**

---

## SECTION 5: BUSINESS RULES AND DOMAIN LOGIC

### R1: Invoice Pattern Notation

| Rule | Implementation | Location |
|------|----------------|----------|
| Exactly ONE sequence marker `[NNN]` required per pattern | `len(sequence_matches) == 0` → error; `> 1` → error | `pattern_parser.py:65-71` |
| Sequence marker content must be all digits | `seq_content.isdigit()` check | `pattern_parser.py:78` |
| Zero or more wildcard `*` markers allowed | `wildcard_matches = list(WILDCARD_PATTERN.finditer(pattern))` | `pattern_parser.py:85` |
| Fixed text is regex-escaped for matching | `re.escape(value)` for fixed parts | `pattern_parser.py:168` |
| Wildcards match zero or more chars (non-greedy) | `(?P<wcN>.*?)` pattern | `pattern_parser.py:173` |
| Sequence matches one or more digits (greedy) | `(?P<seq>\d+)` pattern | `pattern_parser.py:179` |
| Pattern anchored to full string | `'^' + regex + '$'` | `pattern_parser.py:182` |

### R2: Series Grouping

| Rule | Implementation | Location |
|------|----------------|----------|
| Series key = fixed parts + wildcard values + `{SEQ}` placeholder | `key_parts` joined from pattern parts with wildcard values substituted | `invoice_processor.py:84-104` |
| Invoices with same series_key belong to same series | `series_groups[key].append(parsed)` | `invoice_processor.py:162-164` |
| Empty lines in input are silently skipped | `if not line: continue` | `invoice_processor.py:155-156` |
| Whitespace is trimmed from each line | `line = line.strip()` | `invoice_processor.py:152` |
| Windows line endings handled | `text.replace('\r\n', '\n').replace('\r', '\n')` | `invoice_processor.py:145` |

### R3: Gap Analysis & Statistics

| Rule | Implementation | Location |
|------|----------------|----------|
| Total = max_sequence − min_sequence + 1 | `end_number - start_number + 1` | `series_analyzer.py:108` |
| Missing = all integers in [min, max] range not present | `set(range(start, end+1)) - unique_sequences` | `series_analyzer.py:111-112` |
| Cancelled = count of missing numbers | `len(missing_numbers)` | `series_analyzer.py:115` |
| Net Issued = count of unique invoices (duplicates removed) | `len(unique_sequences)` | `series_analyzer.py:101,116` |
| Start/End invoices use ORIGINAL strings (not reconstructed) | `seq_to_invoice[start_number]`, `seq_to_invoice[end_number]` | `series_analyzer.py:104-105` |

### R4: Padding Detection

| Rule | Implementation | Location |
|------|----------------|----------|
| Series is "padded" if ANY sequence string starts with '0' and length > 1 | `if inv.sequence_str and len(inv.sequence_str) > 1 and inv.sequence_str.startswith('0')` | `series_analyzer.py:72-73` |
| Padded series: missing numbers zero-filled to max observed length | `str(num).zfill(max_seq_len)` | `series_analyzer.py:121-126` |
| Unpadded series: missing numbers displayed as plain integers | `str(num)` | `series_analyzer.py:130` |

### R5: Warning Thresholds

| Rule | Value | Implementation | Location |
|------|-------|----------------|----------|
| High cancellation ratio warning | > 20% (`0.20`) | `cancellation_ratio > HIGH_CANCELLATION_THRESHOLD` | `series_analyzer.py:27,143` |
| Large consecutive gap warning | ≥ 50 numbers | `(end - start + 1) >= LARGE_GAP_THRESHOLD` | `series_analyzer.py:28,155` |
| Duplicate invoice info | Any count > 0 | `analysis.duplicate_count > 0` | `series_analyzer.py:165` |
| Unmatched invoice warning | Any count > 0 | `result.total_unmatched > 0` | `series_analyzer.py:230` |
| Multiple series info | > 1 series | `len(series_groups) > 1` | `series_analyzer.py:236` |

### R6: Excel File Validation

| Rule | Implementation | Location |
|------|----------------|----------|
| Filename must start with "GSTR1-Portal-" | `filename.startswith("GSTR1-Portal-")` | `excel_reader.py:41` |
| File extension must be .xlsx | `filepath.lower().endswith('.xlsx')` | `excel_reader.py:45` |
| Sheet search order: DocIssued, docissued, DOCISSUED, b2b, B2B, then active sheet | `sheet_names_to_try` list then `wb.active` fallback | `excel_reader.py:61-70` |
| Header row search: first 15 rows only | `max_row=15` | `excel_reader.py:80` |
| Required columns: Doc Type (or Nature), From, To | Check `headers` dict has all three | `excel_reader.py:101` |

### R7: Continuity Checking

| Rule | Implementation | Location |
|------|----------------|----------|
| Series matched by exact prefix + suffix | `prev.prefix == current_prefix and prev.suffix == current_suffix` | `excel_reader.py:314` |
| Year-like numbers (1900–2100) skipped when finding sequence | `if 1900 <= num_val <= 2100: continue` | `excel_reader.py:246,294` |
| 2-digit codes 00–50 skipped (likely year codes) | `if len(num_str) == 2 and 0 <= num_val <= 50: continue` | `excel_reader.py:248,296` |
| Continuity OK when current_start = previous_end + 1 | `current_start_seq == expected_next` | `excel_reader.py:316` |
| FY boundary respected: only same-FY series compared | `are_same_fy(prev.tax_period, current_tax_period)` | `continuity_checker.py:62` |
| If no tax period info, assume same FY (backward compat) | `else: same_fy_series.append(prev)` | `continuity_checker.py:67-68` |
| Year-change similarity via prefix comparison | `_prefixes_similar()` removes year patterns | `excel_reader.py:342-353` |

### R8: Financial Year Rules

| Rule | Implementation | Location |
|------|----------------|----------|
| Indian FY: April (month 4) through March (month 3) | `if month >= 4: fy_start = year` else `fy_start = year - 1` | `fy_utils.py:58-63` |
| Tax period format: MMYYYY (e.g., "042024" for April 2024) | `month = int(tax_period[:2])`, `year = int(tax_period[2:])` | `fy_utils.py:29-30` |
| Valid year range: 2000–2100 | `if not (2000 <= year <= 2100)` | `fy_utils.py:37` |
| FY display format: "2024-25" (last 2 digits of end year) | `f"{fy_start}-{str(fy_end)[-2:]}"` | `fy_utils.py:65` |

### R9: Document Types (12 types per GST Table 13)

All 12 document nature values are hardcoded in `models.py:12-26`:
1. Invoices for outward supply
2. Invoices for inward supply from unregistered person (RCM)
3. Revised Invoice
4. Debit Note
5. Credit Note
6. Receipt Voucher
7. Payment Voucher
8. Refund Voucher
9. Delivery Challan for job work
10. Delivery Challan for supply on approval
11. Delivery Challan in case of liquid gas
12. Delivery Challan in other cases

### R10: UI Layout Constants

| Constant | Value | Location |
|----------|-------|----------|
| Minimum window size | 800×500 | `main_window.py:77` |
| Screen usage percentage | 85% | `main_window.py:84-85` |
| Max window size | 1400×900 | `main_window.py:84-85` |
| Input panel min width | 320px | `main_window.py:170` |
| Output panel min width | 350px | `main_window.py:189` |
| Splitter ratio (input:output) | 2:3 | `main_window.py:200-201` |
| Table compact max height | 200px | `output_panel.py:228` |
| Table compact min height | 80px | `output_panel.py:227` |
| Processing delay (UI responsiveness) | 30ms | `main_window.py:241` |
| Missing invoices display cap | 20 | `output_panel.py:518` |
| Unmatched invoices display cap | 10 | `output_panel.py:531` |
| Document type truncation | 25 chars (show 22+"...") | `output_panel.py:545-546` |
| Default font | Segoe UI, 11pt | `main.py:32` |
| Scale options | 75%, 80%, 90%, 100%, 110% | `main_window.py:123` |
| Recent tax periods count | 24 months | `input_panel.py:240` |

---

## SECTION 6: EDGE CASES AND DEFENSIVE CODE

### Handled Edge Cases

| Edge Case | How Handled | Location | Rating |
|-----------|------------|----------|--------|
| Empty pattern input | Returns `is_valid=False` with error message | `pattern_parser.py:55-57` | ROBUST |
| Whitespace-only pattern | Stripped first, then checked for empty | `pattern_parser.py:55-59` | ROBUST |
| Multiple sequence markers | Rejected with clear error | `pattern_parser.py:69-71` | ROBUST |
| No sequence marker | Rejected with example in error | `pattern_parser.py:65-67` | ROBUST |
| Non-numeric sequence content | Rejected (note: `[ABC]` doesn't match `\[(\d+)\]` regex, so caught at "no sequence marker" level) | `pattern_parser.py:65-67` | ROBUST |
| Empty invoice line | Silently skipped | `invoice_processor.py:155-156` | ROBUST |
| Whitespace in invoice lines | Trimmed with `.strip()` | `invoice_processor.py:152` | ROBUST |
| Windows line endings (CRLF) | Converted to LF before splitting | `invoice_processor.py:145` | ROBUST |
| Mac line endings (CR) | Converted to LF before splitting | `invoice_processor.py:145` | ROBUST |
| Invoice doesn't match pattern | Classified as "unmatched" and reported separately | `invoice_processor.py:166-167` | ROBUST |
| Duplicate invoices | Counted and ignored (first occurrence kept) | `series_analyzer.py:85-91` | ROBUST |
| Single invoice in series | Works correctly (From=To, Total=1) | Tested in `test_series_analyzer.py:166` | ROBUST |
| Series starting at non-1 number | Uses actual min as start | `series_analyzer.py:99` | ROBUST |
| Very large gaps (>50 consecutive) | Warning generated but processing continues | `series_analyzer.py:154-162` | ROBUST |
| High cancellation ratio (>20%) | Warning generated | `series_analyzer.py:143-148` | ROBUST |
| openpyxl not installed | Graceful error message with install instructions | `excel_reader.py:49-52` | ROBUST |
| Excel file won't open | Generic exception caught with message | `excel_reader.py:54-57` | MODERATE |
| No matching sheet in Excel | Falls back to active sheet | `excel_reader.py:69-70` | MODERATE |
| Missing required columns in Excel | Returns empty list with error message | `excel_reader.py:101-102` | ROBUST |
| Invalid Total/Cancelled values in Excel | `ValueError/TypeError` caught, defaults to 0 | `excel_reader.py:125-134` | ROBUST |
| Processing error in main pipeline | `Exception` caught, shown in QMessageBox | `main_window.py:274-276` | MODERATE |
| Empty series (no valid sequences) | Warning "No invoices in series" | `series_analyzer.py:60-62` | ROBUST |
| Unpadded sequences (e.g., "67", "109") | Detected correctly, displayed without zero-padding | `series_analyzer.py:66-73,127-130` | ROBUST |

**Overall Defensive Coding Rating: ROBUST** — The core business logic handles most edge cases well. The main gap is in the auto-detection module (see Section 7).

---

## SECTION 7: EDGE CASES NOT HANDLED (GAPS AND VULNERABILITIES)

### 7.1 Silent Logic Bugs

**BUG: `num_end` variable leak in `pattern_detector.py:277-279`**

In `_detect_pattern_with_wildcards()`, when processing a numeric section:
```python
num_end = i  # Set in outer scope at line 270
for inv in invoices:
    num_str = inv[num_start:num_end]
    while num_end < len(inv) and inv[num_end].isdigit():
        num_str += inv[num_end]
        num_end += 1  # THIS MODIFIES THE OUTER VARIABLE
    nums.append(num_str)
```
The `while` loop at line 277 advances `num_end` for the first invoice, and subsequent invoices in the `for` loop start with the already-advanced `num_end`. This means the second and third invoices may read beyond their numeric section or read incorrectly. **Impact:** Auto-detection may produce wrong patterns when invoices have varying-length numeric sections. This only affects the auto-detect feature; manual pattern entry is unaffected.

**BUG: Bare `except:` in `continuity_checker.py:53`**

```python
try:
    current_fy = get_fy_from_tax_period(current_tax_period)
except:
    pass
```
This catches ALL exceptions including `SystemExit` and `KeyboardInterrupt`. Should be `except Exception:`. **Impact:** In theory, could prevent the user from force-quitting the application during this code path, though in practice the risk is negligible since `get_fy_from_tax_period()` only does string parsing.

### 7.2 Missing Validations

| Gap | Risk | Severity |
|-----|------|----------|
| **No maximum input size limit** — user could paste millions of lines | Memory exhaustion, UI freeze. The 30ms `QTimer.singleShot` defers processing but it's still single-threaded — the UI will freeze during processing of 100K+ invoices. | MEDIUM |
| **No validation that pattern matches at least some invoices** — if pattern is wrong, all invoices go to "unmatched" with no helpful guidance | User confusion — they see 0 matched, 1000 unmatched, no suggestion for why | LOW |
| **Adjacent wildcards create ambiguous regex** — pattern `**[1]` produces `(?P<wc0>.*?)(?P<wc1>.*?)` — two consecutive non-greedy `.*?` groups | One will always capture empty string, the other captures everything. Technically works but may confuse users. | LOW |
| **`ignore_leading_zeros` feature is stubbed** — parameter accepted but never used, checkbox removed from UI but `get_ignore_leading_zeros()` still returns `False` | No impact currently but misleading code | NEGLIGIBLE |
| **No input sanitization on invoice text** — `sanitize_input()` exists in `validators.py` but is never called | Invoices with control characters could cause display issues | LOW |
| **Tax period dropdown only shows 24 months** — users who need older periods cannot select them | Can't check continuity against periods older than 2 years | LOW |

### 7.3 Scenario-Based Failure Analysis

| Scenario | What Breaks | Severity |
|----------|-------------|----------|
| **Different working directory** | `sys.path.insert(0, ...)` in `main.py:13` uses `__file__` which should resolve correctly regardless of cwd. No issue. | NONE |
| **Network drive disconnects mid-operation** | Only matters during Excel file reading (`excel_reader.py`). openpyxl opens with `read_only=True` which streams data — a disconnection mid-read would raise an exception caught by the generic handler in `main_window.py:274`. | LOW |
| **Run twice on same data** | No issue — the tool is stateless; each run starts fresh. No files are written. | NONE |
| **Two instances simultaneously** | No issue — no shared state, no file locks, no temp files. | NONE |
| **Different OS (Linux/Mac)** | Font "Segoe UI" in `main.py:32` doesn't exist on Linux/Mac — Qt will fall back to default font. No crash but different appearance. The `run_template.bat` is Windows-only. | LOW |
| **Python 3.12+ with stricter typing** | `__pycache__` contains `.cpython-312.pyc` and `.cpython-313.pyc` files, suggesting it has run on both. No f-string or typing issues observed. | NONE |
| **PyQt5 version mismatch** | `requirements.txt` specifies `>=5.15.0`. The code uses no deprecated APIs. `QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)` was deprecated in Qt6 but is fine for PyQt5. | NONE |
| **openpyxl not installed** | Gracefully handled — import is inside function body with try/except. App works without it; only Excel features disabled. | NONE |
| **Very long invoice numbers (100+ chars)** | Document type column truncates at 25 chars (`output_panel.py:545`), but From/To columns don't truncate — table may need horizontal scrolling. Interactive column resize is available. | LOW |
| **Unicode in invoice numbers** | Regex `\d+` only matches ASCII digits 0-9 in Python's `re` module (unless `re.UNICODE` flag is used, which it isn't explicitly but is default in Python 3). `\D+` matches non-digit chars including Unicode. Should work. | NONE |

### 7.4 Performance Concerns

- **No threading for heavy processing** — the `QTimer.singleShot(30)` in `main_window.py:241` defers processing by 30ms to allow the UI to update the "Processing..." state, but the actual processing (`_do_process`) runs on the main thread. For 10,000+ invoices this may cause a brief freeze. For 100,000+ invoices, the freeze could be significant.
- **Regex is compiled once per processing run** (`invoice_processor.py:29`), which is efficient.
- **`_detect_pattern_with_wildcards` has O(n × m) complexity** where n = number of invoices and m = invoice length. For large datasets with the auto-detect feature, this could be slow.

### 7.5 Accessibility and Usability Gaps

- No keyboard shortcut for "Generate Table 13" (e.g., Ctrl+Enter)
- No keyboard shortcut for Auto-Detect
- No "Save/Load session" — user must re-enter everything each time
- No drag-and-drop for invoice text or Excel files
- Color-only status indicators in continuity results (red/green/blue/purple) — not accessible for colorblind users, though emoji icons partially compensate

---

## SECTION 8: DESIGN DECISIONS (INFERRED)

### D1: PyQt5 over Tkinter/Web/Electron

**Choice:** PyQt5 desktop application
**Reasoning:** The user (a CA/GST practitioner) wanted a desktop tool, not a web app. PyQt5 provides a professional, native-looking UI with minimal overhead. Tkinter would look less polished. Electron would be too heavy for a single-purpose tool. The HANDOVER.md confirms this was explicitly discussed and decided.
**Confidence:** HIGH

### D2: Pattern Notation `[NNN]` and `*`

**Choice:** Simple bracket notation for sequence markers and asterisk for wildcards
**Reasoning:** The target users are accountants who understand `*` as "anything" from Excel but would not understand regex syntax. The `[NNN]` notation is intuitive — "put the number part in brackets." The HANDOVER.md confirms alternatives (visual picker, auto-only) were rejected for being too complex or too limiting.
**Confidence:** HIGH

### D3: Original Invoice Strings for From/To Display

**Choice:** Store and display the actual pasted invoice strings, not reconstructed ones
**Reasoning:** This was a bug fix (Bug #2 in HANDOVER.md). Reconstructing invoices from pattern + sequence caused padding bugs (e.g., displaying `19CA25/067` when user pasted `19CA25/67`). Using originals eliminates this entire class of bugs.
**Confidence:** HIGH

### D4: Non-greedy Wildcards `.*?` (Zero or More)

**Choice:** Wildcards match zero or more characters with `.*?` instead of one or more with `.+?`
**Reasoning:** This was a bug fix (Bug #1 in HANDOVER.md). The original `.+?` forced wildcards to consume at least one character, which stripped leading digits from adjacent fixed text. Changing to `.*?` fixed the issue.
**Confidence:** HIGH

### D5: Modular Architecture (core/ui/utils separation)

**Choice:** Three-layer architecture separating business logic, UI, and utilities
**Reasoning:** Clean separation enables unit testing of core logic without PyQt5. All 43 tests only import from `src/core/`, never from `src/ui/`. This also enables future migration to a different UI framework (e.g., web) without changing business logic.
**Confidence:** HIGH

### D6: Deferred Import of openpyxl

**Choice:** `import openpyxl` inside `read_gstr1_excel()` function, not at module top level
**Reasoning:** openpyxl is only needed when reading Excel files. By deferring the import, the application starts and runs fine even without openpyxl installed — only the Excel features fail gracefully. This is consistent with the optional nature of Step 4 in the UI.
**Confidence:** HIGH

### D7: `re` Imported Inside Function Bodies in `excel_reader.py` and `continuity_checker.py`

**Choice:** `import re` appears inside 5 different functions rather than at module top level
**Reasoning:** Likely an artifact of AI-assisted development where functions were added incrementally in separate conversation turns. Not a deliberate design choice.
**Confidence:** MEDIUM (pattern inconsistency — `pattern_parser.py`, `invoice_processor.py`, and `pattern_detector.py` all import `re` at the top level)

### D8: Expand/Collapse Button vs. Always-Show Table

**Choice:** Table starts in compact mode (max 200px height) with "Show All Rows" button
**Reasoning:** HANDOVER.md explicitly states: "User explicitly requested toggle, not drag." A splitter was tried and rejected. The compact default prevents the table from dominating the output when there are many series.
**Confidence:** HIGH

### D9: `SCROLLBAR_STYLE` Defined Inline vs. Using `styles.py`

**Choice:** Scrollbar styles defined as a constant in `main_window.py:23` and duplicated in `input_panel.py:42` and `output_panel.py:38`, rather than imported from `styles.py`
**Reasoning:** The `styles.py` module was originally a large stylesheet module (408 lines in commit `7ebf5e5`) but was stripped down to just a `COLORS` dict in commit `672a65a` when the UI was redesigned. The inline styles replaced it but `styles.py` was never deleted. This is incomplete refactoring, not intentional design.
**Confidence:** HIGH

### D10: FY-Aware Continuity Checking

**Choice:** Filter previous series to same Financial Year only before comparing
**Reasoning:** Per Rule 46 of CGST Rules 2017, invoice numbers must be unique within a financial year but may reset at FY boundaries. Comparing across FY boundaries would produce false "gap" warnings. Added in the last commit (`e650cc5`).
**Confidence:** HIGH

### Pattern Consistency Check

| Pattern | Established In | Applied Consistently? |
|---------|---------------|----------------------|
| Mutable defaults use `field(default_factory=list)` | `models.py` | ✅ Yes — all list defaults use this pattern |
| Module-level `re.compile()` for reused regex | `pattern_parser.py:29,32` | ❌ No — `validators.py:27` recompiles the same regex every call |
| `re` imported at module top level | `pattern_parser.py:20`, `invoice_processor.py:8`, `pattern_detector.py:11` | ❌ No — `excel_reader.py` and `continuity_checker.py` import `re` inside functions |
| Try/except for openpyxl import | `excel_reader.py:49` | ✅ Yes — only one file uses openpyxl |
| Dataclasses for data models | `models.py`, `excel_reader.py:14`, `continuity_checker.py:15` | ✅ Yes — consistent |
| Convenience function wrapping class usage | `parse_pattern()`, `process_invoices()`, `analyze_invoices()` | ✅ Yes — consistent pattern in all core modules |
| `__all__` list in `__init__.py` | `src/core/__init__.py:23` | ❌ Partially — only `core` has `__all__`; `ui` and `utils` don't |

---

## SECTION 9: DEPENDENCIES AND ENVIRONMENT

### External Libraries

| Library | Version Constraint | Purpose | Required? |
|---------|-------------------|---------|-----------|
| PyQt5 | >=5.15.0 | Desktop GUI framework | YES |
| PyQt5-Qt5 | >=5.15.0 | Qt5 runtime (auto-installed with PyQt5) | YES |
| PyQt5-sip | >=12.11.0 | SIP bindings (auto-installed with PyQt5) | YES |
| openpyxl | >=3.0.0 | Excel file reading (.xlsx) | OPTIONAL (only for Step 4) |

> **Note:** `requirements.txt` lists `openpyxl>=3.0.0` twice (lines 2 and 5). This is harmless but messy.

### Python Version

- **Minimum:** Python 3.8+ (uses f-strings, `dataclasses`, `typing`)
- **Tested on:** Python 3.12 and 3.13 (evidenced by `__pycache__` files containing both `.cpython-312.pyc` and `.cpython-313.pyc`)

### OS-Specific Concerns

| Concern | Details |
|---------|---------|
| Font | `Segoe UI` is Windows-only; will fall back to system default on Linux/Mac |
| `run_template.bat` | Windows batch file; irrelevant on Linux/Mac |
| High DPI | `Qt.AA_EnableHighDpiScaling` enabled in `main.py:24` — works on all platforms |
| Path handling | Uses `os.path` throughout — cross-platform compatible |
| Line endings | Explicitly handled (`\r\n` → `\n`) in `invoice_processor.py:145` |

### Setup Steps (Fresh Machine)

```bash
# 1. Install Python 3.8+
# 2. Clone or download the project
# 3. Install dependencies:
pip install PyQt5>=5.15.0 openpyxl>=3.0.0
# Or:
pip install -r requirements.txt
# 4. Run:
python main.py
```

### OS-Specific Import Handling

No OS-specific modules are used (no `win32com`, `winreg`, `ctypes`, etc.). All imports are cross-platform.

---

## SECTION 10: UI/INTERFACE DOCUMENTATION

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Sahaj — Table 13 Generator     UI Scale: [100% ▼]   drag hint │  ← Dark header (#1e293b)
├─────────────────────────┬───────────────────────────────────────┤
│                         │                                       │
│   INPUT PANEL           │   OUTPUT PANEL                        │
│   (scrollable)          │   (scrollable)                        │
│                         │                                       │
│   ① Document Type       │   Results                             │
│   [Dropdown ▼]          │   ┌────┐ ┌────┐ ┌────┐ ┌────┐       │
│                         │   │  0 │ │  0 │ │  0 │ │  0 │        │
│   ② Invoice Format      │   │Tot │ │Mat │ │Can │ │Ser │        │
│   [Pattern field    ]   │   └────┘ └────┘ └────┘ └────┘        │
│   [🔍 Auto-Detect]     │                                       │
│   Examples: ...         │   Table 13 Output     [▼ Show All]   │
│                         │   ┌─────┬──────┬──────┬───┬───┬───┐  │
│   ③ Invoice List        │   │Type │From  │To    │Tot│Can│Net│  │
│   ┌─────────────────┐   │   ├─────┼──────┼──────┼───┼───┼───┤  │
│   │                 │   │   │...  │...   │...   │...│...│...│  │
│   │ Paste invoices  │   │   └─────┴──────┴──────┴───┴───┴───┘  │
│   │ here            │   │   [Copy for Excel]                    │
│   │                 │   │                                       │
│   └─────────────────┘   │   ⚠ Warnings                         │
│   0 invoices            │   [Yellow box with warning text]      │
│                         │                                       │
│   ④ Previous GSTR-1     │   Cancelled/Missing     [Copy]       │
│   Current Tax Period:   │   [Red box with missing numbers]      │
│   [March 2026 ▼]       │                                       │
│   [No file selected]   │   📋 Continuity Check                  │
│   [Browse...] [✕]      │   [Blue box with continuity results]  │
│                         │                                       │
│   [Generate Table 13]   │                                       │
│   [Clear]               │                                       │
│                         │                                       │
├─────────────────────────┴───────────────────────────────────────┤
│  Ready                                                          │  ← Status bar
└─────────────────────────────────────────────────────────────────┘
```

### Widget Inventory

| Widget | Type | Location | Action |
|--------|------|----------|--------|
| "Sahaj" title | QLabel | Header | Display only |
| "— Table 13 Generator" subtitle | QLabel | Header | Display only |
| UI Scale dropdown | QComboBox | Header | Changes scale 75–110% |
| Drag hint text | QLabel | Header | Display only |
| Document Type dropdown | QComboBox | Input Step 1 | Selects from 12 document types |
| Invoice Format field | QLineEdit | Input Step 2 | Monospace font, placeholder text |
| "🔍 Auto-Detect" button | QPushButton | Input Step 2 | Runs pattern detection |
| Pattern feedback label | QLabel | Input Step 2 | Shows ✓ Valid / ✗ Error |
| Invoice List text area | QPlainTextEdit | Input Step 3 | Monospace, placeholder examples |
| Line count label | QLabel | Input Step 3 | Shows "N invoices" |
| Tax Period dropdown | QComboBox | Input Step 4 | 24 months, newest first |
| File path label | QLabel | Input Step 4 | Shows filename or "No file selected" |
| "Browse..." button | QPushButton | Input Step 4 | Opens file dialog |
| "✕" clear file button | QPushButton | Input Step 4 | Clears loaded file |
| File status label | QLabel | Input Step 4 | Shows ✓ Found N series / ✗ Error |
| "Generate Table 13" button | QPushButton | Input bottom | Primary action (blue, bold) |
| "Clear" button | QPushButton | Input bottom | Resets all fields |
| Stats cards (×4) | Custom QWidget | Output top | Total, Matched, Cancelled, Series |
| Results table | QTableWidget | Output middle | 6 columns, resizable, selectable |
| "▼ Show All Rows" button | QPushButton | Output | Toggles table expand/collapse |
| "Copy for Excel" button | QPushButton | Output | Copies TSV to clipboard |
| Warnings section | QLabel | Output | Yellow background |
| Missing section | QTextEdit | Output | Red background, with Copy button |
| Unmatched section | QTextEdit | Output | Gray background |
| Continuity section | QTextEdit | Output | Blue background, HTML content |
| Status bar | QStatusBar | Bottom | Shows "Ready", "Processing...", results summary |

### Typical User Workflow

1. Select document type from dropdown (defaults to "Invoices for outward supply")
2. **Either** type an invoice pattern manually **or** paste invoices first and click "Auto-Detect"
3. Paste invoice numbers from Tally/Excel (one per line) into the text area
4. **(Optional)** Browse for previous month's GSTR-1 file and select current tax period
5. Click **"Generate Table 13"**
6. Review results: stats, table, warnings, missing invoices, continuity
7. Click **"Copy for Excel"** to copy Table 13 to clipboard
8. Paste into Excel or GST Portal

### Color Scheme

- Primary blue: `#2563eb` (Generate button)
- Dark header: `#1e293b`
- Success green: `#16a34a`
- Error red: `#dc2626`
- Warning amber: `#b45309` / `#fef3c7`
- Neutral gray: `#6b7280` / `#9ca3af`
- Continuity blue: `#1e40af` / `#eff6ff`

---

## SECTION 11: RECONSTRUCTION BLUEPRINT

### 1. Foundation

```
Step 1: Create project structure (src/core, src/ui, src/utils, tests)
Step 2: pip install PyQt5 openpyxl pytest
Step 3: Create models.py with all dataclasses
```

### 2. Core Logic Build Order

```
1. models.py          — Data classes (no dependencies)
2. pattern_parser.py  — Depends on models
3. invoice_processor.py — Depends on models, pattern_parser
4. series_analyzer.py  — Depends on models, invoice_processor
5. fy_utils.py         — Standalone (no internal dependencies)
6. pattern_detector.py — Standalone (no internal dependencies)
7. excel_reader.py     — Standalone (uses openpyxl)
8. continuity_checker.py — Depends on excel_reader, models, fy_utils
```

### 3. Feature Priority

| Priority | Feature | Complexity |
|----------|---------|------------|
| 1 (Essential) | Pattern parsing (F1) | SIMPLE |
| 2 (Essential) | Invoice processing & grouping (F2) | MODERATE |
| 3 (Essential) | Series analysis & Table 13 output (F3) | MODERATE |
| 4 (Essential) | Copy to clipboard (F9) | SIMPLE |
| 5 (Important) | Basic UI with input/output panels | COMPLEX |
| 6 (Important) | Pattern auto-detection (F4) | MODERATE |
| 7 (Nice-to-have) | Excel reader (F5) | MODERATE |
| 8 (Nice-to-have) | Continuity checking (F6) | MODERATE |
| 9 (Nice-to-have) | FY utilities (F7) | SIMPLE |
| 10 (Nice-to-have) | UI scaling (F8) | COMPLEX |

### 4. Known Improvements for Rebuild

1. **Fix `_detect_pattern_with_wildcards` variable leak** — use a local variable inside the inner loop instead of modifying `num_end` from the outer scope. See Section 7.1.

2. **Replace bare `except:` with `except Exception:`** — in `continuity_checker.py:53`. Simple one-line fix.

3. **Remove dead code** — delete `styles.py`, remove unused functions from `validators.py`, `formatters.py`, and `fy_utils.py`. This reduces maintenance burden without losing functionality.

4. **Consolidate `re` imports** — move all `import re` statements to module top level for consistency across `excel_reader.py` and `continuity_checker.py`.

5. **Consolidate month-name mappings** — `excel_reader.py:196-209` and `fy_utils.py:99-102,127-131` both define month name→number mappings. Extract to a shared constant.

6. **Add input size limit** — before processing, check `count_lines(text) > 50000` and warn the user, or move processing to a `QThread` for large datasets to prevent UI freezing.

7. **Implement `ignore_leading_zeros`** — either implement the feature or remove the parameter and `get_ignore_leading_zeros()` stub to avoid confusion.

8. **Deduplicate `requirements.txt`** — `openpyxl>=3.0.0` appears twice.

9. **Fix `run_template.bat`** — either restore the file to disk or remove it from git tracking.

> **Note on D4 (non-greedy wildcards):** The current `.*?` approach was chosen specifically to fix Bug #1 where `.+?` stripped leading digits. Do NOT revert to `.+?` — the fix is correct. The tradeoff (adjacent wildcards are ambiguous) is acceptable since the scenario is rare and documented in HANDOVER.md.

### 5. Estimated Complexity (AI-Assisted Rebuild)

| Component | Time Estimate |
|-----------|--------------|
| Models + Pattern Parser | SIMPLE (< 1 hour) |
| Invoice Processor | SIMPLE (< 1 hour) |
| Series Analyzer | MODERATE (1-3 hours) |
| Pattern Detector | MODERATE (1-3 hours) |
| Excel Reader + Continuity | MODERATE (1-3 hours) |
| FY Utilities | SIMPLE (< 1 hour) |
| UI (full, with scaling) | COMPLEX (3+ hours) |
| Tests | MODERATE (1-3 hours) |
| **Total** | **~8-15 hours** |

### 6. Suggested Claude Code Skills

| Feature | Skill Description |
|---------|-------------------|
| Pattern → Regex conversion | "Given a user-friendly notation with `[NNN]` for sequences and `*` for wildcards, generate a Python regex with named capture groups" |
| Excel column auto-detection | "Given an openpyxl worksheet, find the header row by searching for known column names in the first N rows, return column indices" |
| PyQt5 scalable UI | "Create a PyQt5 widget with an `apply_scale(float)` method that proportionally adjusts all font sizes, padding, border radii, and widget dimensions" |
| Indian FY calculation | "Given a date or MMYYYY string, determine Indian Financial Year (April–March)" |

---

## SECTION 12: CHANGELOG ARCHAEOLOGY (FROM GIT HISTORY)

> **Branch awareness:** All 17 commits are on the `main` branch. No feature branches, no unmerged branches. The project has a linear history.

### 12A. Complete Development Timeline

#### Phase 1: Initial Scaffold (Dec 10, 2025, 00:39–00:41)

**Commit `7ebf5e5` — 2025-12-10 00:39:32 — "Update: Replace old files with new files"**
- **What changed:** 23 files added, 3,869 lines. Complete project structure created: models, pattern_parser, invoice_processor, series_analyzer, input_panel, main_window, output_panel, styles (408 lines!), validators, formatters, tests (all 3), .gitignore, CLAUDE.md, README.md, requirements.txt.
- **Why:** Initial code generation. The commit message "Replace old files" suggests this was a fresh start replacing an earlier attempt (possibly in the same or different directory).
- **Reveals:** The entire core architecture was generated in one shot. The original `styles.py` was 408 lines (a full stylesheet module), much larger than the 20-line version that exists now.

**Commit `940f3bd` — 2025-12-10 00:41:34 — "Update: Remove shebang line from main.py"**
- **What changed:** 1 file, 1 line — removed `#!/usr/bin/env python3` from `main.py`.
- **Why:** User requested no shebang (Windows-primary application doesn't need it). HANDOVER.md confirms this.
- **Reveals:** Quick user feedback cycle — 2 minutes after initial commit.

#### Phase 2: UI Redesign — "Technical to Layman" (Dec 10, 2025, 00:51–01:05)

**Commit `672a65a` — 2025-12-10 00:51:39 — "Refactor UI components and styles for Sahaj - Table 13 Generator"**
- **What changed:** 6 files, massive UI rewrite. `styles.py` went from 408→20 lines (stripped from full stylesheet module to just COLORS dict). `input_panel.py`, `main_window.py`, `output_panel.py` heavily rewritten. README updated. `main.py` simplified (removed QIcon import).
- **Why:** First major redesign from a technical interface to a "layman-friendly wizard" with numbered steps. The app was renamed/branded as "Sahaj" (Sanskrit for "simple").
- **Reveals:** The original AI-generated UI was too technical. This commit is where the identity of the app solidified. The `styles.py` gutting happened here but it was never deleted — the beginning of the dead code.

**Commit `11c07c6` — 2025-12-10 01:05:13 — "Refactor: Improve code structure and organization across UI components"**
- **What changed:** 3 UI files, net -274 lines. Significant cleanup and simplification of input_panel, main_window, output_panel.
- **Why:** Code was over-engineered from the initial generation. This commit trimmed excess styling, simplified layouts, and reduced duplication.
- **Reveals:** Iterative refinement — the AI generated too much code initially, then trimmed it.

#### Phase 3: Responsiveness & Interaction Fixes (Dec 10, 2025, 08:09–15:20)

**Commit `a1c75d1` — 2025-12-10 08:09:39 — "Refactor: Update UI components for improved responsiveness and scrollbar visibility"**
- **What changed:** 3 UI files. Added visible scrollbars (14px width), QSplitter for resizable panels, minimum widths instead of fixed sizes, screen-based default sizing.
- **Why:** The original layout was rigid and scrollbars were invisible. User needed resizable panels.
- **Reveals:** Real-world usability testing — scrollbars that blend into the background are a common complaint.

**Commit `3451337` — 2025-12-10 08:30:50 — "Refactor: Update pattern parser and series analyzer for improved wildcard handling and padding detection"**
- **What changed:** 5 files. **Critical fixes:** wildcard regex changed from `.+?` to `.*?` (Bug #1 fix), padding detection logic added to series_analyzer, main_window updated to pass results correctly, test updated.
- **Why:** Bugs discovered during real-world testing with Indian invoice formats. The leading-zero stripping bug and forced-padding bug were both found here.
- **Reveals:** This is where the tool was tested with actual Indian invoice data (like `GTS/001/24-25` and `19CA25/67`). The padding logic was completely rethought.

**Commit `ad77edc` — 2025-12-10 08:43:18 — "Refactor: Enhance output panel with resizable table and improved section organization"**
- **What changed:** `output_panel.py` major update — resizable columns (Interactive mode), cell selection, initial expand/collapse button. README expanded significantly (+268 lines).
- **Why:** User wanted to resize table columns to see full invoice numbers.

**Commit `53495a1` — 2025-12-10 08:55:43 — "Refactor: Update output panel for improved table expansion and scrolling behavior"**
- **What changed:** `output_panel.py` restructured — content flows in a scrollable area, table expand/collapse refined.
- **Why:** The table expansion logic wasn't working correctly with the scrollable layout.

**Commit `640ffdf` — 2025-12-10 14:49:07 — "Refactor: Improve table expansion logic and scrollbar behavior"**
- **What changed:** `output_panel.py`, 14 additions, 5 deletions. Fixed table height calculation to use actual row heights instead of hardcoded 35px.
- **Why:** Bug #3 fix — "Show All Rows" button wasn't actually showing all rows because the height calculation was wrong.
- **Reveals:** The gap between 08:55 and 14:49 suggests the user tested the app, found the bug, and came back.

**Commit `d603fc6` — 2025-12-10 15:20:02 — "Refactor: Enhance output panel with improved cell selection and context menu"**
- **What changed:** `output_panel.py`, +64 lines. Added `eventFilter()` for Ctrl+C, right-click context menu with "Copy Selected" and "Copy All Rows", changed selection mode from SelectRows to SelectItems with ExtendedSelection.
- **Why:** Bug #6 fix — user couldn't copy specific cells, only entire rows. This was the last commit of the first development session.

#### Phase 4: New Features — Auto-Detect, Excel, Continuity (Jan 5–6, 2026)

**Commit `1ff5d7b` — 2026-01-05 13:06:23 — "Refactor: Add run_template.bat for streamlined execution"**
- **What changed:** Added `run_template.bat` (5 lines) and updated `.gitignore` to exclude `run.bat`.
- **Why:** User wanted a batch file template for running the app. The template uses a placeholder path, and the user would customize it for their setup.
- **Reveals:** The 26-day gap (Dec 10 → Jan 5) suggests the user was satisfied with v1 and returned with new requirements.

**Commit `5d68323` — 2026-01-05 22:02:00 — "feat: Enhance Input Panel with Auto-Detect, Manual Pattern, and Previous GSTR-1 Upload"**
- **What changed:** 10 files, +1,148 lines. Three entirely new modules: `pattern_detector.py` (353 lines), `excel_reader.py` (285 lines), `continuity_checker.py` (125 lines). Major updates to `input_panel.py` (added Steps 2 and 4 UI), `output_panel.py` (added continuity section), `main_window.py` (connected continuity checking), `core/__init__.py` (added new exports). `series_analyzer.py` refactored. `requirements.txt` updated to add openpyxl.
- **Why:** User requested three new features in this session: auto-detect patterns, upload previous GSTR-1 for continuity checking, and compare series across periods.
- **Reveals:** This is the biggest single commit — an entire feature expansion implemented in one session. The `series_analyzer.py` changes also rewrote the analyze_series method to use original strings and detect padding.

**Commit `531ffdd` — 2026-01-05 22:08:25 — "Refactor: Update file validation and sheet name handling"**
- **What changed:** 2 files, minor fixes. Excel reader filename validation and sheet name search order adjusted. Input panel file filter updated.
- **Why:** Quick fix after testing the Excel reader feature.

**Commit `c1bd20f` — 2026-01-06 08:00:15 — "Refactor: Change Python execution to use pythonw"**
- **What changed:** `run_template.bat`, 1 line — `python` → `pythonw`.
- **Why:** `pythonw` runs Python without showing a console window. Better for a desktop app.

#### Phase 5: UI Scaling & Polish (Jan 6, 2026)

**Commit `f02b65b` — 2026-01-06 11:33:10 — "feat: Implement UI scaling functionality"**
- **What changed:** 3 UI files, +470 lines. Added `apply_scale()` method to both panels, scale dropdown in header, `_on_scale_changed()` handler.
- **Why:** User wanted the ability to adjust UI size for different screen resolutions or preferences.
- **Reveals:** Significant amount of code (470 lines) is just scaling logic — updating stylesheets with multiplied values. This is inherently verbose with Qt's stylesheet approach.

**Commit `07859fd` — 2026-01-06 13:13:33 — "feat: Enhance Input and Output Panels with dynamic label scaling"**
- **What changed:** 3 UI files. Step labels now scale, header elements scale, stat boxes scale.
- **Why:** Follow-up to scaling — labels and stat boxes were missed in the first pass.

**Commit `e650cc5` — 2026-01-06 15:26:24 — "feat: Add multi-period GSTR-1 support with FY-aware continuity checking"**
- **What changed:** 6 files, +514 lines. New module `fy_utils.py` (199 lines). `continuity_checker.py` heavily rewritten (+91 lines) to support FY boundaries, discontinued series detection, and 4-color status coding. `excel_reader.py` updated with tax period parsing. `input_panel.py` got tax period dropdown. `output_panel.py` got 4-color HTML continuity display with legend.
- **Why:** The initial continuity checker didn't respect FY boundaries. When a new financial year starts in April, invoice series often reset to 1 — the old checker would flag this as a massive gap. This commit adds FY awareness.
- **Reveals:** This is the most domain-sophisticated commit, implementing Rule 46 compliance. The 4-color status system (green=continuous, red=gap, blue=new, purple=discontinued) shows careful UX thinking.

### 12B. File Evolution Map

| File | Created | Major Changes | Current State |
|------|---------|---------------|---------------|
| `main.py` | `7ebf5e5` (Dec 10) | Shebang removed (`940f3bd`), simplified (`672a65a`) | Stable since Dec 10 |
| `models.py` | `7ebf5e5` (Dec 10) | Added `duplicate_count` field (`5d68323`) | Stable since Jan 5 |
| `pattern_parser.py` | `7ebf5e5` (Dec 10) | Wildcard `.*?` fix (`3451337`) | Stable since Dec 10 |
| `invoice_processor.py` | `7ebf5e5` (Dec 10) | No significant changes | Stable since creation |
| `series_analyzer.py` | `7ebf5e5` (Dec 10) | Major rewrite for padding detection (`3451337`, `5d68323`) | Stable since Jan 5 |
| `pattern_detector.py` | `5d68323` (Jan 5) | Created in single commit | Stable since creation |
| `excel_reader.py` | `5d68323` (Jan 5) | Sheet name fix (`531ffdd`), tax period parsing (`e650cc5`) | Stable since Jan 6 |
| `continuity_checker.py` | `5d68323` (Jan 5) | Major rewrite for FY awareness (`e650cc5`) | Stable since Jan 6 |
| `fy_utils.py` | `e650cc5` (Jan 6) | Created in single commit | Stable since creation |
| `main_window.py` | `7ebf5e5` (Dec 10) | Redesigned (`672a65a`, `11c07c6`), splitter added (`a1c75d1`), scaling (`f02b65b`, `07859fd`) | Stable since Jan 6 |
| `input_panel.py` | `7ebf5e5` (Dec 10) | Redesigned (`672a65a`, `11c07c6`), auto-detect+Excel (`5d68323`), scaling (`f02b65b`, `07859fd`), tax period (`e650cc5`) | Stable since Jan 6 |
| `output_panel.py` | `7ebf5e5` (Dec 10) | Most changed file: redesigned, resizable table, expand/collapse, cell copy, context menu, continuity display, scaling | Stable since Jan 6 |
| `styles.py` | `7ebf5e5` (Dec 10, 408 lines) | Gutted to 20 lines (`672a65a`) | Dead code since Dec 10 |
| `validators.py` | `7ebf5e5` (Dec 10) | No changes | Stable since creation |
| `formatters.py` | `7ebf5e5` (Dec 10) | No changes | Stable since creation |
| `tests/*.py` | `7ebf5e5` (Dec 10) | Minor test update (`3451337`) | Stable since Dec 10 |

### 12C. Logic and Rule Evolution

| Rule | First Appearance | Changes | Current State |
|------|-----------------|---------|---------------|
| Pattern notation `[NNN]` | `7ebf5e5` (initial) | None | Foundational, unchanged |
| Wildcard `*` matching | `7ebf5e5` (initial) | Changed from `.+?` to `.*?` in `3451337` | Fixed, stable |
| Padding detection | `3451337` (Dec 10) | Refined in `5d68323` (Jan 5) | Stable |
| Original strings for From/To | `3451337` (Dec 10) | Was reconstruction-based before | Fixed, stable |
| Warning thresholds (20%, 50) | `7ebf5e5` (initial) | None | Unchanged |
| Table 13 column structure | `7ebf5e5` (initial) | None | Unchanged |
| FY-aware continuity | `e650cc5` (Jan 6) | Added in last commit | New, stable |
| Year-skipping in sequence detection | `5d68323` (Jan 5) | None since introduction | Stable |

**Key insight:** The pattern matching and padding rules were discovered through real-world testing. The initial implementation was "correct" in theory but broke on actual Indian invoice formats with mixed padding and year codes.

### 12D. Edge Cases Discovered in Production

| Commit | What Broke | Fix | Related Unhandled Cases |
|--------|-----------|-----|------------------------|
| `3451337` | Leading zeros stripped by `.+?` wildcard regex | Changed to `.*?` (zero-or-more) | Adjacent wildcards still ambiguous (documented, accepted) |
| `3451337` | Unpadded series forced to padded display | Added `is_padded` detection based on actual data | Mixed padding in same series not tested |
| `640ffdf` | "Show All Rows" didn't show all rows | Calculate actual height from `rowHeight()` sum | None identified |
| `d603fc6` | Can't copy individual cells | Added SelectItems mode, Ctrl+C handler, context menu | None identified |
| `531ffdd` | Excel sheet name matching too strict | Added multiple case variants + fallback to active sheet | Custom sheet names still may not match |
| `e650cc5` | Continuity flagged false gaps at FY boundary | Added FY filtering with `are_same_fy()` | Year change handling for continuity still marked as open question |

### 12E. Abandoned Approaches and Reversals

| What Was Tried | When | What Replaced It | Why |
|---------------|------|-------------------|-----|
| Full stylesheet module (`styles.py`, 408 lines) | `7ebf5e5` | Inline stylesheets in each UI file | The centralized approach was too rigid; inline styles allowed per-component customization. The old `styles.py` was gutted in `672a65a` but never deleted. |
| Invoice reconstruction for From/To display | `7ebf5e5` | Using original invoice strings | Reconstruction caused padding bugs (Bug #2). Keeping originals is simpler and correct. |
| Greedy wildcards (`.+?`) | `7ebf5e5` | Non-greedy zero-or-more (`.*?`) | `.+?` consumed at least one character, stripping leading digits from adjacent parts. |
| Hardcoded table row height (35px) | `ad77edc` | Actual `rowHeight()` calculation | Hardcoded value didn't match actual heights with different content. |
| SelectRows selection mode | Before `d603fc6` | SelectItems with ExtendedSelection | Users needed cell-level copy, not row-level. |
| Simple continuity (no FY awareness) | `5d68323` | FY-filtered continuity | False gap warnings at April boundaries. |

**Dead code remnants still in codebase:**
- `styles.py` — entire file is dead (20 lines)
- Multiple unused functions in `validators.py`, `formatters.py`, `fy_utils.py` — see Section 2 for full list
- `ignore_leading_zeros` parameter — stubbed but never implemented

### 12F. Dependency Evolution

| When | Change | Why |
|------|--------|-----|
| `7ebf5e5` (initial) | `requirements.txt` created: `PyQt5>=5.15.0` | Core dependency for GUI |
| `5d68323` (Jan 5) | Added `openpyxl>=3.0.0`, `PyQt5-Qt5>=5.15.0`, `PyQt5-sip>=12.11.0` | openpyxl for Excel reading; PyQt5 sub-packages made explicit |
| — | `openpyxl>=3.0.0` duplicated (appears on lines 2 and 5) | Copy-paste error, harmless |

**Dependencies used but not in requirements.txt:** None — all imports are from stdlib (`sys`, `os`, `re`, `datetime`, `typing`, `dataclasses`, `enum`, `collections`) or from the two listed packages.

**Dependencies in requirements.txt but not used:** `PyQt5-Qt5` and `PyQt5-sip` are automatically installed with `PyQt5` — listing them explicitly is redundant but not harmful.

---

## Self-Consistency Review

This section documents corrections found during the mandatory self-review.

1. **Section 2 vs Section 12E:** Section 2 correctly identifies `styles.py` as dead code. Section 12E confirms it was gutted in commit `672a65a`. Consistent.

2. **Section 3 (Feature F4) vs Section 7.1 (Bug):** F4 describes auto-detection as working correctly for the traced example. Section 7.1 identifies a bug in `_detect_pattern_with_wildcards` that affects multi-structure invoices. These are consistent — F4's traced example goes through `_analyze_invoices` (the simple path), not `_detect_pattern_with_wildcards` (the complex path where the bug lives).

3. **Section 5 (R2) vs actual code:** Series key construction uses `''.join(key_parts)` where the `{SEQ}` placeholder is included. The HANDOVER.md mentions `||` separators, but the actual code at `invoice_processor.py:104` uses simple concatenation with `{SEQ}`. [Corrected during self-review — HANDOVER.md's description of `||` separators is inaccurate; the actual code uses direct string concatenation with `{SEQ}` as a placeholder.]

4. **Section 8 (D9) vs Section 2:** D9 claims styles are duplicated across three files. Verified: `main_window.py:23-60` defines `SCROLLBAR_STYLE`, `input_panel.py:42-61` defines its own scrollbar styles inline, `output_panel.py:38-60` defines similar scrollbar styles inline. These are slightly different (main window uses 14px width, panels use 12px width). This is intentional differentiation, not exact duplication. [Corrected during self-review — the scrollbar styles are similar but not identical across files; the panel scrollbars are narrower (12px) than the main window scrollbars (14px).]

5. **HANDOVER.md claims "41 tests passing":** The test files contain 17 + 13 + 13 = 43 test methods. The HANDOVER.md count of 41 may reflect an earlier state before the test update in commit `3451337`. The FILE_INDEX.md claims "18 tests" for pattern parser and "11 tests" for invoice processor and "12 tests" for series analyzer, totaling 41 — but the actual counts are 17, 13, and 13 = 43. [Corrected during self-review — the documentation is outdated; the actual test count is 43, not 41.]

6. **Section 12B claims `validators.py` and `formatters.py` had "No changes":** Verified against git history — these files were indeed created in `7ebf5e5` and never modified in any subsequent commit. Their current content matches the initial commit. Consistent.

7. **All shared state verified:** The only shared state is the clipboard (written by output_panel, read by external applications). No files, caches, configs, or temp files are written. The `_previous_series` list in `input_panel.py` is written by `_load_previous_gstr1()` (line 446) and read by `get_previous_series()` (line 563) — both in the same class. Consistent.

---

*End of PROJECT_AUDIT_DOC_ISSUED.md*
