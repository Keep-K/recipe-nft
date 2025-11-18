import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { recipeAPI } from '../utils/api';
import './RecipeList.css';

const RecipeList = () => {
  const { walletAddress, isConnected } = useAuth();
  const navigate = useNavigate();
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isConnected) {
      navigate('/login');
      return;
    }

    loadRecipes();
  }, [isConnected, navigate]);

  const loadRecipes = async () => {
    try {
      const data = await recipeAPI.getAll();
      setRecipes(data);
    } catch (err) {
      setError('레시피를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="recipe-list-container">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="recipe-list-container">
      <div className="recipe-list-header">
        <h1>내 레시피</h1>
        <div className="header-actions">
          <Link to="/recipes/create" className="btn btn-primary">
            + 새 레시피 작성
          </Link>
          <Link to="/nft/view" className="btn btn-secondary">
            NFT 확인
          </Link>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {recipes.length === 0 ? (
        <div className="empty-state">
          <p>아직 작성한 레시피가 없습니다.</p>
          <Link to="/recipes/create" className="btn btn-primary">
            첫 레시피 작성하기
          </Link>
        </div>
      ) : (
        <div className="recipe-grid">
          {recipes.map((recipe) => (
            <div key={recipe.id} className="recipe-card">
              <div className="recipe-card-header">
                <h3>{recipe.recipe_name}</h3>
                {recipe.is_minted && (
                  <span className="badge minted">✅ NFT</span>
                )}
              </div>
              <div className="recipe-card-body">
                <p className="recipe-meta">
                  <span>재료: {recipe.ingredients?.length || 0}개</span>
                  <span>도구: {recipe.cooking_tools?.length || 0}개</span>
                </p>
                {recipe.token_id && (
                  <p className="token-id">Token ID: {recipe.token_id}</p>
                )}
              </div>
              <div className="recipe-card-actions">
                <Link to={`/recipes/${recipe.id}`} className="btn-link">
                  상세보기
                </Link>
                {!recipe.is_minted && (
                  <Link to={`/recipes/${recipe.id}/mint`} className="btn-link primary">
                    민팅하기
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecipeList;

