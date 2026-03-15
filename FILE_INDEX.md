# FILE_INDEX.md — Sahaj GSTR-1 Table 13 Generator

## Project Files Overview

Every file in this project, with accurate description of actual behavior and current status.

---

## Root Directory

| File | Description | Status |
|------|-------------|--------|
| `main.py` | Application entry point. Creates QApplication, enables high-DPI scaling, sets Segoe UI 11pt font, instantiates MainWindow, and runs the Qt event loop. No shebang (removed per user request). | ✅ Complete |
| `requirements.txt` | Lists dependencies: `PyQt5>=5.15.0` and `openpyxl>=3.0.0` (openpyxl added for Excel reading) | ✅ Complete |
| `README.md` | User documentation. Covers installation, usage, pattern syntax with examples, interface guide, output format, warnings explained, project structure. Written for end users (accountants), not developers. | ✅ Complete |
| `CLAUDE.md` | Developer notes from an earlier session. Contains project overview, architecture decisions, and implementation notes. May be outdated — use HANDOVER.md for current state. | ⚠️ May be outdated |
| `.gitignore` | Standard Python gitignore (pycache, venv, IDE files) | ✅ Complete |

---

## src/core/ — Business Logic

| File | Description | Status |
|------|-------------|--------|
| `__init__.py` | Package init. Exports: DocumentNature, ParsedPattern, ParsedInvoice, SeriesAnalysis, ProcessingResult, Table13Row, PatternParser, parse_pattern, InvoiceProcessor, process_invoices, SeriesAnalyzer, analyze_invoices, detect_pattern, read_gstr1_excel, PreviousSeriesInfo, check_continuity, ContinuityResult, format_continuity_report. | ✅ Complete |
| `models.py` | Data classes using Python dataclasses. Contains: `DocumentNature` (Enum with 12 GST document types), `ParsedPattern` (parts list, wildcard_count, sequence_length, regex_pattern, is_valid), `ParsedInvoice` (raw, sequence_number, sequence_str, wildcard_values, series_key), `SeriesAnalysis` (start/end numbers, missing_invoices, warnings), `ProcessingResult` (series_results, unmatched, statistics), `Table13Row` (nature_of_document, sr_no_from, sr_no_to, total_number, cancelled, net_issued with to_list() and to_tsv() methods). | ✅ Complete |
| `pattern_parser.py` | Converts user pattern notation to regex. Class `PatternParser` with `parse(pattern_str)` method. Handles: `[NNN]` → `(?P<seq>\d+)`, `*` → `(?P<wcN>.*?)`. Also has `parse_pattern(pattern_str)` convenience function. Escapes special regex chars in fixed parts. Validates pattern structure. Line 173 uses `.*?` (zero-or-more, non-greedy) for wildcards — was `.+?` before bug fix. | ✅ Complete |
| `invoice_processor.py` | Matches invoices against pattern regex. Class `InvoiceProcessor` with `process_text_input(text)` and `parse_invoice(line)` methods. Groups invoices by `series_key` (constructed from fixed parts + wildcard values joined with `\|\|` separator). Returns tuple: (series_groups dict, unmatched list, invalid list). Also has `reconstruct_invoice()` and `get_series_display_name()` helper methods. | ✅ Complete |
| `series_analyzer.py` | Analyzes each series to produce statistics. Class `SeriesAnalyzer` with `analyze_series(series_key, invoices)` and `analyze_all_series(...)` and `to_table13_rows(result)` methods. Key logic: detects padded vs unpadded series by checking if any `sequence_str` starts with '0'. Uses ORIGINAL invoice strings for From/To (not reconstructed). Generates warnings for >20% cancellation or >50 gap. Returns `ProcessingResult`. | ✅ Complete (bug fixed) |
| `pattern_detector.py` | Auto-detects pattern from invoice list. Main function `detect_pattern(invoices)` returns `(pattern, message)`. Logic: splits invoices into text/numeric parts, finds which numeric part varies (the sequence), detects padding, builds pattern string. For multi-series, uses `_detect_pattern_with_wildcards()` for character-by-character analysis. Returns confidence percentage. | ✅ Complete |
| `excel_reader.py` | Reads previous GSTR-1 Excel files. Main function `read_gstr1_excel(filepath)` returns `(list[PreviousSeriesInfo], message)`. Validates filename starts with "GSTR1-Portal-". Looks for "Doc Issued" sheet. Finds columns: Doc Type, From, To, Total, Cancelled. Extracts prefix/suffix from invoice numbers for later matching. Dataclass `PreviousSeriesInfo` stores doc_type, from_invoice, to_invoice, prefix, suffix, end_sequence. | ✅ Complete |
| `continuity_checker.py` | Compares previous period with current. Main function `check_continuity(previous_series, current_result)` returns `list[ContinuityResult]`. For each current series, finds matching previous by prefix/suffix. Reports: is_continuous (bool), message (OK/Gap/New), gap_count. Also has `format_continuity_report()` for text output. Dataclass `ContinuityResult` stores series_key, current_from, current_to, previous_to, is_continuous, message. | ✅ Complete |

---

## src/ui/ — User Interface

