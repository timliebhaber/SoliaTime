"""Profile creation and editing dialog."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)


class ProfileDialog(QDialog):
    """Dialog for creating or editing a profile."""

    def __init__(
        self,
        parent=None,
        title: str = "Profile",
        name: str = "",
        contact_person: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        business_address: str | None = None,
    ) -> None:
        """Initialize profile dialog.
        
        Args:
            parent: Parent widget
            title: Dialog window title
            name: Profile name
            contact_person: Contact person name
            email: Contact email
            phone: Contact phone number
            business_address: Business address
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        
        # Name field
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(name)
        layout.addWidget(QLabel("Name"))
        layout.addWidget(self.name_edit)
        
        # Contact fields
        self.contact_edit = QLineEdit(self)
        self.contact_edit.setText(contact_person or "")
        self.email_edit = QLineEdit(self)
        self.email_edit.setText(email or "")
        self.phone_edit = QLineEdit(self)
        self.phone_edit.setText(phone or "")
        
        layout.addWidget(QLabel("Contact Person"))
        layout.addWidget(self.contact_edit)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Phone"))
        layout.addWidget(self.phone_edit)
        
        # Business address field
        self.business_address_edit = QPlainTextEdit(self)
        self.business_address_edit.setPlainText(business_address or "")
        self.business_address_edit.setPlaceholderText("Enter business address...")
        self.business_address_edit.setMaximumHeight(100)  # 4 lines high
        layout.addWidget(QLabel("Business Address"))
        layout.addWidget(self.business_address_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self) -> str:
        """Get the profile name."""
        return self.name_edit.text().strip()

    def get_contact_fields(self) -> tuple[str | None, str | None, str | None, str | None]:
        """Get contact information fields.
        
        Returns:
            Tuple of (contact_person, email, phone, business_address)
        """
        contact = self.contact_edit.text().strip() or None
        email = self.email_edit.text().strip() or None
        phone = self.phone_edit.text().strip() or None
        business_address = self.business_address_edit.toPlainText().strip() or None
        return contact, email, phone, business_address

