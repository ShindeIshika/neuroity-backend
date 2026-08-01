// src/App.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
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

// ─── HELPERS ───
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
    huggingface: '#FFD54F',
    uci: '#009688',
    openml: '#FDB813',
    zenodo: '#D32F2F',
    figshare: '#E94E1B',
    github: '#24292F',
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

// ─── PROVIDER LOGOS ───
const ProviderLogo = ({ source }) => {
  const logos = {
    kaggle: 'K',
    huggingface: '🤗',
    uci: 'U',
    openml: 'O',
    zenodo: 'Z',
    figshare: 'F',
    github: '🐙',
    openneuro: '🧠',
    physionet: '❤️',
    google_dataset: 'G',
  };
  return <span style={{ marginRight: '4px' }}>{logos[source] || '📊'}</span>;
};

// ─── RESULT CARD ───
const ResultCard = React.memo(({ ds }) => {
  const quality = getQuality(ds);
  const licenseDisplay = getLicenseDisplay(ds.license);
  const sizeDisplay = formatSize(ds.size);
  const samplesDisplay = formatSamples(ds.samples);
  const tags = (ds.tags || []).slice(0, 4).map(cleanTag);
  const sourceColor = getSourceColor(ds.source);
  const sourceLabel = getSourceLabel(ds.source);

  const handleRedirect = () => {
    if (ds.source_url) {
      window.open(ds.source_url, '_blank', 'noopener,noreferrer');
    }
  };

  const handlePreview = () => {
    if (ds.source_url) {
      window.open(ds.source_url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="result-card">
      <div className="card-top">
        <span className="quality">
          <span className="dot"></span> {quality}% Quality
        </span>
        {licenseDisplay !== '—' && (
          <span className="license">{licenseDisplay}</span>
        )}
      </div>

      <div style={{ marginBottom: '4px' }}>
        <span
          className="source-badge"
          style={{
            display: 'inline-block',
            background: sourceColor,
            color: sourceColor === '#FFFFFF' || sourceColor === '#FFD54F' ? '#000' : '#fff',
            padding: '2px 10px',
            borderRadius: '999px',
            fontSize: '10px',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          <ProviderLogo source={ds.source} />
          {sourceLabel}
        </span>
      </div>

      <h3 className="card-title">{ds.title || 'Untitled'}</h3>
      <p className="card-description">
        {(ds.description || 'No description available.').slice(0, 180)}
        {(ds.description || '').length > 180 ? '...' : ''}
      </p>
      <div className="file-tags">
        <span className="file-tag">{ds.file_type || 'dataset'}</span>
        {tags.map((tag, j) => (
          <span key={j} className="file-tag">{tag}</span>
        ))}
      </div>
      <div className="card-divider"></div>
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
      <div className="card-buttons">
        <button
          className="btn-redirect"
          onClick={handleRedirect}
          disabled={!ds.source_url}
        >
          Visit Source →
        </button>
        <button
          className="btn-preview"
          onClick={handlePreview}
          disabled={!ds.source_url}
        >
          Preview
        </button>
      </div>
    </div>
  );
});

ResultCard.displayName = 'ResultCard';

// ─── MAIN APP ───
function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [providers, setProviders] = useState({});
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    source: '',
    filetype: '',
    domain: '',
  });

  const controllerRef = useRef(null);
  const inputRef = useRef(null);
  const isFirstLoad = useRef(true);

  // ─── AI WIDGET STATE ───
  const widgetRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [widgetPos, setWidgetPos] = useState({ x: 0, y: 0 });
  const [widgetWidth, setWidgetWidth] = useState(380);

  useEffect(() => {
    if (isFirstLoad.current) {
      isFirstLoad.current = false;
      search(0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handler = (e) => {
      if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
        const activeElement = document.activeElement;
        if (activeElement?.tagName !== 'INPUT' && activeElement?.tagName !== 'TEXTAREA') {
          e.preventDefault();
          inputRef.current?.focus();
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // ─── SMOOTH DRAG HANDLERS ───
  const handleDragStart = (e) => {
    if (!e.target.closest('.ai-widget-header')) return;
    setIsDragging(true);
    setDragStart({
      x: e.clientX - widgetPos.x,
      y: e.clientY - widgetPos.y
    });
  };

  const handleDragMove = useCallback((e) => {
    if (!isDragging) return;
    setWidgetPos({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  }, [isDragging, dragStart]);

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  // ─── RESIZE HANDLER ───
  const handleResizeStart = (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = widgetWidth;

    const onResize = (ev) => {
      const newWidth = Math.min(520, Math.max(280, startWidth + (ev.clientX - startX)));
      setWidgetWidth(newWidth);
    };

    const onResizeEnd = () => {
      document.removeEventListener('mousemove', onResize);
      document.removeEventListener('mouseup', onResizeEnd);
    };

    document.addEventListener('mousemove', onResize);
    document.addEventListener('mouseup', onResizeEnd);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleDragMove);
      document.addEventListener('mouseup', handleDragEnd);
      return () => {
        document.removeEventListener('mousemove', handleDragMove);
        document.removeEventListener('mouseup', handleDragEnd);
      };
    }
  }, [isDragging, handleDragMove]);

  const search = useCallback(async (offset = 0) => {
    if (!query.trim()) return;

    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);

    let url = `${API_BASE}/api/v1/search?q=${encodeURIComponent(query)}&limit=10&offset=${offset}`;
    if (filters.source) url += `&source=${filters.source}`;
    if (filters.filetype) url += `&filetype=${filters.filetype}`;
    if (filters.domain) url += `&domain=${filters.domain}`;

    try {
      const res = await fetch(url, { signal: controller.signal });
      const data = await res.json();
      if (data.success) {
        setResults(data.results || []);
        setTotalResults(data.total_results || 0);
        setProviders(data.providers || {});
      }
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  }, [query, filters]);

  const handleSearch = (e) => {
    e.preventDefault();
    search(0);
  };

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    search(0);
  };

  return (
    <div className="app">

      {/* ─── NAVBAR ─── */}
      <header>
        <div className="container">
          <div className="logo">
            Neuroity <span className="tag">Data Search</span>
          </div>
          <nav>
            <a href="#" className="active">Datasets</a>
          </nav>
        </div>
      </header>

      {/* ─── MAIN CONTENT ─── */}
      <main>
        <div className="container">

          <div className="hero">
            <h1>Discover data, build intelligence.</h1>
          </div>

          <div className="search-wrapper">
            <form onSubmit={handleSearch} className="search-bar">
              <span className="search-icon"><SearchIcon /></span>
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search datasets across 10+ platforms"
                aria-label="Search datasets"
                disabled={loading}
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Searching...' : (
                  <>
                    <SparkleIcon /> Search
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="ai-tag">
            <span>10+ Dataset Sources • Unified Search</span>
          </div>

          <div className="filters-container">
            <form className="filters" onSubmit={handleFilterSubmit}>
              <div className="filter-group">
                <label htmlFor="source-filter">Source</label>
                <select
                  id="source-filter"
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
                <label htmlFor="filetype-filter">File Type</label>
                <input
                  id="filetype-filter"
                  type="text"
                  placeholder="e.g. csv, json"
                  value={filters.filetype}
                  onChange={(e) => setFilters({ ...filters, filetype: e.target.value })}
                  aria-label="Filter by file type"
                  disabled={loading}
                />
              </div>
              <div className="filter-group">
                <label htmlFor="domain-filter">Domain</label>
                <input
                  id="domain-filter"
                  type="text"
                  placeholder="e.g. medical, nlp"
                  value={filters.domain}
                  onChange={(e) => setFilters({ ...filters, domain: e.target.value })}
                  aria-label="Filter by domain"
                  disabled={loading}
                />
              </div>
              <button type="submit" className="apply-btn" disabled={loading}>
                Apply
              </button>
            </form>
          </div>

          {/* ─── RESULT COUNT ─── */}
          {!loading && results.length > 0 && (
            <div className="result-count">
              Showing {results.length} of {totalResults} datasets
            </div>
          )}

          <div className="results-wrapper">
            {loading && (
              <div className="loading-overlay">
                <div className="loading">
                  Searching datasets
                  <span className="dots">
                    <span>●</span>
                    <span>●</span>
                    <span>●</span>
                  </span>
                </div>
              </div>
            )}

            <div className="results-grid">
              {results.length === 0 && !loading ? (
                <div className="empty-state">
                  <h3>No results found</h3>
                  <p>Try a different search term.</p>
                </div>
              ) : (
                results.map((ds, i) => (
                  <ResultCard key={i} ds={ds} />
                ))
              )}
            </div>
          </div>

        </div>
      </main>

      {/* ─── SMOOTH DRAGGABLE & RESIZABLE AI WIDGET ─── */}
      <div
        ref={widgetRef}
        className="ai-widget"
        style={{
          width: widgetWidth + 'px',
          transform: `translate(${widgetPos.x}px, ${widgetPos.y}px)`,
          transition: isDragging ? 'none' : 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          cursor: isDragging ? 'grabbing' : 'default'
        }}
      >
        <div className="ai-widget-header" onMouseDown={handleDragStart}>
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
        <div className="ai-resize-handle" onMouseDown={handleResizeStart}>
          ↕
        </div>
      </div>

      {/* ─── FOOTER ─── */}
      <footer>
        <div className="container">
          <div className="footer-left">
            <div className="footer-logo">NEUROITY DATA SEARCH</div>
            <p>Unified Dataset Search API • Powered by Kaggle, Hugging Face, UCI, GitHub, Zenodo & more</p>
            <p style={{ marginTop: '4px', fontSize: '12px', color: 'rgba(255,255,255,0.2)' }}>
              © 2026 Neuroity AI. Precision engineered for intelligence.
            </p>
          </div>
          <div className="footer-right">
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Documentation</a>
            <a href="#">Contact</a>
          </div>
        </div>
      </footer>

    </div>
  );
}

export default App;