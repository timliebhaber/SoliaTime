"""Mehrwertsteuer (VAT) Calculator ViewModel."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QObject, Signal


class VatCalculatorViewModel(QObject):
    """ViewModel for the VAT calculator view.
    
    Handles calculation logic for Netto, MwSt (VAT), and Brutto values.
    """
    
    # Signals to notify view of value changes
    values_changed = Signal(str, str, str)  # netto, mwst, brutto as formatted strings
    
    # Standard German VAT rates
    VAT_RATES = [Decimal("19"), Decimal("7")]
    
    def __init__(self) -> None:
        """Initialize VAT calculator ViewModel."""
        super().__init__()
        self._netto = Decimal("0")
        self._mwst = Decimal("0")
        self._brutto = Decimal("0")
        self._vat_rate = Decimal("19")  # Default 19%
    
    @property
    def vat_rate(self) -> Decimal:
        """Get current VAT rate."""
        return self._vat_rate
    
    @vat_rate.setter
    def vat_rate(self, value: Decimal) -> None:
        """Set VAT rate and recalculate from current netto."""
        self._vat_rate = value
        # Recalculate based on current netto value
        if self._netto > 0:
            self.calculate_from_netto(self._format_value(self._netto))
    
    def toggle_vat_rate(self) -> Decimal:
        """Toggle between 19% and 7% VAT rates.
        
        Returns:
            The new VAT rate.
        """
        if self._vat_rate == Decimal("19"):
            self.vat_rate = Decimal("7")
        else:
            self.vat_rate = Decimal("19")
        return self._vat_rate
    
    def _parse_value(self, value: str) -> Decimal:
        """Parse a string value to Decimal, handling German number format.
        
        Args:
            value: String value (may use comma as decimal separator)
            
        Returns:
            Parsed Decimal value, or 0 if invalid.
        """
        if not value or not value.strip():
            return Decimal("0")
        
        # Replace comma with dot for German format
        cleaned = value.strip().replace(",", ".")
        
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return Decimal("0")
    
    def _format_value(self, value: Decimal) -> str:
        """Format a Decimal value to German number format.
        
        Args:
            value: Decimal value to format
            
        Returns:
            Formatted string with comma as decimal separator.
        """
        # Round to 2 decimal places and format with comma
        rounded = value.quantize(Decimal("0.01"))
        return str(rounded).replace(".", ",")
    
    def _emit_values(self) -> None:
        """Emit current values as formatted strings."""
        self.values_changed.emit(
            self._format_value(self._netto),
            self._format_value(self._mwst),
            self._format_value(self._brutto)
        )
    
    def calculate_from_netto(self, netto_str: str) -> None:
        """Calculate MwSt and Brutto from Netto value.
        
        Args:
            netto_str: Netto value as string
        """
        self._netto = self._parse_value(netto_str)
        rate_decimal = self._vat_rate / Decimal("100")
        
        self._mwst = self._netto * rate_decimal
        self._brutto = self._netto + self._mwst
        
        self._emit_values()
    
    def calculate_from_mwst(self, mwst_str: str) -> None:
        """Calculate Netto and Brutto from MwSt value.
        
        Args:
            mwst_str: MwSt value as string
        """
        self._mwst = self._parse_value(mwst_str)
        rate_decimal = self._vat_rate / Decimal("100")
        
        if rate_decimal > 0:
            self._netto = self._mwst / rate_decimal
        else:
            self._netto = Decimal("0")
        
        self._brutto = self._netto + self._mwst
        
        self._emit_values()
    
    def calculate_from_brutto(self, brutto_str: str) -> None:
        """Calculate Netto and MwSt from Brutto value.
        
        Args:
            brutto_str: Brutto value as string
        """
        self._brutto = self._parse_value(brutto_str)
        rate_decimal = self._vat_rate / Decimal("100")
        
        divisor = Decimal("1") + rate_decimal
        self._netto = self._brutto / divisor
        self._mwst = self._brutto - self._netto
        
        self._emit_values()
    
    def clear(self) -> None:
        """Reset all values to zero."""
        self._netto = Decimal("0")
        self._mwst = Decimal("0")
        self._brutto = Decimal("0")
        self._emit_values()
