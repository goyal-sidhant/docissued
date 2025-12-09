"""
Tests for series_analyzer module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.pattern_parser import parse_pattern
from src.core.invoice_processor import InvoiceProcessor
from src.core.series_analyzer import SeriesAnalyzer, analyze_invoices


class TestSeriesAnalyzer:
    """Tests for SeriesAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pattern = parse_pattern("INV/[001]")
        self.processor = InvoiceProcessor(self.pattern)
        self.analyzer = SeriesAnalyzer(self.pattern, self.processor)
    
    def test_analyze_complete_series(self):
        """Test analysis of a complete series with no gaps."""
        invoices = [
            self.processor.process_invoice("INV/001"),
            self.processor.process_invoice("INV/002"),
            self.processor.process_invoice("INV/003"),
        ]
        
        result = self.analyzer.analyze_series("INV/{SEQ}", invoices)
        
        assert result.start_number == 1
        assert result.end_number == 3
        assert result.total_in_range == 3
        assert result.cancelled_count == 0
        assert result.net_issued == 3
        assert len(result.missing_numbers) == 0
    
    def test_analyze_series_with_gaps(self):
        """Test analysis of a series with missing numbers."""
        invoices = [
            self.processor.process_invoice("INV/001"),
            self.processor.process_invoice("INV/002"),
            self.processor.process_invoice("INV/005"),
            self.processor.process_invoice("INV/006"),
        ]
        
        result = self.analyzer.analyze_series("INV/{SEQ}", invoices)
        
        assert result.start_number == 1
        assert result.end_number == 6
        assert result.total_in_range == 6
        assert result.cancelled_count == 2
        assert result.net_issued == 4
        assert 3 in result.missing_numbers
        assert 4 in result.missing_numbers
    
    def test_analyze_series_with_duplicates(self):
        """Test analysis of a series with duplicate invoices."""
        invoices = [
            self.processor.process_invoice("INV/001"),
            self.processor.process_invoice("INV/002"),
            self.processor.process_invoice("INV/002"),  # duplicate
            self.processor.process_invoice("INV/003"),
        ]
        
        result = self.analyzer.analyze_series("INV/{SEQ}", invoices)
        
        assert result.duplicate_count == 1
        assert result.net_issued == 3
        assert "INV/002" in result.duplicate_invoices
    
    def test_analyze_series_start_end_invoices(self):
        """Test that start and end invoice numbers are correctly formatted."""
        pattern = parse_pattern("GST/24-25/[0001]")
        processor = InvoiceProcessor(pattern)
        analyzer = SeriesAnalyzer(pattern, processor)
        
        invoices = [
            processor.process_invoice("GST/24-25/0005"),
            processor.process_invoice("GST/24-25/0010"),
        ]
        
        result = analyzer.analyze_series("GST/24-25/{SEQ}", invoices)
        
        assert result.start_invoice == "GST/24-25/0005"
        assert result.end_invoice == "GST/24-25/0010"
    
    def test_analyze_series_missing_invoices_formatted(self):
        """Test that missing invoice numbers are correctly formatted."""
        pattern = parse_pattern("GST/[001]")
        processor = InvoiceProcessor(pattern)
        analyzer = SeriesAnalyzer(pattern, processor)
        
        invoices = [
            processor.process_invoice("GST/001"),
            processor.process_invoice("GST/003"),
        ]
        
        result = analyzer.analyze_series("GST/{SEQ}", invoices)
        
        assert "GST/002" in result.missing_invoices
    
    def test_high_cancellation_warning(self):
        """Test that high cancellation ratio generates warning."""
        # Create series with >20% missing
        invoices = [
            self.processor.process_invoice("INV/001"),
            self.processor.process_invoice("INV/010"),
        ]
        
        result = self.analyzer.analyze_series("INV/{SEQ}", invoices)
        
        # 8 out of 10 missing = 80%
        assert any("cancellation" in w.lower() for w in result.warnings)
    
    def test_analyze_all_series(self):
        """Test analysis of multiple series."""
        pattern = parse_pattern("*/[001]")
        processor = InvoiceProcessor(pattern)
        analyzer = SeriesAnalyzer(pattern, processor)
        
        text = """A/001
A/002
A/003
B/001
B/002
"""
        series_groups, unmatched, invalid = processor.process_text_input(text)
        
        result = analyzer.analyze_all_series(
            series_groups, unmatched, invalid, "Test Documents"
        )
        
        assert len(result.series_results) == 2
        assert result.total_matched == 5
        assert result.total_unmatched == 0
    
    def test_to_table13_rows(self):
        """Test conversion to Table 13 format."""
        invoices = [
            self.processor.process_invoice("INV/001"),
            self.processor.process_invoice("INV/003"),
        ]
        
        series_groups = {"INV/{SEQ}": invoices}
        result = self.analyzer.analyze_all_series(
            series_groups, [], [], "Invoices for outward supply"
        )
        
        rows = self.analyzer.to_table13_rows(result)
        
        assert len(rows) == 1
        row = rows[0]
        assert row.nature_of_document == "Invoices for outward supply"
        assert row.sr_no_from == "INV/001"
        assert row.sr_no_to == "INV/003"
        assert row.total_number == 3
        assert row.cancelled == 1
        assert row.net_issued == 2
    
    def test_single_invoice_series(self):
        """Test analysis of a series with single invoice."""
        invoices = [
            self.processor.process_invoice("INV/042"),
        ]
        
        result = self.analyzer.analyze_series("INV/{SEQ}", invoices)
        
        assert result.start_number == 42
        assert result.end_number == 42
        assert result.total_in_range == 1
        assert result.cancelled_count == 0
        assert result.net_issued == 1


class TestAnalyzeInvoicesFunction:
    """Tests for the convenience analyze_invoices function."""
    
    def test_analyze_invoices_basic(self):
        """Test basic usage of analyze_invoices function."""
        pattern = parse_pattern("TEST/[001]")
        processor = InvoiceProcessor(pattern)
        
        invoices = [
            processor.process_invoice("TEST/001"),
            processor.process_invoice("TEST/002"),
        ]
        
        series_groups = {"TEST/{SEQ}": invoices}
        
        result = analyze_invoices(
            pattern, series_groups, [], [], "Test Documents"
        )
        
        assert len(result.series_results) == 1


class TestTable13Row:
    """Tests for Table13Row model."""
    
    def test_to_list(self):
        """Test conversion to list."""
        from src.core.models import Table13Row
        
        row = Table13Row(
            nature_of_document="Invoices",
            sr_no_from="INV/001",
            sr_no_to="INV/010",
            total_number=10,
            cancelled=2,
            net_issued=8
        )
        
        result = row.to_list()
        
        assert result == ["Invoices", "INV/001", "INV/010", 10, 2, 8]
    
    def test_to_tsv(self):
        """Test conversion to TSV."""
        from src.core.models import Table13Row
        
        row = Table13Row(
            nature_of_document="Invoices",
            sr_no_from="INV/001",
            sr_no_to="INV/010",
            total_number=10,
            cancelled=2,
            net_issued=8
        )
        
        result = row.to_tsv()
        
        assert "\t" in result
        parts = result.split("\t")
        assert len(parts) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
