#!/bin/bash
# 백엔드 환경 설정 스크립트

echo "=== Recipe NFT Backend Setup ==="

# 가상 환경 생성
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        echo "Please install python3-venv: sudo apt install python3-venv"
        exit 1
    fi
fi

# 가상 환경 활성화
echo "Activating virtual environment..."
source venv/bin/activate

# pip 업그레이드
echo "Upgrading pip..."
pip install --upgrade pip

# 의존성 설치
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To initialize the database, run:"
echo "  python init_db.py"

