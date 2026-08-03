// story: e01s01
export type DependencyState = "ready" | "unavailable" | "not_checked";
export type OverallState = "ready" | "unavailable";

export type ReadinessView = {
  api: "ready" | "unavailable";
  database: DependencyState;
  overall: OverallState;
  pgvector: DependencyState;
};

const UNAVAILABLE_VIEW: ReadinessView = {
  api: "unavailable",
  database: "not_checked",
  overall: "unavailable",
  pgvector: "not_checked",
};

export function interpretReadiness(
  statusCode: number,
  payload: unknown,
): ReadinessView {
  if (!isReadinessPayload(statusCode, payload)) {
    return UNAVAILABLE_VIEW;
  }

  return {
    api: "ready",
    database: payload.checks.database,
    overall: payload.status,
    pgvector: payload.checks.pgvector,
  };
}

export function unavailableReadiness(): ReadinessView {
  return UNAVAILABLE_VIEW;
}

function isReadinessPayload(
  statusCode: number,
  payload: unknown,
): payload is {
  checks: { database: DependencyState; pgvector: DependencyState };
  status: OverallState;
} {
  if (!isRecord(payload) || !isRecord(payload.checks)) {
    return false;
  }
  const expectedStatus = statusCode === 200 ? "ready" : "unavailable";
  if (statusCode !== 200 && statusCode !== 503) {
    return false;
  }
  const database = payload.checks.database;
  const pgvector = payload.checks.pgvector;
  if (
    payload.status !== expectedStatus ||
    !isDependencyState(database) ||
    !isDependencyState(pgvector)
  ) {
    return false;
  }
  return hasCoherentStates(expectedStatus, database, pgvector);
}

function hasCoherentStates(
  overall: OverallState,
  database: DependencyState,
  pgvector: DependencyState,
): boolean {
  if (overall === "ready") {
    return database === "ready" && pgvector === "ready";
  }
  return (
    (database === "unavailable" && pgvector === "not_checked") ||
    (database === "ready" && pgvector === "unavailable")
  );
}

function isDependencyState(value: unknown): value is DependencyState {
  return (
    value === "ready" || value === "unavailable" || value === "not_checked"
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}
