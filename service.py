import hashlib
import hmac
import os
from typing import List, Optional, Tuple

from feature.model import Note
from feature.repository import NoteRepository

MIN_PASSWORD_LENGTH = 4
_PBKDF2_ITERATIONS = 200_000


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS
    ).hex()


class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    # ---- Password handling ----

    def has_password(self) -> bool:
        """True once the user has picked their own password."""
        return self.repository.get_setting("password_hash") is not None

    def _validate_new_password(self, password: str, confirm: str) -> Tuple[bool, str]:
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        if password != confirm:
            return False, "Passwords do not match."
        return True, ""

    def _store_password(self, password: str) -> None:
        salt = os.urandom(16)
        self.repository.set_setting("password_salt", salt.hex())
        self.repository.set_setting("password_hash", _hash_password(password, salt))

    def set_initial_password(self, password: str, confirm: str) -> Tuple[bool, str]:
        """First-run setup: the user chooses their own password."""
        if self.has_password():
            return False, "A password is already set."
        ok, message = self._validate_new_password(password, confirm)
        if not ok:
            return False, message
        self._store_password(password)
        return True, "Password set successfully."

    def authenticate_passkey(self, provided_key: str) -> bool:
        """Validate the user's passkey against the stored hash."""
        stored_hash = self.repository.get_setting("password_hash")
        stored_salt = self.repository.get_setting("password_salt")
        if stored_hash is None or stored_salt is None:
            return False
        candidate = _hash_password(provided_key, bytes.fromhex(stored_salt))
        return hmac.compare_digest(candidate, stored_hash)

    def change_password(self, current: str, new: str, confirm: str) -> Tuple[bool, str]:
        """Change the password after verifying the current one."""
        if not self.authenticate_passkey(current):
            return False, "Current password is incorrect."
        ok, message = self._validate_new_password(new, confirm)
        if not ok:
            return False, message
        if new == current:
            return False, "New password must be different from the current one."
        self._store_password(new)
        return True, "Password changed successfully."

    # ---- Notes ----

    def fetch_all_notes(self) -> List[Note]:
        """Get all stored notes."""
        return self.repository.get_all()

    def get_note(self, note_id: int) -> Optional[Note]:
        """Get a single note (used when the user opens it to read)."""
        return self.repository.get_by_id(note_id)

    def search_notes(self, query: str) -> List[Note]:
        """Filter notes based on query string."""
        query = query.strip()
        if not query:
            return self.fetch_all_notes()
        return self.repository.search(query)

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

    def update_note(self, note_id: int, title: str, category: str, content: str) -> Tuple[bool, str]:
        """Validate inputs and update an existing note."""
        title = title.strip()
        category = category.strip()
        content = content.strip()

        if not title or not category or not content:
            return False, "Please fill in all fields."

        self.repository.update(
            Note(id=note_id, title=title, category=category, content=content)
        )
        return True, "Note updated successfully."

    def delete_note(self, note_id: int) -> None:
        """Remove a note by ID."""
        self.repository.delete(note_id)