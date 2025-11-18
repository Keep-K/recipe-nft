import axios from 'axios';

const inferApiBaseUrl = () => {
  // 브라우저 환경에 따라 기본 API 엔드포인트 추론
  if (typeof window === 'undefined') {
    return 'http://localhost:8000';
  }

  const { hostname, origin } = window.location;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8000';
  }

  // Firebase Hosting 도메인에서 접근 시 Railway 백엔드로 연결
  if (hostname.endsWith('web.app') || hostname.endsWith('firebaseapp.com')) {
    return 'https://recipe-ai-production.up.railway.app';
  }

  // 기타 환경은 동일한 오리진으로 시도
  return origin;
};

const API_BASE_URL = (import.meta.env.VITE_API_URL || inferApiBaseUrl()).replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 레시피 API
export const recipeAPI = {
  // 레시피 생성
  create: async (recipeData, walletAddress) => {
    const response = await api.post('/api/recipes/', recipeData, {
      params: { wallet_address: walletAddress },
    });
    return response.data;
  },

  // 레시피 목록 조회
  getAll: async (params = {}) => {
    const response = await api.get('/api/recipes/', { params });
    return response.data;
  },

  // 레시피 상세 조회
  getById: async (recipeId) => {
    const response = await api.get(`/api/recipes/${recipeId}`);
    return response.data;
  },

  // 레시피 수정
  update: async (recipeId, recipeData, walletAddress) => {
    const response = await api.put(`/api/recipes/${recipeId}`, recipeData, {
      params: { wallet_address: walletAddress },
    });
    return response.data;
  },

  // 레시피 삭제
  delete: async (recipeId, walletAddress) => {
    await api.delete(`/api/recipes/${recipeId}`, {
      params: { wallet_address: walletAddress },
    });
  },
};

// NFT API
export const nftAPI = {
  // NFT 민팅
  mint: async (recipeId, walletAddress) => {
    const response = await api.post(`/api/nft/mint/${recipeId}`, null, {
      params: { wallet_address: walletAddress },
    });
    return response.data;
  },

  // 트랜잭션 해시로 레시피 조회
  getByTxHash: async (txHash, useEtherscan = false) => {
    const response = await api.get(`/api/nft/by-tx/${txHash}`, {
      params: { use_etherscan: useEtherscan },
    });
    return response.data;
  },

  // 토큰 ID로 레시피 조회
  getByTokenId: async (tokenId, contractAddress = null) => {
    const params = contractAddress ? { contract_address: contractAddress } : {};
    const response = await api.get(`/api/nft/by-token/${tokenId}`, { params });
    return response.data;
  },

  // 메타데이터 조회
  getMetadata: async (recipeId) => {
    const response = await api.get(`/api/nft/metadata/${recipeId}`);
    return response.data;
  },

  // 디버그: 트랜잭션 상세 정보
  debugTx: async (txHash) => {
    const response = await api.get(`/api/nft/debug/tx/${txHash}`);
    return response.data;
  },
};

// 사용자 API
export const userAPI = {
  // 사용자 생성
  create: async (userData) => {
    const response = await api.post('/api/users/', userData);
    return response.data;
  },

  // 사용자 조회
  getByWallet: async (walletAddress) => {
    const response = await api.get(`/api/users/${walletAddress}`);
    return response.data;
  },

  // 사용자 레시피 조회
  getRecipes: async (walletAddress) => {
    const response = await api.get(`/api/users/${walletAddress}/recipes`);
    return response.data;
  },
};

export default api;

