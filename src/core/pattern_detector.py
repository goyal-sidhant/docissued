"""
Pattern Detector - Auto-detect invoice pattern from a list of invoices.

Analyzes invoice numbers to find:
- Common prefix and suffix
- Sequence number position
- Whether sequences are padded or not
"""

from typing import List, Tuple, Optional
import re
from collections import Counter


def detect_pattern(invoices: List[str]) -> Tuple[Optional[str], str]:
    """
    Auto-detect invoice pattern from a list of invoice numbers.
    
    Args:
        invoices: List of invoice number strings
        
    Returns:
        Tuple of (detected_pattern, message)
        If detection fails, pattern is None and message explains why
    """
    # Clean and filter
    clean_invoices = [inv.strip() for inv in invoices if inv.strip()]
    
    if len(clean_invoices) < 2:
        return None, "Need at least 2 invoices to detect pattern"
    
    # Remove duplicates but preserve order
    seen = set()
    unique_invoices = []
    for inv in clean_invoices:
        if inv not in seen:
            seen.add(inv)
            unique_invoices.append(inv)
    
    if len(unique_invoices) < 2:
        return None, "Need at least 2 unique invoices to detect pattern"
    
    # Try to detect pattern
    pattern, confidence = _analyze_invoices(unique_invoices)
    
    if pattern:
        return pattern, f"Detected pattern with {confidence}% confidence"
    else:
        return None, "Could not detect a consistent pattern. Please enter manually."


def _analyze_invoices(invoices: List[str]) -> Tuple[Optional[str], int]:
    """
    Analyze invoices to find the pattern.
    
    Returns (pattern, confidence_percentage)
    """
    # Find numeric sequences in each invoice
    invoice_parts = []
    for inv in invoices:
        parts = _split_into_parts(inv)
        if parts:
            invoice_parts.append((inv, parts))
    
    if len(invoice_parts) < 2:
        return None, 0
    
    # Find which numeric position varies (the sequence number)
    first_parts = invoice_parts[0][1]
    
    # Count numeric parts
    numeric_indices = [i for i, (ptype, _) in enumerate(first_parts) if ptype == 'num']
    
    if not numeric_indices:
        return None, 0
    
    # Check which numeric part varies across invoices
    varying_index = None
    for num_idx in numeric_indices:
        values = set()
        for _, parts in invoice_parts:
            if num_idx < len(parts) and parts[num_idx][0] == 'num':
                values.add(parts[num_idx][1])
        
        if len(values) > 1:
            # This numeric field varies
            if varying_index is None:
                varying_index = num_idx
            else:
                # Multiple varying numeric fields - ambiguous
                return None, 0
    
    if varying_index is None:
        return None, 0
    
    # Verify non-varying parts are consistent
    fixed_parts_match = True
    reference_parts = first_parts
    
    for _, parts in invoice_parts[1:]:
        if len(parts) != len(reference_parts):
            fixed_parts_match = False
            break
        
        for i, (ptype, val) in enumerate(parts):
            if i == varying_index:
                continue
            if i >= len(reference_parts):
                fixed_parts_match = False
                break
            ref_type, ref_val = reference_parts[i]
            if ptype != ref_type or val != ref_val:
                fixed_parts_match = False
                break
    
    if not fixed_parts_match:
        # Try grouping by structure for multi-series detection
        return _detect_multi_series_pattern(invoices)
    
    # Build pattern
    pattern_parts = []
    seq_values = []
    
    for i, (ptype, val) in enumerate(reference_parts):
        if i == varying_index:
            # Collect all sequence values to determine padding
            for _, parts in invoice_parts:
                if i < len(parts):
                    seq_values.append(parts[i][1])
            
            # Determine padding
            is_padded = any(v.startswith('0') and len(v) > 1 for v in seq_values)
            if is_padded:
                max_len = max(len(v) for v in seq_values)
                pattern_parts.append(f"[{'0' * max_len}]")
            else:
                pattern_parts.append("[1]")
        else:
            pattern_parts.append(val)
    
    pattern = ''.join(pattern_parts)
    
    # Calculate confidence based on sample size and consistency
    confidence = min(95, 50 + len(invoice_parts) * 5)
    
    return pattern, confidence


