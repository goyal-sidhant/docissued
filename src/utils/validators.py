"""
Validators for GSTR-1 Table 13 Generator.

Provides validation functions for user inputs.
"""

import re
from typing import Tuple, List


def validate_pattern_input(pattern: str) -> Tuple[bool, str]:
    """
    Validate the pattern input string.
    
    Args:
        pattern: User-provided pattern string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern or not pattern.strip():
        return False, "Pattern cannot be empty"
    
    pattern = pattern.strip()
    
    # Check for sequence marker
    sequence_pattern = re.compile(r'\[(\d+)\]')
    matches = sequence_pattern.findall(pattern)
    
    if len(matches) == 0:
        return False, "Pattern must contain a sequence marker [NNN]. Example: GST/24-25/[001]"
    
    if len(matches) > 1:
        return False, "Pattern can only have one sequence marker [NNN]"
    
    # Validate sequence content
    seq_content = matches[0]
    if not seq_content:
        return False, "Sequence marker cannot be empty. Use digits like [001]"
    
    if not seq_content.isdigit():
        return False, "Sequence marker must contain only digits"
    
    # Check for unbalanced brackets
    open_brackets = pattern.count('[')
    close_brackets = pattern.count(']')
    
    if open_brackets != close_brackets:
        return False, "Unbalanced brackets in pattern"
    
    if open_brackets > 1:
        return False, "Only one pair of square brackets allowed for sequence marker"
    
    return True, ""


def validate_invoice_list(text: str) -> Tuple[bool, str, int]:
    """
    Validate the invoice list input.
    
    Args:
        text: Raw text with invoices
        
    Returns:
        Tuple of (is_valid, error_message, line_count)
    """
    if not text or not text.strip():
        return False, "Invoice list cannot be empty", 0
    
    # Split and count non-empty lines
    lines = [line.strip() for line in text.replace('\r\n', '\n').split('\n')]
    non_empty_lines = [line for line in lines if line]
    
    line_count = len(non_empty_lines)
    
    if line_count == 0:
        return False, "Invoice list contains no valid entries", 0
    
    return True, "", line_count


def validate_document_nature(nature: str, valid_natures: List[str]) -> Tuple[bool, str]:
    """
    Validate the selected document nature.
    
    Args:
        nature: Selected document nature
        valid_natures: List of valid document nature values
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not nature:
        return False, "Please select a document nature"
    
    if nature not in valid_natures:
        return False, f"Invalid document nature: {nature}"
    
    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially problematic characters.
    
    Args:
        text: Raw input text
        
    Returns:
        Sanitized text
    """
    # Remove null bytes and other control characters (except newlines and tabs)
    sanitized = ''.join(
        char for char in text 
        if char == '\n' or char == '\t' or char == '\r' or (ord(char) >= 32 and ord(char) < 127) or ord(char) > 127
    )
    
    return sanitized


def count_lines(text: str) -> int:
    """
    Count non-empty lines in text.
    
    Args:
        text: Input text
        
    Returns:
        Number of non-empty lines
    """
    if not text:
        return 0
    
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return sum(1 for line in lines if line.strip())
