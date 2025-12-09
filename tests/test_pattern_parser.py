"""
Tests for pattern_parser module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.pattern_parser import PatternParser, parse_pattern


class TestPatternParser:
    """Tests for PatternParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PatternParser()
    
    # Valid pattern tests
    
    def test_simple_pattern_with_prefix(self):
        """Test simple pattern with prefix."""
        result = self.parser.parse("GST/24-25/[0001]")
        
        assert result.is_valid
        assert result.sequence_length == 4
        assert result.wildcard_count == 0
        assert len(result.parts) == 2  # fixed + sequence
    
    def test_pattern_with_suffix(self):
        """Test pattern with suffix."""
        result = self.parser.parse("[001]-SAL-2024")
        
        assert result.is_valid
        assert result.sequence_length == 3
        assert result.parts[0] == ('sequence', '001')
        assert result.parts[1] == ('fixed', '-SAL-2024')
    
    def test_pattern_with_prefix_and_suffix(self):
        """Test pattern with both prefix and suffix."""
        result = self.parser.parse("INV/[00001]/A")
        
        assert result.is_valid
        assert result.sequence_length == 5
        assert result.parts[0] == ('fixed', 'INV/')
        assert result.parts[1] == ('sequence', '00001')
        assert result.parts[2] == ('fixed', '/A')
    
    def test_bare_sequence(self):
        """Test pattern with just sequence number."""
        result = self.parser.parse("[001]")
        
        assert result.is_valid
        assert result.sequence_length == 3
        assert len(result.parts) == 1
    
    def test_pattern_with_wildcard(self):
        """Test pattern with wildcard."""
        result = self.parser.parse("GST/*/[001]")
        
        assert result.is_valid
        assert result.wildcard_count == 1
        assert result.parts[0] == ('fixed', 'GST/')
        assert result.parts[1] == ('wildcard', '*')
        assert result.parts[2] == ('fixed', '/')
        assert result.parts[3] == ('sequence', '001')
    
    def test_pattern_with_multiple_wildcards(self):
        """Test pattern with multiple wildcards."""
        result = self.parser.parse("*/INV/[0001]/*")
        
        assert result.is_valid
        assert result.wildcard_count == 2
    
    def test_pattern_with_special_chars(self):
        """Test pattern with special characters allowed in Rule 46."""
        result = self.parser.parse("GST-2024/25/[001]")
        
        assert result.is_valid
    
    # Invalid pattern tests
    
    def test_empty_pattern(self):
        """Test empty pattern."""
        result = self.parser.parse("")
        
        assert not result.is_valid
        assert "empty" in result.error_message.lower()
    
    def test_whitespace_only_pattern(self):
        """Test whitespace-only pattern."""
        result = self.parser.parse("   ")
        
        assert not result.is_valid
    
    def test_pattern_without_sequence(self):
        """Test pattern without sequence marker."""
        result = self.parser.parse("GST/24-25/0001")
        
        assert not result.is_valid
        assert "sequence marker" in result.error_message.lower()
    
    def test_pattern_with_multiple_sequences(self):
        """Test pattern with multiple sequence markers."""
        result = self.parser.parse("GST/[001]/[002]")
        
        assert not result.is_valid
        assert "one sequence marker" in result.error_message.lower() or "multiple" in result.error_message.lower()
    
    def test_pattern_with_non_numeric_sequence(self):
        """Test pattern with non-numeric sequence content."""
        result = self.parser.parse("GST/[ABC]")
        
        assert not result.is_valid
    
    # Regex pattern tests
    
    def test_regex_pattern_simple(self):
        """Test regex pattern generation for simple pattern."""
        result = self.parser.parse("INV-[001]")
        
        assert result.is_valid
        assert "(?P<seq>" in result.regex_pattern
        assert result.regex_pattern.startswith("^")
        assert result.regex_pattern.endswith("$")
    
    def test_regex_pattern_with_wildcard(self):
        """Test regex pattern generation with wildcard."""
        result = self.parser.parse("GST/*/[001]")
        
        assert result.is_valid
        assert "(?P<wc0>" in result.regex_pattern
        assert "(?P<seq>" in result.regex_pattern


class TestParsePatternFunction:
    """Tests for the convenience parse_pattern function."""
    
    def test_parse_pattern_valid(self):
        """Test parse_pattern with valid input."""
        result = parse_pattern("TEST/[001]")
        
        assert result.is_valid
    
    def test_parse_pattern_invalid(self):
        """Test parse_pattern with invalid input."""
        result = parse_pattern("invalid")
        
        assert not result.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
