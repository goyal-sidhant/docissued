"""
Tests for invoice_processor module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.pattern_parser import parse_pattern
from src.core.invoice_processor import InvoiceProcessor, process_invoices


class TestInvoiceProcessor:
    """Tests for InvoiceProcessor class."""
    
    def test_process_simple_invoice(self):
        """Test processing a simple invoice."""
        pattern = parse_pattern("GST/24-25/[0001]")
        processor = InvoiceProcessor(pattern)
        
        result = processor.process_invoice("GST/24-25/0001")
        
        assert result.is_valid
        assert result.sequence_number == 1
        assert result.sequence_str == "0001"
    
    def test_process_invoice_with_different_sequence(self):
        """Test processing invoices with different sequence numbers."""
        pattern = parse_pattern("INV-[001]")
        processor = InvoiceProcessor(pattern)
        
        result1 = processor.process_invoice("INV-001")
        result2 = processor.process_invoice("INV-099")
        result3 = processor.process_invoice("INV-100")
        
        assert result1.sequence_number == 1
        assert result2.sequence_number == 99
        assert result3.sequence_number == 100
    
    def test_process_invoice_no_match(self):
        """Test processing invoice that doesn't match pattern."""
        pattern = parse_pattern("GST/[001]")
        processor = InvoiceProcessor(pattern)
        
        result = processor.process_invoice("SAL/001")
        
        assert not result.is_valid
        assert "match" in result.error_message.lower()
    
    def test_process_invoice_with_wildcard(self):
        """Test processing invoice with wildcard pattern."""
        pattern = parse_pattern("GST/*/[001]")
        processor = InvoiceProcessor(pattern)
        
        result1 = processor.process_invoice("GST/A/001")
        result2 = processor.process_invoice("GST/B/001")
        
        assert result1.is_valid
        assert result2.is_valid
        assert result1.wildcard_values == ["A"]
        assert result2.wildcard_values == ["B"]
        assert result1.series_key != result2.series_key
    
    def test_series_key_grouping(self):
        """Test that invoices are grouped correctly by series key."""
        pattern = parse_pattern("GST/*/[001]")
        processor = InvoiceProcessor(pattern)
        
        inv1 = processor.process_invoice("GST/A/001")
        inv2 = processor.process_invoice("GST/A/002")
        inv3 = processor.process_invoice("GST/B/001")
        
        assert inv1.series_key == inv2.series_key
        assert inv1.series_key != inv3.series_key
    
    def test_process_text_input(self):
        """Test processing text input with multiple invoices."""
        pattern = parse_pattern("INV/[001]")
        processor = InvoiceProcessor(pattern)
        
        text = """INV/001
INV/002
INV/003
"""
        series_groups, unmatched, invalid = processor.process_text_input(text)
        
        assert len(series_groups) == 1
        assert len(unmatched) == 0
        assert len(invalid) == 0
        
        key = list(series_groups.keys())[0]
        assert len(series_groups[key]) == 3
    
    def test_process_text_with_mixed_series(self):
        """Test processing text with multiple series."""
        pattern = parse_pattern("*/[001]")
        processor = InvoiceProcessor(pattern)
        
        text = """A/001
A/002
B/001
B/002
"""
        series_groups, unmatched, invalid = processor.process_text_input(text)
        
        assert len(series_groups) == 2
        assert "A/{SEQ}" in series_groups or any("A" in k for k in series_groups.keys())
    
    def test_process_text_with_unmatched(self):
        """Test processing text with unmatched invoices."""
        pattern = parse_pattern("GST/[001]")
        processor = InvoiceProcessor(pattern)
        
        text = """GST/001
GST/002
SAL/001
OTHER/001
"""
        series_groups, unmatched, invalid = processor.process_text_input(text)
        
        assert len(unmatched) == 2
        assert "SAL/001" in unmatched
        assert "OTHER/001" in unmatched
    
    def test_process_text_with_empty_lines(self):
        """Test that empty lines are ignored."""
        pattern = parse_pattern("INV/[001]")
        processor = InvoiceProcessor(pattern)
        
        text = """INV/001

INV/002

INV/003
"""
        series_groups, unmatched, invalid = processor.process_text_input(text)
        
        key = list(series_groups.keys())[0]
        assert len(series_groups[key]) == 3
    
    def test_process_text_with_windows_line_endings(self):
        """Test handling of Windows line endings."""
        pattern = parse_pattern("INV/[001]")
        processor = InvoiceProcessor(pattern)
        
        text = "INV/001\r\nINV/002\r\nINV/003"
        series_groups, unmatched, invalid = processor.process_text_input(text)
        
        key = list(series_groups.keys())[0]
        assert len(series_groups[key]) == 3
    
    def test_reconstruct_invoice(self):
        """Test invoice reconstruction."""
        pattern = parse_pattern("GST/*/[001]/A")
        processor = InvoiceProcessor(pattern)
        
        invoice = processor.reconstruct_invoice(42, ["BRANCH"])
        
        assert invoice == "GST/BRANCH/042/A"
    
    def test_reconstruct_invoice_with_padding(self):
        """Test invoice reconstruction with custom padding."""
        pattern = parse_pattern("INV-[001]")
        processor = InvoiceProcessor(pattern)
        
        inv1 = processor.reconstruct_invoice(5, [], padding=3)
        inv2 = processor.reconstruct_invoice(5, [], padding=5)
        
        assert inv1 == "INV-005"
        assert inv2 == "INV-00005"


class TestProcessInvoicesFunction:
    """Tests for the convenience process_invoices function."""
    
    def test_process_invoices_basic(self):
        """Test basic usage of process_invoices function."""
        pattern = parse_pattern("TEST/[001]")
        text = "TEST/001\nTEST/002"
        
        series_groups, unmatched, invalid = process_invoices(pattern, text)
        
        assert len(series_groups) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
