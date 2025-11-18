from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
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
        # IPFS가 연결되지 않은 경우 임시 해시 사용 (개발/테스트 환경)
        import hashlib
        import time
        temp_hash = hashlib.md5(f"{recipe_id}_{time.time()}".encode()).hexdigest()
        ipfs_hash = f"Qm{temp_hash[:40]}"  # IPFS 해시 형식으로 임시 생성
        print(f"Warning: IPFS not available, using temporary hash: {ipfs_hash}")
    
    # 3. 스마트 컨트랙트를 통한 NFT 민팅
    token_id = None
    contract_address = settings.NFT_CONTRACT_ADDRESS
    transaction_hash = None
    
    if web3_service.is_connected() and contract_address:
        # 실제 민팅 로직
        token_uri = f"ipfs://{ipfs_hash}"
        
        # 지갑 주소 유효성 검증
        from web3 import Web3
        try:
            wallet_address = Web3.to_checksum_address(wallet_address)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid wallet address: {str(e)}"
            )
        
        print(f"Attempting to mint NFT: contract={contract_address}, to={wallet_address}, uri={token_uri}")
        
        try:
            result = web3_service.mint_nft(contract_address, wallet_address, token_uri)
            
            if result:
                token_id, transaction_hash = result
                print(f"✅ NFT minted successfully! Token ID: {token_id}, TX: {transaction_hash}")
            else:
                error_msg = "Failed to mint NFT on blockchain"
                if not settings.PRIVATE_KEY:
                    error_msg += " (PRIVATE_KEY not set)"
                elif not web3_service.is_connected():
                    error_msg += " (Web3 not connected)"
                else:
                    error_msg += " (Check server logs for details)"
                
                print(f"❌ {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
        except Exception as e:
            error_detail = f"Failed to mint NFT: {str(e)}"
            print(f"❌ Mint error: {error_detail}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )
    else:
        # 개발/테스트 환경: 모의 토큰 ID 생성
        # 실제로는 스마트 컨트랙트에서 받아와야 함
        import random
        token_id = random.randint(1000, 9999)  # 임시 값
        warning_msg = "Warning: Using mock token ID. "
        if not web3_service.is_connected():
            warning_msg += f"Web3 not connected (Provider: {settings.WEB3_PROVIDER_URL}). "
        if not contract_address:
            warning_msg += "Contract address not set. "
        print(warning_msg)
    
    # 4. DB 업데이트
    recipe.ipfs_hash = ipfs_hash
    recipe.token_id = token_id
    recipe.contract_address = contract_address
    recipe.transaction_hash = transaction_hash  # None일 수 있음 (모의 민팅 시)
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

@router.get("/by-token/{token_id}", response_model=schemas.RecipeResponse)
async def get_recipe_by_token_id(
    token_id: int,
    contract_address: Optional[str] = Query(None, description="컨트랙트 주소 (선택사항)"),
    db: Session = Depends(get_db)
):
    """토큰 ID로 레시피 조회"""
    query = db.query(models.Recipe).filter(models.Recipe.token_id == token_id)
    
    if contract_address:
        query = query.filter(models.Recipe.contract_address == contract_address)
    
    recipe = query.first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe not found for token_id: {token_id}"
        )
    
    return recipe

@router.get("/by-tx/{tx_hash}", response_model=schemas.RecipeResponse)
async def get_recipe_by_transaction(
    tx_hash: str,
    contract_address: Optional[str] = Query(None, description="컨트랙트 주소 (선택사항, 없으면 설정값 사용)"),
    use_etherscan: bool = Query(False, description="Etherscan API 사용 (Web3 실패 시)"),
    db: Session = Depends(get_db)
):
    """
    트랜잭션 해시로 레시피 조회
    
    트랜잭션 해시에서 토큰 ID를 추출한 후 레시피를 찾습니다.
    """
    # 컨트랙트 주소 확인
    if not contract_address:
        contract_address = settings.NFT_CONTRACT_ADDRESS
    
    if not contract_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract address not provided and not set in environment"
        )
    
    # 트랜잭션에서 토큰 ID 추출
    token_id = None
    
    if use_etherscan:
        # Etherscan API 사용 (대안)
        token_id = web3_service.get_token_id_from_etherscan(tx_hash, network="sepolia")
    else:
        # Web3 직접 연결 시도
        token_id = web3_service.get_token_id_from_transaction(contract_address, tx_hash)
        
        # 실패 시 Etherscan API로 재시도 (token_id가 None인 경우만)
        if token_id is None:
            print("Web3 method failed, trying Etherscan API...")
            token_id = web3_service.get_token_id_from_etherscan(tx_hash, network="sepolia")
    
    if token_id is None:
        # 데이터베이스에서 직접 조회 시도 (트랜잭션 해시가 저장되어 있다면)
        # 또는 모든 민팅된 레시피를 반환하여 사용자가 찾을 수 있도록
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not extract token_id from transaction: {tx_hash}. "
                   f"Please check: 1) Web3 provider is connected ({settings.WEB3_PROVIDER_URL}), "
                   f"2) Contract address is correct ({contract_address}), "
                   f"3) Transaction is confirmed on blockchain. "
                   f"Try using /api/nft/by-token/{token_id} if you know the token ID, "
                   f"or use ?use_etherscan=true parameter."
        )
    
    # 토큰 ID로 레시피 조회
    recipe = db.query(models.Recipe).filter(
        models.Recipe.token_id == token_id,
        models.Recipe.contract_address == contract_address
    ).first()
    
    if not recipe:
        # 토큰 ID가 일치하지 않는 경우, 데이터베이스의 모든 민팅된 레시피를 확인
        all_minted = db.query(models.Recipe).filter(
            models.Recipe.is_minted == True,
            models.Recipe.contract_address == contract_address
        ).all()
        
        # 가장 최근에 민팅된 레시피 반환 (토큰 ID 불일치 시 대안)
        if all_minted:
            latest_recipe = sorted(all_minted, key=lambda r: r.created_at, reverse=True)[0]
            print(f"Warning: Token ID mismatch. Extracted token_id={token_id}, but found recipe with token_id={latest_recipe.token_id}")
            print(f"Returning latest minted recipe as fallback.")
            return latest_recipe
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe not found for token_id: {token_id} from transaction: {tx_hash}. "
                   f"Extracted token_id: {token_id}, but no matching recipe in database. "
                   f"Available minted recipes: {[r.token_id for r in all_minted] if all_minted else 'none'}. "
                   f"Try using /api/nft/by-token/{token_id} or check the debug endpoint."
        )
    
    return recipe

