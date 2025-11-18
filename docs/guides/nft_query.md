# NFT 레시피 조회 가이드

민팅된 NFT 레시피를 조회하는 여러 가지 방법을 안내합니다.

## 방법 1: 트랜잭션 해시로 조회 (가장 간단)

Etherscan에서 본 트랜잭션 해시를 사용하여 레시피를 조회할 수 있습니다.

### API 엔드포인트

```
GET /api/nft/by-tx/{tx_hash}
```

### 사용 예시

```bash
# 트랜잭션 해시만 사용 (환경 변수의 컨트랙트 주소 사용)
curl http://localhost:8000/api/nft/by-tx/0x696913f78b42613213e709429b3ab39c9f3231986565bbb76a59266ffdff5de4

# 특정 컨트랙트 주소 지정
curl "http://localhost:8000/api/nft/by-tx/0x696913f78b42613213e709429b3ab39c9f3231986565bbb76a59266ffdff5de4?contract_address=0x..."
```

### 브라우저에서 확인

```
http://localhost:8000/api/nft/by-tx/0x696913f78b42613213e709429b3ab39c9f3231986565bbb76a59266ffdff5de4
```

### Swagger UI에서 확인

1. `http://localhost:8000/docs` 접속
2. `/api/nft/by-tx/{tx_hash}` 엔드포인트 찾기
3. `tx_hash`에 트랜잭션 해시 입력: `0x696913f78b42613213e709429b3ab39c9f3231986565bbb76a59266ffdff5de4`
4. "Try it out" → "Execute"

---

## 방법 2: 토큰 ID로 조회

Etherscan에서 토큰 ID를 확인한 후 조회할 수 있습니다.

### Etherscan에서 토큰 ID 확인

1. 트랜잭션 페이지에서 "Logs" 탭 클릭
2. `Transfer` 이벤트에서 `tokenId` 값 확인
3. 또는 "Token ID" 필드 확인

### API 엔드포인트

```
GET /api/nft/by-token/{token_id}
```

### 사용 예시

```bash
# 토큰 ID만 사용
curl http://localhost:8000/api/nft/by-token/0

# 특정 컨트랙트 주소 지정
curl "http://localhost:8000/api/nft/by-token/0?contract_address=0x..."
```

---

## 방법 3: 레시피 ID로 조회

레시피를 생성할 때 받은 레시피 ID를 사용합니다.

### API 엔드포인트

```
GET /api/recipes/{recipe_id}
```

### 사용 예시

```bash
curl http://localhost:8000/api/recipes/1
```

---

## 방법 4: NFT 메타데이터 조회

IPFS에 저장된 NFT 메타데이터를 직접 조회합니다.

### API 엔드포인트

```
GET /api/nft/metadata/{recipe_id}
```

### 사용 예시

```bash
curl http://localhost:8000/api/nft/metadata/1
```

### 응답 예시

```json
{
  "recipe_id": 1,
  "token_id": 0,
  "contract_address": "0x...",
  "ipfs_hash": "Qm...",
  "metadata": {
    "name": "김치찌개",
    "description": "Recipe NFT: 김치찌개",
    "attributes": [...],
    "properties": {
      "ingredients": [...],
      "cooking_steps": [...]
    }
  },
  "metadata_uri": "ipfs://Qm..."
}
```

---

## 방법 5: 민팅된 레시피 목록 조회

모든 민팅된 레시피를 한 번에 조회합니다.

### API 엔드포인트

```
GET /api/recipes?is_minted=true
```

### 사용 예시

```bash
curl "http://localhost:8000/api/recipes?is_minted=true"
```

---

## Etherscan에서 직접 확인

### 1. 트랜잭션 확인

1. https://sepolia.etherscan.io/tx/0x696913f78b42613213e709429b3ab39c9f3231986565bbb76a59266ffdff5de4 접속
2. "Logs" 탭에서 `Transfer` 이벤트 확인
3. `tokenId` 값 확인

### 2. 컨트랙트에서 토큰 확인

1. 컨트랙트 주소로 이동
2. "Read Contract" 탭
3. `tokenURI(tokenId)` 함수에 토큰 ID 입력
4. IPFS 해시 확인 (예: `ipfs://Qm...`)
5. IPFS 게이트웨이에서 메타데이터 확인:
   - https://ipfs.io/ipfs/Qm...
   - https://gateway.pinata.cloud/ipfs/Qm...

---

## 문제 해결

### "Could not extract token_id from transaction" 오류

- 트랜잭션이 아직 블록에 포함되지 않았을 수 있습니다. 몇 분 후 다시 시도하세요.
- Web3 프로바이더가 올바르게 설정되었는지 확인하세요.
- 컨트랙트 주소가 올바른지 확인하세요.

### "Recipe not found" 오류

- 레시피가 데이터베이스에 저장되었는지 확인하세요.
- 민팅이 완료되었는지 확인하세요 (`is_minted = true`).
- 토큰 ID와 컨트랙트 주소가 일치하는지 확인하세요.

### Web3 연결 오류

- `.env` 파일의 `WEB3_PROVIDER_URL`이 올바른지 확인하세요.
- Sepolia 테스트넷의 경우: `https://sepolia.infura.io/v3/YOUR_KEY` 또는 `https://rpc.sepolia.org`

---

## 빠른 테스트

트랜잭션 해시로 바로 확인:

```bash
# 서버가 실행 중이어야 합니다
curl http://localhost:8000/api/nft/by-tx/0x696913f78b42613213e709429b3ab39c9f3231986565bbb76a59266ffdff5de4
```

성공하면 레시피 정보가 JSON 형식으로 반환됩니다!

