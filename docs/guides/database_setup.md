# 데이터베이스 설정 가이드

PostgreSQL 데이터베이스 설치 및 설정 방법

## 자동 설정 (권장)

```bash
cd backend
./setup_db.sh
```

스크립트가 다음을 자동으로 수행합니다:
- PostgreSQL 설치 (없는 경우)
- PostgreSQL 서비스 시작
- 데이터베이스 및 사용자 생성

## 수동 설정

### 1. PostgreSQL 설치

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
```

### 2. PostgreSQL 서비스 시작

```bash
# WSL 환경
sudo service postgresql start

# 또는 systemd 사용 환경
sudo systemctl start postgresql
sudo systemctl enable postgresql  # 부팅 시 자동 시작
```

### 3. 데이터베이스 및 사용자 생성

```bash
sudo -u postgres psql
```

PostgreSQL 프롬프트에서:

```sql
-- 데이터베이스 생성
CREATE DATABASE recipe_nft_db;

-- 사용자 생성
CREATE USER recipe_user WITH PASSWORD 'recipe_password';

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE recipe_nft_db TO recipe_user;

-- 연결 권한 부여
ALTER USER recipe_user CREATEDB;

-- 종료
\q
```

### 4. 연결 테스트

```bash
psql -U recipe_user -d recipe_nft_db -h localhost
```

## 환경 변수 설정

`.env` 파일에 데이터베이스 연결 정보를 설정하세요:

```env
DATABASE_URL=postgresql://recipe_user:recipe_password@localhost:5432/recipe_nft_db
```

## 데이터베이스 초기화

환경 변수를 설정한 후:

```bash
cd backend
source venv/bin/activate
python init_db.py
```

## 문제 해결

### Connection refused 오류

PostgreSQL 서비스가 실행 중인지 확인:

```bash
sudo service postgresql status
# 또는
sudo systemctl status postgresql
```

서비스가 중지되어 있다면 시작:

```bash
sudo service postgresql start
# 또는
sudo systemctl start postgresql
```

### 인증 실패

`pg_hba.conf` 파일을 확인하고 필요시 수정:

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

`local` 및 `host` 연결에 대해 `md5` 또는 `trust` 인증 방법을 확인하세요.

### 포트 확인

PostgreSQL이 올바른 포트(기본 5432)에서 실행 중인지 확인:

```bash
sudo netstat -tlnp | grep 5432
# 또는
sudo ss -tlnp | grep 5432
```

