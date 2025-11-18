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
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
if settings.DEBUG:
    # 개발 환경: 모든 origin 허용
    allowed_origins = ["*"]
    allow_credentials = False
else:
    # 프로덕션: 특정 origin만 허용
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