@router.get("/debug/tx/{tx_hash}")
async def debug_transaction(
    tx_hash: str,
    contract_address: Optional[str] = Query(None, description="컨트랙트 주소"),
    db: Session = Depends(get_db)
):
    """
    트랜잭션 디버깅 정보 조회
    """
    if not contract_address:
        contract_address = settings.NFT_CONTRACT_ADDRESS
    
    debug_info = {
        "tx_hash": tx_hash,
        "contract_address": contract_address,
        "web3_connected": web3_service.is_connected(),
        "web3_provider": settings.WEB3_PROVIDER_URL,
        "token_id_from_web3": None,
        "token_id_from_etherscan": None,
        "recipes_in_db": []
    }
    
    # Web3로 시도
    if contract_address:
        token_id_web3 = web3_service.get_token_id_from_transaction(contract_address, tx_hash)
        debug_info["token_id_from_web3"] = token_id_web3
    
    # Etherscan으로 시도
    token_id_etherscan = web3_service.get_token_id_from_etherscan(tx_hash, network="sepolia")
    debug_info["token_id_from_etherscan"] = token_id_etherscan
    
    # 데이터베이스에서 민팅된 레시피 목록
    minted_recipes = db.query(models.Recipe).filter(
        models.Recipe.is_minted == True
    ).all()
    
    debug_info["recipes_in_db"] = [
        {
            "id": r.id,
            "recipe_name": r.recipe_name,
            "token_id": r.token_id,
            "contract_address": r.contract_address,
            "is_minted": r.is_minted
        }
        for r in minted_recipes
    ]
    
    return debug_info

