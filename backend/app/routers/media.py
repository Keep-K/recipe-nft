from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
from app.database import get_db
from app import models, schemas
from app.config import settings

router = APIRouter(prefix="/media", tags=["media"])

# 업로드 디렉토리 생성
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload/{recipe_id}", response_model=schemas.MediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    recipe_id: int,
    file: UploadFile = File(...),
    media_type: str = "photo",  # photo or video
    db: Session = Depends(get_db)
):
    """미디어 파일 업로드"""
    # 레시피 확인
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # 미디어 타입 검증
    if media_type not in ["photo", "video"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="media_type must be 'photo' or 'video'"
        )
    
    # 파일 크기 검증
    file_content = await file.read()
    file_size = len(file_content)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # 파일 확장자 검증
    file_ext = Path(file.filename).suffix.lower()
    allowed_extensions = {
        "photo": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "video": [".mp4", ".mov", ".avi", ".webm"]
    }
    if file_ext not in allowed_extensions.get(media_type, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension for {media_type}"
        )
    
    # 파일 저장
    recipe_dir = UPLOAD_DIR / str(recipe_id)
    recipe_dir.mkdir(exist_ok=True)
    
    file_path = recipe_dir / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)
    
    # DB에 저장
    db_media = models.RecipeMedia(
        recipe_id=recipe_id,
        media_type=media_type,
        file_path=str(file_path),
        file_name=file.filename,
        file_size=file_size
    )
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    
    return db_media

@router.get("/{media_id}", response_model=schemas.MediaResponse)
async def get_media(media_id: int, db: Session = Depends(get_db)):
    """미디어 조회"""
    media = db.query(models.RecipeMedia).filter(models.RecipeMedia.id == media_id).first()
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    return media

@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(media_id: int, db: Session = Depends(get_db)):
    """미디어 삭제"""
    media = db.query(models.RecipeMedia).filter(models.RecipeMedia.id == media_id).first()
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # 파일 삭제
    if media.file_path and os.path.exists(media.file_path):
        os.remove(media.file_path)
    
    db.delete(media)
    db.commit()
    
    return None

