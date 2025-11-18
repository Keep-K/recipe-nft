import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import RecipeList from './pages/RecipeList';
import CreateRecipe from './pages/CreateRecipe';
import RecipeDetail from './pages/RecipeDetail';
import MintNFT from './pages/MintNFT';
import ViewNFT from './pages/ViewNFT';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/recipes" element={<RecipeList />} />
              <Route path="/recipes/create" element={<CreateRecipe />} />
              <Route path="/recipes/:recipeId" element={<RecipeDetail />} />
              <Route path="/recipes/:recipeId/mint" element={<MintNFT />} />
              <Route path="/nft/view" element={<ViewNFT />} />
              <Route path="/" element={<Navigate to="/recipes" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
