from typing import Optional, Tuple
from web3 import Web3
from web3.types import TxReceipt
from app.config import settings
import json
import os

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
    
    def load_contract_abi(self) -> Optional[list]:
        """컨트랙트 ABI 로드"""
        try:
            abi_path = os.path.join(os.path.dirname(__file__), "..", "contracts", "RecipeNFT.abi.json")
            with open(abi_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load ABI: {e}")
            return None
    
    def mint_nft(self, contract_address: str, to_address: str, token_uri: str) -> Optional[Tuple[int, str]]:
        """
        NFT 민팅
        
        Returns:
            Tuple[token_id, transaction_hash] 또는 None
        """
        if not self.is_connected():
            error_msg = f"Web3 not connected. Provider: {settings.WEB3_PROVIDER_URL}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        if not settings.PRIVATE_KEY:
            error_msg = "PRIVATE_KEY not set in environment"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        if not contract_address:
            error_msg = "NFT_CONTRACT_ADDRESS not set in environment"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        try:
            print(f"📝 Starting NFT mint process...")
            
            # 주소를 체크섬 형식으로 변환
            to_address = Web3.to_checksum_address(to_address)
            contract_address = Web3.to_checksum_address(contract_address)
            
            print(f"   Contract: {contract_address}")
            print(f"   To: {to_address}")
            print(f"   Token URI: {token_uri}")
            
            # ABI 로드
            abi = self.load_contract_abi()
            if not abi:
                error_msg = "Failed to load contract ABI"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            print(f"✅ ABI loaded successfully")
            
            # 컨트랙트 인스턴스 생성
            contract = self.get_contract(contract_address, abi)
            if not contract:
                error_msg = f"Failed to create contract instance for {contract_address}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            print(f"✅ Contract instance created")
            
            # 계정 생성
            account = self.w3.eth.account.from_key(settings.PRIVATE_KEY)
            print(f"✅ Account loaded: {account.address}")
            
            # 잔액 확인
            balance = self.w3.eth.get_balance(account.address)
            balance_eth = self.w3.from_wei(balance, 'ether')
            print(f"💰 Account balance: {balance_eth} ETH ({balance} Wei)")
            
            if balance == 0:
                raise Exception(f"Insufficient balance. Account {account.address} has 0 ETH")
            
            # 민팅 함수 호출 (mintRecipe)
            mint_function = contract.functions.mintRecipe(to_address, token_uri)
            print(f"📤 Building transaction...")
            
            # 트랜잭션 빌드
            nonce = self.w3.eth.get_transaction_count(account.address)
            gas_price = self.w3.eth.gas_price
            print(f"   Nonce: {nonce}, Gas Price: {gas_price} Wei")
            
            # Gas 추정
            try:
                estimated_gas = mint_function.estimate_gas({'from': account.address})
                print(f"   Estimated gas: {estimated_gas}")
            except Exception as gas_err:
                print(f"⚠️  Gas estimation failed: {gas_err}")
                estimated_gas = 200000  # 기본값
            
            transaction = mint_function.build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gasPrice': gas_price,
                'gas': estimated_gas,
            })
            
            print(f"✅ Transaction built")
            
            # 트랜잭션 서명
            signed_txn = self.w3.eth.account.sign_transaction(transaction, settings.PRIVATE_KEY)
            print(f"✅ Transaction signed")
            
            # 트랜잭션 전송
            print(f"📡 Sending transaction...")
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"✅ Transaction sent: {tx_hash.hex()}")
            
            # 트랜잭션 영수증 대기
            print(f"⏳ Waiting for transaction receipt...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            print(f"✅ Transaction confirmed in block {receipt.blockNumber}")
            
            # 이벤트에서 토큰 ID 추출
            # mintRecipe 함수는 토큰 ID를 반환하지만, 트랜잭션 receipt에서는
            # Transfer 이벤트를 통해 tokenId를 추출해야 함
            token_id = None
            zero_address = Web3.to_checksum_address('0x0000000000000000000000000000000000000000')
            
            if receipt.logs:
                # Transfer 이벤트 파싱
                transfer_event = contract.events.Transfer()
                for log in receipt.logs:
                    try:
                        event = transfer_event.process_log(log)
                        # Transfer 이벤트: Transfer(address indexed from, address indexed to, uint256 indexed tokenId)
                        # from이 0x0000...이면 민팅 이벤트
                        from_address = Web3.to_checksum_address(event['args']['from'])
                        if from_address == zero_address:
                            token_id = event['args']['tokenId']
                            break
                    except Exception as e:
                        # 이벤트 파싱 실패 시 다음 로그 시도
                        continue
            
            # 토큰 ID를 찾지 못한 경우 에러
            if token_id is None:
                error_msg = "Failed to extract token ID from Transfer event. Check contract events."
                print(f"❌ {error_msg}")
                print(f"   Receipt logs count: {len(receipt.logs)}")
                for i, log in enumerate(receipt.logs):
                    print(f"   Log {i}: address={log.address}, topics={len(log.topics)}")
                raise Exception(error_msg)
            
            print(f"🎉 NFT minted! Token ID: {token_id}")
            return (token_id, receipt.transactionHash.hex())
            
        except Exception as e:
            error_msg = f"Mint NFT error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            raise  # 예외를 다시 발생시켜서 상위에서 처리하도록
    
    def get_token_id_from_transaction(self, contract_address: str, tx_hash: str) -> Optional[int]:
        """
        트랜잭션 해시에서 토큰 ID 추출
        
        Args:
            contract_address: NFT 컨트랙트 주소
            tx_hash: 트랜잭션 해시
            
        Returns:
            token_id 또는 None
        """
        if not self.is_connected():
            print(f"Web3 not connected. Provider: {settings.WEB3_PROVIDER_URL}")
            return None
        
        try:
            print(f"Fetching transaction receipt for: {tx_hash}")
            # 트랜잭션 영수증 가져오기
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            print(f"Transaction receipt received. Block: {receipt.blockNumber}, Logs: {len(receipt.logs)}")
            
            # ABI 로드
            abi = self.load_contract_abi()
            if not abi:
                print("Failed to load ABI")
                return None
            
            # 컨트랙트 인스턴스 생성
            contract = self.get_contract(contract_address, abi)
            if not contract:
                print(f"Failed to create contract instance for: {contract_address}")
                return None
            
            # Transfer 이벤트에서 토큰 ID 추출
            zero_address = Web3.to_checksum_address('0x0000000000000000000000000000000000000000')
            transfer_event = contract.events.Transfer()
            
            print(f"Checking {len(receipt.logs)} logs for Transfer events...")
            for i, log in enumerate(receipt.logs):
                try:
                    # 로그가 이 컨트랙트에서 발생한 것인지 확인
                    if log.address.lower() != contract_address.lower():
                        continue
                    
                    event = transfer_event.process_log(log)
                    from_address = Web3.to_checksum_address(event['args']['from'])
                    to_address = Web3.to_checksum_address(event['args']['to'])
                    token_id = event['args']['tokenId']
                    
                    print(f"Log {i}: Transfer event found - from: {from_address}, to: {to_address}, tokenId: {token_id}")
                    
                    if from_address == zero_address:
                        print(f"Mint event found! Token ID: {token_id}")
                        return token_id
                except Exception as e:
                    print(f"Error processing log {i}: {e}")
                    continue
            
            print("No mint Transfer event found (from == 0x0000...)")
            return None
            
        except Exception as e:
            print(f"Get token ID from transaction error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_token_id_from_etherscan(self, tx_hash: str, network: str = "sepolia") -> Optional[int]:
        """
        Etherscan API를 사용하여 트랜잭션에서 토큰 ID 추출 (대안 방법)
        
        Args:
            tx_hash: 트랜잭션 해시
            network: 네트워크 (sepolia, mainnet 등)
            
        Returns:
            token_id 또는 None
        """
        try:
            import requests
            
            # Etherscan API 엔드포인트
            if network == "sepolia":
                api_url = f"https://api-sepolia.etherscan.io/api"
            elif network == "mainnet":
                api_url = f"https://api.etherscan.io/api"
            else:
                return None
            
            # 트랜잭션 영수증 가져오기
            params = {
                "module": "proxy",
                "action": "eth_getTransactionReceipt",
                "txhash": tx_hash,
                "apikey": "YourApiKeyToken"  # Etherscan API 키가 있으면 사용
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            if response.status_code != 200:
                return None
            
            data = response.json()
            if data.get("status") != "1" or not data.get("result"):
                return None
            
            receipt = data["result"]
            logs = receipt.get("logs", [])
            
            # Transfer 이벤트 찾기 (topic[0] == Transfer event signature)
            # Transfer(address,address,uint256) = 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
            transfer_event_signature = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
            zero_address = "0x0000000000000000000000000000000000000000"
            
            for log in logs:
                topics = log.get("topics", [])
                if len(topics) >= 4 and topics[0].lower() == transfer_event_signature.lower():
                    # topics[1] = from, topics[2] = to, topics[3] = tokenId
                    from_address = "0x" + topics[1][-40:]  # 마지막 40자리 (주소)
                    token_id_hex = topics[3]
                    
                    if from_address.lower() == zero_address.lower():
                        token_id = int(token_id_hex, 16)
                        return token_id
            
            return None
            
        except Exception as e:
            print(f"Etherscan API error: {e}")
            return None

web3_service = Web3Service()

