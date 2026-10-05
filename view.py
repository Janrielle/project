import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QScrollArea,
    QFrame, QMessageBox, QInputDialog, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from feature.service import NoteService
from feature.model import Note


class NoteCard(QFrame):
    """Custom Card widget styled similarly to the original layout."""
    def __init__(self, note_id: int, title: str, category: str, content: str, delete_callback):
        super().__init__()
        self.note_id = note_id

        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #e2e8f0;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(6)

        # Header Row
        top_layout = QHBoxLayout()
        
        category_label = QLabel(category)
        category_label.setStyleSheet("""
            background-color: #e0f2fe;
            color: #0369a1;
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
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a71d2a;
            }
        """)
        delete_btn.clicked.connect(lambda: delete_callback(self.note_id))
        top_layout.addWidget(delete_btn)

        layout.addLayout(top_layout)

        # Note Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        title_label.setStyleSheet("color: #1e293b; border: none;")
        layout.addWidget(title_label)

        # Note Content
        content_label = QLabel(content)
        content_label.setFont(QFont("Arial", 10))
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #475569; border: none;")
        layout.addWidget(content_label)

        self.setLayout(layout)


class NotesApp(QMainWindow):
    def __init__(self, service: NoteService):
        super().__init__()
        self.service = service

        self.setWindowTitle("Notes Organizer")
        self.resize(750, 700)
        self.setStyleSheet("background-color: #f4f6f9;")

        if not self.authenticate():
            sys.exit(0)

        self.setup_ui()
        self.load_notes()

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
            if not ok:
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
        header_title.setStyleSheet("color: #1e293b;")

        lock_btn = QPushButton("Lock App")
        lock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        lock_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        lock_btn.clicked.connect(self.lock_app)

        header_layout.addWidget(header_title)
        header_layout.addStretch()
        header_layout.addWidget(lock_btn)
        main_layout.addLayout(header_layout)

        # Form Section
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e2e8f0;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                background-color: #fafafa;
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
                background-color: #007bff;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        save_btn.clicked.connect(self.add_note)

        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.content_input)
        form_layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        form_frame.setLayout(form_layout)

        main_layout.addWidget(form_frame)

        # Notes Cards Grid
        notes_label = QLabel("Your Notes")
        notes_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        notes_label.setStyleSheet("color: #1e293b;")
        main_layout.addWidget(notes_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.cards_container = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(15)
        self.cards_container.setLayout(self.cards_layout)

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area)

        central_widget.setLayout(main_layout)

    def load_notes(self):
        """Fetch notes from service layer and display them."""
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        notes = self.service.fetch_all_notes()

        if not notes:
            empty_lbl = QLabel("No notes saved yet!")
            empty_lbl.setStyleSheet("color: #64748b; font-size: 13px;")
            self.cards_layout.addWidget(empty_lbl, 0, 0)
            return

        cols = 2
        for idx, note in enumerate(notes):
            row = idx // cols
            col = idx % cols
            card = NoteCard(note.id, note.title, note.category, note.content, self.delete_note)
            self.cards_layout.addWidget(card, row, col)

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