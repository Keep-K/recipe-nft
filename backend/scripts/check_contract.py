#!/usr/bin/env python3
"""
컨트랙트 주소 확인 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web3 import Web3
from app.config import settings

# 확인할 주소들
ADDRESSES_TO_CHECK = [
    "0x95c76D32c1a898514271ED17C98f9F66606A02Eb",  # 현재 설정된 주소
]

def check_address(address):
    """주소가 컨트랙트인지 확인"""
    w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    if not w3.is_connected():
        print(f"❌ Web3 연결 실패")
        return
    
    print(f"\n🔍 주소 확인: {address}")
    print(f"   Checksum: {Web3.to_checksum_address(address)}")
    
    # 컨트랙트 코드 확인
    code = w3.eth.get_code(address)
    if code == b'' or code == '0x':
        print(f"   ❌ 컨트랙트가 아닙니다 (일반 지갑 주소)")
        print(f"   Code length: 0 bytes")
        
        # 잔액 확인
        balance = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance, 'ether')
        print(f"   💰 잔액: {balance_eth} ETH")
    else:
        print(f"   ✅ 컨트랙트입니다!")
        print(f"   Code length: {len(code)} bytes")
        print(f"   Etherscan: https://sepolia.etherscan.io/address/{address}#code")
    
    # 최근 트랜잭션 확인
    print(f"\n   📋 Etherscan 링크:")
    print(f"      https://sepolia.etherscan.io/address/{address}")

def main():
    print("=" * 60)
    print("컨트랙트 주소 확인")
    print("=" * 60)
    
    w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    if not w3.is_connected():
        print(f"❌ Web3 연결 실패: {settings.WEB3_PROVIDER_URL}")
        return
    
    print(f"✅ Web3 연결 성공")
    print(f"   Provider: {settings.WEB3_PROVIDER_URL}")
    print(f"   현재 NFT_CONTRACT_ADDRESS: {settings.NFT_CONTRACT_ADDRESS}")
    
    for address in ADDRESSES_TO_CHECK:
        check_address(address)
    
    print(f"\n" + "=" * 60)
    print("💡 중요:")
    print("   NFT 컨트랙트 주소는 일반 지갑 주소와 달라야 합니다.")
    print("   컨트랙트가 배포된 주소를 확인하세요.")
    print("=" * 60)

if __name__ == "__main__":
    main()

