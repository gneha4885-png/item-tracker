import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import LogItemPage from './pages/LogItemPage';
import FindItemPage from './pages/FindItemPage';
import HistoryPage from './pages/HistoryPage';
import BottomNav from './components/BottomNav';
import './index.css';

function App() {
  const token = localStorage.getItem('token');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={token ? <Navigate to="/log" /> : <LoginPage />} />
        <Route path="/log" element={<><LogItemPage /><BottomNav /></>} />
        <Route path="/find" element={<><FindItemPage /><BottomNav /></>} />
        <Route path="/history" element={<><HistoryPage /><BottomNav /></>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;