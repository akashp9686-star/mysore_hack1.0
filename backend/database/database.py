
"""
SQLite database access layer for HackMysore 1.0.

Aakash-facing interface:
    from backend.database.database import get_connection, fetch_one, fetch_all, execute

The FastAPI layer should use this module rather than opening its own
independent SQLite connections.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "hackmysore.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def get_connection() -> sqlite3.Connection:
    """Open a configured SQLite connection."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """
    Transactional database context.

    Commits on success and rolls back on exception.
    Always closes the connection.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database() -> None:
    """Create the base schema and apply additive, idempotent migrations."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    migration_tables = (MIGRATIONS_DIR / "001_teacher_misconception_authoring_tables.sql").read_text(encoding="utf-8")
    migration_selected_option = (MIGRATIONS_DIR / "002_attempt_selected_option.sql").read_text(encoding="utf-8")
    migration_subjects = (MIGRATIONS_DIR / "003_integrated_subjects.sql").read_text(encoding="utf-8")

    with get_db() as conn:
        conn.executescript(schema)
        conn.executescript(migration_tables)

        columns = {row[1] for row in conn.execute("PRAGMA table_info(attempts)").fetchall()}
        if "selected_option_id" not in columns:
            conn.executescript(migration_selected_option)

        conn.executescript(migration_subjects)


def fetch_one(
    query: str,
    params: Sequence[Any] = (),
) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute(query, params).fetchone()


def fetch_all(
    query: str,
    params: Sequence[Any] = (),
) -> list[sqlite3.Row]:
    with get_db() as conn:
        return conn.execute(query, params).fetchall()


def execute(
    query: str,
    params: Sequence[Any] = (),
) -> int:
    """
    Execute one INSERT/UPDATE/DELETE and return the affected row id
    (lastrowid for INSERT, rowcount otherwise).
    """
    with get_db() as conn:
        cursor = conn.execute(query, params)
        return cursor.lastrowid if cursor.lastrowid is not None else cursor.rowcount


def execute_many(
    query: str,
    rows: Iterable[Sequence[Any]],
) -> None:
    with get_db() as conn:
        conn.executemany(query, rows)


def reset_database() -> None:
    """Delete the local database file so seed.py can recreate it."""
    if DB_PATH.exists():
        DB_PATH.unlink()
