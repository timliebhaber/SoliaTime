from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel


class ProfileDialog(QDialog):
    def __init__(self, parent=None, title: str = "Profile", name: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(name)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self) -> str:
        return self.name_edit.text().strip()


class EntryDialog(QDialog):
    def __init__(self, parent=None, note: str = "", tags: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Entry")
        layout = QVBoxLayout(self)
        self.note_edit = QLineEdit(self)
        self.note_edit.setText(note)
        self.tags_edit = QLineEdit(self)
        self.tags_edit.setText(tags)
        layout.addWidget(QLabel("Note"))
        layout.addWidget(self.note_edit)
        layout.addWidget(QLabel("Tags (comma-separated)"))
        layout.addWidget(self.tags_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self) -> tuple[str, str]:
        return self.note_edit.text().strip(), self.tags_edit.text().strip()


