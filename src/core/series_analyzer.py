"""
Series Analyzer for GSTR-1 Table 13 Generator.

Analyzes grouped invoice series to:
- Find start and end numbers
- Detect gaps (cancelled/missing invoices)
- Identify duplicates
- Generate warnings for anomalies
- Produce Table 13 formatted output
"""

from typing import List, Dict, Tuple, Optional
from .models import (
    ParsedPattern, 
    ParsedInvoice, 
    SeriesAnalysis, 
    ProcessingResult,
    Table13Row
)
from .invoice_processor import InvoiceProcessor


class SeriesAnalyzer:
    """Analyzes invoice series for Table 13 reporting."""
    
    # Warning thresholds
    HIGH_CANCELLATION_THRESHOLD = 0.20  # 20% cancellation triggers warning
    LARGE_GAP_THRESHOLD = 50  # Gap of 50+ numbers triggers warning
    
    def __init__(self, pattern: ParsedPattern, processor: InvoiceProcessor):
        """
        Initialize the analyzer.
        
        Args:
            pattern: The parsed pattern
            processor: The invoice processor (for reconstructing invoice numbers)
        """
        self.pattern = pattern
        self.processor = processor
    
    def analyze_series(self, 
                       series_key: str,
                       invoices: List[ParsedInvoice]) -> SeriesAnalysis:
        """
        Analyze a single series of invoices.
        
        Args:
            series_key: Unique identifier for the series
            invoices: List of parsed invoices in this series
            
        Returns:
            SeriesAnalysis with complete statistics
        """
        result = SeriesAnalysis(
            series_key=series_key,
            series_display_name=self.processor.get_series_display_name(series_key),
            sequence_padding=self.pattern.sequence_length
        )
        
        if not invoices:
            result.warnings.append("No invoices in series")
            return result
        
        # Get wildcard values from first invoice (all should be same for this series)
        wildcard_values = invoices[0].wildcard_values if invoices else []
        
        # Extract all sequence numbers and detect ACTUAL padding from data
        all_sequences = []
        actual_padding = self.pattern.sequence_length
        
        for inv in invoices:
            if inv.sequence_number is not None:
                all_sequences.append(inv.sequence_number)
                # Detect actual padding from the original sequence string
                if inv.sequence_str:
                    actual_padding = max(actual_padding, len(inv.sequence_str))
        
        # Use detected padding
        result.sequence_padding = actual_padding
        
        if not all_sequences:
            result.warnings.append("No valid sequence numbers found")
            return result
        
        # Detect duplicates
        unique_sequences = set()
        duplicates = []
        duplicate_count = 0
        
        for inv in invoices:
            seq = inv.sequence_number
            if seq in unique_sequences:
                duplicates.append(inv.raw)
                duplicate_count += 1
            else:
                unique_sequences.add(seq)
        
        result.duplicate_invoices = duplicates
        result.duplicate_count = duplicate_count
        
        # Calculate statistics
        sorted_sequences = sorted(unique_sequences)
        
        result.start_number = sorted_sequences[0]
        result.end_number = sorted_sequences[-1]
        result.actual_count = len(unique_sequences)
        
        # Reconstruct start and end invoice numbers with ACTUAL padding
        result.start_invoice = self.processor.reconstruct_invoice(
            result.start_number, 
            wildcard_values,
            result.sequence_padding
        )
        result.end_invoice = self.processor.reconstruct_invoice(
            result.end_number,
            wildcard_values,
            result.sequence_padding
        )
        
        # Calculate total in range
        result.total_in_range = result.end_number - result.start_number + 1
        
        # Find missing numbers
        expected_range = set(range(result.start_number, result.end_number + 1))
        missing_numbers = sorted(expected_range - unique_sequences)
        
        result.missing_numbers = missing_numbers
        result.cancelled_count = len(missing_numbers)
        result.net_issued = result.actual_count
        
        # Store missing as JUST the sequence numbers (padded), not full invoice
        result.missing_invoices = [
            str(num).zfill(result.sequence_padding)
            for num in missing_numbers
        ]
        
        # Generate warnings
        self._generate_warnings(result)
        
        return result
    
    def _generate_warnings(self, analysis: SeriesAnalysis) -> None:
        """Generate warnings for anomalies in the series."""
        
        # High cancellation ratio warning
        if analysis.total_in_range > 0:
            cancellation_ratio = analysis.cancelled_count / analysis.total_in_range
            if cancellation_ratio > self.HIGH_CANCELLATION_THRESHOLD:
                pct = int(cancellation_ratio * 100)
                analysis.warnings.append(
                    f"⚠️ High cancellation ratio: {pct}% of invoice range is missing. "
                    "Please verify if this is correct or if multiple series are mixed."
                )
        
        # Large gap detection
        if analysis.missing_numbers:
            # Find consecutive gaps
            gaps = self._find_consecutive_gaps(analysis.missing_numbers)
            large_gaps = [(start, end) for start, end in gaps 
                         if (end - start + 1) >= self.LARGE_GAP_THRESHOLD]
            
            for start, end in large_gaps:
                gap_size = end - start + 1
                analysis.warnings.append(
                    f"⚠️ Large gap detected: {gap_size} consecutive numbers missing "
                    f"from {start} to {end}. This may indicate a series break."
                )
        
        # Duplicate warning
        if analysis.duplicate_count > 0:
            analysis.warnings.append(
                f"ℹ️ {analysis.duplicate_count} duplicate invoice(s) found and ignored."
            )
    
    def _find_consecutive_gaps(self, missing: List[int]) -> List[Tuple[int, int]]:
        """Find consecutive number ranges in missing list."""
        if not missing:
            return []
        
        gaps = []
        start = missing[0]
        end = missing[0]
        
        for num in missing[1:]:
            if num == end + 1:
                end = num
            else:
                gaps.append((start, end))
                start = num
                end = num
        
        gaps.append((start, end))
        return gaps
    
    def analyze_all_series(self,
                          series_groups: Dict[str, List[ParsedInvoice]],
                          unmatched: List[str],
                          invalid: List[Tuple[str, str]],
                          document_nature: str) -> ProcessingResult:
        """
        Analyze all series and produce complete processing result.
        
        Args:
            series_groups: Dictionary of series_key to invoices
            unmatched: List of unmatched invoice strings
            invalid: List of (invoice, error) tuples
            document_nature: The type of document being processed
            
        Returns:
            Complete ProcessingResult
        """
        result = ProcessingResult(
            pattern_used=self.pattern.raw_pattern,
            document_nature=document_nature,
            unmatched_invoices=unmatched,
            invalid_invoices=invalid
        )
        
        # Count totals
        total_matched = sum(len(invs) for invs in series_groups.values())
        result.total_matched = total_matched
        result.total_unmatched = len(unmatched)
        result.total_input_lines = total_matched + len(unmatched) + len(invalid)
        
        # Analyze each series
        for series_key, invoices in series_groups.items():
            analysis = self.analyze_series(series_key, invoices)
            result.series_results.append(analysis)
            result.total_duplicates += analysis.duplicate_count
        
        # Sort series by start number for consistent output
        result.series_results.sort(key=lambda x: (x.series_key, x.start_number))
        
        # Generate global warnings
        if result.total_unmatched > 0:
            result.warnings.append(
                f"ℹ️ {result.total_unmatched} invoice(s) didn't match the pattern. "
                "These may belong to a different series."
            )
        
        if len(series_groups) > 1:
            result.warnings.append(
                f"ℹ️ Multiple series detected: {len(series_groups)} distinct series found "
                "based on variable parts in the pattern."
            )
        
        return result
    
    def to_table13_rows(self, 
                        result: ProcessingResult) -> List[Table13Row]:
        """
        Convert processing result to Table 13 format rows.
        
        Args:
            result: Complete ProcessingResult
            
        Returns:
            List of Table13Row objects
        """
        rows = []
        
        for series in result.series_results:
            row = Table13Row(
                nature_of_document=result.document_nature,
                sr_no_from=series.start_invoice,
                sr_no_to=series.end_invoice,
                total_number=series.total_in_range,
                cancelled=series.cancelled_count,
                net_issued=series.net_issued
            )
            rows.append(row)
        
        return rows


def analyze_invoices(pattern: ParsedPattern,
                    series_groups: Dict[str, List[ParsedInvoice]],
                    unmatched: List[str],
                    invalid: List[Tuple[str, str]],
                    document_nature: str) -> ProcessingResult:
    """
    Convenience function to analyze invoice series.
    
    Args:
        pattern: The parsed pattern
        series_groups: Grouped invoices by series
        unmatched: Unmatched invoices
        invalid: Invalid invoices
        document_nature: Document type
        
    Returns:
        Complete ProcessingResult
    """
    processor = InvoiceProcessor(pattern)
    analyzer = SeriesAnalyzer(pattern, processor)
    return analyzer.analyze_all_series(series_groups, unmatched, invalid, document_nature)
