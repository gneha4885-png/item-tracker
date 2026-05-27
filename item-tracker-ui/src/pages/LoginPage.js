import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = 'http://localhost:8000';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  async function handleSubmit() {
    if (!email || !password) { setError('Please fill all fields'); return; }
    setLoading(true); setError('');

    try {
      const endpoint = isLogin ? '/login' : '/register';
      const response = await axios.post(API + endpoint, { email, password });
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('email', response.data.email);
      navigate('/log');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    }
    setLoading(false);
  }

  return (
    <div className="app-container" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>

      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{
          width: '70px', height: '70px',
          background: 'linear-gradient(135deg, #00d4ff, #0084ff)',
          borderRadius: '20px', display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          fontSize: '32px', margin: '0 auto 16px',
          boxShadow: '0 0 30px rgba(0,212,255,0.3)'
        }}>📍</div>
        <div className="page-title">ItemTracker</div>
        <div className="page-subtitle">Your AI memory assistant</div>
      </div>

      <div className="card neu">
        <div className="card-label">{isLogin ? 'Login to your account' : 'Create new account'}</div>

        <input
          className="input-field neu-inset"
          type="email"
          placeholder="Email address"
          value={email}
          onChange={e => setEmail(e.target.value)}
          style={{ marginBottom: '12px', borderRadius: '14px', display: 'block' }}
        />

        <input
          className="input-field neu-inset"
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{ marginBottom: '16px', borderRadius: '14px', display: 'block' }}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        />

        {error && <p style={{ color: '#ff6b6b', fontSize: '13px', marginBottom: '12px' }}>{error}</p>}

        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Create Account')}
        </button>

        <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '14px', color: '#4a6fa5' }}>
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <span
            onClick={() => { setIsLogin(!isLogin); setError(''); }}
            style={{ color: '#00d4ff', cursor: 'pointer', fontWeight: '600' }}
          >
            {isLogin ? 'Register' : 'Login'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;