import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  BadgeCheck,
  BarChart3,
  Brain,
  CircleDollarSign,
  Circle,
  Gem,
  GitBranch,
  Gift,
  Heart,
  Layers3,
  Loader2,
  Network,
  Search,
  ShoppingBag,
  Sparkles,
  Star,
  Shirt,
  UserRound,
  UsersRound,
  Watch,
  Zap
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';

const api = async (path) => {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API request failed: ${res.status}`);
  }
  return res.json();
};

const fmt = (value) => new Intl.NumberFormat('en').format(value ?? 0);
const pct = (value) => `${Math.round((value ?? 0) * 100)}%`;
const fixed = (value, digits = 3) => Number(value ?? 0).toFixed(digits);

const iconMap = {
  Baseline: Zap,
  'Neural recommender': Brain,
  'Hybrid matrix factorization': Layers3,
  'Graph-based recommender': Network,
  'Latent factor model': GitBranch,
  'Collaborative filtering': UsersRound
};

const productTypes = [
  { key: 'watch', label: 'Watch', icon: Watch, words: ['watch', 'strap', 'band'] },
  { key: 'ring', label: 'Ring', icon: Circle, words: ['ring'] },
  { key: 'necklace', label: 'Necklace', icon: Gem, words: ['necklace', 'pendant', 'chain', 'choker'] },
  { key: 'earrings', label: 'Earrings', icon: Sparkles, words: ['earring', 'earrings', 'stud'] },
  { key: 'charm', label: 'Charm', icon: Heart, words: ['charm', 'bracelet', 'bangle'] },
  { key: 'gift', label: 'Gift', icon: Gift, words: ['gift', 'holiday', 'wedding', 'party'] },
  { key: 'apparel', label: 'Apparel', icon: Shirt, words: ['shirt', 'dress', 'scarf', 'bag', 'wallet'] },
  { key: 'jewelry', label: 'Jewelry', icon: Gem, words: ['jewelry', 'silver', 'pearl', 'bead', 'crystal', 'zirconia'] }
];

function getProductType(item = {}) {
  const text = `${item.title || ''} ${item.category || ''}`.toLowerCase();
  return productTypes.find((type) => type.words.some((word) => text.includes(word))) || {
    key: 'fashion',
    label: 'Fashion',
    icon: ShoppingBag
  };
}

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <Loader2 className="spin" size={34} />
      <h2>Connecting to recommendation backend...</h2>
      <p>Make sure FastAPI is running on <code>http://127.0.0.1:8000</code>.</p>
    </div>
  );
}

function ErrorBox({ error }) {
  return (
    <div className="loading-screen error-box">
      <h2>Could not connect to backend</h2>
      <p>{error}</p>
      <pre>cd backend{"\n"}uvicorn app.main:app --reload --host 127.0.0.1 --port 8000</pre>
    </div>
  );
}

function ProductArtwork({ item = {}, title = '', rank = 1 }) {
  const product = item.title ? item : { title };
  const type = getProductType(product);
  const Icon = type.icon;
  return (
    <div className={`product-art art-${(rank % 6) + 1} type-${type.key}`}>
      <Icon className="product-symbol" size={38} strokeWidth={2.4} />
      <small>#{rank}</small>
      <em>{type.label}</em>
    </div>
  );
}

function MetricBar({ label, value, max = 0.65 }) {
  const width = Math.min(100, Math.max(3, Math.round(((value ?? 0) / max) * 100)));
  return (
    <div className="metric-row">
      <div className="metric-label"><span>{label}</span><strong>{fixed(value)}</strong></div>
      <div className="metric-track"><div className="metric-fill" style={{ width: `${width}%` }} /></div>
    </div>
  );
}

function ProductCard({ item, selected, onClick }) {
  return (
    <button className={`product-card ${selected ? 'selected' : ''}`} onClick={() => onClick?.(item)} aria-label={`View details for ${item.title}`}>
      <ProductArtwork item={item} rank={item.rank || 1} />
      <div className="product-body">
        <div className="product-topline">
          <span>{item.category || 'AMAZON FASHION'}</span>
          <strong>{fixed(item.score)}</strong>
        </div>
        <h3>{item.title}</h3>
        <p>{item.why}</p>
        <div className="product-meta">
          <span><Star size={14} /> {item.rating ?? 'N/A'}</span>
          <span>{fmt(item.ratingCount)} ratings</span>
          <span>{item.price ? `$${item.price}` : 'Price N/A'}</span>
        </div>
      </div>
    </button>
  );
}

function ProductDetails({ item }) {
  if (!item) return null;

  return (
    <section className="panel detail-panel" id="product-details">
      <div className="detail-art-wrap">
        <ProductArtwork item={item} rank={item.rank || 1} />
      </div>
      <div className="detail-content">
        <div className="detail-kicker">{item.category || 'Amazon Fashion'} / Product #{item.id}</div>
        <h2>{item.title}</h2>
        <p>{item.why}</p>
        <div className="detail-stats">
          <div><span>Recommendation Score</span><strong>{fixed(item.score)}</strong></div>
          <div><span>Average Rating</span><strong>{item.rating ?? 'N/A'}</strong></div>
          <div><span>Rating Count</span><strong>{fmt(item.ratingCount)}</strong></div>
        </div>
        <div className="detail-note">
          <ShoppingBag size={18} />
          <span>Selected products refresh the More Like This section through the backend similar-item endpoint.</span>
        </div>
      </div>
    </section>
  );
}

function ModelCard({ model, active, onClick }) {
  const Icon = iconMap[model.family] || Activity;
  return (
    <button className={`model-card ${active ? 'active' : ''}`} onClick={onClick}>
      <div className="model-icon"><Icon size={20} /></div>
      <div>
        <h3>{model.name}</h3>
        <p>{model.description}</p>
        <div className="mini-metrics">
          <span>Hit@10 {pct(model.metrics?.hit10)}</span>
          <span>NDCG@10 {fixed(model.metrics?.ndcg10)}</span>
        </div>
      </div>
    </button>
  );
}

function App() {
  const [boot, setBoot] = useState(null);
  const [error, setError] = useState('');
  const [selectedUserId, setSelectedUserId] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [topK, setTopK] = useState(10);
  const [recommendations, setRecommendations] = useState([]);
  const [history, setHistory] = useState({ history: [], heldout: [] });
  const [similarUsers, setSimilarUsers] = useState([]);
  const [similarItems, setSimilarItems] = useState([]);
  const [sponsored, setSponsored] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    api('/api/bootstrap')
      .then((data) => {
        setBoot(data);
        const firstUser = data.users?.[0]?.id;
        const preferredModel = data.models?.find((m) => m.name === 'Neural Matrix Factorization')?.name || data.models?.[0]?.name;
        setSelectedUserId(String(firstUser ?? ''));
        setSelectedModel(preferredModel ?? '');
      })
      .catch((err) => setError(err.message));
  }, []);

  const selectedUser = useMemo(() => boot?.users?.find((u) => String(u.id) === String(selectedUserId)), [boot, selectedUserId]);
  const model = useMemo(() => boot?.models?.find((m) => m.name === selectedModel), [boot, selectedModel]);

  const handleProductClick = (item) => {
    setSelectedItem(item);
    window.setTimeout(() => {
      document.getElementById('product-details')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 0);
  };

  useEffect(() => {
    if (!selectedUserId || !selectedModel) return;
    setLoadingRecs(true);
    Promise.all([
      api(`/api/recommendations?user_id=${selectedUserId}&model=${encodeURIComponent(selectedModel)}&top_k=${topK}`),
      api(`/api/users/${selectedUserId}/history`),
      api(`/api/similar-users/${selectedUserId}?top_k=5`),
      api(`/api/sponsored?user_id=${selectedUserId}&top_k=5`)
    ])
      .then(([recData, historyData, similarData, sponsoredData]) => {
        setRecommendations(recData.recommendations || []);
        setHistory(historyData || { history: [], heldout: [] });
        setSimilarUsers(similarData.similarUsers || []);
        setSponsored(sponsoredData.sponsoredPicks || []);
        const first = recData.recommendations?.[0] || null;
        setSelectedItem(first);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingRecs(false));
  }, [selectedUserId, selectedModel, topK]);

  useEffect(() => {
    if (!selectedItem) return;
    api(`/api/similar-items/${selectedItem.id}?top_k=6`)
      .then((data) => setSimilarItems(data.similarItems || []))
      .catch(() => setSimilarItems([]));
  }, [selectedItem]);

  useEffect(() => {
    const id = setTimeout(() => {
      if (!query.trim()) {
        setSearchResults([]);
        return;
      }
      api(`/api/search?q=${encodeURIComponent(query)}&limit=8`)
        .then((data) => setSearchResults(data.results || []))
        .catch(() => setSearchResults([]));
    }, 250);
    return () => clearTimeout(id);
  }, [query]);

  if (error) return <ErrorBox error={error} />;
  if (!boot) return <LoadingScreen />;

  const dataset = boot.project?.dataset || {};
  const bestModel = boot.models?.[0];

  return (
    <main className="app-shell">
      <section className="hero">
        <div className="hero-copy">
          <h1>{boot.project?.title || 'Picksy Picks'}</h1>
          <p>{boot.project?.subtitle}</p>
        </div>
        <div className="hero-card">
          <div><span>Users</span><strong>{fmt(dataset.users)}</strong></div>
          <div><span>Items</span><strong>{fmt(dataset.items)}</strong></div>
          <div><span>Interactions</span><strong>{fmt(dataset.interactions)}</strong></div>
        </div>
      </section>

      <section className="controls panel">
        <div>
          <label>Demo user</label>
          <select value={selectedUserId} onChange={(e) => setSelectedUserId(e.target.value)}>
            {boot.users.map((u) => <option key={u.id} value={u.id}>{u.label} - {u.persona}</option>)}
          </select>
        </div>
        <div>
          <label>Model</label>
          <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
            {boot.models.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
          </select>
        </div>
        <div>
          <label>Top-K</label>
          <select value={topK} onChange={(e) => setTopK(Number(e.target.value))}>
            {[5, 10, 15, 20].map((k) => <option key={k} value={k}>{k}</option>)}
          </select>
        </div>
        <div className="search-box">
          <label>Search products</label>
          <div><Search size={16} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search jewelry, necklace, charm..." /></div>
        </div>
      </section>

      {searchResults.length > 0 && (
        <section className="panel search-results">
          <h2>Search Results</h2>
          <div className="compact-grid">
            {searchResults.map((item, i) => <ProductCard key={`${item.id}-${i}`} item={{ ...item, rank: i + 1 }} onClick={handleProductClick} />)}
          </div>
        </section>
      )}

      <section className="grid-main">
        <div className="left-stack">
          <section className="panel user-panel">
            <div className="panel-heading">
              <div><h2><UserRound size={22} /> {selectedUser?.label}</h2><p>{selectedUser?.summary}</p></div>
              <div className="tag-row">{selectedUser?.dominantCategories?.map((c) => <span key={c}>{c}</span>)}</div>
            </div>
            <div className="history-grid">
              <div>
                <h3>Training History</h3>
                {history.history?.slice(0, 6).map((item) => (
                  <div className="history-item" key={`h-${item.id}`}><span>{item.title}</span><strong>Rating {item.rating}</strong></div>
                ))}
              </div>
              <div>
                <h3>Held-out Future Items</h3>
                {history.heldout?.map((item) => (
                  <div className="history-item" key={`v-${item.id}`}><span>{item.split}: {item.title}</span><strong>Rating {item.rating}</strong></div>
                ))}
              </div>
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading horizontal">
              <div><h2><Sparkles size={22} /> Top Recommendations</h2><p>Generated by <b>{selectedModel}</b> from the FastAPI backend.</p></div>
              {loadingRecs && <Loader2 className="spin" />}
            </div>
            <div className="rec-grid">
              {recommendations.map((item) => <ProductCard key={`${selectedModel}-${item.id}`} item={item} selected={selectedItem?.id === item.id} onClick={handleProductClick} />)}
            </div>
          </section>
        </div>

        <aside className="right-stack">
          <section className="panel model-panel">
            <h2><BarChart3 size={22} /> Model Performance</h2>
            {boot.models.map((m) => <ModelCard key={m.name} model={m} active={m.name === selectedModel} onClick={() => setSelectedModel(m.name)} />)}
          </section>

          <section className="panel">
            <h2><BadgeCheck size={22} /> Selected Model Metrics</h2>
            <MetricBar label="HitRate@5" value={model?.metrics?.hit5} />
            <MetricBar label="HitRate@10" value={model?.metrics?.hit10} />
            <MetricBar label="HitRate@20" value={model?.metrics?.hit20} />
            <MetricBar label="NDCG@10" value={model?.metrics?.ndcg10} max={0.35} />
            <MetricBar label="MRR@10" value={model?.metrics?.mrr10} max={0.3} />
            <p className="small-note">Best notebook result by HitRate@10: <b>{bestModel?.name}</b>.</p>
          </section>
        </aside>
      </section>

      <ProductDetails item={selectedItem} />

      <section className="feature-grid">
        <div className="panel">
          <h2><UsersRound size={22} /> Similar Users</h2>
          {similarUsers.map((u) => (
            <div className="similar-row" key={u.id}><div><strong>{u.label}</strong><p>{u.persona} - {u.reason}</p></div><span>{fixed(u.score, 2)}</span></div>
          ))}
        </div>
        <div className="panel">
          <h2><ShoppingBag size={22} /> More Like This</h2>
          <p className="small-note">Based on selected item: <b>{selectedItem?.title || 'None'}</b></p>
          {similarItems.slice(0, 4).map((item) => <ProductCard key={`sim-${item.id}`} item={item} onClick={handleProductClick} />)}
        </div>
        <div className="panel">
          <h2><CircleDollarSign size={22} /> Sponsored Picks</h2>
          {sponsored.map((item) => <ProductCard key={`s-${item.id}`} item={item} onClick={handleProductClick} />)}
        </div>
      </section>

      <section className="panel cluster-panel">
        <h2><Network size={22} /> Product Clusters</h2>
        <div className="cluster-grid">
          {boot.clusters?.map((cluster) => (
            <div className="cluster-card" key={cluster.name}>
              <span>{fmt(cluster.size)} items</span>
              <h3>{cluster.name}</h3>
              <p>{cluster.description}</p>
              <div className="tag-row">{cluster.items?.map((item) => <small key={item}>{item}</small>)}</div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default App;
