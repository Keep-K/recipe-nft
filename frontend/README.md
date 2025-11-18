# Recipe NFT Frontend

레시피 NFT 플랫폼의 프론트엔드 프로토타입입니다.

## 기능

- ✅ 로그인 (지갑 주소 입력 또는 MetaMask 연결)
- ✅ 레시피 작성 (NFT 내용 기입)
- ✅ NFT 민팅 (레시피를 NFT로 업로드)
- ✅ NFT 확인 (트랜잭션 해시 또는 토큰 ID로 검색)

## 시작하기

### 1. 의존성 설치

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
VITE_API_URL=http://localhost:8000
```

### 3. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:5173`으로 접속하세요.

## 프로젝트 구조

```
src/
├── components/          # 재사용 가능한 컴포넌트
│   └── Navbar.jsx      # 네비게이션 바
├── contexts/           # React Context
│   └── AuthContext.jsx # 인증 컨텍스트 (지갑 주소 관리)
├── pages/              # 페이지 컴포넌트
│   ├── Login.jsx       # 로그인 페이지
│   ├── RecipeList.jsx  # 레시피 목록
│   ├── CreateRecipe.jsx # 레시피 작성
│   ├── RecipeDetail.jsx # 레시피 상세
│   ├── MintNFT.jsx     # NFT 민팅
│   └── ViewNFT.jsx     # NFT 확인
├── utils/              # 유틸리티 함수
│   └── api.js          # API 클라이언트
├── App.jsx             # 메인 앱 컴포넌트
└── main.jsx            # 진입점
```

## 주요 기능 설명

### 1. 로그인 (`/login`)
- 지갑 주소 직접 입력
- MetaMask 자동 연결
- 지갑 주소는 localStorage에 저장

### 2. 레시피 작성 (`/recipes/create`)
- 레시피 이름, 재료, 조리 도구, 조리 과정 입력
- 동적으로 항목 추가/삭제 가능
- 백엔드 API로 레시피 생성

### 3. NFT 민팅 (`/recipes/:id/mint`)
- 작성한 레시피를 NFT로 민팅
- IPFS에 메타데이터 업로드
- 블록체인에 트랜잭션 전송

### 4. NFT 확인 (`/nft/view`)
- 트랜잭션 해시로 검색
- 토큰 ID로 검색
- 레시피 내용 및 메타데이터 확인

## API 엔드포인트

프론트엔드는 다음 백엔드 API를 사용합니다:

- `POST /api/recipes/` - 레시피 생성
- `GET /api/recipes/` - 레시피 목록
- `GET /api/recipes/:id` - 레시피 상세
- `POST /api/nft/mint/:recipe_id` - NFT 민팅
- `GET /api/nft/by-tx/:tx_hash` - 트랜잭션으로 레시피 조회
- `GET /api/nft/by-token/:token_id` - 토큰 ID로 레시피 조회

## 다음 단계 (Firebase 연동)

현재는 프로토타입 단계이며, Firebase 연동은 아직 구현되지 않았습니다.

향후 추가 예정:
- Firebase Authentication
- Firebase Firestore
- Firebase Storage
- 실시간 데이터 동기화

## 빌드

프로덕션 빌드:

```bash
npm run build
```

빌드 결과물은 `dist/` 디렉토리에 생성됩니다.

