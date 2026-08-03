// story: e01s01
import { ReadinessPanel } from "../src/ReadinessPanel";


export default function ReviewerWorkspacePage() {
  return (
    <main>
      <header className="workspace-header">
        <p className="product-name">medinfo-ops-agent</p>
        <h1>Reviewer workspace</h1>
        <p className="synthetic-notice">
          Synthetic demonstration only. Not for clinical use.
        </p>
      </header>
      <ReadinessPanel />
    </main>
  );
}
