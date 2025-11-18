import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { recipeAPI } from '../utils/api';
import './CreateRecipe.css';

const CreateRecipe = () => {
  const { walletAddress, isConnected } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    recipe_name: '',
    ingredients: [''],
    cooking_tools: [''],
    cooking_steps: [''],
  });

  if (!isConnected) {
    navigate('/login');
    return null;
  }

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleArrayChange = (field, index, value) => {
    setFormData((prev) => {
      const newArray = [...prev[field]];
      newArray[index] = value;
      return { ...prev, [field]: newArray };
    });
  };

  const addArrayItem = (field) => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...prev[field], ''],
    }));
  };

  const removeArrayItem = (field, index) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 빈 항목 제거
      const cleanedData = {
        recipe_name: formData.recipe_name.trim(),
        ingredients: formData.ingredients.filter((item) => item.trim() !== ''),
        cooking_tools: formData.cooking_tools.filter((item) => item.trim() !== ''),
        cooking_steps: formData.cooking_steps.filter((item) => item.trim() !== ''),
      };

      // 유효성 검사
      if (!cleanedData.recipe_name) {
        throw new Error('레시피 이름을 입력해주세요.');
      }
      if (cleanedData.ingredients.length === 0) {
        throw new Error('재료를 최소 1개 이상 입력해주세요.');
      }
      if (cleanedData.cooking_tools.length === 0) {
        throw new Error('조리 도구를 최소 1개 이상 입력해주세요.');
      }
      if (cleanedData.cooking_steps.length === 0) {
        throw new Error('조리 과정을 최소 1개 이상 입력해주세요.');
      }

      const recipe = await recipeAPI.create(cleanedData, walletAddress);
      navigate(`/recipes/${recipe.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || '레시피 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-recipe-container">
      <div className="create-recipe-card">
        <h1>새 레시피 작성</h1>
        <p className="subtitle">NFT로 민팅할 레시피를 작성하세요</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="recipe-form">
          <div className="form-group">
            <label htmlFor="recipe_name">레시피 이름 *</label>
            <input
              id="recipe_name"
              type="text"
              value={formData.recipe_name}
              onChange={(e) => handleInputChange('recipe_name', e.target.value)}
              placeholder="예: 김치찌개"
              required
            />
          </div>

          <div className="form-group">
            <label>재료 *</label>
            {formData.ingredients.map((item, index) => (
              <div key={index} className="array-input-group">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => handleArrayChange('ingredients', index, e.target.value)}
                  placeholder="예: 김치 200g"
                />
                {formData.ingredients.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeArrayItem('ingredients', index)}
                    className="btn-remove"
                  >
                    삭제
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={() => addArrayItem('ingredients')}
              className="btn-add"
            >
              + 재료 추가
            </button>
          </div>

          <div className="form-group">
            <label>조리 도구 *</label>
            {formData.cooking_tools.map((item, index) => (
              <div key={index} className="array-input-group">
                <input
                  type="text"
                  value={item}
                  onChange={(e) => handleArrayChange('cooking_tools', index, e.target.value)}
                  placeholder="예: 냄비"
                />
                {formData.cooking_tools.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeArrayItem('cooking_tools', index)}
                    className="btn-remove"
                  >
                    삭제
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={() => addArrayItem('cooking_tools')}
              className="btn-add"
            >
              + 도구 추가
            </button>
          </div>

          <div className="form-group">
            <label>조리 과정 *</label>
            {formData.cooking_steps.map((item, index) => (
              <div key={index} className="array-input-group">
                <textarea
                  value={item}
                  onChange={(e) => handleArrayChange('cooking_steps', index, e.target.value)}
                  placeholder="예: 1. 김치를 적당한 크기로 썬다"
                  rows={3}
                />
                {formData.cooking_steps.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeArrayItem('cooking_steps', index)}
                    className="btn-remove"
                  >
                    삭제
                  </button>
                )}
              </div>
            ))}
            <button
              type="button"
              onClick={() => addArrayItem('cooking_steps')}
              className="btn-add"
            >
              + 과정 추가
            </button>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/recipes')}
              className="btn btn-secondary"
            >
              취소
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? '생성 중...' : '레시피 생성'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateRecipe;

