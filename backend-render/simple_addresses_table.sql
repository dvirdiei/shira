-- 🚀 הנוסע המתמיד - יצירת טבלת addresses בלבד (מה שהבאק-אנד צריך)
-- העתק והדבק את הקוד הזה ב-Supabase SQL Editor

-- 🗂️ טבלה יחידה: addresses (כל מה שהבאק-אנד משתמש בו)
CREATE TABLE IF NOT EXISTS addresses (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    city TEXT DEFAULT 'ירושלים',
    neighborhood TEXT DEFAULT 'לא ידוע',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    visited BOOLEAN DEFAULT FALSE,
    source TEXT DEFAULT 'manual',
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 📊 יצירת אינדקסים לביצועים מהירים
CREATE INDEX IF NOT EXISTS idx_addresses_coordinates ON addresses(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_addresses_city ON addresses(city);
CREATE INDEX IF NOT EXISTS idx_addresses_neighborhood ON addresses(neighborhood);
CREATE INDEX IF NOT EXISTS idx_addresses_visited ON addresses(visited);
CREATE INDEX IF NOT EXISTS idx_addresses_created_at ON addresses(created_at);

-- 🔒 הגדרת Row Level Security (RLS)
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;

-- 🛡️ מדיניות גישה - אפשר הכל לשרת
CREATE POLICY "Enable all for service role on addresses" ON addresses FOR ALL USING (auth.role() = 'service_role');

-- ✅ בדיקה שהטבלה נוצרה
SELECT 
    'addresses' as table_name, 
    COUNT(*) as row_count 
FROM addresses;

-- 📋 הצגת מבנה הטבלה
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'addresses'
ORDER BY ordinal_position;
