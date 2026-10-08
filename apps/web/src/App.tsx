import { FormEvent, useState } from "react";
import {
  InvestigationResponse,
  resumeInvestigation,
  startInvestigation
} from "./api";
import "./styles.css";

export default function App() {
  const [subject, setSubject] = useState("customer-123");
  const [question, setQuestion] = useState(
    "Why are payments failing, are there active incidents, and what should we do?"
  );
  const [result, setResult] = useState<InvestigationResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setResult(await startInvestigation(question, subject));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function decide(approved: boolean) {
    if (!result) return;
    setBusy(true);
    setError("");
    try {
      setResult(await resumeInvestigation(result.workflow_id, approved));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header>
        <p className="eyebrow">Governed Enterprise Agentic Platform</p>
        <h1>Enterprise Investigation</h1>
        <p className="subtitle">
          The agent chooses capabilities. Policy decides what it may access.
        </p>
      </header>

      <section className="card">
        <form onSubmit={submit}>
          <label>
            Subject
            <input value={subject} onChange={(e) => setSubject(e.target.value)} />
          </label>
          <label>
            Investigation request
            <textarea
              rows={6}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
          </label>
          <button disabled={busy}>{busy ? "Running…" : "Investigate"}</button>
        </form>
      </section>

      {error && <section className="card error">{error}</section>}

      {result && (
        <section className="card">
          <div className="status">{result.status}</div>
          <p className="mono">workflow: {result.workflow_id}</p>
          {result.answer && <p className="answer">{result.answer}</p>}
          {result.errors.length > 0 && (
            <pre>{JSON.stringify(result.errors, null, 2)}</pre>
          )}

          {result.status === "awaiting_approval" && result.approval_request && (
            <div className="approval">
              <h2>Human approval required</h2>
              <pre>
                {JSON.stringify(result.approval_request.proposed_action, null, 2)}
              </pre>
              <div className="actions">
                <button disabled={busy} onClick={() => decide(true)}>
                  Approve
                </button>
                <button className="secondary" disabled={busy} onClick={() => decide(false)}>
                  Reject
                </button>
              </div>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
