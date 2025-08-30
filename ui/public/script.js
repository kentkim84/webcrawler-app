// Simple config: change this if your API isn’t on localhost:8000
const API_BASE = (window.API_BASE_OVERRIDE) || "http://localhost:8000";
document.getElementById("api-base").textContent = API_BASE;

// tiny helper
const j = (sel) => document.querySelector(sel);
const show = (sel, obj) => j(sel).textContent = JSON.stringify(obj, null, 2);

// Start crawl
j("#crawl-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = j("#crawl-url").value.trim();
  try {
    const res = await fetch(`${API_BASE}/crawl/start?url=${encodeURIComponent(url)}`, {
      method: "POST"
    });
    const data = await res.json();
    show("#crawl-start-result", data);
    j("#job-id").value = data.job_id || "";
    j("#analysis-job-id").value = data.job_id || "";
  } catch (err) {
    show("#crawl-start-result", { error: String(err) });
  }
});

// Crawl status
j("#btn-crawl-status").addEventListener("click", async () => {
  const jobId = j("#job-id").value.trim();
  try {
    const res = await fetch(`${API_BASE}/crawl/status/${encodeURIComponent(jobId)}`);
    const data = await res.json();
    show("#crawl-status", data);
  } catch (err) {
    show("#crawl-status", { error: String(err) });
  }
});

// Crawl result
j("#btn-crawl-result").addEventListener("click", async () => {
  const jobId = j("#job-id").value.trim();
  try {
    const res = await fetch(`${API_BASE}/crawl/result/${encodeURIComponent(jobId)}`);
    const data = await res.json();
    show("#crawl-result", data);
  } catch (err) {
    show("#crawl-result", { error: String(err) });
  }
});

// Analysis run
j("#btn-analysis-run").addEventListener("click", async () => {
  const jobId = j("#analysis-job-id").value.trim();
  try {
    const res = await fetch(`${API_BASE}/analysis/run?job_id=${encodeURIComponent(jobId)}`, {
      method: "POST"
    });
    const data = await res.json();
    show("#analysis-status", data);
  } catch (err) {
    show("#analysis-status", { error: String(err) });
  }
});

// Analysis status
j("#btn-analysis-status").addEventListener("click", async () => {
  const jobId = j("#analysis-job-id").value.trim();
  try {
    const res = await fetch(`${API_BASE}/analysis/status/${encodeURIComponent(jobId)}`);
    const data = await res.json();
    show("#analysis-status", data);
  } catch (err) {
    show("#analysis-status", { error: String(err) });
  }
});

// Analysis result
j("#btn-analysis-result").addEventListener("click", async () => {
  const jobId = j("#analysis-job-id").value.trim();
  try {
    const res = await fetch(`${API_BASE}/analysis/result/${encodeURIComponent(jobId)}`);
    const data = await res.json();
    show("#analysis-result", data);
  } catch (err) {
    show("#analysis-result", { error: String(err) });
  }
});