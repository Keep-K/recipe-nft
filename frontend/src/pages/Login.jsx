import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Login.css';

const Login = () => {
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const { connectWallet, connectMetaMask } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    try {
      connectWallet(address);
      navigate('/recipes');
    } catch (err) {
      setError('올바른 지갑 주소를 입력해주세요. (0x로 시작하는 42자)');
    }
  };

  const handleMetaMask = async () => {
    setError('');
    try {
      await connectMetaMask();
      navigate('/recipes');
    } catch (err) {
      if (err.message === 'MetaMask is not installed') {
        setError('MetaMask가 설치되어 있지 않습니다.');
      } else {
        setError('MetaMask 연결에 실패했습니다.');
      }
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>레시피 NFT 플랫폼</h1>
        <p className="subtitle">지갑 주소를 입력하거나 MetaMask로 연결하세요</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="wallet-address">지갑 주소</label>
            <input
              id="wallet-address"
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="0x..."
              required
              pattern="^0x[a-fA-F0-9]{40}$"
            />
          </div>

          <button type="submit" className="btn btn-primary">
            연결
          </button>
        </form>

        <div className="divider">
          <span>또는</span>
        </div>

        <button onClick={handleMetaMask} className="btn btn-metamask">
          <span>🦊</span>
          MetaMask로 연결
        </button>
      </div>
    </div>
  );
};

export default Login;

