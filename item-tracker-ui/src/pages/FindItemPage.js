import { useState } from 'react';
import axios from 'axios';

const API = 'http://localhost:8000';

function FindItemPage() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');

  const userId = localStorage.getItem('user_id') || 'neha123';

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  }

  async function handleFind() {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const response = await axios.get(API + '/find-item', {
        params: { query: query, user_id: userId }
      });
      setAnswer(response.data.answer);
    } catch (err) {
      showToast('Cannot connect to server');
    }
    setLoading(false);
  }

  return (
    <div className="app-container">
      <div className="page-title">Find Item</div>
      <div className="page-subtitle">Ask me where you kept something</div>

      <div style={{ position: 'relative', marginBottom: '14px' }}>
        <input
          className="input-field neu-inset"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleFind()}
          placeholder="Where are my keys? Where is my passport?"
          style={{ borderRadius: '14px', paddingRight: '52px', display: 'block' }}
        />
        <button
          onClick={handleFind}
          style={{
            position: 'absolute', right: '8px', top: '50%',
            transform: 'translateY(-50%)',
            width: '38px', height: '38px',
            background: 'linear-gradient(135deg, #00d4ff, #0084ff)',
            border: 'none', borderRadius: '10px', cursor: 'pointer',
            fontSize: '16px', display: 'flex', alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px rgba(0,212,255,0.25)'
          }}
        >
          🔍
        </button>
      </div>

      {loading && (
        <div className="card neu" style={{ textAlign: 'center', color: '#00d4ff' }}>
          Searching...
        </div>
      )}

      {answer && !loading && (
        <div className="card neu" style={{ border: '1px solid rgba(0,255,204,0.15)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{
              width: '34px', height: '34px',
              background: 'rgba(0,255,204,0.15)',
              borderRadius: '10px', display: 'flex',
              alignItems: 'center', justifyContent: 'center', fontSize: '16px'
            }}>🤖</div>
            <span style={{ fontSize: '11px', fontWeight: '600', color: '#00ffcc', textTransform: 'uppercase', letterSpacing: '1px' }}>
              AI Found It
            </span>
          </div>
          <p style={{ fontSize: '15px', lineHeight: '1.7', color: '#e8f4fd' }}>{answer}</p>
        </div>
      )}

      {!answer && !loading && (
        <div style={{ textAlign: 'center', padding: '40px 20px', color: '#4a6fa5' }}>
          <div style={{ fontSize: '44px', marginBottom: '14px' }}>🔍</div>
          <p style={{ fontSize: '14px', lineHeight: '1.6' }}>
            Ask me anything like<br />
            <strong style={{ color: '#00d4ff' }}>"where are my car keys?"</strong>
          </p>
        </div>
      )}

      <div className={`toast ${toast ? 'show' : ''}`}>{toast}</div>
    </div>
  );
}

export default FindItemPage;