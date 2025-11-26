"""Mehrwertsteuer (VAT) Calculator view."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.viewmodels import VatCalculatorViewModel


class VatCalculatorView(QWidget):
    """VAT Calculator view with Netto, MwSt, and Brutto fields.
    
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
        self._updating = False  # Prevent recursive updates
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Build the UI components."""
        # Main layout centers the content container
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Fixed-width container to keep UI together
        container = QWidget()
        container.setFixedWidth(500)
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 40, 20, 40)
        
        # Input fields row
        fields_widget = self._build_input_fields()
        layout.addWidget(fields_widget, alignment=Qt.AlignCenter)
        
        layout.addSpacing(20)
        
        # VAT rate selector
        rate_widget = self._build_rate_selector()
        layout.addWidget(rate_widget, alignment=Qt.AlignCenter)
        
        layout.addSpacing(20)
        
        # Calculate button
        self.calculate_btn = QPushButton("Berechnen")
        self.calculate_btn.setMinimumHeight(50)
        self.calculate_btn.setMinimumWidth(300)
        self.calculate_btn.setCursor(Qt.PointingHandCursor)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b5998;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
                padding: 12px 40px;
            }
            QPushButton:hover {
                background-color: #4a69ad;
            }
            QPushButton:pressed {
                background-color: #2d4373;
            }
        """)
        layout.addWidget(self.calculate_btn, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(container)

    def _build_input_fields(self) -> QWidget:
        """Build the three input fields with labels and operators."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)
        
        input_style = """
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 16px;
                min-width: 100px;
                max-width: 140px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border-color: #3b5998;
            }
        """
        
        label_style = """
            QLabel {
                font-size: 14px;
                color: black;
                font-weight: 500;
            }
        """
        
        operator_style = """
            QLabel {
                font-size: 20px;
                color: black;
                padding: 0 8px;
            }
        """
        
        # Netto field
        netto_container = QWidget()
        netto_layout = QVBoxLayout(netto_container)
        netto_layout.setSpacing(4)
        netto_layout.setContentsMargins(0, 0, 0, 0)
        
        netto_label = QLabel("Netto:")
        netto_label.setStyleSheet(label_style)
        netto_label.setAlignment(Qt.AlignCenter)
        netto_layout.addWidget(netto_label)
        
        self.netto_input = QLineEdit("0,00")
        self.netto_input.setStyleSheet(input_style)
        self.netto_input.setAlignment(Qt.AlignCenter)
        netto_layout.addWidget(self.netto_input)
        
        layout.addWidget(netto_container)
        
        # Plus operator
        plus_label = QLabel("+")
        plus_label.setStyleSheet(operator_style)
        plus_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(plus_label)
        
        # MwSt field
        mwst_container = QWidget()
        mwst_layout = QVBoxLayout(mwst_container)
        mwst_layout.setSpacing(4)
        mwst_layout.setContentsMargins(0, 0, 0, 0)
        
        mwst_label = QLabel("MwSt:")
        mwst_label.setStyleSheet(label_style)
        mwst_label.setAlignment(Qt.AlignCenter)
        mwst_layout.addWidget(mwst_label)
        
        self.mwst_input = QLineEdit("0,00")
        self.mwst_input.setStyleSheet(input_style)
        self.mwst_input.setAlignment(Qt.AlignCenter)
        mwst_layout.addWidget(self.mwst_input)
        
        layout.addWidget(mwst_container)
        
        # Equals operator
        equals_label = QLabel("=")
        equals_label.setStyleSheet(operator_style)
        equals_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(equals_label)
        
        # Brutto field
        brutto_container = QWidget()
        brutto_layout = QVBoxLayout(brutto_container)
        brutto_layout.setSpacing(4)
        brutto_layout.setContentsMargins(0, 0, 0, 0)
        
        brutto_label = QLabel("Brutto:")
        brutto_label.setStyleSheet(label_style)
        brutto_label.setAlignment(Qt.AlignCenter)
        brutto_layout.addWidget(brutto_label)
        
        self.brutto_input = QLineEdit("0,00")
        self.brutto_input.setStyleSheet(input_style)
        self.brutto_input.setAlignment(Qt.AlignCenter)
        brutto_layout.addWidget(self.brutto_input)
        
        layout.addWidget(brutto_container)
        
        return widget

    def _build_rate_selector(self) -> QWidget:
        """Build the VAT rate selector with toggle button."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Label
        rate_label = QLabel("Mehrwertsteuersatz:")
        rate_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: black;
            }
        """)
        rate_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(rate_label)
        
        # Rate pill button
        self.rate_btn = QPushButton("19 %")
        self.rate_btn.setCursor(Qt.PointingHandCursor)
        self.rate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3c;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 24px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a4a4c;
            }
            QPushButton:pressed {
                background-color: #2a2a2c;
            }
        """)
        layout.addWidget(self.rate_btn, alignment=Qt.AlignCenter)
        
        return widget

    def _connect_signals(self) -> None:
        """Connect UI signals to ViewModel methods."""
        # Connect input field editing
        self.netto_input.editingFinished.connect(self._on_netto_edited)
        self.mwst_input.editingFinished.connect(self._on_mwst_edited)
        self.brutto_input.editingFinished.connect(self._on_brutto_edited)
        
        # Connect calculate button - recalculate from netto
        self.calculate_btn.clicked.connect(self._on_calculate_clicked)
        
        # Connect rate toggle button
        self.rate_btn.clicked.connect(self._on_rate_toggle)
        
        # Connect ViewModel signals
        self.viewmodel.values_changed.connect(self._update_fields)

    def _on_netto_edited(self) -> None:
        """Handle netto field editing finished."""
        if self._updating:
            return
        self.viewmodel.calculate_from_netto(self.netto_input.text())

    def _on_mwst_edited(self) -> None:
        """Handle mwst field editing finished."""
        if self._updating:
            return
        self.viewmodel.calculate_from_mwst(self.mwst_input.text())

    def _on_brutto_edited(self) -> None:
        """Handle brutto field editing finished."""
        if self._updating:
            return
        self.viewmodel.calculate_from_brutto(self.brutto_input.text())

    def _on_calculate_clicked(self) -> None:
        """Handle calculate button click - recalculate from the last edited field."""
        # Determine which field has focus or default to netto
        if self.mwst_input.hasFocus():
            self.viewmodel.calculate_from_mwst(self.mwst_input.text())
        elif self.brutto_input.hasFocus():
            self.viewmodel.calculate_from_brutto(self.brutto_input.text())
        else:
            self.viewmodel.calculate_from_netto(self.netto_input.text())

    def _on_rate_toggle(self) -> None:
        """Handle VAT rate toggle button click."""
        new_rate = self.viewmodel.toggle_vat_rate()
        self.rate_btn.setText(f"{int(new_rate)} %")

    def _update_fields(self, netto: str, mwst: str, brutto: str) -> None:
        """Update all input fields with new values.
        
        Args:
            netto: Formatted netto value
            mwst: Formatted mwst value
            brutto: Formatted brutto value
        """
        self._updating = True
        try:
            self.netto_input.setText(netto)
            self.mwst_input.setText(mwst)
            self.brutto_input.setText(brutto)
        finally:
            self._updating = False
