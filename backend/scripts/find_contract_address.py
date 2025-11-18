#!/usr/bin/env python3
"""
트랜잭션 해시에서 실제 NFT 컨트랙트 주소 찾기
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web3 import Web3
from app.config import settings

TX_HASH = "0x84229f9b17d31f0f36fe5381aaf3ffb413b13666062c91b4de9508f555ef0c3e"

def find_contract_address():
    """트랜잭션에서 컨트랙트 주소 찾기"""
    print("=" * 60)
    print("트랜잭션에서 컨트랙트 주소 찾기")
    print("=" * 60)
    
    # Web3 연결
    w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    if not w3.is_connected():
        print(f"❌ Web3 연결 실패: {settings.WEB3_PROVIDER_URL}")
        return
    
    print(f"✅ Web3 연결 성공")
    print(f"   Provider: {settings.WEB3_PROVIDER_URL}")
    
    try:
        # 트랜잭션 정보 가져오기
        print(f"\n📝 트랜잭션 정보 조회 중...")
        tx = w3.eth.get_transaction(TX_HASH)
        receipt = w3.eth.get_transaction_receipt(TX_HASH)
        
        print(f"   From: {tx['from']}")
        print(f"   To: {tx['to']}")
        print(f"   Status: {receipt.status} (1 = success)")
        print(f"   Logs: {len(receipt.logs)}")
        print(f"   Gas Used: {receipt.gasUsed}")
        
        # 트랜잭션의 'to' 필드 확인
        tx_to = tx['to']
        if tx_to:
            print(f"\n🔍 트랜잭션의 'To' 주소 확인 중...")
            print(f"   Address: {tx_to}")
            
            # 컨트랙트 코드 확인
            code = w3.eth.get_code(tx_to)
            if code == b'' or code == '0x':
                print(f"   ❌ 이 주소는 컨트랙트가 아닙니다 (일반 지갑 주소)")
            else:
                print(f"   ✅ 이 주소는 컨트랙트입니다!")
                print(f"   Code length: {len(code)} bytes")
                print(f"\n📋 Railway 환경 변수:")
                print(f"   NFT_CONTRACT_ADDRESS={tx_to}")
        
        # 로그에서 컨트랙트 주소 찾기
        if receipt.logs:
            print(f"\n🔍 로그에서 컨트랙트 주소 찾기...")
            contract_addresses = set()
            for i, log in enumerate(receipt.logs):
                contract_addresses.add(log.address)
                print(f"   Log {i}: {log.address} ({len(log.topics)} topics)")
            
            if contract_addresses:
                print(f"\n📋 발견된 컨트랙트 주소들:")
                for addr in contract_addresses:
                    code = w3.eth.get_code(addr)
                    is_contract = code != b'' and code != '0x'
                    status = "✅ 컨트랙트" if is_contract else "❌ 지갑 주소"
                    print(f"   {addr} - {status}")
                    
                    if is_contract:
                        print(f"\n📋 Railway 환경 변수 (권장):")
                        print(f"   NFT_CONTRACT_ADDRESS={addr}")
        else:
            print(f"\n⚠️  로그가 없습니다. Transfer 이벤트가 발생하지 않았을 수 있습니다.")
        
        # 트랜잭션 입력 데이터 분석
        print(f"\n🔍 트랜잭션 입력 데이터 분석...")
        input_data = tx.input
        input_hex = input_data.hex() if hasattr(input_data, 'hex') else str(input_data)
        
        if input_hex.startswith('0x675f0173'):
            print(f"   ✅ mintRecipe 함수 호출 감지")
            # mintRecipe(address to, string tokenURI)
            # 함수 시그니처(4 bytes) + to 주소(32 bytes)
            if len(input_hex) >= 74:
                to_address_hex = input_hex[34:74]
                mint_to = Web3.to_checksum_address('0x' + to_address_hex)
                print(f"   민팅 대상 주소: {mint_to}")
        
        print(f"\n" + "=" * 60)
        print(f"📋 Etherscan 링크:")
        print(f"   https://sepolia.etherscan.io/tx/{TX_HASH}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_contract_address()

