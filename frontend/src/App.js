import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const isValidUrl = (string) => {
    try {
      const parsedUrl = new URL(string);
      return ['http:', 'https:'].includes(parsedUrl.protocol) && !!parsedUrl.hostname;
    } catch (_) {
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!isValidUrl(url)) {
      setError('Please enter a valid URL (e.g., https://example.com)');
      return;
    }

    try {
      const response = await axios.post('http://localhost:8000/scrape/', { url });
      setResult(response.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Error scraping URL. Please try again.');
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Web Scraper</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL (e.g., https://example.com)"
          style={{ width: '300px', marginRight: '10px' }}
          required
        />
        <button type="submit">Scrape</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <div>
          <h2>Results for {result.url}</h2>
          <p><strong>Title:</strong> {result.title}</p>
          <p><strong>Content:</strong> {result.content}</p>
          <p><strong>Timestamp:</strong> {result.timestamp}</p>
        </div>
      )}
    </div>
  );
}

export default App;