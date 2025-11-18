#!/bin/bash
# Railway DB 마이그레이션 스크립트
# 사용법: DATABASE_URL="postgresql://..." ./migrate_railway.sh

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL 환경 변수를 설정해주세요."
    echo "예: DATABASE_URL='postgresql://postgres:PASSWORD@HOST:PORT/railway' ./migrate_railway.sh"
    exit 1
fi

echo "📦 Railway DB 마이그레이션 시작..."
export DATABASE_URL
python3 init_db.py
echo "✅ 마이그레이션 완료!"
