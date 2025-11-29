"""Mehrwertsteuer (VAT) Calculator view."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
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
        # Background with gradient
        self.setStyleSheet("""
            VatCalculatorView {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1a1a2e,
                    stop: 0.5 #16213e,
                    stop: 1 #0f3460
                );
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Card container with glass effect
        card = QFrame()
        card.setFixedWidth(520)
        card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(Qt.black)
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 35, 40, 40)
        card_layout.setSpacing(0)
        
        # Title section
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)
        
        # Main title
        title = QLabel("MwSt Rechner")
        title_font = QFont("Segoe UI", 28)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #1a1a2e; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Mehrwertsteuer einfach berechnen")
        subtitle_font = QFont("Segoe UI", 11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #6b7280; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle)
        
        card_layout.addWidget(title_container)
        card_layout.addSpacing(30)
        
        # Divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #e5e7eb;")
        card_layout.addWidget(divider)
        card_layout.addSpacing(30)
        
        # Input fields
        fields_widget = self._build_input_fields()
        card_layout.addWidget(fields_widget, alignment=Qt.AlignCenter)
        
        card_layout.addSpacing(25)
        
        # VAT rate selector
        rate_widget = self._build_rate_selector()
        card_layout.addWidget(rate_widget, alignment=Qt.AlignCenter)
        
        card_layout.addSpacing(30)
        
        # Calculate button
        self.calculate_btn = QPushButton("Berechnen")
        self.calculate_btn.setMinimumHeight(54)
        self.calculate_btn.setFixedWidth(420)
        self.calculate_btn.setCursor(Qt.PointingHandCursor)
        btn_font = QFont("Segoe UI", 15)
        btn_font.setWeight(QFont.Weight.DemiBold)
        self.calculate_btn.setFont(btn_font)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #059669,
                    stop: 1 #10b981
                );
                color: white;
                border: none;
                border-radius: 14px;
                padding: 14px 40px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #047857,
                    stop: 1 #059669
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #065f46,
                    stop: 1 #047857
                );
            }
        """)
        card_layout.addWidget(self.calculate_btn, alignment=Qt.AlignCenter)
        
        main_layout.addWidget(card)

    def _build_input_fields(self) -> QWidget:
        """Build the three input fields with labels and operators."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        input_style = """
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 14px 12px;
                font-size: 17px;
                font-family: 'Segoe UI';
                font-weight: 500;
                min-width: 95px;
                max-width: 110px;
                background-color: #f9fafb;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #10b981;
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #d1d5db;
            }
        """
        
        label_style = """
            QLabel {
                font-size: 13px;
                font-family: 'Segoe UI';
                color: #4b5563;
                font-weight: 600;
                letter-spacing: 0.5px;
                background: transparent;
            }
        """
        
        operator_style = """
            QLabel {
                font-size: 22px;
                font-family: 'Segoe UI';
                color: #9ca3af;
                font-weight: 300;
                padding: 0 4px;
                background: transparent;
            }
        """
        
        # Netto field
        netto_container = QWidget()
        netto_container.setStyleSheet("background: transparent;")
        netto_layout = QVBoxLayout(netto_container)
        netto_layout.setSpacing(6)
        netto_layout.setContentsMargins(0, 0, 0, 0)
        
        netto_label = QLabel("NETTO")
        netto_label.setStyleSheet(label_style)
        netto_label.setAlignment(Qt.AlignCenter)
        netto_layout.addWidget(netto_label)
        
        netto_input_row = QHBoxLayout()
        netto_input_row.setSpacing(0)
        self.netto_input = QLineEdit("0,00")
        self.netto_input.setStyleSheet(input_style)
        self.netto_input.setAlignment(Qt.AlignRight)
        netto_input_row.addWidget(self.netto_input)
        
        euro1 = QLabel("€")
        euro1.setStyleSheet("font-size: 16px; color: #6b7280; font-weight: 500; padding-left: 6px; background: transparent;")
        netto_input_row.addWidget(euro1)
        netto_layout.addLayout(netto_input_row)
        
        layout.addWidget(netto_container)
        
        # Plus operator
        plus_label = QLabel("+")
        plus_label.setStyleSheet(operator_style)
        plus_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(plus_label)
        
        # MwSt field
        mwst_container = QWidget()
        mwst_container.setStyleSheet("background: transparent;")
        mwst_layout = QVBoxLayout(mwst_container)
        mwst_layout.setSpacing(6)
        mwst_layout.setContentsMargins(0, 0, 0, 0)
        
        mwst_label = QLabel("MWST")
        mwst_label.setStyleSheet(label_style)
        mwst_label.setAlignment(Qt.AlignCenter)
        mwst_layout.addWidget(mwst_label)
        
        mwst_input_row = QHBoxLayout()
        mwst_input_row.setSpacing(0)
        self.mwst_input = QLineEdit("0,00")
        self.mwst_input.setStyleSheet(input_style)
        self.mwst_input.setAlignment(Qt.AlignRight)
        mwst_input_row.addWidget(self.mwst_input)
        
        euro2 = QLabel("€")
        euro2.setStyleSheet("font-size: 16px; color: #6b7280; font-weight: 500; padding-left: 6px; background: transparent;")
        mwst_input_row.addWidget(euro2)
        mwst_layout.addLayout(mwst_input_row)
        
        layout.addWidget(mwst_container)
        
        # Equals operator
        equals_label = QLabel("=")
        equals_label.setStyleSheet(operator_style)
        equals_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(equals_label)
        
        # Brutto field
        brutto_container = QWidget()
        brutto_container.setStyleSheet("background: transparent;")
        brutto_layout = QVBoxLayout(brutto_container)
        brutto_layout.setSpacing(6)
        brutto_layout.setContentsMargins(0, 0, 0, 0)
        
        brutto_label = QLabel("BRUTTO")
        brutto_label.setStyleSheet(label_style)
        brutto_label.setAlignment(Qt.AlignCenter)
        brutto_layout.addWidget(brutto_label)
        
        brutto_input_row = QHBoxLayout()
        brutto_input_row.setSpacing(0)
        self.brutto_input = QLineEdit("0,00")
        self.brutto_input.setStyleSheet(input_style)
        self.brutto_input.setAlignment(Qt.AlignRight)
        brutto_input_row.addWidget(self.brutto_input)
        
        euro3 = QLabel("€")
        euro3.setStyleSheet("font-size: 16px; color: #6b7280; font-weight: 500; padding-left: 6px; background: transparent;")
        brutto_input_row.addWidget(euro3)
        brutto_layout.addLayout(brutto_input_row)
        
        layout.addWidget(brutto_container)
        
        return widget

    def _build_rate_selector(self) -> QWidget:
        """Build the VAT rate selector with toggle button."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Label
        rate_label = QLabel("Steuersatz:")
        rate_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-family: 'Segoe UI';
                color: #6b7280;
                font-weight: 500;
                background: transparent;
            }
        """)
        layout.addWidget(rate_label)
        
        # Rate toggle buttons container
        btn_container = QWidget()
        btn_container.setStyleSheet("""
            QWidget {
                background-color: #f3f4f6;
                border-radius: 10px;
            }
        """)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(4, 4, 4, 4)
        btn_layout.setSpacing(4)
        
        # 19% button
        self.rate_19_btn = QPushButton("19%")
        self.rate_19_btn.setCursor(Qt.PointingHandCursor)
        self.rate_19_btn.setFixedSize(60, 34)
        self.rate_19_btn.setCheckable(True)
        self.rate_19_btn.setChecked(True)
        btn_layout.addWidget(self.rate_19_btn)
        
        # 7% button
        self.rate_7_btn = QPushButton("7%")
        self.rate_7_btn.setCursor(Qt.PointingHandCursor)
        self.rate_7_btn.setFixedSize(60, 34)
        self.rate_7_btn.setCheckable(True)
        btn_layout.addWidget(self.rate_7_btn)
        
        # Style for toggle buttons
        toggle_style = """
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-family: 'Segoe UI';
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:checked {
                background-color: white;
                color: #059669;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
        """
        self.rate_19_btn.setStyleSheet(toggle_style)
        self.rate_7_btn.setStyleSheet(toggle_style)
        
        layout.addWidget(btn_container)
        
        # Keep old rate_btn reference for compatibility, but hide it
        self.rate_btn = QPushButton()
        self.rate_btn.hide()
        
        return widget

    def _connect_signals(self) -> None:
        """Connect UI signals to ViewModel methods."""
        # Connect input field editing
        self.netto_input.editingFinished.connect(self._on_netto_edited)
        self.mwst_input.editingFinished.connect(self._on_mwst_edited)
        self.brutto_input.editingFinished.connect(self._on_brutto_edited)
        
        # Connect calculate button - recalculate from netto
        self.calculate_btn.clicked.connect(self._on_calculate_clicked)
        
        # Connect rate toggle buttons
        self.rate_19_btn.clicked.connect(self._on_rate_19_selected)
        self.rate_7_btn.clicked.connect(self._on_rate_7_selected)
        
        # Connect ViewModel signals
        self.viewmodel.values_changed.connect(self._update_fields)

    def _on_rate_19_selected(self) -> None:
        """Handle 19% rate selection."""
        self.rate_19_btn.setChecked(True)
        self.rate_7_btn.setChecked(False)
        from decimal import Decimal
        self.viewmodel.vat_rate = Decimal("19")

    def _on_rate_7_selected(self) -> None:
        """Handle 7% rate selection."""
        self.rate_7_btn.setChecked(True)
        self.rate_19_btn.setChecked(False)
        from decimal import Decimal
        self.viewmodel.vat_rate = Decimal("7")

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
        """Handle VAT rate toggle button click (legacy support)."""
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
