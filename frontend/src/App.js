// src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'https://neuroity-backend.onrender.com';

// ─── SVG ICONS ───
const SearchIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

const SparkleIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L13.5 10.5L22 12L13.5 13.5L12 22L10.5 13.5L2 12L10.5 10.5L12 2Z" />
  </svg>
);

const ArrowIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const AIStarIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L13.5 10.5L22 12L13.5 13.5L12 22L10.5 13.5L2 12L10.5 10.5L12 2Z" />
    <path d="M8 8L16 16" />
    <path d="M16 8L8 16" />
  </svg>
);

function App() {
  const [query, setQuery] = useState('iris');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    source: '',
    filetype: '',
    domain: '',
  });

  useEffect(() => {
    search(0);
  }, []);

  const search = async (offset = 0) => {
    if (!query.trim()) return;
    setLoading(true);

    let url = `${API_BASE}/api/v1/search?q=${encodeURIComponent(query)}&limit=10&offset=${offset}`;
    if (filters.source) url += `&source=${filters.source}`;
    if (filters.filetype) url += `&filetype=${filters.filetype}`;
    if (filters.domain) url += `&domain=${filters.domain}`;

    try {
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) {
        setResults(data.results || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    search(0);
  };

  const formatSize = (bytes) => {
    if (!bytes || bytes === 0) return '—';
    if (bytes >= 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} TB`;
    if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} GB`;
    if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${bytes} B`;
  };

  const formatSamples = (num) => {
    if (!num || num === 0) return '—';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const cleanTag = (tag) => {
    const map = {
      'size_categories:n<1K': 'Small',
      'size_categories:1K<n<10K': 'Medium',
      'size_categories:10K<n<100K': 'Large',
      'size_categories:100K<n<1M': 'XL',
      'size_categories:1M<n<10M': 'XXL',
      'format:csv': 'CSV',
      'format:json': 'JSON',
      'format:parquet': 'Parquet',
      'format:jsonl': 'JSONL',
      'format:txt': 'Text',
      'modality:tabular': 'Tabular',
      'modality:text': 'Text',
      'modality:image': 'Image',
      'modality:audio': 'Audio',
      'license:mit': 'MIT',
      'license:cc0-1.0': 'CC0',
      'license:cc': 'CC',
      'license:apache-2.0': 'Apache 2.0',
      'region:us': 'US',
      'region:eu': 'EU',
      'language:en': 'English',
      'language:pt': 'Portuguese',
      'language:ga': 'Irish',
    };
    return map[tag] || tag.replace(/_/g, ' ').replace(/:/g, ': ');
  };

  const getLicenseDisplay = (license) => {
    if (!license || license === 'Unknown' || license === 'N/A') return '—';
    return license;
  };

  const getQuality = (ds) => {
    let score = 70;
    if (ds.samples && ds.samples > 1000) score += 10;
    if (ds.features && ds.features > 10) score += 5;
    if (ds.size && ds.size > 1024 * 1024) score += 5;
    if (ds.source && ds.source !== 'unknown') score += 5;
    if (ds.license && ds.license !== 'Unknown') score += 5;
    return Math.min(score, 99);
  };

  const getSourceColor = (source) => {
    const colors = {
      kaggle: '#20BEFF',
      huggingface: '#FFD21E',
      uci: '#5B3E8D',
      openml: '#FDB813',
      zenodo: '#1682B8',
      figshare: '#E94E1B',
      github: '#FFFFFF',
      openneuro: '#6B4EFF',
      physionet: '#00B4D8',
      google_dataset: '#4285F4',
    };
    return colors[source] || '#888888';
  };

  const getSourceLabel = (source) => {
    const labels = {
      kaggle: 'Kaggle',
      huggingface: 'Hugging Face',
      uci: 'UCI',
      openml: 'OpenML',
      zenodo: 'Zenodo',
      figshare: 'Figshare',
      github: 'GitHub',
      openneuro: 'OpenNeuro',
      physionet: 'PhysioNet',
      google_dataset: 'Google Dataset',
    };
    return labels[source] || source || 'Unknown';
  };

  return (
    <div className="app">
      {/* ─── NAVBAR ─── */}
      <header>
        <div className="logo">Neuroity Data Search</div>
        <nav>
          <a href="#" className="active">Datasets</a>
          <a href="#">Research</a>
          <a href="#">API</a>
          <a href="#">Pricing</a>
        </nav>
      </header>

      {/* ─── HERO ─── */}
      <main>
        <div className="hero">
          <h1>Discover Data, Build Intelligence.</h1>
        </div>

        {/* ─── SEARCH BAR ─── */}
        <form onSubmit={handleSearch} className="search-bar">
          <span className="search-icon"><SearchIcon /></span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search datasets, research papers, images, audio, video, CSV, JSON..."
          />
          <button type="submit"><SparkleIcon /> Search</button>
        </form>

        {/* ─── AI TRAINING TAG ─── */}
        <div className="ai-tag">
          <span>AI Training</span>
        </div>

        {/* ─── FILTERS ─── */}
        <div className="filters-container">
          <div className="filters">
            <div className="filter-group">
              <label>Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters({ ...filters, source: e.target.value })}
              >
                <option value="">All Sources</option>
                <option value="kaggle">Kaggle</option>
                <option value="huggingface">Hugging Face</option>
                <option value="uci">UCI</option>
                <option value="openml">OpenML</option>
                <option value="zenodo">Zenodo</option>
                <option value="figshare">Figshare</option>
                <option value="github">GitHub</option>
                <option value="openneuro">OpenNeuro</option>
                <option value="physionet">PhysioNet</option>
              </select>
            </div>
            <div className="filter-group">
              <label>File Type</label>
              <input
                type="text"
                placeholder="e.g. csv, json"
                value={filters.filetype}
                onChange={(e) => setFilters({ ...filters, filetype: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>Domain</label>
              <input
                type="text"
                placeholder="e.g. medical, nlp"
                value={filters.domain}
                onChange={(e) => setFilters({ ...filters, domain: e.target.value })}
              />
            </div>
            <button className="apply-btn" onClick={() => search(0)}>Apply</button>
          </div>
        </div>

        {/* ─── RESULTS ─── */}
        {loading ? (
          <div className="loading">Searching across 10+ platforms...</div>
        ) : (
          <div className="results-grid">
            {results.length === 0 ? (
              <div className="empty-state">
                <h3>No results found</h3>
                <p>Try a different search term.</p>
              </div>
            ) : (
              results.map((ds, i) => {
                const quality = getQuality(ds);
                const licenseDisplay = getLicenseDisplay(ds.license);
                const sizeDisplay = formatSize(ds.size);
                const samplesDisplay = formatSamples(ds.samples);
                const tags = (ds.tags || []).slice(0, 4).map(cleanTag);
                const sourceColor = getSourceColor(ds.source);
                const sourceLabel = getSourceLabel(ds.source);

                return (
                  <div key={i} className="result-card">
                    {/* ─── TOP ROW: Quality + License ─── */}
                    <div className="card-top">
                      <span className="quality">
                        <span className="dot"></span> {quality}% Quality
                      </span>
                      {licenseDisplay !== '—' && (
                        <span className="license">{licenseDisplay}</span>
                      )}
                    </div>

                    {/* ─── TITLE ─── */}
                    <h3 className="card-title">{ds.title || 'Untitled'}</h3>

                    {/* ─── DESCRIPTION ─── */}
                    <p className="card-description">
                      {(ds.description || 'No description available.').slice(0, 180)}
                      {(ds.description || '').length > 180 ? '...' : ''}
                    </p>

                    {/* ─── FILE TAGS ─── */}
                    <div className="file-tags">
                      <span className="file-tag">{ds.file_type || 'dataset'}</span>
                      {tags.map((tag, j) => (
                        <span key={j} className="file-tag">{tag}</span>
                      ))}
                    </div>

                    {/* ─── DIVIDER ─── */}
                    <div className="card-divider"></div>

                    {/* ─── METADATA: SIZE + SAMPLES ─── */}
                    <div className="card-meta">
                      <div className="meta-item">
                        <span className="meta-label">SIZE</span>
                        <span className="meta-value">{sizeDisplay}</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">SAMPLES</span>
                        <span className="meta-value">{samplesDisplay}</span>
                      </div>
                    </div>

                    {/* ─── BUTTONS ─── */}
                    <div className="card-buttons">
                      <button
                        className="btn-redirect"
                        onClick={() => window.open(ds.source_url || '#', '_blank')}
                      >
                        Redirect →
                      </button>
                      <button
                        className="btn-preview"
                        onClick={() => window.open(ds.source_url || '#', '_blank')}
                      >
                        Preview
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </main>

      {/* ─── FLOATING AI WIDGET ─── */}
      <div className="ai-widget">
        <div className="ai-widget-header">
          <span className="ai-icon"><AIStarIcon /></span>
          <span className="ai-label">NEURO AI</span>
        </div>
        <p className="ai-text">
          Describe the data you need.<br />
          I'll find the best datasets for your AI model.
        </p>
        <div className="ai-input">
          <input type="text" placeholder="I need 10k images of..." />
          <span className="ai-arrow"><ArrowIcon /></span>
        </div>
      </div>

      {/* ─── FOOTER ─── */}
      <footer>
        <div className="footer-left">
          <div className="footer-logo">NEUROITY DATA SEARCH</div>
          <p>© 2026 Neuroity Data Search. Precision engineered for intelligence.</p>
        </div>
        <div className="footer-right">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Documentation</a>
          <a href="#">Contact</a>
        </div>
      </footer>
    </div>
  );
}

export default App;