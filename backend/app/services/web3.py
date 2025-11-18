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
            
            # 컨트랙트 코드 확인 (컨트랙트가 실제로 배포되었는지)
            try:
                code = self.w3.eth.get_code(contract_address)
                if code == b'' or code == '0x':
                    error_msg = f"No contract code found at address {contract_address}. This address is NOT a contract!"
                    print(f"❌ {error_msg}")
                    raise Exception(error_msg)
                else:
                    print(f"✅ Contract code verified (length: {len(code)} bytes)")
            except Exception as e:
                if "NOT a contract" in str(e):
                    raise
                print(f"⚠️  Warning: Could not verify contract code: {e}")
            
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
            
            # 트랜잭션 전에 call로 반환값 확인 (토큰 ID 미리 얻기)
            expected_token_id = None
            try:
                print(f"   Pre-calling mintRecipe to get expected token ID...")
                expected_token_id = mint_function.call({'from': account.address})
                print(f"   Expected token ID from call: {expected_token_id}")
            except Exception as e:
                print(f"   Could not pre-call mintRecipe (this is normal): {e}")
            
            # 트랜잭션 전에 balanceOf 확인 (최신 토큰 ID 찾기용)
            balance_before = 0
            try:
                balance_before = contract.functions.balanceOf(to_address).call()
                print(f"   Balance before mint: {balance_before}")
            except Exception as e:
                print(f"   Could not get balance before mint: {e}")
            
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
            
            # 트랜잭션 상태 확인
            if receipt.status != 1:
                error_msg = f"Transaction failed with status {receipt.status}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            print(f"✅ Transaction status: {receipt.status} (1 = success)")
            print(f"   Gas used: {receipt.gasUsed} / {transaction['gas']}")
            print(f"   Logs count: {len(receipt.logs)}")
            print(f"🔍 Analyzing {len(receipt.logs)} logs for Transfer events...")
            
            # 트랜잭션이 실제로 성공했는지 확인 (gasUsed가 0이면 revert)
            if receipt.gasUsed == transaction['gas']:
                print(f"⚠️  Warning: All gas was used, transaction might have reverted")
            
            # 토큰 ID 추출 시도
            token_id = None
            
            # 방법 0: 트랜잭션 반환값 확인 시도
            try:
                tx_result = self.w3.eth.call({
                    'to': contract_address,
                    'data': transaction['data'],
                    'from': account.address,
                }, receipt.blockNumber - 1)  # 이전 블록에서 call
                
                if tx_result and len(tx_result) > 0:
                    # 반환값 디코딩 (uint256)
                    decoded_result = int.from_bytes(tx_result, byteorder='big')
                    print(f"   Transaction return value (from call): {decoded_result}")
                    if decoded_result > 0:
                        token_id = decoded_result
                        print(f"✅ Using transaction return value: Token ID = {token_id}")
            except Exception as e:
                print(f"   Could not decode transaction return value: {e}")
            
            # 방법 1: 이벤트에서 토큰 ID 추출
            zero_address = Web3.to_checksum_address('0x0000000000000000000000000000000000000000')
            
            if receipt.logs:
                # Transfer 이벤트 파싱
                transfer_event = contract.events.Transfer()
                contract_address_lower = contract_address.lower()
                
                for i, log in enumerate(receipt.logs):
                    try:
                        # 로그가 이 컨트랙트에서 발생한 것인지 확인
                        if log.address.lower() != contract_address_lower:
                            print(f"   Log {i}: Skipping (different contract: {log.address})")
                            continue
                        
                        print(f"   Log {i}: Processing Transfer event from contract {log.address}")
                        event = transfer_event.process_log(log)
                        
                        # Transfer 이벤트: Transfer(address indexed from, address indexed to, uint256 indexed tokenId)
                        # from이 0x0000...이면 민팅 이벤트
                        from_address = Web3.to_checksum_address(event['args']['from'])
                        to_address = Web3.to_checksum_address(event['args']['to'])
                        potential_token_id = event['args']['tokenId']
                        
                        print(f"      From: {from_address}, To: {to_address}, TokenID: {potential_token_id}")
                        
                        if from_address == zero_address:
                            token_id = potential_token_id
                            print(f"✅ Found mint Transfer event! Token ID: {token_id}")
                            break
                    except Exception as e:
                        # 이벤트 파싱 실패 시 다음 로그 시도
                        print(f"   Log {i}: Failed to parse Transfer event: {e}")
                        continue
            
            # 토큰 ID를 찾지 못한 경우 대안 방법 시도
            if token_id is None:
                print(f"⚠️  Token ID not found in Transfer events (logs: {len(receipt.logs)}). Trying alternative methods...")
                
                # 방법 0: 예상 토큰 ID 사용 (call로 미리 얻은 값)
                if expected_token_id is not None:
                    try:
                        # 예상 토큰 ID가 실제로 해당 주소에 속하는지 확인
                        owner = contract.functions.ownerOf(expected_token_id).call()
                        if owner.lower() == to_address.lower():
                            token_id = expected_token_id
                            print(f"✅ Using pre-call token ID: {token_id}")
                    except Exception as e:
                        print(f"   Pre-call token ID verification failed: {e}")
                
                # 방법 1: balanceOf를 사용하여 최신 토큰 ID 찾기
                try:
                    print(f"   Method 1: Using balanceOf to find latest token...")
                    # 블록이 확정될 때까지 잠시 대기
                    import time
                    time.sleep(2)  # 2초 대기
                    
                    balance_after = contract.functions.balanceOf(to_address).call()
                    print(f"      Balance before: {balance_before}, Balance after: {balance_after}")
                    
                    if balance_after > balance_before:
                        # balance가 증가했다면, 새로 민팅된 토큰을 찾아야 함
                        print(f"      Balance increased! Searching for new token...")
                        
                        # 효율적인 검색: 작은 범위부터 시작
                        # 일반적으로 토큰 ID는 순차적으로 증가하므로, 0부터 시작
                        max_search = 1000  # 최대 1000개까지 검색
                        found_tokens = []
                        
                        # 순차적으로 검색하여 to_address가 소유한 모든 토큰 찾기
                        for check_id in range(max_search):
                            try:
                                owner = contract.functions.ownerOf(check_id).call()
                                if owner.lower() == to_address.lower():
                                    found_tokens.append(check_id)
                                    print(f"      Found token {check_id} owned by {to_address}")
                                    # balance_after만큼 찾았으면 중단
                                    if len(found_tokens) >= balance_after:
                                        break
                            except Exception:
                                # 토큰이 존재하지 않으면 계속
                                continue
                        
                        if found_tokens:
                            # balance_before 이후의 토큰만 필터링 (새로 민팅된 것)
                            new_tokens = found_tokens[balance_before:]
                            if new_tokens:
                                # 가장 큰 토큰 ID가 최신일 가능성이 높음
                                token_id = max(new_tokens)
                                print(f"✅ Using balanceOf method: New Token ID = {token_id}")
                            else:
                                # 모든 토큰이 새 것일 수도 있음
                                token_id = max(found_tokens)
                                print(f"✅ Using balanceOf method (fallback): Latest Token ID = {token_id}")
                        else:
                            print(f"      Could not find any tokens owned by {to_address}")
                    elif balance_after > 0:
                        # balance가 증가하지 않았지만 0보다 크면, 기존 토큰 중 최신 것 사용
                        print(f"      Balance did not increase, but balance > 0. Searching...")
                        # 위와 동일한 검색 로직
                        for check_id in range(1000):
                            try:
                                owner = contract.functions.ownerOf(check_id).call()
                                if owner.lower() == to_address.lower():
                                    found_tokens.append(check_id)
                                    if len(found_tokens) >= balance_after:
                                        break
                            except Exception:
                                continue
                        
                        if found_tokens:
                            token_id = max(found_tokens)
                            print(f"✅ Using balanceOf fallback: Latest Token ID = {token_id}")
                    else:
                        print(f"      Balance is 0, cannot determine token ID")
                except Exception as e:
                    print(f"   balanceOf method failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 방법 2: 트랜잭션 반환값 디코딩 시도 (일반적으로 불가능하지만 시도)
                if token_id is None:
                    try:
                        print(f"   Method 2: Attempting to decode transaction return value...")
                        # 트랜잭션 반환값은 receipt에 없으므로, 트랜잭션을 다시 call로 실행
                        # 하지만 이미 실행된 트랜잭션이므로 이 방법은 작동하지 않음
                        # 대신 트랜잭션 데이터를 디코딩하여 확인
                        tx = self.w3.eth.get_transaction(tx_hash)
                        print(f"      Transaction data length: {len(tx.input)}")
                    except Exception as e:
                        print(f"   Transaction decoding failed: {e}")
                
                # 방법 3: 모든 로그를 자세히 출력
                if token_id is None and receipt.logs:
                    print(f"   Method 3: Detailed log analysis:")
                    for i, log in enumerate(receipt.logs):
                        print(f"      Log {i}:")
                        print(f"         Address: {log.address}")
                        print(f"         Topics: {[t.hex() if hasattr(t, 'hex') else str(t) for t in log.topics]}")
                        print(f"         Data: {log.data.hex() if hasattr(log.data, 'hex') else str(log.data)}")
                elif token_id is None:
                    print(f"   ⚠️  No logs found in transaction receipt!")
                    print(f"      This might indicate:")
                    print(f"      1. Contract doesn't emit Transfer events")
                    print(f"      2. Transaction reverted silently")
                    print(f"      3. Contract address or ABI mismatch")
            
            # 여전히 토큰 ID를 찾지 못한 경우, 트랜잭션이 실제로 성공했는지 확인
            if token_id is None:
                # 트랜잭션이 실제로 revert되었는지 확인
                try:
                    # 트랜잭션을 다시 call하여 확인
                    print(f"   Verifying transaction actually succeeded...")
                    call_result = mint_function.call({'from': account.address})
                    if call_result is not None:
                        token_id = call_result
                        print(f"✅ Using call result after transaction: Token ID = {token_id}")
                except Exception as e:
                    print(f"   Call verification failed: {e}")
            
            # 여전히 토큰 ID를 찾지 못한 경우 에러
            if token_id is None:
                # 컨트랙트 코드 재확인
                contract_code_issue = ""
                try:
                    code = self.w3.eth.get_code(contract_address)
                    if code == b'' or code == '0x':
                        contract_code_issue = f" CRITICAL: No contract code at {contract_address} - this is NOT a contract!"
                except Exception:
                    pass
                
                error_msg = (
                    f"Failed to extract token ID. "
                    f"Transaction hash: {receipt.transactionHash.hex()}, "
                    f"Logs: {len(receipt.logs)}, "
                    f"Status: {receipt.status}, "
                    f"Gas used: {receipt.gasUsed}.{contract_code_issue} "
                    f"Possible issues: 1) Contract address is incorrect ({contract_address}), "
                    f"2) Contract is not deployed on Sepolia, "
                    f"3) Contract does not emit Transfer events, "
                    f"4) Transaction did not actually mint an NFT, "
                    f"5) Contract ABI does not match deployed contract. "
                    f"View transaction: https://sepolia.etherscan.io/tx/{receipt.transactionHash.hex()}"
                )
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            print(f"🎉 NFT minted! Token ID: {token_id}")
            return (token_id, receipt.transactionHash.hex())
            
        except Exception as e:
            error_msg = f"Mint NFT error: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            raise  # 예외를 다시 발생시켜서 상위에서 처리하도록
    
    def get_contract_address_from_transaction(self, tx_hash: str) -> Optional[str]:
        """
        트랜잭션 해시에서 컨트랙트 주소 추출
        
        Args:
            tx_hash: 트랜잭션 해시
            
        Returns:
            컨트랙트 주소 또는 None
        """
        if not self.is_connected():
            return None
        
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            # 트랜잭션의 'to' 필드가 컨트랙트 주소
            if tx['to']:
                return Web3.to_checksum_address(tx['to'])
            return None
        except Exception as e:
            print(f"Get contract address from transaction error: {e}")
            return None
    
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
            print(f"🔍 Fetching transaction receipt for: {tx_hash}")
            # 트랜잭션 영수증 가져오기
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            print(f"✅ Transaction receipt received. Block: {receipt.blockNumber}, Status: {receipt.status}, Logs: {len(receipt.logs)}")
            
            # 트랜잭션 상태 확인
            if receipt.status != 1:
                print(f"❌ Transaction failed with status {receipt.status}")
                return None
            
            # 트랜잭션 정보 가져오기
            tx = self.w3.eth.get_transaction(tx_hash)
            print(f"   Transaction from: {tx['from']}, to: {tx['to']}")
            
            # ABI 로드
            abi = self.load_contract_abi()
            if not abi:
                print("❌ Failed to load ABI")
                return None
            
            # 컨트랙트 인스턴스 생성
            contract_address = Web3.to_checksum_address(contract_address)
            contract = self.get_contract(contract_address, abi)
            if not contract:
                print(f"❌ Failed to create contract instance for: {contract_address}")
                return None
            
            # 컨트랙트 코드 확인 (컨트랙트가 실제로 배포되었는지)
            try:
                code = self.w3.eth.get_code(contract_address)
                if code == b'' or code == '0x':
                    print(f"⚠️  Warning: No contract code found at address {contract_address}")
                    print(f"   This address might not be a contract or contract is not deployed")
            except Exception as e:
                print(f"⚠️  Warning: Could not verify contract code: {e}")
            
            # 방법 1: Transfer 이벤트에서 토큰 ID 추출
            zero_address = Web3.to_checksum_address('0x0000000000000000000000000000000000000000')
            transfer_event = contract.events.Transfer()
            
            print(f"🔍 Checking {len(receipt.logs)} logs for Transfer events...")
            token_id = None
            mint_to_address = None
            
            for i, log in enumerate(receipt.logs):
                try:
                    # 로그가 이 컨트랙트에서 발생한 것인지 확인
                    if log.address.lower() != contract_address.lower():
                        print(f"   Log {i}: Skipping (different contract: {log.address})")
                        continue
                    
                    event = transfer_event.process_log(log)
                    from_address = Web3.to_checksum_address(event['args']['from'])
                    to_address = Web3.to_checksum_address(event['args']['to'])
                    potential_token_id = event['args']['tokenId']
                    
                    print(f"   Log {i}: Transfer event - from: {from_address}, to: {to_address}, tokenId: {potential_token_id}")
                    
                    if from_address == zero_address:
                        token_id = potential_token_id
                        mint_to_address = to_address
                        print(f"✅ Found mint Transfer event! Token ID: {token_id}, To: {mint_to_address}")
                        break
                except Exception as e:
                    print(f"   Log {i}: Failed to parse Transfer event: {e}")
                    continue
            
            # 방법 2: Transfer 이벤트가 없을 때 balanceOf 사용
            if token_id is None:
                print(f"⚠️  No mint Transfer event found. Trying balanceOf method...")
                
                # 트랜잭션 입력 데이터에서 민팅 대상 주소 추출 시도
                mint_to_address = None
                try:
                    # tx.input은 HexBytes이거나 문자열일 수 있음
                    input_hex = tx.input.hex() if hasattr(tx.input, 'hex') else str(tx.input)
                    
                    # mintRecipe 함수 시그니처: 0x675f0173
                    if input_hex.startswith('0x675f0173') and len(input_hex) >= 138:
                        # mintRecipe(address to, string tokenURI)
                        # 함수 시그니처(4 bytes) + to 주소(32 bytes, 패딩 포함)
                        to_address_hex = input_hex[34:74]  # 0x prefix 제거 후 34-74 (20 bytes = 40 hex chars)
                        mint_to_address = Web3.to_checksum_address('0x' + to_address_hex)
                        print(f"   Extracted mint target from input data: {mint_to_address}")
                except Exception as e:
                    print(f"   Failed to extract mint target from input: {e}")
                
                # 입력 데이터에서 추출 실패 시 트랜잭션 정보 사용
                if not mint_to_address:
                    tx_to = tx['to']
                    if tx_to and tx_to.lower() == contract_address.lower():
                        # 컨트랙트에 직접 호출한 경우, 발신자가 민팅 대상일 가능성이 높음
                        mint_to_address = Web3.to_checksum_address(tx['from'])
                        print(f"   Transaction to contract. Assuming mint to: {mint_to_address}")
                    else:
                        # 'to' 주소가 민팅 대상일 수 있음
                        mint_to_address = Web3.to_checksum_address(tx_to) if tx_to else None
                        print(f"   Transaction to: {mint_to_address}")
                
                if mint_to_address:
                    try:
                        import time
                        time.sleep(2)  # 블록 확정 대기
                        
                        # balanceOf로 소유한 토큰 찾기
                        balance = contract.functions.balanceOf(mint_to_address).call()
                        print(f"   Balance of {mint_to_address}: {balance}")
                        
                        if balance > 0:
                            # 소유한 모든 토큰 찾기
                            max_search = 1000
                            found_tokens = []
                            
                            for check_id in range(max_search):
                                try:
                                    owner = contract.functions.ownerOf(check_id).call()
                                    if owner.lower() == mint_to_address.lower():
                                        found_tokens.append(check_id)
                                        if len(found_tokens) >= balance:
                                            break
                                except Exception:
                                    continue
                            
                            if found_tokens:
                                # 가장 큰 토큰 ID가 최신일 가능성이 높음
                                token_id = max(found_tokens)
                                print(f"✅ Using balanceOf method: Token ID = {token_id}")
                            else:
                                print(f"   Could not find any tokens owned by {mint_to_address}")
                        else:
                            print(f"   Balance is 0, cannot determine token ID")
                    except Exception as e:
                        print(f"   balanceOf method failed: {e}")
                        import traceback
                        traceback.print_exc()
            
            # 방법 3: 트랜잭션 입력 데이터 디코딩 시도
            if token_id is None:
                print(f"⚠️  Trying to decode transaction input data...")
                try:
                    # tx.input은 HexBytes이거나 문자열일 수 있음
                    input_hex = tx.input.hex() if hasattr(tx.input, 'hex') else str(tx.input)
                    
                    # mintRecipe 함수 시그니처: 0x675f0173
                    if input_hex.startswith('0x675f0173'):
                        print(f"   Transaction is mintRecipe call")
                        # to 주소는 input[4:68]에 있음 (32 bytes, 패딩 포함)
                        # 하지만 토큰 ID는 반환값이므로 입력에서 알 수 없음
                        print(f"   Cannot extract token ID from input data (it's a return value)")
                except Exception as e:
                    print(f"   Input decoding failed: {e}")
            
            # 방법 4: 모든 로그 상세 출력
            if token_id is None and receipt.logs:
                print(f"⚠️  Detailed log analysis:")
                for i, log in enumerate(receipt.logs):
                    print(f"   Log {i}:")
                    print(f"      Address: {log.address}")
                    print(f"      Topics: {[t.hex() if hasattr(t, 'hex') else str(t) for t in log.topics]}")
                    print(f"      Data: {log.data.hex() if hasattr(log.data, 'hex') else str(log.data)}")
            
            if token_id is None:
                print(f"❌ Could not extract token ID from transaction")
                print(f"   Transaction: https://sepolia.etherscan.io/tx/{tx_hash}")
                print(f"   Possible issues:")
                print(f"   1. Contract address might be incorrect: {contract_address}")
                print(f"   2. Contract might not be deployed on Sepolia")
                print(f"   3. Contract might not emit Transfer events")
                print(f"   4. Transaction might not have actually minted an NFT")
                print(f"   5. Contract ABI might not match the deployed contract")
                
                # 컨트랙트 코드 확인
                try:
                    code = self.w3.eth.get_code(contract_address)
                    if code == b'' or code == '0x':
                        print(f"   ⚠️  CRITICAL: No contract code found at {contract_address}")
                        print(f"      This address is NOT a contract!")
                    else:
                        print(f"   ✅ Contract code found (length: {len(code)} bytes)")
                except Exception as e:
                    print(f"   ⚠️  Could not verify contract code: {e}")
                
                return None
            
            return token_id
            
        except Exception as e:
            print(f"❌ Get token ID from transaction error: {e}")
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

