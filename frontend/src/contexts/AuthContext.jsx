import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [walletAddress, setWalletAddress] = useState(() => {
    // localStorage에서 지갑 주소 불러오기
    return localStorage.getItem('walletAddress') || '';
  });

  const [isConnected, setIsConnected] = useState(!!walletAddress);

  // 지갑 주소 저장
  const connectWallet = (address) => {
    if (address && address.startsWith('0x') && address.length === 42) {
      setWalletAddress(address);
      setIsConnected(true);
      localStorage.setItem('walletAddress', address);
    } else {
      throw new Error('Invalid wallet address');
    }
  };

  // 지갑 연결 해제
  const disconnectWallet = () => {
    setWalletAddress('');
    setIsConnected(false);
    localStorage.removeItem('walletAddress');
  };

  // MetaMask 연결 시도
  const connectMetaMask = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({
          method: 'eth_requestAccounts',
        });
        if (accounts.length > 0) {
          connectWallet(accounts[0]);
          return accounts[0];
        }
      } catch (error) {
        console.error('MetaMask connection error:', error);
        throw error;
      }
    } else {
      throw new Error('MetaMask is not installed');
    }
  };

  useEffect(() => {
    // MetaMask 계정 변경 감지
    if (typeof window.ethereum !== 'undefined') {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length > 0) {
          connectWallet(accounts[0]);
        } else {
          disconnectWallet();
        }
      });
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        walletAddress,
        isConnected,
        connectWallet,
        disconnectWallet,
        connectMetaMask,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

