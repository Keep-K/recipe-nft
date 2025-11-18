-- 기존 recipes 테이블 삭제 및 재생성
-- 주의: 이 작업은 기존 데이터를 모두 삭제합니다!

DROP TABLE IF EXISTS recipes CASCADE;

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token_id INTEGER UNIQUE,
    recipe_name VARCHAR(255) NOT NULL,
    ingredients JSONB NOT NULL,
    cooking_tools JSONB NOT NULL,
    cooking_steps JSONB NOT NULL,
    machine_instructions JSONB,
    ipfs_hash VARCHAR(255),
    contract_address VARCHAR(42),
    transaction_hash VARCHAR(66),
    is_minted BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Foreign key 추가 (users 테이블이 있는 경우)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'users'
    ) THEN
        ALTER TABLE recipes ADD CONSTRAINT recipes_user_id_fkey 
            FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

-- 인덱스 생성
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_recipes_token_id ON recipes(token_id);
CREATE INDEX idx_recipes_recipe_name ON recipes(recipe_name);
CREATE INDEX idx_recipes_is_minted ON recipes(is_minted);
CREATE INDEX idx_recipes_transaction_hash ON recipes(transaction_hash);
CREATE INDEX idx_recipes_ipfs_hash ON recipes(ipfs_hash);

