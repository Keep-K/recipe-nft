# Railway 환경 변수 설정 가이드

## 현재 문제

Railway의 `NFT_CONTRACT_ADDRESS` 환경 변수가 **지갑 주소**로 설정되어 있습니다:
- ❌ 잘못된 주소: `0x95c76D32c1a898514271ED17C98f9F66606A02Eb` (지갑 주소)
- ✅ 올바른 주소: `0xd5C13269b3e886a1065A2c5Bbd3FC31B14C956F0` (컨트랙트 주소)

## 해결 방법

### 1. Railway 대시보드에서 환경 변수 업데이트

1. Railway 대시보드 접속
2. 프로젝트 선택 → **Variables** 탭
3. `NFT_CONTRACT_ADDRESS` 환경 변수 찾기
4. 값을 다음으로 변경:
   ```
   NFT_CONTRACT_ADDRESS=0xd5C13269b3e886a1065A2c5Bbd3FC31B14C956F0
   ```
5. **Save** 클릭
6. 자동으로 재배포됨

### 2. 컨트랙트 주소 확인

컨트랙트 주소가 맞는지 확인:
```bash
# 로컬에서 실행
cd backend
source .venv/bin/activate
python3 scripts/check_contract.py
```

또는 Etherscan에서 확인:
- https://sepolia.etherscan.io/address/0xd5C13269b3e886a1065A2c5Bbd3FC31B14C956F0#code
- "Contract" 탭에서 컨트랙트 코드가 보여야 함

### 3. 현재 설정된 환경 변수들

**필수 환경 변수:**
- `NFT_CONTRACT_ADDRESS`: NFT 컨트랙트 주소 (✅ `0xd5C13269b3e886a1065A2c5Bbd3FC31B14C956F0`)
- `PRIVATE_KEY`: 민팅에 사용할 지갑의 개인키 (✅ 설정됨)
- `WEB3_PROVIDER_URL`: Alchemy 또는 Infura RPC URL (✅ 설정됨)
- `DATABASE_URL`: PostgreSQL 연결 URL (✅ 설정됨)

**선택적 환경 변수:**
- `PINATA_API_KEY`: IPFS Pinata API 키 (✅ 설정됨)
- `PINATA_SECRET_KEY`: IPFS Pinata Secret 키 (✅ 설정됨)
- `ALLOWED_ORIGINS`: CORS 허용 오리진 (✅ 설정됨)

## 확인 방법

업데이트 후 다음 엔드포인트로 확인:
```
GET https://recipe-nft-production.up.railway.app/api/nft/debug/tx/0x84229f9b17d31f0f36fe5381aaf3ffb413b13666062c91b4de9508f555ef0c3e
```

응답에서 `contract_address_from_env` 필드가 올바른 컨트랙트 주소를 표시해야 합니다.

## 주의사항

⚠️ **중요**: 
- `NFT_CONTRACT_ADDRESS`는 **컨트랙트 주소**여야 합니다 (지갑 주소 아님)
- `PRIVATE_KEY`는 **지갑의 개인키**입니다 (컨트랙트 주소 아님)
- 두 주소는 **다를 수 있습니다**

