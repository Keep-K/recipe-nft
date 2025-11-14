#!/bin/bash
# PostgreSQL 데이터베이스 설정 스크립트

echo "=== PostgreSQL Database Setup ==="

# PostgreSQL 설치 확인
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed."
    echo "Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# PostgreSQL 서비스 시작
echo "Starting PostgreSQL service..."
sudo service postgresql start 2>/dev/null || sudo systemctl start postgresql 2>/dev/null

# 잠시 대기
sleep 2

# 데이터베이스 및 사용자 생성
echo "Creating database and user..."

# 기본 설정 (변경 가능)
DB_NAME="recipe_nft_db"
DB_USER="recipe_user"
DB_PASSWORD="recipe_password"

# postgres 사용자로 데이터베이스 생성
sudo -u postgres psql <<EOF
-- 데이터베이스가 이미 있으면 삭제 (주의!)
DROP DATABASE IF EXISTS $DB_NAME;

-- 데이터베이스 생성
CREATE DATABASE $DB_NAME;

-- 사용자가 이미 있으면 삭제
DROP USER IF EXISTS $DB_USER;

-- 사용자 생성
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- 권한 부여
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- 연결 권한 부여
ALTER USER $DB_USER CREATEDB;

\q
EOF

echo ""
echo "=== Database Setup Complete ==="
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Password: $DB_PASSWORD"
echo ""
echo "Update your .env file with:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""

