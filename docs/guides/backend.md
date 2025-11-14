# Backend API

FastAPI 기반 레시피 NFT 백엔드 서버

## 프로젝트 구조

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # 설정 관리
│   ├── database.py        # 데이터베이스 연결
│   ├── models.py          # SQLAlchemy 모델
│   ├── schemas.py         # Pydantic 스키마
│   ├── routers/           # API 라우터
│   │   ├── recipes.py     # 레시피 API
│   │   ├── users.py       # 사용자 API
│   │   └── media.py       # 미디어 업로드 API
│   └── services/          # 서비스 레이어
│       ├── ipfs.py        # IPFS 연동
│       └── web3.py        # Web3 연동
├── main.py                # FastAPI 앱 진입점
├── init_db.py            # 데이터베이스 초기화
├── requirements.txt      # Python 의존성
└── .env.example          # 환경 변수 예제
```

## 설치

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값 입력
```

주요 환경 변수:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `SECRET_KEY`: JWT 서명용 시크릿 키
- `IPFS_HOST`, `IPFS_PORT`: IPFS 노드 주소
- `WEB3_PROVIDER_URL`: 블록체인 프로바이더 URL

## 데이터베이스 설정

### PostgreSQL 설치 및 데이터베이스 생성

```bash
# PostgreSQL 설치 (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib

# 데이터베이스 생성
sudo -u postgres psql
CREATE DATABASE recipe_nft_db;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE recipe_nft_db TO your_user;
\q
```

### 데이터베이스 테이블 생성

```bash
python init_db.py
```

또는 Alembic을 사용한 마이그레이션:

```bash
# Alembic 초기화 (처음 한 번만)
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

## 실행

```bash
python main.py
# 또는
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 문서

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 주요 API 엔드포인트

### 레시피 (Recipes)
- `POST /api/recipes` - 레시피 생성
- `GET /api/recipes` - 레시피 목록 조회
- `GET /api/recipes/{id}` - 레시피 상세 조회
- `PUT /api/recipes/{id}` - 레시피 수정
- `DELETE /api/recipes/{id}` - 레시피 삭제
- `GET /api/recipes/{id}/media` - 레시피 미디어 조회

### 사용자 (Users)
- `POST /api/users` - 사용자 생성
- `GET /api/users/{wallet_address}` - 사용자 조회
- `GET /api/users/{wallet_address}/recipes` - 사용자 레시피 목록

### 미디어 (Media)
- `POST /api/media/upload/{recipe_id}` - 미디어 업로드
- `GET /api/media/{media_id}` - 미디어 조회
- `DELETE /api/media/{media_id}` - 미디어 삭제

## 개발 참고사항

- 현재 인증은 임시로 `wallet_address`를 파라미터로 받습니다
- 나중에 JWT 기반 인증으로 변경 예정
- IPFS와 Web3 서비스는 기본 구조만 구현되어 있습니다
- 실제 NFT 민팅 기능은 스마트 컨트랙트 연동 후 구현 예정

