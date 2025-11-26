"""Mehrwertsteuer (VAT) Calculator view - Coming Soon placeholder."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from src.viewmodels import VatCalculatorViewModel


class VatCalculatorView(QWidget):
    """VAT Calculator view - placeholder for future functionality.
    
    Pure UI component - delegates all actions to ViewModel.
    """

    def __init__(self, viewmodel: "VatCalculatorViewModel", parent: QWidget | None = None) -> None:
        """Initialize VAT calculator view.
        
        Args:
            viewmodel: VAT Calculator ViewModel
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._build_ui()

    def _build_ui(self) -> None:
        """Build the UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title_label = QLabel("🧮 Mehrwertsteuer Calculator")
        title_font = title_label.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        # Coming Soon message
        coming_soon = QLabel("Coming Soon")
        coming_soon_font = coming_soon.font()
        coming_soon_font.setPointSize(18)
        coming_soon.setFont(coming_soon_font)
        coming_soon.setAlignment(Qt.AlignCenter)
        coming_soon.setStyleSheet("color: #888;")
        layout.addWidget(coming_soon)
        
        layout.addStretch()

