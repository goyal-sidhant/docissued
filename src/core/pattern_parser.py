"""
Pattern Parser for GSTR-1 Table 13 Generator.

Parses user-defined invoice patterns with bracket notation for sequence
and wildcard notation for variable series identifiers.

Pattern Notation:
    [NNN]  - Sequence marker (exactly one required)
             The content defines expected padding (e.g., [001] = 3 digits)
    *      - Wildcard marker (zero or more allowed)
             Matches any characters, used to identify sub-series

Examples:
    GST/24-25/[0001]     -> Simple pattern, 4-digit sequence
    GST/*/[001]          -> Wildcard for sub-series, 3-digit sequence
    */INV/[00001]/*      -> Multiple wildcards
    [001]-SAL            -> Sequence first, then suffix
"""

import re
from typing import Tuple, Optional
from .models import ParsedPattern


class PatternParser:
    """Parses invoice patterns into structured format for matching."""
    
    # Regex to find sequence marker [NNN]
    SEQUENCE_PATTERN = re.compile(r'\[(\d+)\]')
    
    # Regex to find wildcard marker *
    WILDCARD_PATTERN = re.compile(r'\*')
    
    def __init__(self):
        self._last_error: str = ""
    
    @property
    def last_error(self) -> str:
        """Return the last error message."""
        return self._last_error
    
    def parse(self, pattern: str) -> ParsedPattern:
        """
        Parse a pattern string into a ParsedPattern object.
        
        Args:
            pattern: User-provided pattern like "GST/*/[001]"
            
        Returns:
            ParsedPattern object with parsed components
        """
        result = ParsedPattern(raw_pattern=pattern)
        
        # Validate pattern is not empty
        if not pattern or not pattern.strip():
            result.error_message = "Pattern cannot be empty"
            return result
        
        pattern = pattern.strip()
        
        # Find sequence markers
        sequence_matches = list(self.SEQUENCE_PATTERN.finditer(pattern))
        
        # Validate exactly one sequence marker
        if len(sequence_matches) == 0:
            result.error_message = "Pattern must contain exactly one sequence marker [NNN]. Example: GST/[001]"
            return result
        
        if len(sequence_matches) > 1:
            result.error_message = "Pattern must contain only one sequence marker [NNN], found multiple"
            return result
        
        # Extract sequence info
        seq_match = sequence_matches[0]
        seq_content = seq_match.group(1)
        
        # Validate sequence content is numeric
        if not seq_content.isdigit():
            result.error_message = f"Sequence marker must contain only digits, found: [{seq_content}]"
            return result
        
        result.sequence_length = len(seq_content)
        
        # Count wildcards
        wildcard_matches = list(self.WILDCARD_PATTERN.finditer(pattern))
        result.wildcard_count = len(wildcard_matches)
        
        # Build parts list by parsing the pattern
        result.parts = self._build_parts(pattern, seq_match, wildcard_matches)
        
        # Build regex pattern for matching invoices
        result.regex_pattern = self._build_regex(result.parts, result.sequence_length)
        
        result.is_valid = True
        return result
    
    def _build_parts(self, pattern: str, seq_match, wildcard_matches) -> list:
        """
        Build a list of parts from the pattern.
        
        Each part is a tuple of (type, value) where type is:
        - 'fixed': Literal text that must match exactly
        - 'wildcard': Variable text (series identifier)
        - 'sequence': The incrementing number
        """
        parts = []
        
        # Create a list of all markers with their positions and types
        markers = []
        
        # Add sequence marker
        markers.append({
            'start': seq_match.start(),
            'end': seq_match.end(),
            'type': 'sequence',
            'value': seq_match.group(1)
        })
        
        # Add wildcard markers
        for wm in wildcard_matches:
            markers.append({
                'start': wm.start(),
                'end': wm.end(),
                'type': 'wildcard',
                'value': '*'
            })
        
        # Sort markers by position
        markers.sort(key=lambda x: x['start'])
        
        # Build parts by iterating through the pattern
        current_pos = 0
        
        for marker in markers:
            # Add fixed part before this marker (if any)
            if marker['start'] > current_pos:
                fixed_text = pattern[current_pos:marker['start']]
                if fixed_text:
                    parts.append(('fixed', fixed_text))
            
            # Add the marker
            parts.append((marker['type'], marker['value']))
            
            current_pos = marker['end']
        
        # Add any remaining fixed part after the last marker
        if current_pos < len(pattern):
            fixed_text = pattern[current_pos:]
            if fixed_text:
                parts.append(('fixed', fixed_text))
        
        return parts
    
    def _build_regex(self, parts: list, seq_length: int) -> str:
        """
        Build a regex pattern from parsed parts.
        
        The regex will have named groups:
        - seq: for the sequence number
        - wc0, wc1, ...: for wildcard values
        """
        regex_parts = []
        wildcard_index = 0
        
        for part_type, value in parts:
            if part_type == 'fixed':
                # Escape special regex characters in fixed text
                regex_parts.append(re.escape(value))
            
            elif part_type == 'wildcard':
                # Wildcard matches one or more non-separator characters
                # Using .+? (non-greedy) to match minimally
                # But we need to be smarter - match until next fixed part
                regex_parts.append(f'(?P<wc{wildcard_index}>.+?)')
                wildcard_index += 1
            
            elif part_type == 'sequence':
                # Sequence matches digits, with flexible length
                # We capture it for extraction
                regex_parts.append(f'(?P<seq>\\d+)')
        
        # Combine into full pattern with start/end anchors
        full_regex = '^' + ''.join(regex_parts) + '$'
        
        return full_regex
    
    def validate_pattern(self, pattern: str) -> Tuple[bool, str]:
        """
        Validate a pattern string.
        
        Args:
            pattern: User-provided pattern
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        parsed = self.parse(pattern)
        return (parsed.is_valid, parsed.error_message)
    
    def get_pattern_description(self, parsed: ParsedPattern) -> str:
        """
        Generate a human-readable description of the pattern.
        
        Args:
            parsed: A ParsedPattern object
            
        Returns:
            Description string
        """
        if not parsed.is_valid:
            return f"Invalid pattern: {parsed.error_message}"
        
        parts_desc = []
        for part_type, value in parsed.parts:
            if part_type == 'fixed':
                parts_desc.append(f'"{value}"')
            elif part_type == 'wildcard':
                parts_desc.append('[variable part - series identifier]')
            elif part_type == 'sequence':
                parts_desc.append(f'[{parsed.sequence_length}-digit sequence number]')
        
        desc = " + ".join(parts_desc)
        
        if parsed.wildcard_count > 0:
            desc += f"\n\nThis pattern has {parsed.wildcard_count} wildcard(s), so invoices will be grouped into separate series based on the variable part(s)."
        
        return desc


# Module-level convenience function
def parse_pattern(pattern: str) -> ParsedPattern:
    """Parse a pattern string into a ParsedPattern object."""
    parser = PatternParser()
    return parser.parse(pattern)
