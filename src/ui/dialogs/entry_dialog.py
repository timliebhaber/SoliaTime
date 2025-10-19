"""Time entry editing dialog."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class EntryDialog(QDialog):
    """Dialog for editing a time entry's note and tags."""

    def __init__(self, parent=None, note: str = "", tags: str = "") -> None:
        """Initialize entry dialog.
        
        Args:
            parent: Parent widget
            note: Entry note text
            tags: Comma-separated tags
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Entry")
        layout = QVBoxLayout(self)
        
        # Note field
        self.note_edit = QLineEdit(self)
        self.note_edit.setText(note)
        layout.addWidget(QLabel("Note"))
        layout.addWidget(self.note_edit)
        
        # Tags field
        self.tags_edit = QLineEdit(self)
        self.tags_edit.setText(tags)
        layout.addWidget(QLabel("Tags (comma-separated)"))
        layout.addWidget(self.tags_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> tuple[str, str]:
        """Get the note and tags values.
        
        Returns:
            Tuple of (note, tags)
        """
        return self.note_edit.text().strip(), self.tags_edit.text().strip()

