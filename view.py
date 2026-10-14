import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QScrollArea,
    QFrame, QMessageBox, QInputDialog, QGridLayout, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from feature.service import NoteService, MIN_PASSWORD_LENGTH

PRIMARY_BTN = """
    QPushButton {
        background-color: #ec4899;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #db2777; }
"""

SECONDARY_BTN = """
    QPushButton {
        background-color: #fce7f3;
        color: #be185d;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #fbcfe8; }
"""

DIALOG_STYLE = """
    QDialog { background-color: #fdf2f8; }
    QLabel { color: #831843; }
    QLineEdit, QTextEdit {
        border: 1px solid #f472b6;
        border-radius: 6px;
        padding: 8px;
        background-color: #ffffff;
        color: #831843;
    }
    QLineEdit:focus, QTextEdit:focus { border: 1px solid #db2777; }
"""


class PasswordDialog(QDialog):
    """Dialog used both for first-time password setup and for changing it."""

    def __init__(self, parent, title: str, intro: str, ask_current: bool):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(360)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        intro_label = QLabel(intro)
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)

        form = QFormLayout()
        self.current_input = None
        if ask_current:
            self.current_input = self._password_field()
            form.addRow("Current password:", self.current_input)
        self.new_input = self._password_field()
        self.confirm_input = self._password_field()
        form.addRow("New password:", self.new_input)
        form.addRow("Confirm password:", self.confirm_input)
        layout.addLayout(form)

        hint = QLabel(f"At least {MIN_PASSWORD_LENGTH} characters.")
        hint.setStyleSheet("color: #9d174d; font-size: 11px;")
        layout.addWidget(hint)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(SECONDARY_BTN)
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Save Password")
        ok_btn.setStyleSheet(PRIMARY_BTN)
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)

    @staticmethod
    def _password_field() -> QLineEdit:
        field = QLineEdit()
        field.setEchoMode(QLineEdit.EchoMode.Password)
        return field

    def values(self):
        current = self.current_input.text() if self.current_input else ""
        return current, self.new_input.text(), self.confirm_input.text()


