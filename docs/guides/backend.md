# Backend API

FastAPI 기반 레시피 NFT 백엔드 서버

## 설치

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/recipe_nft_db
SECRET_KEY=your-secret-key
IPFS_HOST=127.0.0.1
IPFS_PORT=5001
WEB3_PROVIDER_URL=http://localhost:8545
```

## 실행

```bash
python main.py
# 또는
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

