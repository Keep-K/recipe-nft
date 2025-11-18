import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { recipeAPI } from '../utils/api';
import './RecipeDetail.css';

const RecipeDetail = () => {
  const { recipeId } = useParams();
  const { isConnected } = useAuth();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

  if (loading) {
    return (
      <div className="recipe-detail-container">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className="recipe-detail-container">
        <div className="error-message">{error || '레시피를 찾을 수 없습니다.'}</div>
      </div>
    );
  }

  return (
    <div className="recipe-detail-container">
      <div className="recipe-detail-card">
        <div className="recipe-header">
          <Link to="/recipes" className="back-link">← 목록으로</Link>
          <h1>{recipe.recipe_name}</h1>
          {recipe.is_minted && (
            <div className="mint-badge">
              <span className="badge minted">✅ NFT 민팅 완료</span>
              {recipe.token_id && <span>Token ID: {recipe.token_id}</span>}
            </div>
          )}
        </div>

        <div className="recipe-content">
          <div className="content-section">
            <h2>재료</h2>
            <ul>
              {recipe.ingredients.map((ing, idx) => (
                <li key={idx}>{ing}</li>
              ))}
            </ul>
          </div>

          <div className="content-section">
            <h2>조리 도구</h2>
            <ul>
              {recipe.cooking_tools.map((tool, idx) => (
                <li key={idx}>{tool}</li>
              ))}
            </ul>
          </div>

          <div className="content-section">
            <h2>조리 과정</h2>
            <ol>
              {recipe.cooking_steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
          </div>

          {recipe.machine_instructions && recipe.machine_instructions.length > 0 && (
            <div className="content-section">
              <h2>기계 작동 과정</h2>
              <div className="machine-instructions">
                {recipe.machine_instructions.map((instruction, idx) => (
                  <div key={idx} className="instruction-item">
                    <h3>{instruction.name || `과정 ${idx + 1}`}</h3>
                    <p>{instruction.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="recipe-actions">
          {!recipe.is_minted && (
            <Link to={`/recipes/${recipeId}/mint`} className="btn btn-primary">
              NFT 민팅하기
            </Link>
          )}
          {recipe.is_minted && (
            <>
              {recipe.ipfs_hash && (
                <a
                  href={`https://ipfs.io/ipfs/${recipe.ipfs_hash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  IPFS 메타데이터 보기
                </a>
              )}
              {recipe.transaction_hash ? (
                <a
                  href={`https://sepolia.etherscan.io/tx/${recipe.transaction_hash}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  트랜잭션 확인
                </a>
              ) : (
                recipe.contract_address && recipe.token_id && (
                  <a
                    href={`https://sepolia.etherscan.io/token/${recipe.contract_address}?a=${recipe.token_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                  >
                    NFT 확인 (Etherscan)
                  </a>
                )
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default RecipeDetail;

