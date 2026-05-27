import { useState, useEffect } from 'react';
import axios from 'axios';

const API = 'http://localhost:8000';

const EMOJI = { key:'🗝️', keys:'🗝️', passport:'📘', glasses:'👓', phone:'📱', medicine:'💊', medicines:'💊', wallet:'👛', laptop:'💻', charger:'🔌', book:'📚', watch:'⌚', card:'💳' };

function getEmoji(name) {
  const l = name.toLowerCase();
  for (const [k, v] of Object.entries(EMOJI)) if (l.includes(k)) return v;
  return '📦';
}

function timeAgo(ts) {
  const d = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (d < 60) return 'just now';
  if (d < 3600) return Math.floor(d/60) + 'm ago';
  if (d < 86400) return Math.floor(d/3600) + 'h ago';
  return Math.floor(d/86400) + 'd ago';
}

function HistoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const userId = localStorage.getItem('user_id') || 'neha123';

  useEffect(() => {
    async function fetchItems() {
      try {
        const response = await axios.get(API + '/my-items', {
          params: { user_id: userId }
        });
        setItems(response.data.items);
      } catch (err) {
        console.error('Error fetching items');
      }
      setLoading(false);
    }
    fetchItems();
  }, []);

  return (
    <div className="app-container">
      <div className="page-title">History</div>
      <div className="page-subtitle">{items.length} items saved</div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#00d4ff' }}>
          Loading...
        </div>
      )}

      {!loading && items.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px 20px', color: '#4a6fa5' }}>
          <div style={{ fontSize: '44px', marginBottom: '14px' }}>📭</div>
          <p style={{ fontSize: '14px', lineHeight: '1.6' }}>
            No items saved yet.<br />
            Go to <strong style={{ color: '#00d4ff' }}>Log</strong> to start!
          </p>
        </div>
      )}

      {!loading && items.map((item, i) => (
        <div key={i} className="neu" style={{
          display: 'flex', alignItems: 'center', gap: '14px',
          padding: '14px 16px', marginBottom: '10px',
          cursor: 'pointer', transition: 'transform 0.2s'
        }}>
          <div style={{
            width: '44px', height: '44px',
            background: 'rgba(0,212,255,0.08)',
            borderRadius: '12px', display: 'flex',
            alignItems: 'center', justifyContent: 'center', fontSize: '20px'
          }}>
            {getEmoji(item.item_name || '')}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: '15px', fontWeight: '600', color: '#e8f4fd', marginBottom: '3px' }}>
              {item.item_name ? item.item_name.charAt(0).toUpperCase() + item.item_name.slice(1) : 'Item'}
            </div>
            <div style={{ fontSize: '12px', color: '#7fa3c4' }}>
              {item.location} · {item.timestamp ? timeAgo(item.timestamp) : ''}
            </div>
          </div>
          <div style={{
            fontSize: '11px', padding: '4px 10px',
            background: 'rgba(0,212,255,0.1)',
            color: '#00d4ff', borderRadius: '20px',
            fontWeight: '500', flexShrink: 0
          }}>
            {item.room ? item.room.charAt(0).toUpperCase() + item.room.slice(1) : 'Unknown'}
          </div>
        </div>
      ))}
    </div>
  );
}

export default HistoryPage;