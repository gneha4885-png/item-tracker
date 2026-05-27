import { useState } from 'react';
import axios from 'axios';

const API = 'http://localhost:8000';

function LogItemPage() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');

  const userId = localStorage.getItem('user_id') || 'neha123';

  function showToast(msg) {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  }

  async function handleSave() {
    if (!text.trim() || text.length < 5) {
      showToast('Please describe where you kept the item!');
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(API + '/log-item', {
        text: text,
        user_id: userId
      });
      showToast('Saved! ' + response.data.item_name + ' → ' + response.data.location);
      setText('');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Cannot connect to server');
    }
    setLoading(false);
  }

  const suggestions = [
    { icon: '💳', text: 'I kept my Aadhaar card in the top drawer of my desk' },
    { icon: '🔑', text: 'Car keys are on the hook near the main door' },
    { icon: '💊', text: 'Medicines are in the kitchen cabinet top shelf' },
  ];

  return (
    <div className="app-container">
      <div className="page-title">Log Item</div>
      <div className="page-subtitle">Tell me where you kept something</div>

      <div className="card neu">
        <div className="card-label">Where did you keep it?</div>
        <div style={{ position: 'relative' }}>
          <textarea
            className="input-field neu-inset"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="e.g. I kept my passport in the blue drawer in the bedroom..."
            style={{ height: '110px', resize: 'none', paddingRight: '50px', borderRadius: '14px', display: 'block' }}
          />
        </div>
        <button className="btn-primary" onClick={handleSave} disabled={loading} style={{ marginTop: '14px' }}>
          {loading ? 'Saving...' : 'Save Location'}
        </button>
      </div>

      <div className="card neu">
        <div className="card-label">Quick examples — tap to use</div>
        {suggestions.map((s, i) => (
          <div
            key={i}
            onClick={() => setText(s.text)}
            style={{
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: '12px', borderRadius: '12px', cursor: 'pointer',
              marginBottom: '8px', transition: 'all 0.2s',
              background: '#0a1628', border: '1px solid rgba(0,212,255,0.08)',
              color: '#7fa3c4', fontSize: '13px'
            }}
          >
            <span style={{ fontSize: '20px' }}>{s.icon}</span>
            {s.text}
          </div>
        ))}
      </div>

      <div className={`toast ${toast ? 'show' : ''}`}>{toast}</div>
    </div>
  );
}

export default LogItemPage;