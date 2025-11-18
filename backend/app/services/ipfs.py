from typing import Optional
import ipfshttpclient
import requests
import json
from app.config import settings

class IPFSService:
    def __init__(self):
        self.client = None
        self.use_pinata = bool(settings.PINATA_API_KEY and settings.PINATA_SECRET_KEY)
        self._connect()
    
    def _connect(self):
        """IPFS 클라이언트 연결"""
        try:
            if self.use_pinata:
                # Pinata 사용
                print("Using Pinata for IPFS")
            else:
                # 로컬 IPFS 노드
                self.client = ipfshttpclient.connect(
                    f"/ip4/{settings.IPFS_HOST}/tcp/{settings.IPFS_PORT}/http"
                )
                print(f"Connected to local IPFS node at {settings.IPFS_HOST}:{settings.IPFS_PORT}")
        except Exception as e:
            print(f"IPFS connection error: {e}")
            self.client = None
    
    def _upload_to_pinata(self, data: dict, is_json: bool = True) -> Optional[str]:
        """Pinata에 파일/JSON 업로드"""
        try:
            url = "https://api.pinata.cloud/pinning/pinJSONToIPFS" if is_json else "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {
                "pinata_api_key": settings.PINATA_API_KEY,
                "pinata_secret_api_key": settings.PINATA_SECRET_KEY,
            }
            
            if is_json:
                payload = {
                    "pinataContent": data,
                    "pinataMetadata": {
                        "name": "recipe-nft-metadata"
                    }
                }
                response = requests.post(url, json=payload, headers=headers, timeout=30)
            else:
                # 파일 업로드의 경우 multipart/form-data 사용
                files = {"file": data}
                response = requests.post(url, files=files, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("IpfsHash")
            else:
                print(f"Pinata upload error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Pinata upload error: {e}")
            return None
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """파일을 IPFS에 업로드하고 해시 반환"""
        if self.use_pinata:
            # Pinata 파일 업로드
            try:
                with open(file_path, 'rb') as f:
                    return self._upload_to_pinata(f, is_json=False)
            except Exception as e:
                print(f"Pinata file upload error: {e}")
                return None
        
        if not self.client:
            return None
        
        try:
            result = self.client.add(file_path)
            return result["Hash"]
        except Exception as e:
            print(f"IPFS upload error: {e}")
            return None
    
    def upload_json(self, data: dict) -> Optional[str]:
        """JSON 데이터를 IPFS에 업로드하고 해시 반환"""
        if self.use_pinata:
            # Pinata JSON 업로드
            return self._upload_to_pinata(data, is_json=True)
        
        if not self.client:
            return None
        
        try:
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f)
                temp_path = f.name
            
            result = self.client.add(temp_path)
            import os
            os.unlink(temp_path)
            return result["Hash"]
        except Exception as e:
            print(f"IPFS JSON upload error: {e}")
            return None
    
    def get_file(self, ipfs_hash: str) -> Optional[bytes]:
        """IPFS에서 파일 다운로드"""
        if not self.client:
            return None
        
        try:
            return self.client.cat(ipfs_hash)
        except Exception as e:
            print(f"IPFS get error: {e}")
            return None

ipfs_service = IPFSService()

