import sys
from PyQt6.QtWidgets import QApplication

from repository import NoteRepository
from service import NoteService
from view import NotesApp


def main():
    # Dependency Injection
    repository = NoteRepository(db_path="notes.db")
    service = NoteService(repository=repository)

    app = QApplication(sys.argv)
    window = NotesApp(service=service)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()