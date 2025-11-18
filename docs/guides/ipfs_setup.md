# IPFS 설정 가이드

IPFS를 사용하는 방법은 여러 가지가 있습니다. 프로젝트에서는 두 가지 방법을 지원합니다:

## 방법 1: Pinata 사용 (권장 - 프로덕션)

Pinata는 가장 인기 있는 IPFS 핀닝 서비스입니다. 무료 플랜도 제공하며, 파일을 영구적으로 저장할 수 있습니다.

### 1. Pinata 계정 생성

1. [Pinata 웹사이트](https://www.pinata.cloud/) 방문
2. "Sign Up" 클릭하여 계정 생성
3. 이메일 인증 완료

### 2. API 키 생성

1. Pinata 대시보드 로그인
2. 좌측 메뉴에서 "API Keys" 클릭
3. "New Key" 버튼 클릭
4. Key 이름 입력 (예: "Recipe NFT")
5. 권한 설정:
   - `pinFileToIPFS`: ✅ 체크
   - `pinJSONToIPFS`: ✅ 체크
   - `unpin`: ✅ 체크 (선택사항)
6. "Create Key" 클릭
7. **API Key**와 **Secret Key** 복사 (한 번만 표시됨!)

### 3. 환경 변수 설정

`backend/.env` 파일에 추가:

```bash
PINATA_API_KEY=your_api_key_here
PINATA_SECRET_KEY=your_secret_key_here
```

### 4. Pinata 무료 플랜 제한

- 월 1GB 저장 공간
- 무제한 API 호출
- 파일은 영구 저장 (핀 상태 유지)

---

## 방법 2: 로컬 IPFS 노드 (개발/테스트용)

로컬에서 IPFS 노드를 실행하여 사용할 수 있습니다.

### 1. IPFS 설치

#### Linux (Ubuntu/Debian)
```bash
# IPFS 바이너리 다운로드
wget https://dist.ipfs.tech/kubo/v0.30.0/kubo_v0.30.0_linux-amd64.tar.gz
tar -xvzf kubo_v0.30.0_linux-amd64.tar.gz
cd kubo
sudo ./install.sh
```

#### 또는 패키지 매니저 사용
```bash
# Snap 사용
sudo snap install ipfs

# 또는 직접 설치
wget https://github.com/ipfs/kubo/releases/download/v0.30.0/kubo_v0.30.0_linux-amd64.tar.gz
```

### 2. IPFS 초기화

```bash
ipfs init
```

### 3. IPFS 데몬 실행

```bash
# 포그라운드 실행
ipfs daemon

# 또는 백그라운드 실행
ipfs daemon &
```

### 4. 환경 변수 설정

`backend/.env` 파일:

```bash
IPFS_HOST=127.0.0.1
IPFS_PORT=5001
# PINATA_API_KEY와 PINATA_SECRET_KEY는 비워두거나 주석 처리
```

### 5. 로컬 IPFS 제한사항

- 로컬 노드가 실행 중이어야만 파일 접근 가능
- 다른 사용자들이 파일을 찾기 어려움
- 프로덕션 환경에는 부적합

---

## 방법 3: NFT.Storage (무료, 간단)

NFT.Storage는 Protocol Labs에서 제공하는 무료 IPFS 서비스입니다.

### 1. 계정 생성

1. [NFT.Storage](https://nft.storage/) 방문
2. "Get Started" 클릭
3. 이메일로 로그인 또는 GitHub 연동

### 2. API 키 생성

1. 대시보드에서 "Create API Key" 클릭
2. 키 이름 입력
3. API 키 복사

### 3. 사용 방법

NFT.Storage는 HTTP API를 사용하므로, 별도 라이브러리 설치 필요:

```bash
pip install nft-storage
```

코드에서 사용:
```python
from nft_storage import NFTStorage

client = NFTStorage(api_key="your_api_key")
result = client.store_file("path/to/file")
```

---

## 현재 프로젝트 설정

프로젝트는 다음 순서로 IPFS를 사용합니다:

1. **Pinata 키가 설정된 경우**: Pinata 사용 (우선순위)
2. **Pinata 키가 없는 경우**: 로컬 IPFS 노드 사용

### 환경 변수 예시

```bash
# 방법 1: Pinata 사용 (권장)
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_KEY=your_pinata_secret_key

# 방법 2: 로컬 IPFS 사용
IPFS_HOST=127.0.0.1
IPFS_PORT=5001
```

---

## 테스트

IPFS가 제대로 설정되었는지 테스트:

```bash
cd backend
source venv/bin/activate
python -c "from app.services.ipfs import ipfs_service; print(ipfs_service.upload_json({'test': 'data'}))"
```

성공하면 IPFS 해시가 출력됩니다.

---

## 문제 해결

### "Connection refused" 오류
- 로컬 IPFS 노드가 실행 중인지 확인: `ipfs daemon`
- 포트가 올바른지 확인: 기본값은 5001

### Pinata API 오류
- API 키와 Secret 키가 올바른지 확인
- Pinata 대시보드에서 키 상태 확인
- 무료 플랜 한도 초과 여부 확인

### 파일이 사라지는 문제
- 로컬 IPFS는 노드가 꺼지면 접근 불가
- 프로덕션에서는 Pinata 같은 핀닝 서비스 사용 권장

