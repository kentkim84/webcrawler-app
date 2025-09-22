import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './Dashboard';

function App() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [scrapes, setScrapes] = useState([]);
  const [search, setSearch] = useState('');
  const [isRegister, setIsRegister] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      setIsLoggedIn(true);
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      fetchScrapes();
    }
  }, []);

  const isValidUrl = (string) => {
    try {
      const parsedUrl = new URL(string);
      return ['http:', 'https:'].includes(parsedUrl.protocol) && !!parsedUrl.hostname;
    } catch (_) {
      return false;
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const response = await axios.post('http://localhost:8000/token', { username, password }, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      const newToken = response.data.access_token;
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setIsLoggedIn(true);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      fetchScrapes();
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      await axios.post('http://localhost:8000/register', { username, password });
      setError('Registration successful. Please login.');
      setIsRegister(false);
    } catch (err) {
      setError('Registration failed. Username may already exist.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsLoggedIn(false);
    delete axios.defaults.headers.common['Authorization'];
    setScrapes([]);
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
      fetchScrapes();
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(detail || 'Error scraping URL. Please try again.');
    }
  };

  const fetchScrapes = async (searchTerm = '') => {
    try {
      const response = await axios.get(`http://localhost:8000/scrapes/?search=${searchTerm}`);
      setScrapes(response.data);
    } catch (err) {
      setError('Failed to fetch scrapes.');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchScrapes(search);
  };

  if (!isLoggedIn) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Web Scraper</h1>
        {isRegister ? (
          <form onSubmit={handleRegister}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              required
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
            <button type="submit">Register</button>
            <button onClick={() => setIsRegister(false)}>Back to Login</button>
          </form>
        ) : (
          <form onSubmit={handleLogin}>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Username"
              required
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
            />
            <button type="submit">Login</button>
            <button onClick={() => setIsRegister(true)}>Register</button>
          </form>
        )}
        {error && <p style={{ color: 'red' }}>{error}</p>}
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Web Scraper</h1>
      <button onClick={handleLogout}>Logout</button>
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
      <h2>My Scrapes</h2>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search scrapes..."
          style={{ width: '300px', marginRight: '10px' }}
        />
        <button type="submit">Search</button>
      </form>
      <ul>
        {scrapes.map((scrape) => (
          <li key={scrape.id}>
            <strong>{scrape.title}</strong> - {scrape.url} ({scrape.timestamp})
            <p>{scrape.content.substring(0, 100)}...</p>
          </li>
        ))}
      </ul>
      <Dashboard />
    </div>
  );
}

export default App;