class NoteDialog(QDialog):
    """Opens when a note card is clicked: read the note, then optionally edit it."""

    def __init__(self, parent, service: NoteService, note_id: int):
        super().__init__(parent)
        self.service = service
        self.note_id = note_id
        self.changed = False

        note = service.get_note(note_id)
        self.note = note

        self.setWindowTitle("Note")
        self.setModal(True)
        self.resize(480, 460)
        self.setStyleSheet(DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Title"))
        self.title_input = QLineEdit(note.title)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Category"))
        self.category_input = QLineEdit(note.category)
        layout.addWidget(self.category_input)

        layout.addWidget(QLabel("Content"))
        self.content_input = QTextEdit()
        self.content_input.setPlainText(note.content)
        layout.addWidget(self.content_input)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(SECONDARY_BTN)
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setStyleSheet(PRIMARY_BTN)
        self.save_btn.clicked.connect(self.save)
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet(PRIMARY_BTN)
        self.edit_btn.clicked.connect(lambda: self.set_editing(True))
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(SECONDARY_BTN)
        self.close_btn.clicked.connect(self.accept)
        for btn in (self.cancel_btn, self.save_btn, self.edit_btn, self.close_btn):
            buttons.addWidget(btn)
        layout.addLayout(buttons)

        self.set_editing(False)

    def set_editing(self, editing: bool) -> None:
        self.title_input.setReadOnly(not editing)
        self.category_input.setReadOnly(not editing)
        self.content_input.setReadOnly(not editing)
        self.edit_btn.setVisible(not editing)
        self.close_btn.setVisible(not editing)
        self.save_btn.setVisible(editing)
        self.cancel_btn.setVisible(editing)
        self.setWindowTitle("Edit Note" if editing else "Note")

    def cancel_edit(self) -> None:
        self.title_input.setText(self.note.title)
        self.category_input.setText(self.note.category)
        self.content_input.setPlainText(self.note.content)
        self.set_editing(False)

    def save(self) -> None:
        success, message = self.service.update_note(
            self.note_id,
            self.title_input.text(),
            self.category_input.text(),
            self.content_input.toPlainText(),
        )
        if not success:
            QMessageBox.warning(self, "Missing Info", message)
            return
        self.note = self.service.get_note(self.note_id)
        self.changed = True
        self.set_editing(False)


class NoteCard(QFrame):
    """Card showing only title + category. Click it to read the note."""
    def __init__(self, note_id: int, title: str, category: str, open_callback, delete_callback):
        super().__init__()
        self.note_id = note_id
        self.open_callback = open_callback
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 12px;
                border: 1px solid #fbcfe8;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        # Header Row (Category Tag + Delete Button)
        top_layout = QHBoxLayout()

        category_label = QLabel(category)
        category_label.setStyleSheet("""
            background-color: #fce7f3;
            color: #be185d;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: bold;
        """)
        top_layout.addWidget(category_label, alignment=Qt.AlignmentFlag.AlignLeft)
        top_layout.addStretch()

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f43f5e;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e11d48;
            }
        """)
        delete_btn.clicked.connect(lambda: delete_callback(self.note_id))
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        # Note Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #831843; border: none;")
        layout.addWidget(title_label)

        # Hint instead of the note content
        hint_label = QLabel("Click to read")
        hint_label.setFont(QFont("Arial", 9))
        hint_label.setStyleSheet("color: #be185d; border: none; font-style: italic;")
        layout.addWidget(hint_label)

        self.setLayout(layout)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            self.open_callback(self.note_id)
        super().mouseReleaseEvent(event)


class NotesApp(QMainWindow):
    def __init__(self, service: NoteService):
        super().__init__()
        self.service = service

        self.setWindowTitle("Notes Organizer")
        self.resize(750, 750)
        self.setStyleSheet("background-color: #fdf2f8;")

        # The user must pick their own password before the passcode prompt appears.
        if not self.service.has_password() and not self.setup_password():
            sys.exit(0)

        if not self.authenticate():
            sys.exit(0)

        self.setup_ui()
        self.load_notes()

    def setup_password(self) -> bool:
        """First run: make the user choose a password."""
        while True:
            dialog = PasswordDialog(
                self,
                "Create Your Password",
                "Welcome! Choose a password to protect your notes. "
                "You'll be asked for it every time you open or lock the app.",
                ask_current=False,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
            _, new, confirm = dialog.values()
            success, message = self.service.set_initial_password(new, confirm)
            if success:
                QMessageBox.information(self, "Password Set", message)
                return True
            QMessageBox.warning(self, "Invalid Password", message)

    def change_password(self):
        """Let the user change their password from inside the app."""
        while True:
            dialog = PasswordDialog(
                self,
                "Change Password",
                "Enter your current password, then choose a new one.",
                ask_current=True,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            current, new, confirm = dialog.values()
            success, message = self.service.change_password(current, new, confirm)
            if success:
                QMessageBox.information(self, "Password Changed", message)
                return
            QMessageBox.warning(self, "Could Not Change Password", message)

    def authenticate(self) -> bool:
        """Prompt for passkey before launching."""
        attempts = 0
        while attempts < 3:
            key, ok = QInputDialog.getText(
                self,
                "Passkey Required",
                "Enter Passkey to Unlock Notes:",
                QLineEdit.EchoMode.Password
            )
            if not ok:  # User cancelled
                return False
            if self.service.authenticate_passkey(key):
                return True
            else:
                attempts += 1
                QMessageBox.critical(self, "Access Denied", "Invalid Passkey. Try again.")

        QMessageBox.critical(self, "Error", "Too many failed attempts. Exiting.")
        return False

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        # Header Row
        header_layout = QHBoxLayout()
        header_title = QLabel("Notes Organizer")
        header_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_title.setStyleSheet("color: #831843;")

        change_pw_btn = QPushButton("Change Password")
        change_pw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pw_btn.setStyleSheet("""
            QPushButton {
                background-color: #f9a8d4;
                color: #831843;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f472b6;
            }
        """)
        change_pw_btn.clicked.connect(self.change_password)

        lock_btn = QPushButton("Lock App")
        lock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        lock_btn.setStyleSheet("""
            QPushButton {
                background-color: #db2777;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #be185d;
            }
        """)
        lock_btn.clicked.connect(self.lock_app)

        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(change_pw_btn)
        header_layout.addWidget(lock_btn)
        main_layout.addLayout(header_layout)

        # Form Section
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #fbcfe8;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #f472b6;
                border-radius: 6px;
                padding: 8px;
                background-color: #fff1f2;
                color: #831843;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #db2777;
            }
        """)
        form_layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Note Title")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category (e.g. Work, Personal, Ideas)")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Write your note here...")
        self.content_input.setMaximumHeight(90)

        save_btn = QPushButton("Save Note")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #ec4899;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #db2777;
            }
        """)
        save_btn.clicked.connect(self.add_note)

        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.content_input)
        form_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        form_frame.setLayout(form_layout)

        main_layout.addWidget(form_frame)

        # Search Bar Section
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search notes by title, category, or keyword...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #f472b6;
                border-radius: 8px;
                padding: 8px;
                background-color: #ffffff;
                color: #831843;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #db2777;
            }
        """)
        self.search_input.textChanged.connect(self.filter_notes)
        main_layout.addWidget(self.search_input)

        # Notes Cards Grid
        notes_label = QLabel("Your Notes")
        notes_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        notes_label.setStyleSheet("color: #831843;")
        main_layout.addWidget(notes_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_container.setLayout(self.cards_layout)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)

        central_widget.setLayout(main_layout)

    def load_notes(self):
        """Fetch notes based on current search input and display them."""
        self.filter_notes()

    def filter_notes(self):
        """Fetch filtered notes dynamically as user types."""
        query = self.search_input.text()
        notes = self.service.search_notes(query)

        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not notes:
            empty_lbl = QLabel("No matching notes found!")
            empty_lbl.setStyleSheet("color: #9d174d; font-size: 13px;")
            self.cards_layout.addWidget(empty_lbl, 0, 0)
            return

        cols = 2
        for idx, note in enumerate(notes):
            row = idx // cols
            col = idx % cols
            card = NoteCard(note.id, note.title, note.category, self.open_note, self.delete_note)
            self.cards_layout.addWidget(card, row, col)

    def open_note(self, note_id: int):
        """Open the clicked note so the user can read (and optionally edit) it."""
        if self.service.get_note(note_id) is None:
            self.load_notes()
            return
        dialog = NoteDialog(self, self.service, note_id)
        dialog.exec()
        if dialog.changed:
            self.load_notes()

    def add_note(self):
        """Delegate note creation to service layer."""
        title = self.title_input.text()
        category = self.category_input.text()
        content = self.content_input.toPlainText()

        success, message = self.service.create_note(title, category, content)

        if not success:
            QMessageBox.warning(self, "Missing Info", message)
            return

        self.title_input.clear()
        self.category_input.clear()
        self.content_input.clear()
        self.search_input.clear()
        self.load_notes()

    def delete_note(self, note_id: int):
        """Delegate note deletion to service layer."""
        self.service.delete_note(note_id)
        self.load_notes()

    def lock_app(self):
        """Hide window and prompt for passkey to unlock again."""
        self.hide()
        if self.authenticate():
            self.show()
        else:
            sys.exit(0)