"""Small SQLite persistence layer; no external database service required."""

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from app.production.schemas import ProjectCreate, ProjectRead


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _database_path() -> Path:
    default_path = "/tmp/lyra-production.sqlite3" if os.getenv("VERCEL") else "data/production.sqlite3"
    configured = os.getenv("LYRA_PRODUCTION_DB_PATH", default_path)
    path = Path(configured).expanduser()
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class ProductionStore:
    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or _database_path()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS production_projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    language TEXT NOT NULL,
                    aspect_ratio TEXT NOT NULL,
                    visual_style TEXT NOT NULL,
                    target_duration_seconds INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS production_jobs (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled')
                    ),
                    payload_json TEXT NOT NULL,
                    result_json TEXT,
                    error_code TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES production_projects(id)
                        ON DELETE CASCADE
                )"""
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_production_jobs_project "
                "ON production_jobs(project_id, created_at)"
            )

    @staticmethod
    def _to_project(row: sqlite3.Row) -> ProjectRead:
        return ProjectRead(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            language=row["language"],
            aspect_ratio=row["aspect_ratio"],
            visual_style=row["visual_style"],
            target_duration_seconds=row["target_duration_seconds"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create_project(self, payload: ProjectCreate) -> ProjectRead:
        project_id = str(uuid.uuid4())
        now = _utc_now()
        data = payload.model_dump()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO production_projects (
                    id, title, description, language, aspect_ratio, visual_style,
                    target_duration_seconds, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    project_id, data["title"], data["description"], data["language"],
                    data["aspect_ratio"], data["visual_style"],
                    data["target_duration_seconds"],
                    json.dumps(data["metadata"], ensure_ascii=False), now, now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM production_projects WHERE id = ?", (project_id,)
            ).fetchone()
        return self._to_project(row)

    def get_project(self, project_id: str) -> ProjectRead | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM production_projects WHERE id = ?", (project_id,)
            ).fetchone()
        return self._to_project(row) if row else None


@lru_cache(maxsize=1)
def get_store() -> ProductionStore:
    """Initialize storage lazily so importing the FastAPI app has no disk side effects."""
    return ProductionStore()
