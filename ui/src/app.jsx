import React, { useState } from 'react'
import axios from 'axios'


const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'


export default function App() {
const [url, setUrl] = useState('')
const [loading, setLoading] = useState(false)
const [result, setResult] = useState(null)
const [error, setError] = useState(null)


async function startScrape() {
setLoading(true)
setError(null)
setResult(null)
try {
const resp = await axios.post(`${API_URL}/scrape`, { url })
setResult(resp.data)
} catch (err) {
setError(err?.response?.data || err.message)
} finally {
setLoading(false)
}
}


return (
<div style={{ maxWidth: 900, margin: '40px auto', fontFamily: 'sans-serif' }}>
<h1>Simple Web Scraper</h1>
<div style={{ display: 'flex', gap: 8 }}>
<input
style={{ flex: 1, padding: 8 }}
value={url}
onChange={e => setUrl(e.target.value)}
placeholder="Enter URL to scrape (e.g. https://example.com)"
/>
<button onClick={startScrape} disabled={!url || loading}>
{loading ? 'Scraping...' : 'Start'}
</button>
</div>


<div style={{ marginTop: 24 }}>
{error && (
<pre style={{ color: 'crimson' }}>{JSON.stringify(error, null, 2)}</pre>
)}


{result && (
<div>
<h2>Result</h2>
<p><strong>URL:</strong> {result.url}</p>
<p><strong>Title:</strong> {result.title}</p>
<p><strong>Text snippet:</strong></p>
<pre style={{ whiteSpace: 'pre-wrap', maxHeight: 300, overflow: 'auto', background: '#f5f5f5', padding: 12 }}>
{result.text_snippet}
</pre>
<h3>Normalized data (table)</h3>
<pre style={{ background: '#f0f0f0', padding: 12 }}>{JSON.stringify(result.normalized, null, 2)}</pre>
</div>
)}
</div>
</div>
)
}