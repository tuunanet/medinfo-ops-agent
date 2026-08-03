# story: e01s01
from dataclasses import dataclass
from typing import Literal

DependencyStatus = Literal["ready", "unavailable", "not_checked"]


@dataclass(frozen=True, slots=True)
class ReadinessSnapshot:
    database: DependencyStatus
    pgvector: DependencyStatus

    @property
    def is_ready(self) -> bool:
        return self.database == "ready" and self.pgvector == "ready"
