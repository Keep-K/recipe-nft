from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """사용자 생성"""
    # 이미 존재하는지 확인
    existing_user = db.query(models.User).filter(
        models.User.wallet_address == user.wallet_address
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this wallet address already exists"
        )
    
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{wallet_address}", response_model=schemas.UserResponse)
async def get_user(wallet_address: str, db: Session = Depends(get_db)):
    """사용자 조회"""
    user = db.query(models.User).filter(models.User.wallet_address == wallet_address).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{wallet_address}/recipes", response_model=list[schemas.RecipeListResponse])
async def get_user_recipes(wallet_address: str, db: Session = Depends(get_db)):
    """사용자의 레시피 목록 조회"""
    user = db.query(models.User).filter(models.User.wallet_address == wallet_address).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user.recipes

