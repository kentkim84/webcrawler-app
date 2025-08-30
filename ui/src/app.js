import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [status, setStatus] = useState("No jobs started");

  const startCrawl = async () => {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/crawl/start`, {
      url: "https://example.com",
    });
    setStatus(`Crawl started: ${res.data.job_id}`);
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Web Scraper Dashboard</h1>
      <button onClick={startCrawl}>Start Crawl</button>
      <p>Status: {status}</p>
    </div>
  );
}

export default App;