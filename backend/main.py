from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import recipes, users, media, nft

app = FastAPI(
    title="Recipe NFT API",
    description="음식 레시피 NFT 플랫폼 API",
    version="1.0.0"
)

# CORS 설정
import os
# 환경 변수에서 ALLOWED_ORIGINS 읽기 (settings보다 우선)
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", settings.ALLOWED_ORIGINS)
if allowed_origins_str:
    # 공백 제거 및 빈 문자열 필터링
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
else:
    allowed_origins = ["http://localhost:5173", "http://localhost:3000"]

if settings.DEBUG:
    # 개발 환경: 모든 origin 허용
    allowed_origins = ["*"]
    allow_credentials = False
else:
    # 프로덕션: 특정 origin만 허용
    if not allowed_origins:
        # ALLOWED_ORIGINS가 비어있으면 기본값 사용
        allowed_origins = ["http://localhost:5173", "http://localhost:3000"]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 라우터 등록
app.include_router(recipes.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(nft.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Recipe NFT API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

