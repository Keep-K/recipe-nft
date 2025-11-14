from typing import Optional
from web3 import Web3
from app.config import settings

class Web3Service:
    def __init__(self):
        self.w3 = None
        self._connect()
    
    def _connect(self):
        """Web3 프로바이더 연결"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
            if not self.w3.is_connected():
                print("Web3 connection failed")
                self.w3 = None
        except Exception as e:
            print(f"Web3 connection error: {e}")
            self.w3 = None
    
    def is_connected(self) -> bool:
        """Web3 연결 상태 확인"""
        return self.w3 is not None and self.w3.is_connected()
    
    def get_contract(self, contract_address: str, abi: list):
        """컨트랙트 인스턴스 반환"""
        if not self.is_connected():
            return None
        return self.w3.eth.contract(address=contract_address, abi=abi)
    
    def verify_address(self, address: str) -> bool:
        """지갑 주소 유효성 검증"""
        return Web3.is_address(address)
    
    def get_balance(self, address: str) -> Optional[int]:
        """지갑 잔액 조회 (Wei 단위)"""
        if not self.is_connected():
            return None
        try:
            return self.w3.eth.get_balance(address)
        except Exception as e:
            print(f"Get balance error: {e}")
            return None

web3_service = Web3Service()

