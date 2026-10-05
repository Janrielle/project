import sys
from PyQt6.QtWidgets import QApplication

from feature.repository import NoteRepository
from feature.service import NoteService
from feature.view import NotesApp

def main():
    repository = NoteRepository(db_path="notes.db")
    service = NoteService(repository=repository)

    app = QApplication(sys.argv)
    window = NotesApp(service=service)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()