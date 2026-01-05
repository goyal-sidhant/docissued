"""
Continuity Checker - Check series continuity between previous and current GSTR-1.

Compares previous period's ending invoice numbers with current period's
starting invoice numbers to detect gaps.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .excel_reader import PreviousSeriesInfo, match_series
from .models import ProcessingResult, SeriesAnalysis


@dataclass
class ContinuityResult:
    """Result of continuity check for a single series."""
    series_key: str
    series_display_name: str
    current_from: str
    current_to: str
    previous_to: Optional[str]
    is_continuous: bool
    message: str
    gap_count: int = 0


def check_continuity(
    previous_series: List[PreviousSeriesInfo],
    current_result: ProcessingResult
) -> List[ContinuityResult]:
    """
    Check continuity between previous GSTR-1 series and current month's invoices.
    
    Args:
        previous_series: List of series from previous GSTR-1 Excel
        current_result: Processing result from current month's invoices
        
    Returns:
        List of ContinuityResult for each current series
    """
    results = []
    
    for current in current_result.series_results:
        result = ContinuityResult(
            series_key=current.series_key,
            series_display_name=current.series_display_name,
            current_from=current.start_invoice,
            current_to=current.end_invoice,
            previous_to=None,
            is_continuous=True,
            message="",
            gap_count=0
        )
        
        # Try to find matching previous series
        match = match_series(
            previous_series,
            current.series_key,
            current.start_invoice
        )
        
        if match:
            prev, is_continuous, msg = match
            result.previous_to = prev.to_invoice
            result.is_continuous = is_continuous
            result.message = msg
            
            if not is_continuous:
                # Calculate gap count
                import re
                current_matches = list(re.finditer(r'\d+', current.start_invoice))
                if current_matches:
                    # Find sequence number in current
                    for m in current_matches:
                        num_val = int(m.group())
                        if not (1900 <= num_val <= 2100) and not (len(m.group()) == 2 and 0 <= num_val <= 50):
                            current_seq = num_val
                            result.gap_count = current_seq - prev.end_sequence - 1
                            break
        else:
            result.message = "ℹ️ New series (no matching series in previous GSTR-1)"
        
        results.append(result)
    
    return results


def format_continuity_report(results: List[ContinuityResult]) -> str:
    """
    Format continuity check results as a readable report.
    
    Args:
        results: List of ContinuityResult
        
    Returns:
        Formatted string report
    """
    lines = []
    lines.append("=" * 50)
    lines.append("CONTINUITY CHECK REPORT")
    lines.append("=" * 50)
    lines.append("")
    
    continuous_count = sum(1 for r in results if r.is_continuous)
    gap_count = sum(1 for r in results if not r.is_continuous and r.previous_to)
    new_count = sum(1 for r in results if r.previous_to is None)
    
    lines.append(f"Summary: {continuous_count} OK, {gap_count} with gaps, {new_count} new series")
    lines.append("")
    
    for result in results:
        lines.append(f"Series: {result.series_display_name}")
        lines.append(f"  Current: {result.current_from} → {result.current_to}")
        
        if result.previous_to:
            lines.append(f"  Previous ended: {result.previous_to}")
        
        lines.append(f"  Status: {result.message}")
        
        if result.gap_count > 0:
            lines.append(f"  Gap: {result.gap_count} invoice(s) missing")
        
        lines.append("")
    
    return "\n".join(lines)
