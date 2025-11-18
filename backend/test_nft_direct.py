#!/usr/bin/env python3
"""NFT 민팅 직접 테스트 (서버 없이)"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app import models
from app.services.web3 import web3_service
from app.services.ipfs import ipfs_service
from app.config import settings

WALLET_ADDRESS = "0x95c76D32c1a898514271ED17C98f9F66606A02Eb"

def test_web3_connection():
    """Web3 연결 테스트"""
    print("\n[1/5] Web3 연결 확인...")
    if web3_service.is_connected():
        print(f"✅ Web3 연결 성공")
        print(f"   - Provider: {settings.WEB3_PROVIDER_URL[:50]}...")
        return True
    else:
        print(f"❌ Web3 연결 실패")
        return False

def test_contract_abi():
    """컨트랙트 ABI 로드 테스트"""
    print("\n[2/5] 컨트랙트 ABI 로드...")
    abi = web3_service.load_contract_abi()
    if abi:
        print(f"✅ ABI 로드 성공 ({len(abi)} 항목)")
        return True
    else:
        print(f"❌ ABI 로드 실패")
        return False

def create_test_recipe(db):
    """테스트 레시피 생성"""
    print("\n[3/5] 테스트 레시피 생성...")
    
    # 사용자 조회 또는 생성
    user = db.query(models.User).filter(models.User.wallet_address == WALLET_ADDRESS).first()
    if not user:
        user = models.User(
            wallet_address=WALLET_ADDRESS,
            email="test@example.com",
            username="testuser"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   ✅ 사용자 생성: {user.id}")
    else:
        print(f"   ✅ 사용자 조회: {user.id}")
    
    # 레시피 생성
    recipe = models.Recipe(
        user_id=user.id,
        recipe_name="테스트 김치찌개",
        ingredients=[
            {"name": "김치", "amount": "200g"},
            {"name": "돼지고기", "amount": "100g"},
            {"name": "물", "amount": "500ml"}
        ],
        cooking_tools=["냄비", "국자", "볶음팬"],
        cooking_steps=[
            {"step": 1, "description": "돼지고기를 볶는다"},
            {"step": 2, "description": "김치를 넣고 볶는다"},
            {"step": 3, "description": "물을 넣고 끓인다"},
            {"step": 4, "description": "15분간 끓인다"}
        ]
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    print(f"   ✅ 레시피 생성: ID={recipe.id}, 이름={recipe.recipe_name}")
    return recipe

def test_ipfs():
    """IPFS 연결 테스트"""
    print("\n[4/5] IPFS 연결 확인...")
    try:
        # 간단한 테스트 데이터 업로드
        test_data = {"test": "data"}
        hash_result = ipfs_service.upload_json(test_data)
        if hash_result:
            print(f"✅ IPFS 연결 성공 (테스트 해시: {hash_result})")
            return True
        else:
            print(f"⚠️ IPFS 연결 실패 (로컬 노드가 실행 중이 아닐 수 있음)")
            return False
    except Exception as e:
        print(f"⚠️ IPFS 테스트 오류: {e}")
        return False

def test_mint_nft(recipe):
    """NFT 민팅 테스트"""
    print("\n[5/5] NFT 민팅 테스트...")
    
    if not settings.NFT_CONTRACT_ADDRESS:
        print("❌ NFT_CONTRACT_ADDRESS가 설정되지 않았습니다")
        return False
    
    if not settings.PRIVATE_KEY:
        print("❌ PRIVATE_KEY가 설정되지 않았습니다")
        return False
    
    # 메타데이터 생성
    metadata = {
        "name": recipe.recipe_name,
        "description": f"Recipe NFT: {recipe.recipe_name}",
        "attributes": [
            {"trait_type": "Ingredients Count", "value": len(recipe.ingredients)},
            {"trait_type": "Cooking Steps", "value": len(recipe.cooking_steps)},
        ],
        "properties": {
            "ingredients": recipe.ingredients,
            "cooking_tools": recipe.cooking_tools,
            "cooking_steps": recipe.cooking_steps,
        }
    }
    
    # IPFS 업로드
    print("   🔄 IPFS에 메타데이터 업로드 중...")
    ipfs_hash = ipfs_service.upload_json(metadata)
    if not ipfs_hash:
        print("   ⚠️ IPFS 업로드 실패 (로컬 노드 없음), 임시 해시 사용")
        # IPFS가 없어도 테스트를 위해 임시 해시 사용
        ipfs_hash = "QmTestHash123456789"  # 임시 해시
    else:
        print(f"   ✅ IPFS 업로드 성공: {ipfs_hash}")
    
    # NFT 민팅
    print("   🔄 블록체인에 NFT 민팅 중...")
    token_uri = f"ipfs://{ipfs_hash}"
    result = web3_service.mint_nft(
        settings.NFT_CONTRACT_ADDRESS,
        WALLET_ADDRESS,
        token_uri
    )
    
    if result:
        token_id, tx_hash = result
        print(f"   ✅ NFT 민팅 성공!")
        print(f"      - 토큰 ID: {token_id}")
        print(f"      - 트랜잭션 해시: {tx_hash}")
        print(f"      - Etherscan: https://sepolia.etherscan.io/tx/{tx_hash}")
        return True
    else:
        print(f"   ❌ NFT 민팅 실패")
        return False

def main():
    print("=" * 60)
    print("NFT 민팅 직접 테스트")
    print("=" * 60)
    
    # Web3 연결 확인
    if not test_web3_connection():
        print("\n❌ Web3 연결이 필요합니다. .env 파일을 확인해주세요.")
        return
    
    # ABI 로드 확인
    if not test_contract_abi():
        print("\n❌ 컨트랙트 ABI를 로드할 수 없습니다.")
        return
    
    # IPFS 테스트 (선택사항)
    ipfs_ok = test_ipfs()
    if not ipfs_ok:
        print("   ⚠️ IPFS가 연결되지 않았지만 계속 진행합니다...")
    
    # 데이터베이스 연결
    db = SessionLocal()
    try:
        # 레시피 생성
        recipe = create_test_recipe(db)
        
        # NFT 민팅
        if test_mint_nft(recipe):
            print("\n" + "=" * 60)
            print("✅ 모든 테스트 통과!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ NFT 민팅 실패")
            print("=" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    main()

