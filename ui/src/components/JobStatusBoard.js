import React, { useEffect, useState } from "react";
import { getStatus, getResult } from "../services/api";

export default function JobStatusBoard({ jobId }) {
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;

    async function poll() {
      try {
        const s = await getStatus(jobId);
        if (cancelled) return;
        setStatus(s);
        if (s.status === "finished") {
          const r = await getResult(jobId);
          setResult(r);
        } else if (s.status === "failed") {
          // stop polling
        } else {
          setTimeout(poll, 2000);
        }
      } catch (err) {
        console.error(err);
        setTimeout(poll, 3000);
      }
    }
    poll();
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  if (!jobId) return <div>No job started yet.</div>;
  return (
    <div>
      <h3>Job {jobId}</h3>
      <p>Status: {status ? status.status : "starting..."}</p>
      <p>Message: {status ? status.message : "-"}</p>
      {result && (
        <>
          <h4>Result (first 3 items)</h4>
          <pre style={{ maxHeight: 300, overflow: "auto" }}>
            {JSON.stringify(result.slice(0, 3), null, 2)}
          </pre>
          <a href={`/api/download/${jobId}`} target="_blank" rel="noreferrer">Download full result (if available)</a>
        </>
      )}
    </div>
  );
}