| File | Description | Status |
|------|-------------|--------|
| `__init__.py` | Empty package init. | ✅ Complete |
| `main_window.py` | QMainWindow subclass. Creates header (dark blue bar with "Sahaj" title), QSplitter with left/right panels (minimum widths 320px/350px, stretch factors 2:3), status bar. Connects input_panel signals to processing logic. Processing is deferred via QTimer.singleShot(30ms) for UI responsiveness. Calls `check_continuity()` if previous GSTR-1 loaded. Sets `Qt.SplitHCursor` on splitter handle. | ✅ Complete |
| `input_panel.py` | QWidget with 4 numbered steps in a QScrollArea. Step 1: Document Type (QComboBox with all DocumentNature values). Step 2: Invoice Format (QLineEdit) + Auto-Detect button (yellow, calls `detect_pattern()`). Step 3: Invoice List (QPlainTextEdit with line counter). Step 4: Previous GSTR-1 (optional, Browse button, shows file status). Generate Table 13 / Clear buttons at bottom. Emits: `process_requested`, `clear_requested`, `input_changed`, `previous_gstr1_loaded` signals. Stores `_previous_series` list. | ✅ Complete |
| `output_panel.py` | QWidget showing results in QScrollArea. Components: Stats cards (Total, Matched, Cancelled, Series), Table 13 table (QTableWidget with 6 columns, resizable via Interactive mode), Expand/Collapse button, Warnings section (yellow), Cancelled/Missing section (red), Continuity Check section (blue). Features: `_toggle_table_expand()` calculates actual row heights, `eventFilter()` for Ctrl+C, `_show_table_context_menu()` for right-click, `display_continuity_results()` for showing continuity check. Selection mode: SelectItems + ExtendedSelection. | ✅ Complete |
| `styles.py` | Contains `SCROLLBAR_STYLE` constant (14px visible scrollbars with gray track, darker handle). Imported by main_window.py. | ✅ Complete |

---

## src/utils/ — Utilities

| File | Description | Status |
|------|-------------|--------|
| `__init__.py` | Empty package init. | ✅ Complete |
| `validators.py` | Input validation functions. `validate_pattern_input(pattern)` returns `(is_valid, error_message)`. Checks: not empty, has `[...]` sequence marker, no multiple sequence markers. `count_lines(text)` returns count of non-empty lines. | ✅ Complete |
| `formatters.py` | Output formatting. `format_table13_tsv(rows)` converts list of Table13Row to tab-separated string with header row. Used by "Copy for Excel" button. | ✅ Complete |

---

## tests/ — Unit Tests

| File | Description | Status |
|------|-------------|--------|
| `__init__.py` | Empty package init. | ✅ Complete |
| `test_pattern_parser.py` | 18 pytest tests for PatternParser. Tests: basic pattern, wildcard pattern, multiple wildcards, special chars, empty pattern, whitespace, pattern without sequence, multiple sequences (should fail), non-numeric sequence, regex generation. | ✅ Complete (all passing) |
| `test_invoice_processor.py` | 11 pytest tests for InvoiceProcessor. Tests: simple matching, multi-series grouping, unmatched handling, duplicate detection, various edge cases. | ✅ Complete (all passing) |
| `test_series_analyzer.py` | 12 pytest tests for SeriesAnalyzer. Tests: complete series, gaps, duplicates, start_end invoices (uses original strings), missing_invoices formatting, high cancellation warning, analyze_all_series, to_table13_rows, single invoice series. Note: Test for missing_invoices checks for `['002']` not `['GST/002']` — updated to match new behavior. | ✅ Complete (all passing) |

---

## Files NOT in Project (but mentioned in discussions)

| File | Description | Status |
|------|-------------|--------|
| Pattern library dropdown | Pre-defined patterns for common formats | ❌ Not implemented |
| Sample data button | Load example data for first-time users | ❌ Not implemented |
| Excel export | Export Table 13 to .xlsx | ❌ Not implemented |
| PDF export | Export Table 13 to .pdf | ❌ Not implemented |

---

## Summary Statistics

- **Total files:** 20 (excluding __pycache__ and .pyc)
- **Python files:** 15
- **Test files:** 3 (41 tests total)
- **Documentation files:** 2 (README.md, CLAUDE.md)
- **Config files:** 2 (requirements.txt, .gitignore)
- **Lines of code:** ~3,500 (approximate)

---

## Dependency Graph

```
main.py
└── src/ui/main_window.py
    ├── src/ui/input_panel.py
    │   ├── src/core/models.py (DocumentNature)
    │   ├── src/core/pattern_detector.py
    │   ├── src/core/excel_reader.py
    │   └── src/utils/validators.py
    ├── src/ui/output_panel.py
    │   ├── src/core/models.py
    │   └── src/utils/formatters.py
    ├── src/core/pattern_parser.py
    │   └── src/core/models.py
    ├── src/core/invoice_processor.py
    │   └── src/core/models.py
    ├── src/core/series_analyzer.py
    │   └── src/core/models.py
    └── src/core/continuity_checker.py
        ├── src/core/excel_reader.py
        └── src/core/models.py
```

---

*End of FILE_INDEX.md*
