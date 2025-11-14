# 레시피 NFT 민팅 가이드

## NFT화 과정 개요

레시피를 NFT로 만들기 위해서는 다음 단계가 필요합니다:

### 1. 레시피 메타데이터 생성
레시피 정보를 NFT 표준 메타데이터 형식(ERC-721 Metadata)으로 변환

### 2. IPFS에 메타데이터 업로드
메타데이터 JSON을 IPFS에 업로드하여 영구 저장 및 해시 획득

### 3. 스마트 컨트랙트 배포
ERC-721 표준 NFT 컨트랙트를 블록체인에 배포

### 4. NFT 민팅
스마트 컨트랙트의 `mint` 함수를 호출하여 NFT 생성

### 5. DB 업데이트
민팅된 토큰 ID와 IPFS 해시를 레시피 레코드에 저장

## 현재 상태

✅ **완료된 것:**
- 레시피 데이터 저장 (DB)
- IPFS 서비스 기본 구조
- Web3 서비스 기본 구조
- Recipe 모델에 NFT 관련 필드 준비됨 (token_id, ipfs_hash, contract_address, is_minted)

❌ **아직 구현 안 된 것:**
- NFT 민팅 API 엔드포인트
- 메타데이터 JSON 생성 로직
- 스마트 컨트랙트 작성 및 배포
- 실제 IPFS 업로드 연동
- Web3를 통한 민팅 트랜잭션 전송

## 다음 단계

1. **메타데이터 생성 함수 구현**
2. **NFT 민팅 API 엔드포인트 추가** (`POST /api/nft/mint/{recipe_id}`)
3. **스마트 컨트랙트 작성** (Solidity, ERC-721)
4. **IPFS 실제 연동** (Pinata 또는 로컬 IPFS 노드)
5. **민팅 플로우 통합**

