"""
Data models for GSTR-1 Table 13 Generator.

This module contains all data classes used throughout the application.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum


class DocumentNature(Enum):
    """Document types as per GSTR-1 Table 13."""
    
    INVOICES_OUTWARD = "Invoices for outward supply"
    INVOICES_INWARD_RCM = "Invoices for inward supply from unregistered person (RCM)"
    REVISED_INVOICE = "Revised Invoice"
    DEBIT_NOTE = "Debit Note"
    CREDIT_NOTE = "Credit Note"
    RECEIPT_VOUCHER = "Receipt Voucher"
    PAYMENT_VOUCHER = "Payment Voucher"
    REFUND_VOUCHER = "Refund Voucher"
    DELIVERY_CHALLAN_JOB_WORK = "Delivery Challan for job work"
    DELIVERY_CHALLAN_APPROVAL = "Delivery Challan for supply on approval"
    DELIVERY_CHALLAN_LIQUID_GAS = "Delivery Challan in case of liquid gas"
    DELIVERY_CHALLAN_OTHERS = "Delivery Challan in other cases"
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Return all document nature values as strings."""
        return [member.value for member in cls]


@dataclass
class ParsedPattern:
    """
    Represents a parsed invoice pattern.
    
    Example: For pattern "GST/*/[001]/A"
    - parts: [('fixed', 'GST/'), ('wildcard', '*'), ('fixed', '/'), ('sequence', '001'), ('fixed', '/A')]
    - wildcard_count: 1
    - sequence_length: 3
    - raw_pattern: "GST/*/[001]/A"
    """
    
    # List of tuples: (part_type, value) where part_type is 'fixed', 'wildcard', 'sequence'
    parts: List[Tuple[str, str]] = field(default_factory=list)
    wildcard_count: int = 0
    sequence_length: int = 0
    raw_pattern: str = ""
    regex_pattern: str = ""
    is_valid: bool = False
    error_message: str = ""


@dataclass
class ParsedInvoice:
    """
    Represents a parsed invoice number.
    
    Attributes:
        raw: Original invoice string as provided
        sequence_number: Extracted sequence number as integer
        sequence_str: Extracted sequence number as string (preserves padding)
        wildcard_values: Values extracted from wildcard positions
        series_key: Unique key identifying the series (combines fixed parts + wildcard values)
        is_valid: Whether the invoice matched the pattern
        error_message: Error description if invalid
    """
    
    raw: str
    sequence_number: Optional[int] = None
    sequence_str: Optional[str] = None
    wildcard_values: List[str] = field(default_factory=list)
    series_key: str = ""
    is_valid: bool = False
    error_message: str = ""


@dataclass
class SeriesAnalysis:
    """
    Analysis results for a single invoice series.
    
    This represents one row in the Table 13 output.
    """
    
    series_key: str
    series_display_name: str  # Human readable series identifier
    
    # Core statistics
    start_number: int = 0
    end_number: int = 0
    start_invoice: str = ""   # Full invoice number for "From"
    end_invoice: str = ""     # Full invoice number for "To"
    
    total_in_range: int = 0       # end - start + 1
    actual_count: int = 0         # Number of invoices actually present
    cancelled_count: int = 0      # Number of missing/cancelled
    net_issued: int = 0           # actual_count (after removing duplicates)
    
    # Detailed information
    missing_numbers: List[int] = field(default_factory=list)
    missing_invoices: List[str] = field(default_factory=list)  # Full invoice numbers
    duplicate_invoices: List[str] = field(default_factory=list)
    duplicate_count: int = 0
    
    # Warnings
    warnings: List[str] = field(default_factory=list)
    
    # For output formatting
    sequence_padding: int = 0


@dataclass
class ProcessingResult:
    """
    Complete result of processing an invoice list.
    
    Contains all series analyses plus metadata about the processing.
    """
    
    # Results per series
    series_results: List[SeriesAnalysis] = field(default_factory=list)
    
    # Unmatched invoices (didn't fit the pattern)
    unmatched_invoices: List[str] = field(default_factory=list)
    
    # Invalid invoices (matched pattern but had issues)
    invalid_invoices: List[Tuple[str, str]] = field(default_factory=list)  # (invoice, error)
    
    # Statistics
    total_input_lines: int = 0
    total_matched: int = 0
    total_unmatched: int = 0
    total_duplicates: int = 0
    
    # Processing metadata
    pattern_used: str = ""
    document_nature: str = ""
    
    # Global warnings
    warnings: List[str] = field(default_factory=list)


@dataclass
class Table13Row:
    """
    Single row for GSTR-1 Table 13 output.
    
    Maps directly to the columns in Table 13.
    """
    
    nature_of_document: str
    sr_no_from: str
    sr_no_to: str
    total_number: int
    cancelled: int
    net_issued: int
    
    def to_list(self) -> List:
        """Convert to list for table display."""
        return [
            self.nature_of_document,
            self.sr_no_from,
            self.sr_no_to,
            self.total_number,
            self.cancelled,
            self.net_issued
        ]
    
    def to_tsv(self) -> str:
        """Convert to tab-separated string for copying."""
        return "\t".join([
            self.nature_of_document,
            self.sr_no_from,
            self.sr_no_to,
            str(self.total_number),
            str(self.cancelled),
            str(self.net_issued)
        ])
