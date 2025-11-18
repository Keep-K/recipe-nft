#!/usr/bin/env python3
"""NFT 민팅 함수만 테스트 (DB 없이)"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.web3 import web3_service
from app.services.ipfs import ipfs_service
from app.config import settings

WALLET_ADDRESS = "0x95c76D32c1a898514271ED17C98f9F66606A02Eb"

def main():
    print("=" * 60)
    print("NFT 민팅 함수 테스트 (DB 없이)")
    print("=" * 60)
    
    # Web3 연결 확인
    print("\n[1/3] Web3 연결 확인...")
    if not web3_service.is_connected():
        print("❌ Web3 연결 실패")
        return
    print(f"✅ Web3 연결 성공")
    print(f"   - Provider: {settings.WEB3_PROVIDER_URL[:50]}...")
    print(f"   - Contract: {settings.NFT_CONTRACT_ADDRESS}")
    
    # ABI 로드
    print("\n[2/3] 컨트랙트 ABI 로드...")
    abi = web3_service.load_contract_abi()
    if not abi:
        print("❌ ABI 로드 실패")
        return
    print(f"✅ ABI 로드 성공 ({len(abi)} 항목)")
    
    # 테스트 메타데이터 생성
    print("\n[3/3] NFT 민팅 테스트...")
    metadata = {
        "name": "테스트 레시피 NFT",
        "description": "테스트용 레시피 NFT입니다",
        "attributes": [
            {"trait_type": "Test", "value": "True"}
        ],
        "properties": {
            "ingredients": ["테스트 재료"],
            "cooking_steps": ["테스트 단계"]
        }
    }
    
    # IPFS 업로드 (선택사항)
    print("   🔄 IPFS에 메타데이터 업로드 중...")
    ipfs_hash = ipfs_service.upload_json(metadata)
    if ipfs_hash:
        print(f"   ✅ IPFS 업로드 성공: {ipfs_hash}")
        token_uri = f"ipfs://{ipfs_hash}"
    else:
        print("   ⚠️ IPFS 업로드 실패 (로컬 노드 없음), 임시 URI 사용")
        token_uri = "ipfs://QmTest123"  # 임시 URI
    
    # NFT 민팅
    print(f"   🔄 블록체인에 NFT 민팅 중...")
    print(f"      - 수신 주소: {WALLET_ADDRESS}")
    print(f"      - Token URI: {token_uri}")
    
    result = web3_service.mint_nft(
        settings.NFT_CONTRACT_ADDRESS,
        WALLET_ADDRESS,
        token_uri
    )
    
    if result:
        token_id, tx_hash = result
        print(f"\n   ✅ NFT 민팅 성공!")
        print(f"      - 토큰 ID: {token_id}")
        print(f"      - 트랜잭션 해시: {tx_hash}")
        print(f"      - Etherscan: https://sepolia.etherscan.io/tx/{tx_hash}")
        print("\n" + "=" * 60)
        print("✅ 테스트 성공!")
        print("=" * 60)
    else:
        print(f"\n   ❌ NFT 민팅 실패")
        print("\n" + "=" * 60)
        print("❌ 테스트 실패")
        print("=" * 60)

if __name__ == "__main__":
    main()


