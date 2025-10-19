"""Tile button component for dashboard navigation."""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout, QWidget


class TileButton(QFrame):
    """A clickable tile button for the home dashboard."""

    def __init__(self, title: str, icon_char: str, parent: QWidget | None = None) -> None:
        """Initialize tile button.
        
        Args:
            title: Display title for the tile
            icon_char: Unicode character or emoji for the icon
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(200, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        
        # Apply rounded corners and lighter background
        self.setStyleSheet("""
            TileButton {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
            TileButton:hover {
                background-color: rgba(255, 255, 255, 0.12);
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon label (using emoji/unicode character)
        icon_label = QLabel(icon_char)
        icon_font = icon_label.font()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Title label
        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        
        self._callback: Optional[Callable[[], None]] = None
        self._is_hovered = False
    
    def set_click_callback(self, callback: Callable[[], None]) -> None:
        """Set the callback to be called when tile is clicked.
        
        Args:
            callback: Function to call on click
        """
        self._callback = callback
    
    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.LeftButton and self._callback:
            self._callback()
        super().mousePressEvent(event)
    
    def enterEvent(self, event) -> None:  # type: ignore[override]
        self._is_hovered = True
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:  # type: ignore[override]
        self._is_hovered = False
        super().leaveEvent(event)

