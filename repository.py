import sqlite3
from typing import List, Optional
from feature.model import Note


class NoteRepository:
    def __init__(self, db_path: str = "notes.db"):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
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
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            conn.commit()

    # ---- Settings (used to store the password hash) ----

    def get_setting(self, key: str) -> Optional[str]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def set_setting(self, key: str, value: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
            conn.commit()

    # ---- Notes ----

    def get_all(self) -> List[Note]:
        """Fetch all notes ordered by ID descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, category, content FROM notes ORDER BY id DESC")
            rows = cursor.fetchall()
            return [Note(id=row[0], title=row[1], category=row[2], content=row[3]) for row in rows]

    def get_by_id(self, note_id: int) -> Optional[Note]:
        """Fetch a single note by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, category, content FROM notes WHERE id = ?", (note_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Note(id=row[0], title=row[1], category=row[2], content=row[3])

    def search(self, query: str) -> List[Note]:
        """Search notes matching title, category, or content."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            term = f"%{query}%"
            cursor.execute(
                """
                SELECT id, title, category, content FROM notes
                WHERE title LIKE ? OR category LIKE ? OR content LIKE ?
                ORDER BY id DESC
                """,
                (term, term, term)
            )
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

    def update(self, note: Note) -> None:
        """Update an existing note."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE notes SET title = ?, category = ?, content = ? WHERE id = ?",
                (note.title, note.category, note.content, note.id)
            )
            conn.commit()

    def delete(self, note_id: int) -> None:
        """Delete a note by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()