# 레시피 NFT 프로젝트 작업 계획서

## 프로젝트 개요
음식 레시피를 NFT로 민팅하고 관리하는 플랫폼

## 기술 스택

### 프론트엔드
- React (Create React App)
- Web3.js 또는 Ethers.js (지갑 연동)
- UI 라이브러리 (Material-UI, Tailwind CSS 등)

### 백엔드
- Node.js (Express 또는 NestJS)
- PostgreSQL
- TypeORM 또는 Prisma (ORM)
- JWT (인증)

### 블록체인
- Solidity (스마트 컨트랙트)
- Hardhat 또는 Truffle (개발 환경)
- Web3.js/Ethers.js

### 스토리지
- IPFS (이미지/영상 저장)
- 또는 Arweave

## 데이터베이스 스키마 설계

### users (사용자 정보)
- id (PK)
- wallet_address (지갑 주소, UNIQUE)
- email
- username
- created_at
- updated_at

### recipes (레시피 정보)
- id (PK)
- user_id (FK)
- token_id (NFT 토큰 ID)
- recipe_name (요리 이름)
- ingredients (JSON - 재료 배열)
- cooking_tools (JSON - 조리 도구 배열)
- cooking_steps (JSON - 조리 과정 배열)
- machine_instructions (JSON - 기계 작동 과정, nullable)
- ipfs_hash (메타데이터 IPFS 해시)
- contract_address (스마트 컨트랙트 주소)
- created_at
- updated_at

### recipe_media (레시피 미디어)
- id (PK)
- recipe_id (FK)
- media_type (photo/video)
- ipfs_hash
- file_path
- created_at

### ownership_transfers (소유주 이전 기록)
- id (PK)
- recipe_id (FK)
- from_address
- to_address
- transaction_hash
- block_number
- created_at

### recipe_validation (레시피 교차 검증 데이터)
- id (PK)
- recipe_id (FK)
- validator_address
- validation_score
- validation_comment
- created_at

### monetization_links (파워링크/수익화)
- id (PK)
- recipe_id (FK)
- link_url
- link_type
- revenue_share
- created_at
- updated_at

## 작업 순서

### Phase 1: 프로젝트 초기 설정 (1-2일)
1. **프로젝트 구조 생성**
   - 프론트엔드 디렉토리 (CRA)
   - 백엔드 디렉토리 (Express/NestJS)
   - 스마트 컨트랙트 디렉토리 (Hardhat)

2. **의존성 설치**
   - 프론트엔드: React, Web3 라이브러리, UI 프레임워크
   - 백엔드: Express, TypeORM/Prisma, PostgreSQL 드라이버
   - 스마트 컨트랙트: Hardhat, OpenZeppelin

### Phase 2: 데이터베이스 설계 (1일)
1. **PostgreSQL 스키마 생성**
   - 마이그레이션 파일 작성
   - 관계 설정 (Foreign Keys)
   - 인덱스 추가

2. **ORM 모델 정의**
   - TypeORM 엔티티 또는 Prisma 스키마

### Phase 3: 스마트 컨트랙트 개발 (2-3일)
1. **NFT 컨트랙트 작성**
   - ERC-721 표준 구현
   - 민팅 함수
   - 소유권 전송 함수
   - 메타데이터 URI 관리

2. **컨트랙트 테스트**
   - Hardhat 테스트 작성
   - 로컬 네트워크에서 테스트

3. **배포 스크립트 작성**
   - 테스트넷/메인넷 배포

### Phase 4: 백엔드 API 개발 (3-4일)
1. **인증 API**
   - 회원가입/로그인
   - JWT 토큰 발급
   - 지갑 주소 검증

2. **레시피 API**
   - 레시피 생성 (POST /api/recipes)
   - 레시피 조회 (GET /api/recipes)
   - 레시피 상세 (GET /api/recipes/:id)
   - 레시피 수정 (PUT /api/recipes/:id)
   - 레시피 삭제 (DELETE /api/recipes/:id)

3. **미디어 API**
   - 이미지 업로드 (POST /api/media/upload)
   - IPFS 업로드 처리
   - 미디어 조회

4. **NFT API**
   - NFT 민팅 요청 (POST /api/nft/mint)
   - 소유권 이전 기록 조회
   - NFT 메타데이터 생성

5. **검증 API**
   - 레시피 검증 데이터 저장
   - 검증 점수 조회

6. **수익화 API**
   - 파워링크 생성/수정
   - 수익 데이터 조회

### Phase 5: IPFS 연동 (1일)
1. **IPFS 클라이언트 설정**
   - Pinata 또는 Infura IPFS 사용
   - 또는 자체 IPFS 노드

2. **파일 업로드 함수**
   - 이미지 업로드
   - 영상 업로드
   - 메타데이터 JSON 업로드

### Phase 6: 프론트엔드 개발 (4-5일)
1. **지갑 연동**
   - MetaMask 연결
   - 지갑 주소 표시
   - 네트워크 확인

2. **레시피 입력 폼**
   - 요리 이름 입력
   - 재료 입력 (동적 추가)
   - 조리 도구 입력
   - 조리 과정 입력 (단계별)
   - 기계 작동 과정 입력 (선택)
   - 이미지/영상 업로드

3. **NFT 목록 페이지**
   - 내가 만든 레시피 목록
   - 전체 레시피 목록
   - 필터링/검색 기능

4. **NFT 상세 페이지**
   - 레시피 상세 정보 표시
   - 미디어 갤러리
   - 소유권 정보
   - 소유권 전송 기능
   - 검증 데이터 표시

5. **마이페이지**
   - 내 레시피 관리
   - 소유한 NFT 목록
   - 수익화 링크 관리

### Phase 7: 통합 및 테스트 (2-3일)
1. **전체 플로우 테스트**
   - 레시피 생성 → IPFS 업로드 → NFT 민팅
   - 소유권 전송
   - 검증 데이터 입력

2. **에러 핸들링**
   - 트랜잭션 실패 처리
   - 네트워크 오류 처리
   - 파일 업로드 실패 처리

3. **성능 최적화**
   - 이미지 최적화
   - API 응답 최적화
   - 데이터베이스 쿼리 최적화

### Phase 8: 배포 (1-2일)
1. **스마트 컨트랙트 배포**
   - 테스트넷 배포 및 검증
   - 메인넷 배포 (선택)

2. **백엔드 배포**
   - 서버 환경 설정
   - 환경 변수 설정
   - 데이터베이스 마이그레이션

3. **프론트엔드 배포**
   - Firebase Hosting 또는 다른 호스팅
   - 환경 변수 설정

## 추가 고려사항

### 보안
- 지갑 서명 검증
- SQL Injection 방지
- XSS 방지
- 파일 업로드 검증 (크기, 타입)

### 확장성
- 이미지 CDN 사용 고려
- 데이터베이스 인덱싱
- API 레이트 리미팅
- 캐싱 전략

### 사용자 경험
- 로딩 상태 표시
- 트랜잭션 진행 상태 표시
- 에러 메시지 개선
- 반응형 디자인

### 모니터링
- 로깅 시스템
- 에러 트래킹 (Sentry 등)
- 블록체인 이벤트 모니터링

## 예상 개발 기간
총 **15-20일** (개발자 1명 기준)

