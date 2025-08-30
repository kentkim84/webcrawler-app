import axios from "axios";

const SCRAPER_BASE = process.env.REACT_APP_SCRAPER_URL || "http://localhost:8000";

export async function startCrawl(payload) {
  // payload: { url: string, depth?: number, spider?: string }
  const resp = await axios.post(`${SCRAPER_BASE}/crawl`, payload);
  return resp.data; // { job_id }
}

export async function getStatus(jobId) {
  const resp = await axios.get(`${SCRAPER_BASE}/status/${jobId}`);
  return resp.data; // { job_id, status, message }
}

export async function getResult(jobId) {
  const resp = await axios.get(`${SCRAPER_BASE}/result/${jobId}`);
  return resp.data; // JSON results or 404
}
