"""
Invoice Processor for GSTR-1 Table 13 Generator.

Processes invoice lists against parsed patterns to extract sequence numbers,
identify series, and detect matches/mismatches.
"""

import re
from typing import List, Dict, Tuple, Optional
from .models import ParsedPattern, ParsedInvoice


class InvoiceProcessor:
    """Processes invoice lists against a parsed pattern."""
    
    def __init__(self, pattern: ParsedPattern, ignore_leading_zeros: bool = False):
        """
        Initialize the processor with a parsed pattern.
        
        Args:
            pattern: A valid ParsedPattern object
            ignore_leading_zeros: If True, treat '01' and '001' as same sequence
        """
        if not pattern.is_valid:
            raise ValueError(f"Cannot process with invalid pattern: {pattern.error_message}")
        
        self.pattern = pattern
        self.ignore_leading_zeros = ignore_leading_zeros
        self._compiled_regex = re.compile(pattern.regex_pattern)
    
    def process_invoice(self, invoice: str) -> ParsedInvoice:
        """
        Process a single invoice string against the pattern.
        
        Args:
            invoice: Raw invoice string
            
        Returns:
            ParsedInvoice object with extracted components
        """
        result = ParsedInvoice(raw=invoice)
        
        # Clean the invoice string
        invoice_clean = invoice.strip()
        
        if not invoice_clean:
            result.error_message = "Empty invoice"
            return result
        
        # Try to match against the pattern
        match = self._compiled_regex.match(invoice_clean)
        
        if not match:
            result.error_message = "Does not match pattern"
            return result
        
        # Extract sequence number
        seq_str = match.group('seq')
        result.sequence_str = seq_str
        
        try:
            result.sequence_number = int(seq_str)
        except ValueError:
            result.error_message = f"Invalid sequence number: {seq_str}"
            return result
        
        # Extract wildcard values
        wildcard_values = []
        for i in range(self.pattern.wildcard_count):
            try:
                wc_value = match.group(f'wc{i}')
                wildcard_values.append(wc_value)
            except IndexError:
                wildcard_values.append('')
        
        result.wildcard_values = wildcard_values
        
        # Build series key (unique identifier for this series)
        result.series_key = self._build_series_key(wildcard_values)
        
        result.is_valid = True
        return result
    
    def _build_series_key(self, wildcard_values: List[str]) -> str:
        """
        Build a unique series key from fixed parts and wildcard values.
        
        The series key identifies which series an invoice belongs to.
        Invoices with the same series key are in the same series.
        """
        key_parts = []
        wildcard_index = 0
        
        for part_type, value in self.pattern.parts:
            if part_type == 'fixed':
                key_parts.append(value)
            elif part_type == 'wildcard':
                if wildcard_index < len(wildcard_values):
                    key_parts.append(wildcard_values[wildcard_index])
                wildcard_index += 1
            elif part_type == 'sequence':
                key_parts.append('{SEQ}')
        
        return ''.join(key_parts)
    
    def process_invoice_list(self, invoices: List[str]) -> Dict[str, List[ParsedInvoice]]:
        """
        Process a list of invoices and group by series.
        
        Args:
            invoices: List of invoice strings
            
        Returns:
            Dictionary mapping series_key to list of parsed invoices
        """
        series_groups: Dict[str, List[ParsedInvoice]] = {}
        
        for invoice in invoices:
            parsed = self.process_invoice(invoice)
            
            if parsed.is_valid:
                key = parsed.series_key
                if key not in series_groups:
                    series_groups[key] = []
                series_groups[key].append(parsed)
        
        return series_groups
    
    def process_text_input(self, text: str) -> Tuple[Dict[str, List[ParsedInvoice]], 
                                                      List[str], 
                                                      List[Tuple[str, str]]]:
        """
        Process raw text input (invoice list pasted as text).
        
        Args:
            text: Raw text with one invoice per line
            
        Returns:
            Tuple of:
            - Dictionary mapping series_key to list of valid parsed invoices
            - List of unmatched invoice strings
            - List of (invoice, error) tuples for invalid invoices
        """
        # Split text into lines
        lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        
        series_groups: Dict[str, List[ParsedInvoice]] = {}
        unmatched: List[str] = []
        invalid: List[Tuple[str, str]] = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            parsed = self.process_invoice(line)
            
            if parsed.is_valid:
                key = parsed.series_key
                if key not in series_groups:
                    series_groups[key] = []
                series_groups[key].append(parsed)
            else:
                if "Does not match pattern" in parsed.error_message:
                    unmatched.append(line)
                else:
                    invalid.append((line, parsed.error_message))
        
        return series_groups, unmatched, invalid
    
    def reconstruct_invoice(self, sequence_number: int, 
                           wildcard_values: List[str],
                           padding: Optional[int] = None) -> str:
        """
        Reconstruct a full invoice number from components.
        
        Args:
            sequence_number: The sequence number
            wildcard_values: List of wildcard values for this series
            padding: Optional override for sequence padding
            
        Returns:
            Full invoice number string
        """
        if padding is None:
            padding = self.pattern.sequence_length
        
        parts = []
        wildcard_index = 0
        
        for part_type, value in self.pattern.parts:
            if part_type == 'fixed':
                parts.append(value)
            elif part_type == 'wildcard':
                if wildcard_index < len(wildcard_values):
                    parts.append(wildcard_values[wildcard_index])
                wildcard_index += 1
            elif part_type == 'sequence':
                # Pad the sequence number
                seq_str = str(sequence_number).zfill(padding)
                parts.append(seq_str)
        
        return ''.join(parts)
    
    def get_series_display_name(self, series_key: str) -> str:
        """
        Generate a human-readable display name for a series.
        
        Args:
            series_key: The series key
            
        Returns:
            Display name string
        """
        # Replace {SEQ} placeholder with more readable format
        return series_key.replace('{SEQ}', '<seq>')


def process_invoices(pattern: ParsedPattern, 
                    text: str,
                    ignore_leading_zeros: bool = False) -> Tuple[Dict[str, List[ParsedInvoice]], 
                                                                  List[str], 
                                                                  List[Tuple[str, str]]]:
    """
    Convenience function to process invoice text with a pattern.
    
    Args:
        pattern: A valid ParsedPattern
        text: Raw invoice text
        ignore_leading_zeros: Whether to normalize leading zeros
        
    Returns:
        Tuple of (series_groups, unmatched, invalid)
    """
    processor = InvoiceProcessor(pattern, ignore_leading_zeros)
    return processor.process_text_input(text)
