import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const isValidUrl = (string) => {
    try {
      const parsedUrl = new URL(string);
      // Ensure the URL has a valid scheme and hostname
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
      console.error('Axios error:', err);
      // Handle Pydantic validation errors
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // Extract message from Pydantic error array
          const errorMessage = detail.map((e) => e.msg).join('; ') || 'Error scraping URL';
          setError(errorMessage);
        } else {
          setError(detail || 'Error scraping URL');
        }
      } else {
        setError('Error scraping URL. Please try again.');
      }
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