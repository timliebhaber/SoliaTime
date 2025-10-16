from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel, QHBoxLayout


class ProfileDialog(QDialog):
    def __init__(
        self,
        parent=None,
        title: str = "Profile",
        name: str = "",
        target_seconds: int | None = None,
        company: str | None = None,
        contact_person: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(name)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name_edit)
        # Target time (HH:MM)
        self.target_edit = QLineEdit(self)
        self.target_edit.setPlaceholderText("HH:MM (optional)")
        if target_seconds is not None and target_seconds > 0:
            h = target_seconds // 3600
            m = (target_seconds % 3600) // 60
            self.target_edit.setText(f"{h:02d}:{m:02d}")
        layout.addWidget(QLabel("Daily Target (HH:MM)"))
        layout.addWidget(self.target_edit)
        # Contact fields
        self.company_edit = QLineEdit(self)
        self.company_edit.setText(company or "")
        self.contact_edit = QLineEdit(self)
        self.contact_edit.setText(contact_person or "")
        self.email_edit = QLineEdit(self)
        self.email_edit.setText(email or "")
        self.phone_edit = QLineEdit(self)
        self.phone_edit.setText(phone or "")
        layout.addWidget(QLabel("Company"))
        layout.addWidget(self.company_edit)
        layout.addWidget(QLabel("Contact Person"))
        layout.addWidget(self.contact_edit)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self) -> str:
        return self.name_edit.text().strip()

    def get_target_seconds(self) -> int | None:
        text = self.target_edit.text().strip()
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

    def get_contact_fields(self) -> tuple[str | None, str | None, str | None, str | None]:
        company = self.company_edit.text().strip() or None
        contact = self.contact_edit.text().strip() or None
        email = self.email_edit.text().strip() or None
        phone = self.phone_edit.text().strip() or None
        return company, contact, email, phone


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


