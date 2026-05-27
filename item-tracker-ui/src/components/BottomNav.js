import { useNavigate, useLocation } from 'react-router-dom';

function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { path: '/log', label: 'Log', icon: '✏️' },
    { path: '/find', label: 'Find', icon: '🔍' },
    { path: '/history', label: 'History', icon: '📋' },
  ];

  return (
    <div style={{
      position: 'fixed', bottom: 0, left: 0, right: 0,
      background: '#112240',
      borderTop: '1px solid rgba(0,212,255,0.1)',
      display: 'flex',
      maxWidth: '400px',
      margin: '0 auto',
      zIndex: 100
    }}>
      {tabs.map(tab => (
        <button
          key={tab.path}
          onClick={() => navigate(tab.path)}
          style={{
            flex: 1, padding: '12px 8px',
            background: 'transparent', border: 'none',
            color: location.pathname === tab.path ? '#00d4ff' : '#4a6fa5',
            cursor: 'pointer', fontSize: '11px',
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', gap: '4px',
            fontWeight: location.pathname === tab.path ? '600' : '400',
            transition: 'color 0.2s'
          }}
        >
          <span style={{ fontSize: '20px' }}>{tab.icon}</span>
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export default BottomNav;