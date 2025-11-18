from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.post("/", response_model=schemas.RecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    recipe: schemas.RecipeCreate,
    wallet_address: str = Query(..., description="지갑 주소 (임시 인증)"),
    db: Session = Depends(get_db)
):
    """레시피 생성"""
    # 사용자 조회 또는 생성
    user = db.query(models.User).filter(models.User.wallet_address == wallet_address).first()
    if not user:
        user = models.User(wallet_address=wallet_address)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 레시피 생성
    db_recipe = models.Recipe(
        user_id=user.id,
        recipe_name=recipe.recipe_name,
        ingredients=recipe.ingredients,
        cooking_tools=recipe.cooking_tools,
        cooking_steps=recipe.cooking_steps,
        machine_instructions=recipe.machine_instructions
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    return db_recipe

@router.get("/", response_model=List[schemas.RecipeListResponse])
async def get_recipes(
    skip: int = 0,
    limit: int = 100,
    is_minted: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """레시피 목록 조회"""
    try:
        query = db.query(models.Recipe)
        
        if is_minted is not None:
            query = query.filter(models.Recipe.is_minted == is_minted)
        
        recipes = query.offset(skip).limit(limit).all()
        return recipes
    except Exception as e:
        import traceback
        print(f"❌ get_recipes error: {e}")
        traceback.print_exc()
        raise

@router.get("/{recipe_id}", response_model=schemas.RecipeResponse)
async def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """레시피 상세 조회"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    return recipe

@router.put("/{recipe_id}", response_model=schemas.RecipeResponse)
async def update_recipe(
    recipe_id: int,
    recipe_update: schemas.RecipeUpdate,
    wallet_address: str = Query(..., description="지갑 주소 (임시 인증)"),
    db: Session = Depends(get_db)
):
    """레시피 수정"""
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # 소유자 확인 (임시)
    user = db.query(models.User).filter(models.User.wallet_address == wallet_address).first()
    if not user or db_recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this recipe"
        )
    
    # 이미 민팅된 레시피는 수정 불가
    if db_recipe.is_minted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update minted recipe"
        )
    
    # 업데이트
    update_data = recipe_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recipe, field, value)
    
    db.commit()
    db.refresh(db_recipe)
    
    return db_recipe

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    wallet_address: str = Query(..., description="지갑 주소 (임시 인증)"),
    db: Session = Depends(get_db)
):
    """레시피 삭제"""
    db_recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # 소유자 확인 (임시)
    user = db.query(models.User).filter(models.User.wallet_address == wallet_address).first()
    if not user or db_recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this recipe"
        )
    
    # 이미 민팅된 레시피는 삭제 불가
    if db_recipe.is_minted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete minted recipe"
        )
    
    db.delete(db_recipe)
    db.commit()
    
    return None

@router.get("/{recipe_id}/media", response_model=List[schemas.MediaResponse])
async def get_recipe_media(recipe_id: int, db: Session = Depends(get_db)):
    """레시피 미디어 조회"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    return recipe.media

