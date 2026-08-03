# story: e01s01
import unittest
from types import TracebackType

from services.api.medinfo_api.postgres_readiness import PostgresReadinessProbe
from services.api.medinfo_api.readiness import ReadinessSnapshot


class FakeCursor:
    def __init__(self, vector_version: str | None) -> None:
        self._vector_version = vector_version

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def execute(self, query: str) -> None:
        return None

    def fetchone(self) -> tuple[str] | None:
        if self._vector_version is None:
            return None
        return (self._vector_version,)


class FakeConnection:
    def __init__(self, vector_version: str | None) -> None:
        self._vector_version = vector_version

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return FakeCursor(self._vector_version)


class FakeConnector:
    def __init__(self, vector_version: str | None) -> None:
        self._vector_version = vector_version

    def __call__(self, database_url: str, connect_timeout: int) -> FakeConnection:
        return FakeConnection(self._vector_version)


class FailedConnector:
    def __call__(self, database_url: str, connect_timeout: int) -> FakeConnection:
        raise ConnectionError("postgresql://credential-that-must-not-escape")


class PostgresReadinessProbeTests(unittest.TestCase):
    def test_probe_without_database_url_is_unavailable(self) -> None:
        probe = PostgresReadinessProbe("", connector=FailedConnector())

        self.assertEqual(
            probe.check(),
            ReadinessSnapshot(database="unavailable", pgvector="not_checked"),
        )

    def test_probe_maps_database_outcomes_to_bounded_states(self) -> None:
        cases = (
            (
                FailedConnector(),
                ReadinessSnapshot(
                    database="unavailable",
                    pgvector="not_checked",
                ),
            ),
            (
                FakeConnector(None),
                ReadinessSnapshot(database="ready", pgvector="unavailable"),
            ),
            (
                FakeConnector("0.8.5"),
                ReadinessSnapshot(database="ready", pgvector="unavailable"),
            ),
            (
                FakeConnector("0.8.6"),
                ReadinessSnapshot(database="ready", pgvector="ready"),
            ),
        )

        for connector, expected in cases:
            with self.subTest(expected=expected):
                probe = PostgresReadinessProbe(
                    "postgresql://local-test",
                    connector=connector,
                )
                self.assertEqual(probe.check(), expected)


if __name__ == "__main__":
    unittest.main()
