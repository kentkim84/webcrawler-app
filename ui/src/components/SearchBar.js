import React, { useState } from "react";

export default function SearchBar({ onStart }) {
  const [url, setUrl] = useState("");
  const [spider, setSpider] = useState("news");

  const submit = (e) => {
    e.preventDefault();
    if (!url) return alert("Please provide a URL");
    onStart({ url, spider, depth: 1 });
  };

  return (
    <form onSubmit={submit} style={{ display: "flex", gap: 8 }}>
      <input
        placeholder="https://example.com/article"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ flex: 1, padding: 8 }}
      />
      <select value={spider} onChange={(e) => setSpider(e.target.value)}>
        <option value="news">news</option>
        <option value="blog">blog</option>
        <option value="ecommerce">ecommerce</option>
      </select>
      <button type="submit">Start Crawl</button>
    </form>
  );
}
