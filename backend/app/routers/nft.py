from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.ipfs import ipfs_service
from app.services.web3 import web3_service
from app.config import settings
import json

router = APIRouter(prefix="/nft", tags=["nft"])

def create_recipe_metadata(recipe: models.Recipe) -> dict:
    """레시피를 NFT 메타데이터 형식으로 변환"""
    # ERC-721 Metadata 표준 형식
    metadata = {
        "name": recipe.recipe_name,
        "description": f"Recipe NFT: {recipe.recipe_name}",
        "image": "",  # 대표 이미지 IPFS 해시 (추후 추가)
        "attributes": [
            {
                "trait_type": "Ingredients Count",
                "value": len(recipe.ingredients)
            },
            {
                "trait_type": "Cooking Steps",
                "value": len(recipe.cooking_steps)
            },
            {
                "trait_type": "Tools Count",
                "value": len(recipe.cooking_tools)
            }
        ],
        "properties": {
            "ingredients": recipe.ingredients,
            "cooking_tools": recipe.cooking_tools,
            "cooking_steps": recipe.cooking_steps,
            "machine_instructions": recipe.machine_instructions or []
        }
    }
    return metadata

@router.post("/mint/{recipe_id}", response_model=schemas.RecipeResponse)
async def mint_recipe_nft(
    recipe_id: int,
    wallet_address: str = Query(..., description="지갑 주소 (민팅 대상)"),
    db: Session = Depends(get_db)
):
    """
    레시피를 NFT로 민팅
    
    1. 레시피 메타데이터 생성
    2. IPFS에 메타데이터 업로드
    3. 스마트 컨트랙트를 통해 NFT 민팅
    4. DB에 토큰 ID 및 IPFS 해시 저장
    """
    # 레시피 조회
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    # 소유자 확인
    user = db.query(models.User).filter(models.User.wallet_address == wallet_address).first()
    if not user or recipe.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mint this recipe"
        )
    
    # 이미 민팅된 레시피인지 확인
    if recipe.is_minted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe already minted"
        )
    
    # 1. 메타데이터 생성
    metadata = create_recipe_metadata(recipe)
    
    # 2. IPFS에 메타데이터 업로드
    ipfs_hash = ipfs_service.upload_json(metadata)
    if not ipfs_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload metadata to IPFS"
        )
    
    # 3. 스마트 컨트랙트를 통한 NFT 민팅
    # TODO: 실제 스마트 컨트랙트 연동 구현 필요
    # 현재는 모의(mock) 구현
    token_id = None
    contract_address = settings.NFT_CONTRACT_ADDRESS
    
    if web3_service.is_connected() and contract_address:
        # 실제 민팅 로직 (추후 구현)
        # contract = web3_service.get_contract(contract_address, abi)
        # tx = contract.functions.mint(wallet_address, f"ipfs://{ipfs_hash}").transact(...)
        # receipt = web3_service.w3.eth.wait_for_transaction_receipt(tx)
        # token_id = contract.functions.totalSupply().call() - 1
        pass
    else:
        # 개발/테스트 환경: 모의 토큰 ID 생성
        # 실제로는 스마트 컨트랙트에서 받아와야 함
        import random
        token_id = random.randint(1000, 9999)  # 임시 값
    
    # 4. DB 업데이트
    recipe.ipfs_hash = ipfs_hash
    recipe.token_id = token_id
    recipe.contract_address = contract_address
    recipe.is_minted = True
    
    db.commit()
    db.refresh(recipe)
    
    return recipe

@router.get("/metadata/{recipe_id}")
async def get_recipe_metadata(recipe_id: int, db: Session = Depends(get_db)):
    """레시피의 NFT 메타데이터 조회"""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    if not recipe.is_minted or not recipe.ipfs_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe not minted yet"
        )
    
    # IPFS에서 메타데이터 가져오기
    metadata_bytes = ipfs_service.get_file(recipe.ipfs_hash)
    if not metadata_bytes:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metadata from IPFS"
        )
    
    metadata = json.loads(metadata_bytes.decode('utf-8'))
    return {
        "recipe_id": recipe.id,
        "token_id": recipe.token_id,
        "contract_address": recipe.contract_address,
        "ipfs_hash": recipe.ipfs_hash,
        "metadata": metadata,
        "metadata_uri": f"ipfs://{recipe.ipfs_hash}"
    }

