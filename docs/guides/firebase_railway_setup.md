# Firebase + Railway 배포 가이드

## 아키텍처 선택

### 옵션 1: Railway PostgreSQL 사용 (권장) ✅

**구조:**
- **프론트엔드**: Firebase Hosting
- **백엔드**: Railway (FastAPI)
- **데이터베이스**: Railway PostgreSQL
- **인증**: Firebase Authentication
- **스토리지**: Firebase Storage (이미지/영상)

**장점:**
- ✅ 현재 코드 구조 그대로 사용 가능
- ✅ 관계형 데이터베이스의 강력한 기능 (JOIN, 트랜잭션 등)
- ✅ SQLAlchemy ORM 그대로 사용
- ✅ 복잡한 쿼리 가능
- ✅ 데이터 무결성 보장

**단점:**
- ❌ PostgreSQL 관리 필요
- ❌ 비용 (Railway 무료 티어 제한)

### 옵션 2: Firebase Firestore 사용

**구조:**
- **프론트엔드**: Firebase Hosting
- **백엔드**: Railway (FastAPI) 또는 Firebase Functions
- **데이터베이스**: Firebase Firestore (NoSQL)
- **인증**: Firebase Authentication
- **스토리지**: Firebase Storage

**장점:**
- ✅ Firebase 통합 관리
- ✅ 실시간 동기화
- ✅ 자동 확장

**단점:**
- ❌ 코드 대폭 수정 필요 (SQLAlchemy → Firestore)
- ❌ 복잡한 쿼리 제한
- ❌ 관계형 데이터 모델링 어려움

## 권장: Railway PostgreSQL 사용

현재 프로젝트 구조를 유지하면서 Firebase와 통합하는 것이 가장 효율적입니다.

## Railway PostgreSQL 설정

### 1. Railway에서 PostgreSQL 추가

1. [Railway 대시보드](https://railway.app) 접속
2. 새 프로젝트 생성
3. "New" → "Database" → "Add PostgreSQL" 선택
4. PostgreSQL 서비스가 생성되면 자동으로 환경 변수가 설정됨

### 2. 환경 변수 확인

Railway PostgreSQL 서비스의 "Variables" 탭에서 다음 변수 확인:
- `DATABASE_URL` (자동 생성됨)
- 또는 `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

### 3. 백엔드 배포

Railway에서 FastAPI 백엔드를 배포할 때:
- `DATABASE_URL` 환경 변수를 Railway PostgreSQL의 연결 문자열로 설정
- 다른 환경 변수들도 설정

## Firebase 설정

### 1. Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com) 접속
2. 새 프로젝트 생성
3. Authentication 활성화
4. Hosting 활성화
5. Storage 활성화 (선택사항)

### 2. Firebase Authentication 설정

- 이메일/비밀번호 인증 활성화
- 또는 소셜 로그인 (Google, GitHub 등)

### 3. Firebase Hosting 설정

프론트엔드를 Firebase Hosting에 배포

## 하이브리드 아키텍처 (권장)

```
┌─────────────────┐
│  Firebase       │
│  - Hosting      │  ← 프론트엔드 (React)
│  - Auth         │  ← 사용자 인증
│  - Storage      │  ← 이미지/영상 (선택)
└─────────────────┘
         │
         │ API 호출
         ▼
┌─────────────────┐
│  Railway        │
│  - FastAPI      │  ← 백엔드 API
│  - PostgreSQL   │  ← 데이터베이스
└─────────────────┘
```

## 환경 변수 설정

### Railway (백엔드)

```env
# Database (Railway PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT
SECRET_KEY=your-production-secret-key

# Web3
WEB3_PROVIDER_URL=https://eth-sepolia.g.alchemy.com/v2/...
NFT_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...

# IPFS (Pinata 권장)
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key

# CORS
ALLOWED_ORIGINS=https://your-firebase-app.web.app,https://your-firebase-app.firebaseapp.com
```

### Firebase (프론트엔드)

```env
# .env.production
VITE_API_URL=https://your-railway-app.railway.app
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
```

## 결론

**Railway에서 PostgreSQL을 사용하는 것을 권장합니다.**

이유:
1. 현재 코드 구조 그대로 사용 가능
2. 관계형 데이터베이스의 강력한 기능 활용
3. SQLAlchemy ORM 유지
4. Firebase는 인증/호스팅에 집중

Firebase Firestore로 전환하려면 백엔드 코드를 대폭 수정해야 하므로, PostgreSQL을 유지하는 것이 효율적입니다.

