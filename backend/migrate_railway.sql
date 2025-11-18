-- Railway DB 스키마 마이그레이션 스크립트
-- recipes 테이블에 누락된 컬럼 추가

-- user_id 컬럼 추가 (이미 있으면 에러 무시)
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS token_id INTEGER;
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS contract_address VARCHAR(42);
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS transaction_hash VARCHAR(66);
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS is_minted BOOLEAN DEFAULT FALSE;
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Foreign key 추가 (users 테이블이 있는 경우)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        ALTER TABLE recipes ADD CONSTRAINT IF NOT EXISTS recipes_user_id_fkey 
            FOREIGN KEY (user_id) REFERENCES users(id);
    END IF;
END $$;

-- 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_token_id ON recipes(token_id);
CREATE INDEX IF NOT EXISTS idx_recipes_is_minted ON recipes(is_minted);
CREATE INDEX IF NOT EXISTS idx_recipes_transaction_hash ON recipes(transaction_hash);

-- 기존 데이터가 있다면 user_id를 NULL에서 기본값으로 설정 (필요시)
-- UPDATE recipes SET user_id = 1 WHERE user_id IS NULL;  -- 주의: 실제 사용자 ID로 변경 필요

