"""
Formatters for GSTR-1 Table 13 Generator.

Provides formatting functions for output display and export.
"""

from typing import List
from ..core.models import ProcessingResult, SeriesAnalysis, Table13Row


def format_missing_invoices(missing: List[str], max_display: int = 20) -> str:
    """
    Format missing invoice list for display.
    
    Args:
        missing: List of missing invoice numbers
        max_display: Maximum number to display before truncating
        
    Returns:
        Formatted string
    """
    if not missing:
        return "None"
    
    count = len(missing)
    
    if count <= max_display:
        return ", ".join(missing)
    else:
        displayed = ", ".join(missing[:max_display])
        remaining = count - max_display
        return f"{displayed}\n... and {remaining} more"


def format_series_summary(analysis: SeriesAnalysis) -> str:
    """
    Format a series analysis as a summary string.
    
    Args:
        analysis: SeriesAnalysis object
        
    Returns:
        Formatted summary string
    """
    lines = [
        f"Series: {analysis.series_display_name}",
        f"  From: {analysis.start_invoice}",
        f"  To: {analysis.end_invoice}",
        f"  Total in Range: {analysis.total_in_range}",
        f"  Cancelled/Missing: {analysis.cancelled_count}",
        f"  Net Issued: {analysis.net_issued}",
    ]
    
    if analysis.duplicate_count > 0:
        lines.append(f"  Duplicates Ignored: {analysis.duplicate_count}")
    
    if analysis.missing_invoices:
        missing_str = format_missing_invoices(analysis.missing_invoices)
        lines.append(f"  Missing Numbers: {missing_str}")
    
    if analysis.warnings:
        lines.append("  Warnings:")
        for warning in analysis.warnings:
            lines.append(f"    {warning}")
    
    return "\n".join(lines)


def format_result_summary(result: ProcessingResult) -> str:
    """
    Format complete processing result as summary text.
    
    Args:
        result: ProcessingResult object
        
    Returns:
        Formatted summary string
    """
    lines = [
        "=" * 60,
        "GSTR-1 TABLE 13 - DOCUMENT SUMMARY",
        "=" * 60,
        "",
        f"Document Nature: {result.document_nature}",
        f"Pattern Used: {result.pattern_used}",
        "",
        f"Total Lines Processed: {result.total_input_lines}",
        f"Matched: {result.total_matched}",
        f"Unmatched: {result.total_unmatched}",
        f"Duplicates Found: {result.total_duplicates}",
        "",
        "-" * 60,
    ]
    
    # Add each series
    for i, series in enumerate(result.series_results, 1):
        lines.append(f"\nSeries {i}:")
        lines.append(format_series_summary(series))
    
    # Add global warnings
    if result.warnings:
        lines.extend(["", "-" * 60, "WARNINGS:", ""])
        for warning in result.warnings:
            lines.append(f"  {warning}")
    
    # Add unmatched invoices
    if result.unmatched_invoices:
        lines.extend(["", "-" * 60, "UNMATCHED INVOICES:", ""])
        unmatched_str = format_missing_invoices(result.unmatched_invoices, max_display=10)
        lines.append(f"  {unmatched_str}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_table13_tsv(rows: List[Table13Row]) -> str:
    """
    Format Table 13 rows as tab-separated values for copying.
    
    Args:
        rows: List of Table13Row objects
        
    Returns:
        TSV formatted string with headers
    """
    headers = [
        "Nature of Document",
        "Sr. No. From",
        "Sr. No. To",
        "Total Number",
        "Cancelled",
        "Net Issued"
    ]
    
    lines = ["\t".join(headers)]
    
    for row in rows:
        lines.append(row.to_tsv())
    
    return "\n".join(lines)


def format_table13_csv(rows: List[Table13Row]) -> str:
    """
    Format Table 13 rows as CSV for export.
    
    Args:
        rows: List of Table13Row objects
        
    Returns:
        CSV formatted string with headers
    """
    headers = [
        "Nature of Document",
        "Sr. No. From",
        "Sr. No. To",
        "Total Number",
        "Cancelled",
        "Net Issued"
    ]
    
    def escape_csv(value: str) -> str:
        """Escape a value for CSV."""
        if ',' in str(value) or '"' in str(value):
            return f'"{str(value).replace(chr(34), chr(34)+chr(34))}"'
        return str(value)
    
    lines = [",".join(headers)]
    
    for row in rows:
        row_values = [
            escape_csv(row.nature_of_document),
            escape_csv(row.sr_no_from),
            escape_csv(row.sr_no_to),
            str(row.total_number),
            str(row.cancelled),
            str(row.net_issued)
        ]
        lines.append(",".join(row_values))
    
    return "\n".join(lines)


def format_number_with_commas(number: int) -> str:
    """
    Format a number with comma separators (Indian style).
    
    Args:
        number: Integer to format
        
    Returns:
        Formatted string like "1,23,456"
    """
    s = str(number)
    
    if len(s) <= 3:
        return s
    
    # Indian numbering: last 3 digits, then groups of 2
    result = s[-3:]
    s = s[:-3]
    
    while s:
        result = s[-2:] + "," + result
        s = s[:-2]
    
    return result
