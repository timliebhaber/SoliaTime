"""Formatting and parsing utilities for time, currency, and other data types."""
from __future__ import annotations

import time
from typing import Optional


def format_duration(seconds: int) -> str:
    """Format duration in seconds as HH:MM:SS string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "02:30:15"
    """
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_timestamp(ts: int, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format Unix timestamp as human-readable string.
    
    Args:
        ts: Unix timestamp in seconds
        fmt: strftime format string
        
    Returns:
        Formatted timestamp string
    """
    return time.strftime(fmt, time.localtime(ts))


def parse_time_input(text: str) -> Optional[int]:
    """Parse time input in HH:MM or hours format to seconds.
    
    Args:
        text: Input string like "02:30" or "2"
        
    Returns:
        Time in seconds, or None if invalid
    """
    text = text.strip()
    if not text:
        return None
    try:
        if ":" in text:
            hh, mm = text.split(":", 1)
            hours = int(hh)
            minutes = int(mm)
        else:
            hours = int(text)
            minutes = 0
        if hours < 0 or minutes < 0 or minutes >= 60:
            return None
        return hours * 3600 + minutes * 60
    except Exception:
        return None


def parse_rate_input(text: str) -> Optional[int]:
    """Parse currency rate input to cents.
    
    Accepts formats: "85", "85,5", "85,50", "85.50"
    
    Args:
        text: Input string representing currency amount
        
    Returns:
        Amount in cents, or None if invalid
    """
    text = text.strip()
    if not text:
        return None
    
    # Normalize: remove spaces, €, and convert . to ,
    norm = text.replace(" ", "").replace("€", "").replace(".", ",")
    
    try:
        if "," in norm:
            left, right = norm.split(",", 1)
            euros = int(left) if left else 0
            # Pad/truncate to 2 decimals
            right2 = (right + "00")[:2]
            cents = int(right2)
        else:
            euros = int(norm)
            cents = 0
        
        if euros < 0 or cents < 0 or cents >= 100:
            return None
        
        return euros * 100 + cents
    except Exception:
        return None


def format_rate(cents: int) -> str:
    """Format rate in cents as currency string.
    
    Args:
        cents: Amount in cents
        
    Returns:
        Formatted string like "85,50 €"
    """
    euros = cents // 100
    cent_part = cents % 100
    return f"{euros},{cent_part:02d} €"


def format_time_hhmm(seconds: int) -> str:
    """Format seconds as HH:MM string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string like "02:30"
    """
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"


def parse_timestamp(text: str) -> Optional[int]:
    """Parse timestamp string to Unix timestamp.
    
    Args:
        text: Timestamp string in format "YYYY-MM-DD HH:MM:SS"
        
    Returns:
        Unix timestamp in seconds, or None if invalid
    """
    text = text.strip()
    if not text or text == "—":
        return None
    try:
        return int(time.mktime(time.strptime(text, "%Y-%m-%d %H:%M:%S")))
    except Exception:
        return None
