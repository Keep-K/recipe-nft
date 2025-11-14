# Recipe NFT Platform

음식 레시피를 NFT로 민팅하고 관리하는 플랫폼

## 프로젝트 구조

```
recipe-nft/
├── backend/          # FastAPI 백엔드
├── frontend/         # Vite + React 프론트엔드
└── docs/             # 프로젝트 문서
    ├── planning/     # 프로젝트 계획서
    ├── guides/       # 개발 가이드
    ├── api/          # API 문서
    └── deployment/   # 배포 문서
```

자세한 문서는 [docs/](./docs/) 폴더를 참고하세요.

## 기술 스택

### 백엔드
- FastAPI
- PostgreSQL
- SQLAlchemy
- Web3.py
- IPFS

### 프론트엔드
- Vite + React
- Ethers.js (Web3)
- React Router
- Axios

## 시작하기

### 백엔드 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# .env 파일 생성 (backend/.env.example 참고)
cp .env.example .env
# .env 파일 수정

# 서버 실행
python main.py
# 또는
uvicorn main:app --reload
```

### 프론트엔드 설정

```bash
cd frontend
npm install
npm run dev
```

## 개발 환경

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

## 배포 예정

- 백엔드: Railway
- 프론트엔드: Firebase Hosting

# recipe-nft
