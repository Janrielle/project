import sqlite3
from typing import List
from feature.model import Note

class NoteRepository:
    def __init__(self, db_path: str = "notes.db"):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        """Initialize database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_all(self) -> List[Note]:
        """Fetch all notes ordered by ID descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, category, content FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
            return [Note(id=row[0], title=row[1], category=row[2], content=row[3]) for row in rows]

    def add(self, note: Note) -> int:
        """Insert a new note into the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, category, content) VALUES (?, ?, ?)",
                (note.title, note.category, note.content)
            )
            conn.commit()
            return cursor.lastrowid

    def delete(self, note_id: int) -> None:
        """Delete a note by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()