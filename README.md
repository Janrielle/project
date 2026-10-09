Notes Organizer
---

Project Description :
The Notes Organizer is a desktop-based note management system built with Python and PyQt6.

* Problem Addressed: Many standard note-taking applications lack basic security or validation, making simple personal notes accessible to unauthorized local users.
  
* System Purpose: This system provides a secure, organized environment to create, view, and manage notes locally with integrated passkey authentication to safeguard note operations.

---

## Project Objectives

* Provide a clean Graphical User Interface (GUI) for creating and managing categorized notes.
* Implement passkey validation (ELLIE GANDA) to authenticate note operations and unlock/lock application states.
* Maintain strict input validation to prevent empty or incomplete records from being stored.
* Ensure data persistence using a local SQLite database engine.
* Follow layered software design principles (Model-View-Repository-Service / Layered Architecture).

---

## Features

* Passkey Authentication & Application Locking: Protects system interactions through passkey verification on startup and includes a custom "Lock App" action to temporarily secure active sessions.
* Note Creation: Add notes with a title, category, and main body text.
* Validation Check: Input fields are validated; empty notes or missing parameters are rejected.
* Persistent Storage: Saves created notes to an SQLite database file (notes.db).
* Custom Card UI Display: Renders saved notes in a styled 2-column grid layout with customizable categories and individual note deletion triggers.
* Note Viewing & Removal: Retrieve all stored notes in reverse chronological order and delete specific notes by ID.

---

## Technologies Used

* Programming Language: Python 3
* GUI Framework: PyQt6 (using QMainWindow, QScrollArea, QGridLayout, QFrame, etc.)
* Database: SQLite3
* Tools & Libraries: dataclasses, typing, sys

---

## Project Structure

project/
 main.py  -  Entry point of the application; initializes dependency injection and starts GUI loop.
 model.py - Defines the data structures (Note dataclass).
 repository.py - Database interaction layer handling direct SQLite queries.
 service.py  - Business logic layer handling validation, authentication, and rules.
 view.py  - Modernized PyQt6 GUI implementation featuring custom NoteCard components and grid UI layouts.
 notes.db - SQLite database file (created automatically at runtime).

---

Installation and Setup
Prerequisites
Python 3.10+ installed on your system.

---

## Step-by-Step Setup

1. Clone the Repository:
git clone https://github.com/Janrielle/project.git
cd project
2. Install Required Dependencies:
pip install PyQt6
3. Run the Application:
python main.py

---

## How to Use the System

Launch the application by executing main.py.

Enter the passkey (ELLIE GANDA) in the startup authentication dialog to unlock the main application interface.

To create a note, fill in the Title, Category, and Content fields in the top form panel, then click Save Note.

To delete a note, click the red Delete button located on any specific note card.

To lock the session, click the Lock App button at the top header area. Re-entering the valid passkey is required to resume using the app.

---

## OOP Implementation

Classes & Objects
Note (model.py): Dataclass serving as the data model representing individual note entities.
NoteRepository (repository.py): Encapsulates direct SQLite operations.
NoteService (service.py): Encapsulates business domain operations and validation rules.
NoteCard (view.py): Inherits from PyQt6's QFrame to construct visual cards containing note information and interactive deletion buttons.
NotesApp (view.py): Inherits from PyQt6's QMainWindow to assemble the main application view, handle user inputs, manage layout grids, and route passkey prompts.

Object-Oriented Principles Applied

Encapsulation:
NoteRepository encapsulates database connection management and raw query logic behind direct operational methods.
NoteService encapsulates validation rules and authentication constants (PASSKEY), keeping passkey comparison details hidden from UI elements.
NoteCard encapsulates layout rendering and custom styling for individual note elements.

Inheritance:
NotesApp inherits from PyQt6 QMainWindow.
NoteCard inherits from PyQt6 QFrame to build composite custom widgets.

Polymorphism / Event Callbacks:
The delete_callback mechanism in NoteCard dynamically connects GUI button click events to deletion actions managed by the main window and service layer.

Dependency Injection:
Objects are passed into constructors (e.g., NoteRepository injected into NoteService, and NoteService injected into NotesApp) to decouple implementation layers.

---

## Database


**Table Name:** `notes`

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | Unique identifier for each note. |
| `title` | `TEXT` | `NOT NULL` | The title of the note. |
| `category` | `TEXT` | `NOT NULL` | Group or category tag for the note. |
| `content` | `TEXT` | `NOT NULL` | The detailed content of the note. |

## Database Operations (CRUD)

| Operation | SQL Query | Method Call |
| :--- | :--- | :--- |
| **Create** | `INSERT INTO notes (title, category, content) VALUES (?, ?, ?)` | `NoteRepository.add()` |
| **Read** | `SELECT id, title, category, content FROM notes ORDER BY id DESC` | `NoteRepository.get_all()` |
| **Update** | `UPDATE notes SET title = ?, category = ?, content = ? WHERE id = ?` | `NoteRepository.update()` |
| **Delete** | `DELETE FROM notes WHERE id = ?` | `NoteRepository.delete()` |

---

## Screenshots/Test

<img width="255" height="167" alt="pass" src="https://github.com/user-attachments/assets/f1274321-aa85-4edd-8124-068e8fe30f71" />

Security dialog requesting passkey input (ELLIE GANDA) to authenticate user access before launching or unlocking the main notes organizer UI.

<img width="922" height="281" alt="output" src="https://github.com/user-attachments/assets/88433b57-b463-4f07-918e-1a819aea05af" />

The top input form containing Title (THOUGHTS), Category (PERSONAL), and Content body text (ELLIE GANDA SAUR MUCH) fields alongside the "Save Note" action button.

<img width="1830" height="402" alt="inpt " src="https://github.com/user-attachments/assets/a47e9640-0ad6-468a-b434-3a37165f635e" />

The main notes area displaying saved records as custom cards featuring category badges (PERSONAL), titles (THOUGHTS), body text (ELLIE GANDA SAUR MUCH), and action controls (Edit and Delete)

---

## Known Issues / Limitations

Hardcoded Passkey: The passkey (ELLIE GANDA) is hardcoded as plain text in the code rather than encrypted or hashed.

Single User System: No multi-user support or separate account profiles.

Unencrypted Database: The SQLite database file (notes.db) is stored locally without file-level encryption.


---

## AUTHOR

# JAN MARIEL P. PAGTAKHAN
      CS26L 3581
