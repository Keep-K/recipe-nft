from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# User Schemas
class UserBase(BaseModel):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Recipe Schemas
class RecipeBase(BaseModel):
    recipe_name: str = Field(..., min_length=1, max_length=255)
    ingredients: List[str] = Field(..., min_items=1)
    cooking_tools: List[str] = Field(..., min_items=1)
    cooking_steps: List[str] = Field(..., min_items=1)
    machine_instructions: Optional[List[dict]] = None

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    recipe_name: Optional[str] = None
    ingredients: Optional[List[str]] = None
    cooking_tools: Optional[List[str]] = None
    cooking_steps: Optional[List[str]] = None
    machine_instructions: Optional[List[dict]] = None

class RecipeResponse(RecipeBase):
    id: int
    user_id: int
    token_id: Optional[int] = None
    ipfs_hash: Optional[str] = None
    contract_address: Optional[str] = None
    is_minted: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

class RecipeListResponse(BaseModel):
    id: int
    recipe_name: str
    token_id: Optional[int] = None
    is_minted: bool
    created_at: datetime
    owner: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True

# Media Schemas
class MediaBase(BaseModel):
    media_type: str = Field(..., pattern="^(photo|video)$")
    file_name: Optional[str] = None

class MediaCreate(MediaBase):
    recipe_id: int

class MediaResponse(MediaBase):
    id: int
    recipe_id: int
    ipfs_hash: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Ownership Transfer Schemas
class OwnershipTransferCreate(BaseModel):
    recipe_id: int
    from_address: str = Field(..., min_length=42, max_length=42)
    to_address: str = Field(..., min_length=42, max_length=42)
    transaction_hash: str = Field(..., min_length=66, max_length=66)
    block_number: Optional[int] = None

class OwnershipTransferResponse(OwnershipTransferCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Validation Schemas
class RecipeValidationCreate(BaseModel):
    recipe_id: int
    validator_address: str = Field(..., min_length=42, max_length=42)
    validation_score: Decimal = Field(..., ge=0, le=5)
    validation_comment: Optional[str] = None

class RecipeValidationResponse(RecipeValidationCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Monetization Link Schemas
class MonetizationLinkCreate(BaseModel):
    recipe_id: int
    link_url: str = Field(..., max_length=500)
    link_type: str = Field(..., max_length=50)
    revenue_share: Optional[Decimal] = Field(None, ge=0, le=100)
    is_active: bool = True

class MonetizationLinkResponse(MonetizationLinkCreate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