def _detect_multi_series_pattern(invoices: List[str]) -> Tuple[Optional[str], int]:
    """
    Detect pattern when multiple series are present.
    Uses wildcard (*) for varying non-sequence parts.
    """
    # Group invoices by structure (length and position of numbers)
    structure_groups = {}
    
    for inv in invoices:
        structure = _get_structure_key(inv)
        if structure not in structure_groups:
            structure_groups[structure] = []
        structure_groups[structure].append(inv)
    
    # If we have multiple structure groups, try to find common pattern
    if len(structure_groups) > 1:
        # Try character-by-character comparison across ALL invoices
        return _detect_pattern_with_wildcards(invoices)
    
    # Take the largest group
    if not structure_groups:
        return None, 0
    
    main_group = max(structure_groups.values(), key=len)
    
    if len(main_group) < 2:
        return None, 0
    
    # Analyze the main group to find varying positions
    parts_list = [_split_into_parts(inv) for inv in main_group]
    
    if not all(parts_list):
        return None, 0
    
    # All should have same length
    ref_len = len(parts_list[0])
    if not all(len(p) == ref_len for p in parts_list):
        return None, 0
    
    # Find which positions vary
    varying_positions = set()
    seq_position = None
    
    for pos in range(ref_len):
        values = [p[pos][1] for p in parts_list]
        unique_values = set(values)
        
        if len(unique_values) > 1:
            varying_positions.add(pos)
            # Check if this is numeric (potential sequence)
            if parts_list[0][pos][0] == 'num':
                # Check if values look like a sequence (incrementing)
                try:
                    nums = [int(v) for v in values]
                    if len(set(nums)) == len(nums):  # All unique
                        seq_position = pos
                except ValueError:
                    pass
    
    if seq_position is None:
        return None, 0
    
    # Build pattern with wildcards
    pattern_parts = []
    seq_values = [p[seq_position][1] for p in parts_list]
    
    for i, (ptype, val) in enumerate(parts_list[0]):
        if i == seq_position:
            is_padded = any(v.startswith('0') and len(v) > 1 for v in seq_values)
            if is_padded:
                max_len = max(len(v) for v in seq_values)
                pattern_parts.append(f"[{'0' * max_len}]")
            else:
                pattern_parts.append("[1]")
        elif i in varying_positions:
            pattern_parts.append("*")
        else:
            pattern_parts.append(val)
    
    pattern = ''.join(pattern_parts)
    
    # Lower confidence for multi-series
    confidence = min(80, 40 + len(main_group) * 3)
    
    return pattern, confidence


def _detect_pattern_with_wildcards(invoices: List[str]) -> Tuple[Optional[str], int]:
    """
    Detect pattern by character-by-character analysis with wildcards.
    Used when invoices have different structures but common elements.
    """
    if len(invoices) < 2:
        return None, 0
    
    # Find shortest and longest invoice
    min_len = min(len(inv) for inv in invoices)
    
    # Character-by-character analysis
    pattern_chars = []
    i = 0
    
    while i < min_len:
        # Get character at position i from all invoices
        chars_at_pos = [inv[i] for inv in invoices]
        unique_chars = set(chars_at_pos)
        
        if len(unique_chars) == 1:
            # All same - fixed character
            pattern_chars.append(chars_at_pos[0])
            i += 1
        else:
            # Characters differ - could be wildcard or sequence
            # Check if all are digits
            all_digits = all(c.isdigit() for c in chars_at_pos)
            
            if all_digits:
                # Find the extent of this numeric section
                num_start = i
                while i < min_len and all(inv[i].isdigit() for inv in invoices):
                    i += 1
                num_end = i
                
                # Extract numbers from this section
                nums = []
                for inv in invoices:
                    num_str = inv[num_start:num_end]
                    # Extend if invoice is longer and has more digits
                    while num_end < len(inv) and inv[num_end].isdigit():
                        num_str += inv[num_end]
                        num_end += 1
                    nums.append(num_str)
                
                # Check if these look like sequence numbers
                try:
                    int_nums = [int(n) for n in nums]
                    if len(set(int_nums)) > 1:  # Values differ
                        is_padded = any(n.startswith('0') and len(n) > 1 for n in nums)
                        if is_padded:
                            max_len = max(len(n) for n in nums)
                            pattern_chars.append(f"[{'0' * max_len}]")
                        else:
                            pattern_chars.append("[1]")
                    else:
                        # All same number - just use the value
                        pattern_chars.append(nums[0])
                except ValueError:
                    pattern_chars.append("*")
            else:
                # Not all digits - this is a wildcard section
                # Find where this section ends (next common character)
                wildcard_start = i
                while i < min_len:
                    chars_at_pos = [inv[i] for inv in invoices]
                    if len(set(chars_at_pos)) == 1 and not chars_at_pos[0].isalnum():
                        # Found common delimiter
                        break
                    i += 1
                
                pattern_chars.append("*")
    
    pattern = ''.join(pattern_chars)
    
    # Simplify pattern - merge adjacent wildcards
    while '**' in pattern:
        pattern = pattern.replace('**', '*')
    
    # Validate pattern has a sequence marker
    if '[' not in pattern:
        return None, 0
    
    confidence = min(70, 30 + len(invoices) * 5)
    
    return pattern, confidence


def _split_into_parts(invoice: str) -> List[Tuple[str, str]]:
    """
    Split invoice into alternating text and numeric parts.
    
    Returns list of (type, value) where type is 'text' or 'num'
    """
    parts = []
    pattern = r'(\d+|\D+)'
    
    for match in re.findall(pattern, invoice):
        if match.isdigit():
            parts.append(('num', match))
        else:
            parts.append(('text', match))
    
    return parts


def _get_structure_key(invoice: str) -> str:
    """Get a structure key for grouping similar invoices."""
    parts = _split_into_parts(invoice)
    # Key is the pattern of text/num with text values (num replaced with placeholder)
    key_parts = []
    for ptype, val in parts:
        if ptype == 'text':
            key_parts.append(f"T:{val}")
        else:
            key_parts.append(f"N:{len(val)}")
    return '|'.join(key_parts)
