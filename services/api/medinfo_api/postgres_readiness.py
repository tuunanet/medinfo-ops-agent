# story: e01s01
import os
from contextlib import AbstractContextManager
from typing import Protocol, cast

import psycopg

from services.api.medinfo_api.readiness import ReadinessSnapshot

EXPECTED_VECTOR_VERSION = "0.8.6"
VECTOR_VERSION_QUERY = "SELECT extversion FROM pg_extension WHERE extname = 'vector'"


class QueryCursor(Protocol):
    def execute(self, query: str) -> object:
        """Execute one developer-authored readiness query."""

    def fetchone(self) -> tuple[str] | None:
        """Return the extension version when installed."""


class QueryConnection(Protocol):
    def cursor(self) -> AbstractContextManager[QueryCursor]:
        """Open a cursor for one bounded readiness query."""


class Connector(Protocol):
    def __call__(
        self,
        database_url: str,
        *,
        connect_timeout: int,
    ) -> AbstractContextManager[QueryConnection]:
        """Open a bounded PostgreSQL connection."""


class PostgresReadinessProbe:
    def __init__(
        self,
        database_url: str,
        connector: Connector | None = None,
    ) -> None:
        self._database_url = database_url
        self._connector = connector or cast(Connector, psycopg.connect)

    @classmethod
    def from_environment(cls) -> PostgresReadinessProbe:
        return cls(os.environ.get("DATABASE_URL", ""))

    def check(self) -> ReadinessSnapshot:
        if not self._database_url:
            return self._database_unavailable()

        try:
            vector_version = self._read_vector_version()
        except Exception:
            return self._database_unavailable()

        return ReadinessSnapshot(
            database="ready",
            pgvector=(
                "ready" if vector_version == EXPECTED_VECTOR_VERSION else "unavailable"
            ),
        )

    def _read_vector_version(self) -> str | None:
        with self._connector(
            self._database_url,
            connect_timeout=1,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(VECTOR_VERSION_QUERY)
                row = cursor.fetchone()
        return row[0] if row else None

    def _database_unavailable(self) -> ReadinessSnapshot:
        return ReadinessSnapshot(
            database="unavailable",
            pgvector="not_checked",
        )
