from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Numeric, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(42), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    username = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recipes = relationship("Recipe", back_populates="owner")
    validations = relationship("RecipeValidation", back_populates="validator")

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_id = Column(Integer, unique=True, index=True, nullable=True)  # NFT 토큰 ID
    recipe_name = Column(String(255), nullable=False, index=True)
    ingredients = Column(JSON, nullable=False)  # 재료 배열
    cooking_tools = Column(JSON, nullable=False)  # 조리 도구 배열
    cooking_steps = Column(JSON, nullable=False)  # 조리 과정 배열
    machine_instructions = Column(JSON, nullable=True)  # 기계 작동 과정
    ipfs_hash = Column(String(255), nullable=True, index=True)  # 메타데이터 IPFS 해시
    contract_address = Column(String(42), nullable=True)  # 스마트 컨트랙트 주소
    transaction_hash = Column(String(66), nullable=True, index=True)  # 민팅 트랜잭션 해시
    is_minted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="recipes")
    media = relationship("RecipeMedia", back_populates="recipe", cascade="all, delete-orphan")
    ownership_transfers = relationship("OwnershipTransfer", back_populates="recipe")
    validations = relationship("RecipeValidation", back_populates="recipe")
    monetization_links = relationship("MonetizationLink", back_populates="recipe")

class RecipeMedia(Base):
    __tablename__ = "recipe_media"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    media_type = Column(String(20), nullable=False)  # photo, video
    ipfs_hash = Column(String(255), nullable=True, index=True)
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recipe = relationship("Recipe", back_populates="media")

class OwnershipTransfer(Base):
    __tablename__ = "ownership_transfers"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    transaction_hash = Column(String(66), unique=True, index=True, nullable=False)
    block_number = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recipe = relationship("Recipe", back_populates="ownership_transfers")

class RecipeValidation(Base):
    __tablename__ = "recipe_validation"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    validator_address = Column(String(42), ForeignKey("users.wallet_address"), nullable=False)
    validation_score = Column(Numeric(3, 2), nullable=False)  # 0.00 ~ 5.00
    validation_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recipe = relationship("Recipe", back_populates="validations")
    validator = relationship("User", back_populates="validations")

class MonetizationLink(Base):
    __tablename__ = "monetization_links"
    
    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    link_url = Column(String(500), nullable=False)
    link_type = Column(String(50), nullable=False)  # affiliate, sponsor, etc.
    revenue_share = Column(Numeric(5, 2), nullable=True)  # 수익 분배율 (%)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    recipe = relationship("Recipe", back_populates="monetization_links")

