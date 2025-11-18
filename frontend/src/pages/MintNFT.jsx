import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { recipeAPI, nftAPI } from '../utils/api';
import './MintNFT.css';

const MintNFT = () => {
  const { recipeId } = useParams();
  const { walletAddress, isConnected } = useAuth();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [minting, setMinting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (!isConnected) {
      navigate('/login');
      return;
    }

    loadRecipe();
  }, [recipeId, isConnected, navigate]);

  const loadRecipe = async () => {
    try {
      const data = await recipeAPI.getById(recipeId);
      setRecipe(data);
    } catch (err) {
      setError('레시피를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleMint = async () => {
    if (!recipe) return;

    if (recipe.is_minted) {
      setError('이미 민팅된 레시피입니다.');
      return;
    }

    setMinting(true);
    setError('');
    setSuccess('');

    try {
      const result = await nftAPI.mint(recipeId, walletAddress);
      
      if (result.transaction_hash) {
        const etherscanUrl = `https://sepolia.etherscan.io/tx/${result.transaction_hash}`;
        setSuccess(`NFT 민팅 성공! 트랜잭션: ${result.transaction_hash.slice(0, 10)}...${result.transaction_hash.slice(-8)}`);
        // 트랜잭션 링크를 별도로 표시하기 위해 window.open 사용
        setTimeout(() => {
          window.open(etherscanUrl, '_blank');
        }, 500);
      } else {
        setSuccess('NFT 민팅 성공!');
      }
      
      // 레시피 정보 업데이트
      setTimeout(() => {
        loadRecipe();
      }, 2000);
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        err.message || 
        'NFT 민팅에 실패했습니다.'
      );
    } finally {
      setMinting(false);
    }
  };

  if (loading) {
    return (
      <div className="mint-nft-container">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="mint-nft-container">
        <div className="error-message">레시피를 찾을 수 없습니다.</div>
      </div>
    );
  }

  return (
    <div className="mint-nft-container">
      <div className="mint-nft-card">
        <h1>NFT 민팅</h1>
        <p className="subtitle">레시피를 NFT로 민팅합니다</p>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="recipe-preview">
          <h2>{recipe.recipe_name}</h2>
          
          <div className="recipe-info">
            <div className="info-section">
              <h3>재료</h3>
              <ul>
                {recipe.ingredients.map((ing, idx) => (
                  <li key={idx}>{ing}</li>
                ))}
              </ul>
            </div>

            <div className="info-section">
              <h3>조리 도구</h3>
              <ul>
                {recipe.cooking_tools.map((tool, idx) => (
                  <li key={idx}>{tool}</li>
                ))}
              </ul>
            </div>

            <div className="info-section">
              <h3>조리 과정</h3>
              <ol>
                {recipe.cooking_steps.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ol>
            </div>
          </div>

          {recipe.is_minted && (
            <div className="mint-status">
              <div className="status-badge minted">✅ 이미 민팅됨</div>
              {recipe.token_id && (
                <div className="token-info">
                  <p><strong>Token ID:</strong> {recipe.token_id}</p>
                  {recipe.contract_address && (
                    <p><strong>Contract:</strong> {recipe.contract_address}</p>
                  )}
                  {recipe.transaction_hash && (
                    <p>
                      <strong>Transaction:</strong>{' '}
                      <a
                        href={`https://sepolia.etherscan.io/tx/${recipe.transaction_hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="tx-link"
                      >
                        {recipe.transaction_hash.slice(0, 10)}...{recipe.transaction_hash.slice(-8)}
                      </a>
                    </p>
                  )}
                  {recipe.ipfs_hash && (
                    <p>
                      <strong>IPFS Hash:</strong>{' '}
                      <a
                        href={`https://ipfs.io/ipfs/${recipe.ipfs_hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="tx-link"
                      >
                        {recipe.ipfs_hash}
                      </a>
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="mint-actions">
          <button
            onClick={() => navigate(`/recipes/${recipeId}`)}
            className="btn btn-secondary"
          >
            돌아가기
          </button>
          {!recipe.is_minted && (
            <button
              onClick={handleMint}
              className="btn btn-primary"
              disabled={minting}
            >
              {minting ? '민팅 중...' : 'NFT 민팅'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default MintNFT;

