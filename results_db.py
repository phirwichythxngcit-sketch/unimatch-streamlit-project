"""SQLite persistence for UniMatch result history."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DATABASE_PATH = Path(__file__).with_name("results.db")


def _connect(database_path: Path | str = DATABASE_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path | str = DATABASE_PATH) -> None:
    with _connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                mbti TEXT NOT NULL,
                top_faculty TEXT NOT NULL,
                compatibility INTEGER NOT NULL CHECK (compatibility BETWEEN 0 AND 100),
                budget TEXT,
                selection_basis TEXT NOT NULL DEFAULT 'จัดอันดับจากคะแนนความเข้ากัน'
            )
            """
        )
        columns = {row["name"] for row in connection.execute("PRAGMA table_info(results)")}
        if "selection_basis" not in columns:
            connection.execute(
                "ALTER TABLE results ADD COLUMN selection_basis TEXT NOT NULL DEFAULT 'จัดอันดับจากคะแนนความเข้ากัน'"
            )


def save_result(
    participant_name: str,
    mbti: str,
    top_faculty: str,
    compatibility: int,
    budget: str | None,
    selection_basis: str,
    database_path: Path | str = DATABASE_PATH,
) -> int:
    """Save one completed assessment and return its database id."""
    name = participant_name.strip()
    if not name:
        raise ValueError("กรุณาระบุชื่อก่อนบันทึกผล")
    if not 0 <= compatibility <= 100:
        raise ValueError("คะแนนความเข้ากันต้องอยู่ระหว่าง 0 ถึง 100")
    if not selection_basis.strip():
        raise ValueError("ต้องระบุเกณฑ์คัดเลือก")

    initialize_database(database_path)
    with _connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO results (participant_name, mbti, top_faculty, compatibility, budget, selection_basis)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, mbti, top_faculty, compatibility, budget, selection_basis.strip()),
        )
        return int(cursor.lastrowid)


def list_results(database_path: Path | str = DATABASE_PATH) -> list[dict[str, Any]]:
    """Return the public history, newest result first."""
    initialize_database(database_path)
    with _connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT id, participant_name, created_at, mbti, top_faculty, compatibility, budget, selection_basis
            FROM results
            ORDER BY id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_result(result_id: int, database_path: Path | str = DATABASE_PATH) -> bool:
    """Delete exactly one record. Authorization is enforced by the Streamlit UI."""
    initialize_database(database_path)
    with _connect(database_path) as connection:
        cursor = connection.execute("DELETE FROM results WHERE id = ?", (result_id,))
        return cursor.rowcount == 1
