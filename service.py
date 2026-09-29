from typing import List, Tuple
from model import Note
from repository import NoteRepository

PASSKEY = "ELLIE GANDA"


class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def authenticate_passkey(self, provided_key: str) -> bool:
        """Validate user passkey."""
        return provided_key == PASSKEY

    def fetch_all_notes(self) -> List[Note]:
        """Get all stored notes."""
        return self.repository.get_all()

    def create_note(self, title: str, category: str, content: str) -> Tuple[bool, str]:
        """Validate inputs and save a new note."""
        title = title.strip()
        category = category.strip()
        content = content.strip()

        if not title or not category or not content:
            return False, "Please fill in all fields."

        new_note = Note(title=title, category=category, content=content)
        self.repository.add(new_note)
        return True, "Note saved successfully."

    def delete_note(self, note_id: int) -> None:
        """Remove a note by ID."""
        self.repository.delete(note_id)