import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { walletAddress, isConnected, disconnectWallet } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleDisconnect = () => {
    disconnectWallet();
    navigate('/login');
    setMenuOpen(false);
  };

  const shortenAddress = (address) => {
    if (!address) return '';
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/recipes" className="navbar-brand" onClick={() => setMenuOpen(false)}>
          🍳 Recipe NFT
        </Link>

        <button className="mobile-menu-toggle" onClick={toggleMenu} aria-label="메뉴">
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className={`navbar-menu ${menuOpen ? 'active' : ''}`}>
          {isConnected ? (
            <>
              <Link to="/recipes" className="nav-link" onClick={() => setMenuOpen(false)}>
                레시피
              </Link>
              <Link to="/recipes/create" className="nav-link" onClick={() => setMenuOpen(false)}>
                작성
              </Link>
              <Link to="/nft/view" className="nav-link" onClick={() => setMenuOpen(false)}>
                NFT 확인
              </Link>
              <div className="wallet-info">
                <span className="wallet-address">{shortenAddress(walletAddress)}</span>
                <button onClick={handleDisconnect} className="btn-disconnect">
                  연결 해제
                </button>
              </div>
            </>
          ) : (
            <Link to="/login" className="nav-link" onClick={() => setMenuOpen(false)}>
              로그인
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

