"""
Financial Year (FY) Utilities - Handle Indian FY calculations.

Indian Financial Year runs from April 1 to March 31.
Tax Period format: MMYYYY (e.g., "042024" for April 2024, "032025" for March 2025)
"""

from datetime import datetime
from typing import Tuple, Optional


def parse_tax_period(tax_period: str) -> Tuple[int, int]:
    """
    Parse tax period string to (month, year).

    Args:
        tax_period: String in format MMYYYY (e.g., "042024", "122024")

    Returns:
        Tuple of (month, year)

    Raises:
        ValueError: If tax period format is invalid
    """
    if not tax_period or len(tax_period) != 6:
        raise ValueError(f"Tax period must be in MMYYYY format. Got: {tax_period}")

    try:
        month = int(tax_period[:2])
        year = int(tax_period[2:])
    except ValueError:
        raise ValueError(f"Tax period must be numeric. Got: {tax_period}")

    if not (1 <= month <= 12):
        raise ValueError(f"Invalid month in tax period: {month}")

    if not (2000 <= year <= 2100):
        raise ValueError(f"Invalid year in tax period: {year}")

    return month, year


def get_fy_from_tax_period(tax_period: str) -> str:
    """
    Get Financial Year from tax period.

    Indian FY runs from April to March:
    - April 2024 to March 2025 = FY 2024-25

    Args:
        tax_period: String in format MMYYYY (e.g., "042024")

    Returns:
        FY string like "2024-25"
    """
    month, year = parse_tax_period(tax_period)

    if month >= 4:  # April onwards
        fy_start = year
        fy_end = year + 1
    else:  # January to March
        fy_start = year - 1
        fy_end = year

    return f"{fy_start}-{str(fy_end)[-2:]}"


def are_same_fy(tax_period1: str, tax_period2: str) -> bool:
    """
    Check if two tax periods are in the same Financial Year.

    Args:
        tax_period1: First tax period (MMYYYY format)
        tax_period2: Second tax period (MMYYYY format)

    Returns:
        True if both periods are in same FY
    """
    try:
        fy1 = get_fy_from_tax_period(tax_period1)
        fy2 = get_fy_from_tax_period(tax_period2)
        return fy1 == fy2
    except ValueError:
        return False


def format_tax_period_display(tax_period: str) -> str:
    """
    Format tax period for display.

    Args:
        tax_period: Tax period in MMYYYY format (e.g., "042024")

    Returns:
        Display string like "April 2024"
    """
    try:
        month, year = parse_tax_period(tax_period)
        month_names = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return f"{month_names[month]} {year}"
    except ValueError:
        return tax_period


def parse_display_to_tax_period(display: str) -> str:
    """
    Convert display format to tax period format.

    Args:
        display: Display string like "April 2024"

    Returns:
        Tax period string like "042024"

    Raises:
        ValueError: If format is invalid
    """
    parts = display.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid display format. Expected 'Month YYYY'. Got: {display}")

    month_name, year_str = parts

    month_names = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }

    month = month_names.get(month_name.lower())
    if month is None:
        raise ValueError(f"Invalid month name: {month_name}")

    try:
        year = int(year_str)
    except ValueError:
        raise ValueError(f"Invalid year: {year_str}")

    return f"{month:02d}{year}"


def get_current_tax_period() -> str:
    """
    Get current tax period based on system date.

    Returns:
        Current tax period in MMYYYY format
    """
    now = datetime.now()
    return f"{now.month:02d}{now.year}"


def get_recent_tax_periods(count: int = 24) -> list:
    """
    Get list of recent tax periods for dropdown.

    Args:
        count: Number of months to include (default 24 = 2 years)

    Returns:
        List of (display_text, tax_period) tuples, newest first
    """
    periods = []
    current = datetime.now()
    year = current.year
    month = current.month

    for i in range(count):
        tax_period = f"{month:02d}{year}"
        display = format_tax_period_display(tax_period)
        periods.append((display, tax_period))

        # Go back one month
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    return periods


def is_fy_boundary(tax_period: str) -> bool:
    """
    Check if tax period is April (FY boundary month).

    Args:
        tax_period: Tax period in MMYYYY format

    Returns:
        True if month is April (start of new FY)
    """
    try:
        month, _ = parse_tax_period(tax_period)
        return month == 4
    except ValueError:
        return False
