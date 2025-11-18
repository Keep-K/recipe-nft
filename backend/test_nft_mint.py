#!/usr/bin/env python3
"""NFT 민팅 테스트 스크립트"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"
WALLET_ADDRESS = "0x95c76D32c1a898514271ED17C98f9F66606A02Eb"

def test_server():
    """서버 상태 확인"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 서버 상태: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def create_user():
    """사용자 생성"""
    try:
        data = {
            "wallet_address": WALLET_ADDRESS,
            "email": "test@example.com",
            "username": "testuser"
        }
        response = requests.post(f"{BASE_URL}/api/users", json=data, timeout=10)
        if response.status_code in [200, 201]:
            print(f"✅ 사용자 생성/조회 성공")
            return True
        else:
            print(f"⚠️ 사용자 생성 응답: {response.status_code} - {response.text}")
            return True  # 이미 존재할 수 있음
    except Exception as e:
        print(f"❌ 사용자 생성 실패: {e}")
        return False

def create_recipe():
    """레시피 생성"""
    try:
        data = {
            "recipe_name": "테스트 김치찌개",
            "ingredients": [
                "김치 200g",
                "돼지고기 100g",
                "물 500ml"
            ],
            "cooking_tools": ["냄비", "국자", "볶음팬"],
            "cooking_steps": [
                "1. 돼지고기를 볶는다",
                "2. 김치를 넣고 볶는다",
                "3. 물을 넣고 끓인다",
                "4. 15분간 끓인다"
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/recipes/?wallet_address={WALLET_ADDRESS}",
            json=data,
            timeout=10
        )
        if response.status_code == 201:
            recipe = response.json()
            print(f"✅ 레시피 생성 성공: ID={recipe['id']}, 이름={recipe['recipe_name']}")
            return recipe['id']
        else:
            print(f"❌ 레시피 생성 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 레시피 생성 오류: {e}")
        return None

def mint_nft(recipe_id):
    """NFT 민팅"""
    try:
        print(f"\n🔄 NFT 민팅 시작 (레시피 ID: {recipe_id})...")
        response = requests.post(
            f"{BASE_URL}/api/nft/mint/{recipe_id}?wallet_address={WALLET_ADDRESS}",
            timeout=60  # 블록체인 트랜잭션은 시간이 걸릴 수 있음
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ NFT 민팅 성공!")
            print(f"   - 토큰 ID: {result.get('token_id')}")
            print(f"   - 컨트랙트 주소: {result.get('contract_address')}")
            print(f"   - IPFS 해시: {result.get('ipfs_hash')}")
            print(f"   - 민팅 상태: {result.get('is_minted')}")
            return True
        else:
            print(f"❌ NFT 민팅 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
    except Exception as e:
        print(f"❌ NFT 민팅 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("NFT 민팅 테스트 시작")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    if not test_server():
        print("\n❌ 서버가 실행 중이 아닙니다. 서버를 먼저 시작해주세요.")
        return
    
    # 2. 사용자 생성
    print("\n[1/4] 사용자 생성/조회...")
    if not create_user():
        return
    
    # 3. 레시피 생성
    print("\n[2/4] 레시피 생성...")
    recipe_id = create_recipe()
    if not recipe_id:
        return
    
    # 4. NFT 민팅
    print("\n[3/4] NFT 민팅...")
    if mint_nft(recipe_id):
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 통과!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ NFT 민팅 실패")
        print("=" * 50)

if __name__ == "__main__":
    main()

