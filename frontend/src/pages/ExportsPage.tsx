import { useState } from "react";
import { downloadPdf } from "../api";
import { ErrorBox } from "../components/Layout";

const REPORTS = [
  ["weekly", "Weekly report"],
  ["alltime", "All-time records"],
  ["sagarin", "Sagarin ratings"],
  ["playoffs", "Playoff report"],
] as const;

export function ExportsPage() {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  async function onDownload(report: string) {
    setError("");
    setBusy(report);
    try {
      await downloadPdf(report);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    } finally {
      setBusy("");
    }
  }

  return (
    <div className="panel">
      <h2>PDF exports</h2>
      <p className="muted">Same structured data as the dashboard, packaged for easy sharing.</p>
      {error ? <ErrorBox message={error} /> : null}
      <div className="btn-row">
        {REPORTS.map(([id, label]) => (
          <button key={id} onClick={() => onDownload(id)} disabled={busy === id}>
            {busy === id ? "Generating…" : label}
          </button>
        ))}
      </div>
    </div>
  );
}
