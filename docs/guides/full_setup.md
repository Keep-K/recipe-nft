# 전체 개발 환경 가이드

## 1. FastAPI 서버 실행 (HTTPS 포함)

### 1-1. 기본 HTTP 개발 서버
```bash
cd backend
source venv/bin/activate        # 가상환경 활성화
uvicorn main:app --reload
```
- Swagger: `http://localhost:8000/docs`
- 헬스 체크: `GET /health`

### 1-2. 로컬 HTTPS 개발
1. OpenSSL 등으로 self-signed 인증서 생성
   ```bash
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout cert/key.pem -out cert/cert.pem
   ```
2. HTTPS 서버 실행
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8443 \
     --ssl-keyfile cert/key.pem --ssl-certfile cert/cert.pem
   ```
   > 브라우저에서 인증서 경고가 뜨는 것은 정상 (개발용).

3. 프록시/실서버 환경(Nginx 등)에서는 Let’s Encrypt로 TLS 설정 후
   `gunicorn -k uvicorn.workers.UvicornWorker main:app` 형태로 운영.

## 2. PostgreSQL 서버 구동

### 2-1. 서비스 시작/확인
```bash
sudo service postgresql start          # WSL/Ubuntu
sudo service postgresql status
```
(systemd 환경이면 `sudo systemctl start postgresql`)

### 2-2. 자동 초기화 스크립트
```bash
cd backend
./scripts/setup_db.sh
```
- `recipe_nft_db`, `recipe_user/recipe_password` 생성
- 권한 부여까지 자동 처리

### 2-3. 수동 설정 요약
```bash
sudo -u postgres psql
CREATE DATABASE recipe_nft_db;
CREATE USER recipe_user WITH PASSWORD 'recipe_password';
GRANT ALL PRIVILEGES ON DATABASE recipe_nft_db TO recipe_user;
GRANT USAGE ON SCHEMA public TO recipe_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO recipe_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO recipe_user;
\q
```
- 접속 테스트: `psql -U recipe_user -d recipe_nft_db -h localhost`

## 3. GitHub 업로드 가이드

1. 변경 사항 확인
   ```bash
   git status -sb
   ```
2. 스테이징 & 커밋
   ```bash
   git add .
   git commit -m "Describe your changes"
   ```
3. 원격 저장소 설정(최초 1회)
   ```bash
   git remote add origin https://github.com/<user>/<repo>.git
   ```
4. 푸시
   ```bash
   git push origin main
   ```

### 자주 발생하는 이슈
- **push 실패 (권한)**: GitHub 토큰/SSH 키 확인.
- **충돌**: `git pull --rebase origin main` 후 해결.
- **대용량 파일**: `.gitignore` 확인 후 필요 시 Git LFS 사용.

---
이 문서는 HTTPS 서버 기동, PostgreSQL 운영, GitHub 배포 흐름을 한 곳에 정리한 것입니다. 필요한 명령어와 절차를 그대로 따라 하면 환경 구축부터 배포까지 빠르게 진행할 수 있습니다.

