# story: e01s01
from typing import Literal, Protocol

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from services.api.medinfo_api.postgres_readiness import PostgresReadinessProbe
from services.api.medinfo_api.readiness import DependencyStatus, ReadinessSnapshot


class ReadinessProbe(Protocol):
    """Check whether bounded application dependencies are ready."""

    def check(self) -> ReadinessSnapshot:
        """Return the current dependency state."""


class LivenessResponse(BaseModel):
    service: Literal["api"] = "api"
    status: Literal["live"] = "live"


class ReadinessChecks(BaseModel):
    database: DependencyStatus
    pgvector: DependencyStatus


class ReadinessResponse(BaseModel):
    checks: ReadinessChecks
    status: Literal["ready", "unavailable"]


def check_readiness(probe: ReadinessProbe) -> ReadinessSnapshot:
    try:
        return probe.check()
    except Exception:
        return ReadinessSnapshot(
            database="unavailable",
            pgvector="not_checked",
        )


def create_app(readiness_probe: ReadinessProbe | None = None) -> FastAPI:
    """Create the API and accept its dependency probe explicitly."""
    application = FastAPI(title="medinfo-ops-agent")
    selected_probe = readiness_probe or PostgresReadinessProbe.from_environment()

    @application.get("/health/live", response_model=LivenessResponse)
    def get_liveness() -> LivenessResponse:
        return LivenessResponse()

    @application.get("/health/ready", response_model=ReadinessResponse)
    def get_readiness(response: Response) -> ReadinessResponse:
        snapshot = check_readiness(selected_probe)
        if not snapshot.is_ready:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            checks=ReadinessChecks(
                database=snapshot.database,
                pgvector=snapshot.pgvector,
            ),
            status="ready" if snapshot.is_ready else "unavailable",
        )

    return application


app = create_app()
