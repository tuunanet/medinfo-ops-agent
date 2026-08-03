# story: e01s01
import unittest

from httpx import ASGITransport, AsyncClient

from services.api.medinfo_api.main import create_app
from services.api.medinfo_api.readiness import ReadinessSnapshot


class ExplodingReadinessProbe:
    def check(self) -> None:
        raise ConnectionError("postgresql://credential-that-must-not-escape@database")


class StaticReadinessProbe:
    def __init__(self, snapshot: ReadinessSnapshot) -> None:
        self._snapshot = snapshot

    def check(self) -> ReadinessSnapshot:
        return self._snapshot


class HealthApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_liveness_succeeds_without_querying_dependencies(self) -> None:
        transport = ASGITransport(app=create_app(ExplodingReadinessProbe()))

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            response = await client.get("/health/live")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"service": "api", "status": "live"},
        )

    async def test_readiness_reports_current_dependency_states(self) -> None:
        cases = (
            (
                ReadinessSnapshot(database="ready", pgvector="ready"),
                200,
                "ready",
            ),
            (
                ReadinessSnapshot(
                    database="unavailable",
                    pgvector="not_checked",
                ),
                503,
                "unavailable",
            ),
            (
                ReadinessSnapshot(database="ready", pgvector="unavailable"),
                503,
                "unavailable",
            ),
        )

        for snapshot, expected_code, expected_status in cases:
            with self.subTest(snapshot=snapshot):
                response = await self._get(
                    "/health/ready",
                    StaticReadinessProbe(snapshot),
                )
                self.assertEqual(response.status_code, expected_code)
                self.assertEqual(
                    response.json(),
                    {
                        "checks": {
                            "database": snapshot.database,
                            "pgvector": snapshot.pgvector,
                        },
                        "status": expected_status,
                    },
                )

    async def test_readiness_failure_returns_bounded_unavailable_state(self) -> None:
        response = await self._get(
            "/health/ready",
            ExplodingReadinessProbe(),
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "checks": {
                    "database": "unavailable",
                    "pgvector": "not_checked",
                },
                "status": "unavailable",
            },
        )
        self.assertNotIn("credential-that-must-not-escape", response.text)

    async def _get(self, path: str, probe: object):
        transport = ASGITransport(
            app=create_app(probe),
            raise_app_exceptions=False,
        )
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get(path)


if __name__ == "__main__":
    unittest.main()
