"use client";

// story: e01s01
import { useEffect, useState } from "react";

import {
  interpretReadiness,
  type DependencyState,
  type ReadinessView,
  unavailableReadiness,
} from "./readiness";


type DisplayState = DependencyState | "checking";

const CHECKING_VIEW: ReadinessView = {
  api: "unavailable",
  database: "not_checked",
  overall: "unavailable",
  pgvector: "not_checked",
};

export function ReadinessPanel() {
  const [readiness, setReadiness] = useState<ReadinessView>(CHECKING_VIEW);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    async function loadReadiness() {
      try {
        const response = await fetch("/api/health/ready", { cache: "no-store" });
        setReadiness(interpretReadiness(response.status, await response.json()));
      } catch {
        setReadiness(unavailableReadiness());
      } finally {
        setChecking(false);
      }
    }

    void loadReadiness();
  }, []);

  const overallState: DisplayState = checking ? "checking" : readiness.overall;
  const failureGuidance = getFailureGuidance(checking, readiness);

  return (
    <section aria-labelledby="readiness-heading" className="readiness-panel">
      <div className="readiness-summary" aria-live="polite" role="status">
        <h2 id="readiness-heading">Local readiness</h2>
        <strong data-state={overallState} data-testid="overall-status">
          {formatState(overallState)}
        </strong>
      </div>
      <dl className="readiness-checks">
        <StatusRow label="API" state={checking ? "checking" : readiness.api} testId="api-status" />
        <StatusRow label="Database" state={checking ? "checking" : readiness.database} testId="database-status" />
        <StatusRow label="pgvector" state={checking ? "checking" : readiness.pgvector} testId="pgvector-status" />
      </dl>
      {failureGuidance ? (
        <p className="failure-guidance" role="alert">
          {failureGuidance}
        </p>
      ) : null}
    </section>
  );
}

type StatusRowProps = {
  label: string;
  state: DisplayState;
  testId: string;
};

function StatusRow({ label, state, testId }: StatusRowProps) {
  return (
    <div className="status-row">
      <dt>{label}</dt>
      <dd data-state={state} data-testid={testId}>
        {formatState(state)}
      </dd>
    </div>
  );
}

function getFailureGuidance(
  checking: boolean,
  readiness: ReadinessView,
): string | null {
  if (checking || readiness.overall === "ready") {
    return null;
  }
  if (readiness.api === "unavailable") {
    return "Check that the FastAPI process is running, then refresh this page.";
  }
  if (readiness.database === "unavailable") {
    return "Start the local PostgreSQL container, then refresh this page.";
  }
  return "Verify that pgvector 0.8.6 is installed, then refresh this page.";
}

function formatState(state: DisplayState): string {
  if (state === "not_checked") {
    return "Not checked";
  }
  return `${state.charAt(0).toUpperCase()}${state.slice(1)}`;
}
