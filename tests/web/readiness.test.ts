// story: e01s01
import assert from "node:assert/strict";
import test from "node:test";

import {
  interpretReadiness,
  unavailableReadiness,
} from "../../apps/web/src/readiness.ts";


test("API responses map to truthful reviewer readiness states", () => {
  const readyPayload = {
    checks: { database: "ready", pgvector: "ready" },
    status: "ready",
  };
  assert.deepEqual(interpretReadiness(200, readyPayload), {
    api: "ready",
    database: "ready",
    overall: "ready",
    pgvector: "ready",
  });

  const databaseUnavailable = {
    checks: { database: "unavailable", pgvector: "not_checked" },
    status: "unavailable",
  };
  assert.deepEqual(interpretReadiness(503, databaseUnavailable), {
    api: "ready",
    database: "unavailable",
    overall: "unavailable",
    pgvector: "not_checked",
  });

  const pgvectorUnavailable = {
    checks: { database: "ready", pgvector: "unavailable" },
    status: "unavailable",
  };
  assert.deepEqual(interpretReadiness(503, pgvectorUnavailable), {
    api: "ready",
    database: "ready",
    overall: "unavailable",
    pgvector: "unavailable",
  });

  const unavailableView = {
    api: "unavailable",
    database: "not_checked",
    overall: "unavailable",
    pgvector: "not_checked",
  } as const;
  assert.deepEqual(unavailableReadiness(), unavailableView);

  for (const [statusCode, payload] of [
    [200, { status: "ready" }],
    [500, { detail: "internal error" }],
    [500, readyPayload],
    [503, readyPayload],
    [
      503,
      {
        checks: { database: "unknown", pgvector: "ready" },
        status: "unavailable",
      },
    ],
  ] as const) {
    assert.deepEqual(
      interpretReadiness(statusCode, payload),
      unavailableView,
    );
  }

  for (const [statusCode, payload] of [
    [
      200,
      {
        checks: { database: "unavailable", pgvector: "not_checked" },
        status: "ready",
      },
    ],
    [
      503,
      {
        checks: { database: "unavailable", pgvector: "unavailable" },
        status: "unavailable",
      },
    ],
    [
      503,
      {
        checks: { database: "ready", pgvector: "ready" },
        status: "unavailable",
      },
    ],
  ] as const) {
    assert.deepEqual(
      interpretReadiness(statusCode, payload),
      unavailableView,
    );
  }
});
