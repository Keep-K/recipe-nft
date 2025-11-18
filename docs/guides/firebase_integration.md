# Firebase 통합 가이드

## 개요

프론트엔드를 Firebase에 연결하고, 백엔드는 Railway에 배포하는 방법입니다.

## 아키텍처

```
Firebase (프론트엔드)
  ├─ Hosting: React 앱 배포
  ├─ Authentication: 사용자 인증
  └─ Storage: 이미지/영상 저장 (선택)

Railway (백엔드)
  ├─ FastAPI: REST API
  └─ PostgreSQL: 데이터베이스
```

## 1단계: Firebase 프로젝트 설정

### 1.1 Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com) 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: `recipe-nft`)
4. Google Analytics 설정 (선택사항)

### 1.2 Authentication 활성화

1. Firebase Console → Authentication
2. "시작하기" 클릭
3. "이메일/비밀번호" 인증 방법 활성화
4. 필요시 소셜 로그인 추가 (Google, GitHub 등)

### 1.3 Hosting 활성화

1. Firebase Console → Hosting
2. "시작하기" 클릭
3. Firebase CLI 설치 안내 확인

### 1.4 Storage 활성화 (선택사항)

1. Firebase Console → Storage
2. "시작하기" 클릭
3. 보안 규칙 설정

## 2단계: Railway PostgreSQL 설정

### 2.1 Railway 프로젝트 생성

1. [Railway](https://railway.app) 접속 및 로그인
2. "New Project" 클릭
3. "Empty Project" 선택

### 2.2 PostgreSQL 추가

1. 프로젝트에서 "+ New" 클릭
2. "Database" → "Add PostgreSQL" 선택
3. PostgreSQL 서비스가 생성됨

### 2.3 데이터베이스 연결 정보 확인

1. PostgreSQL 서비스 클릭
2. "Variables" 탭 확인
3. `DATABASE_URL` 또는 개별 변수 확인:
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

### 2.4 데이터베이스 초기화

Railway PostgreSQL에 접속하여 테이블 생성:

```bash
# Railway CLI 사용 또는
# Railway 대시보드에서 "Connect" 버튼으로 psql 접속

# 또는 백엔드 배포 후 init_db.py 실행
```

## 3단계: 백엔드 Railway 배포

### 3.1 Railway에 백엔드 추가

1. Railway 프로젝트에서 "+ New" 클릭
2. "GitHub Repo" 선택 (또는 "Empty Service")
3. GitHub 저장소 연결

### 3.2 환경 변수 설정

Railway 서비스의 "Variables" 탭에서 설정:

```env
# Database (Railway PostgreSQL 자동 연결)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# 또는 수동 설정
# DATABASE_URL=postgresql://user:password@host:port/dbname

# JWT
SECRET_KEY=your-production-secret-key-here

# Web3
WEB3_PROVIDER_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY
NFT_CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...

# IPFS (Pinata 권장)
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key

# CORS (Firebase 도메인)
ALLOWED_ORIGINS=https://your-app.web.app,https://your-app.firebaseapp.com

# Server
HOST=0.0.0.0
PORT=${{PORT}}
DEBUG=False
```

### 3.3 배포 설정

Railway가 자동으로 감지:
- Python 프로젝트 인식
- `requirements.txt` 자동 설치
- 시작 명령: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3.4 커스텀 도메인 (선택사항)

1. Railway 서비스 → "Settings" → "Networking"
2. "Generate Domain" 클릭
3. 또는 커스텀 도메인 추가

## 4단계: 프론트엔드 Firebase 설정

### 4.1 Firebase SDK 설치

```bash
cd frontend
npm install firebase
```

### 4.2 Firebase 설정 파일 생성

`frontend/src/firebase/config.js`:

```javascript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const storage = getStorage(app);
export default app;
```

### 4.3 환경 변수 설정

`frontend/.env.production`:

```env
VITE_API_URL=https://your-railway-app.railway.app
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

### 4.4 Firebase Hosting 배포

```bash
# Firebase CLI 설치
npm install -g firebase-tools

# Firebase 로그인
firebase login

# 프로젝트 초기화
cd frontend
firebase init

# 빌드
npm run build

# 배포
firebase deploy --only hosting
```

## 5단계: CORS 설정 업데이트

Railway 백엔드의 `main.py`에서 Firebase 도메인 허용:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.web.app",
        "https://your-app.firebaseapp.com",
        "http://localhost:5173",  # 개발 환경
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 비용 비교

### Railway

- **무료 티어**: $5 크레딧/월
- **PostgreSQL**: 약 $5-20/월 (사용량에 따라)
- **FastAPI 서비스**: 약 $5-10/월

### Firebase

- **Hosting**: 무료 (10GB 저장, 360MB/일 전송)
- **Authentication**: 무료 (50,000 MAU까지)
- **Storage**: 무료 (5GB 저장, 1GB/일 다운로드)

## 대안: Firebase Firestore 사용

PostgreSQL 대신 Firebase Firestore를 사용하려면:

1. **백엔드 코드 대폭 수정 필요**
   - SQLAlchemy → Firestore SDK
   - 관계형 모델 → NoSQL 문서 모델
   - 쿼리 로직 전면 수정

2. **장점**
   - Firebase 통합 관리
   - 실시간 동기화
   - 자동 확장

3. **단점**
   - 개발 시간 증가
   - 복잡한 쿼리 제한
   - 관계형 데이터 모델링 어려움

## 권장 사항

**Railway PostgreSQL을 사용하는 것을 권장합니다.**

이유:
- ✅ 현재 코드 구조 그대로 사용
- ✅ 관계형 데이터베이스의 강력한 기능
- ✅ 빠른 배포 가능
- ✅ Firebase는 인증/호스팅에 집중

## 다음 단계

1. Railway PostgreSQL 설정
2. Railway에 백엔드 배포
3. Firebase 프로젝트 생성
4. Firebase Authentication 통합
5. Firebase Hosting에 프론트엔드 배포

