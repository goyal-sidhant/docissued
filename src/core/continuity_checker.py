"""
Continuity Checker - Check series continuity between previous and current GSTR-1.

Compares previous period's ending invoice numbers with current period's
starting invoice numbers to detect gaps. Respects FY boundaries per Rule 46.
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
    status: str = "new"  # "continuous", "gap", "new", "discontinued"


def check_continuity(
    previous_series: List[PreviousSeriesInfo],
    current_result: ProcessingResult,
    current_tax_period: str = ""
) -> List[ContinuityResult]:
    """
    Check continuity between previous GSTR-1 series and current month's invoices.

    Respects FY boundaries per Rule 46 of CGST Rules 2017.

    Args:
        previous_series: List of series from previous GSTR-1 Excel (may include multiple periods)
        current_result: Processing result from current month's invoices
        current_tax_period: Current tax period in MMYYYY format (e.g., "042024")

    Returns:
        List of ContinuityResult for each current series, plus discontinued series
    """
    from ..utils.fy_utils import get_fy_from_tax_period, are_same_fy

    results = []
    current_fy = ""
    if current_tax_period:
        try:
            current_fy = get_fy_from_tax_period(current_tax_period)
        except:
            pass

    # Filter previous series to same FY only (Rule 46 compliance)
    same_fy_series = []
    other_fy_series = []

    for prev in previous_series:
        if prev.tax_period and current_tax_period:
            if are_same_fy(prev.tax_period, current_tax_period):
                same_fy_series.append(prev)
            else:
                other_fy_series.append(prev)
        else:
            # No tax period info, assume same FY for backward compatibility
            same_fy_series.append(prev)

    # Check continuity for current series
    matched_previous_keys = set()

    for current in current_result.series_results:
        result = ContinuityResult(
            series_key=current.series_key,
            series_display_name=current.series_display_name,
            current_from=current.start_invoice,
            current_to=current.end_invoice,
            previous_to=None,
            is_continuous=True,
            message="",
            gap_count=0,
            status="new"
        )

        # Try to find matching previous series in same FY
        match = match_series(
            same_fy_series,
            current.series_key,
            current.start_invoice
        )

        if match:
            prev, is_continuous, msg = match
            matched_previous_keys.add(_get_series_signature(prev))
            result.previous_to = prev.to_invoice
            result.is_continuous = is_continuous
            result.message = msg

            if is_continuous:
                result.status = "continuous"
            else:
                result.status = "gap"
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
            result.status = "new"
            result.message = "ℹ️ New series (no matching series in previous GSTR-1)"

        results.append(result)

    # Find discontinued series (in same FY previous periods but not in current)
    for prev in same_fy_series:
        prev_key = _get_series_signature(prev)
        if prev_key not in matched_previous_keys:
            # This series was in previous period but not in current
            result = ContinuityResult(
                series_key=prev_key,
                series_display_name=f"{prev.prefix}[seq]{prev.suffix}",
                current_from="",
                current_to="",
                previous_to=prev.to_invoice,
                is_continuous=False,
                message=f"⚠️ Series discontinued (last seen: {prev.to_invoice})",
                gap_count=0,
                status="discontinued"
            )
            results.append(result)

    return results


def _get_series_signature(prev: PreviousSeriesInfo) -> str:
    """Get a unique signature for a series based on prefix and suffix."""
    return f"{prev.prefix}|{prev.suffix}"


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
