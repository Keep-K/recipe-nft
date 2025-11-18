import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { nftAPI } from '../utils/api';
import './ViewNFT.css';

const ViewNFT = () => {
  const { isConnected } = useAuth();
  const [searchType, setSearchType] = useState('tx'); // 'tx' or 'token'
  const [searchValue, setSearchValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [recipe, setRecipe] = useState(null);
  const [metadata, setMetadata] = useState(null);

  const handleSearch = async () => {
    if (!searchValue.trim()) {
      setError('검색 값을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    setRecipe(null);
    setMetadata(null);

    try {
      let recipeData;

      if (searchType === 'tx') {
        // 트랜잭션 해시로 검색
        recipeData = await nftAPI.getByTxHash(searchValue.trim());
      } else {
        // 토큰 ID로 검색
        const tokenId = parseInt(searchValue.trim());
        if (isNaN(tokenId)) {
          throw new Error('올바른 토큰 ID를 입력해주세요.');
        }
        recipeData = await nftAPI.getByTokenId(tokenId);
      }

      setRecipe(recipeData);

      // 메타데이터도 가져오기
      try {
        const meta = await nftAPI.getMetadata(recipeData.id);
        setMetadata(meta);
      } catch (metaErr) {
        console.warn('메타데이터를 가져올 수 없습니다:', metaErr);
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        err.message || 
        'NFT를 찾을 수 없습니다.'
      );
    } finally {
      setLoading(false);
    }
  };

  const getEtherscanUrl = (txHash) => {
    // Sepolia 테스트넷
    return `https://sepolia.etherscan.io/tx/${txHash}`;
  };

  return (
    <div className="view-nft-container">
      <div className="view-nft-card">
        <h1>NFT 확인</h1>
        <p className="subtitle">트랜잭션 해시 또는 토큰 ID로 NFT를 검색하세요</p>

        <div className="search-section">
          <div className="search-type-selector">
            <button
              className={`type-btn ${searchType === 'tx' ? 'active' : ''}`}
              onClick={() => setSearchType('tx')}
            >
              트랜잭션 해시
            </button>
            <button
              className={`type-btn ${searchType === 'token' ? 'active' : ''}`}
              onClick={() => setSearchType('token')}
            >
              토큰 ID
            </button>
          </div>

          <div className="search-input-group">
            <input
              type="text"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              placeholder={
                searchType === 'tx'
                  ? '0x... (트랜잭션 해시)'
                  : '123 (토큰 ID)'
              }
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} className="btn btn-primary" disabled={loading}>
              {loading ? '검색 중...' : '검색'}
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {recipe && (
          <div className="recipe-details">
            <h2>{recipe.recipe_name}</h2>

            <div className="nft-info">
              <div className="info-card">
                <h3>NFT 정보</h3>
                {recipe.token_id && (
                  <p><strong>Token ID:</strong> {recipe.token_id}</p>
                )}
                {recipe.contract_address && (
                  <p><strong>Contract Address:</strong> {recipe.contract_address}</p>
                )}
                {recipe.ipfs_hash && (
                  <p>
                    <strong>IPFS Hash:</strong>{' '}
                    <a
                      href={`https://ipfs.io/ipfs/${recipe.ipfs_hash}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {recipe.ipfs_hash}
                    </a>
                  </p>
                )}
                {recipe.is_minted && (
                  <p className="status-badge minted">✅ 민팅 완료</p>
                )}
              </div>

              {metadata && (
                <div className="info-card">
                  <h3>메타데이터</h3>
                  {metadata.metadata_uri && (
                    <p>
                      <strong>Metadata URI:</strong>{' '}
                      <a
                        href={metadata.metadata_uri}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {metadata.metadata_uri}
                      </a>
                    </p>
                  )}
                  {metadata.metadata && (
                    <div className="metadata-content">
                      <h4>속성</h4>
                      <ul>
                        {metadata.metadata.attributes?.map((attr, idx) => (
                          <li key={idx}>
                            <strong>{attr.trait_type}:</strong> {attr.value}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="recipe-content">
              <div className="content-section">
                <h3>재료</h3>
                <ul>
                  {recipe.ingredients.map((ing, idx) => (
                    <li key={idx}>{ing}</li>
                  ))}
                </ul>
              </div>

              <div className="content-section">
                <h3>조리 도구</h3>
                <ul>
                  {recipe.cooking_tools.map((tool, idx) => (
                    <li key={idx}>{tool}</li>
                  ))}
                </ul>
              </div>

              <div className="content-section">
                <h3>조리 과정</h3>
                <ol>
                  {recipe.cooking_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ViewNFT;

