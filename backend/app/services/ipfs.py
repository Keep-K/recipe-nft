from typing import Optional
import ipfshttpclient
from app.config import settings

class IPFSService:
    def __init__(self):
        self.client = None
        self._connect()
    
    def _connect(self):
        """IPFS 클라이언트 연결"""
        try:
            if settings.PINATA_API_KEY and settings.PINATA_SECRET_KEY:
                # Pinata 사용 (추후 구현)
                pass
            else:
                # 로컬 IPFS 노드
                self.client = ipfshttpclient.connect(
                    f"/ip4/{settings.IPFS_HOST}/tcp/{settings.IPFS_PORT}/http"
                )
        except Exception as e:
            print(f"IPFS connection error: {e}")
            self.client = None
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """파일을 IPFS에 업로드하고 해시 반환"""
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
        if not self.client:
            return None
        
        try:
            import json
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

