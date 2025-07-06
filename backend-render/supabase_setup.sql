-- Supabase SQL Setup for הנוסע המתמיד
-- יצירת הטבלאות הנדרשות לאפליקציה

-- יצירת טבלת כתובות
CREATE TABLE addresses (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    city TEXT,
    neighborhood TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    visited BOOLEAN DEFAULT FALSE,
    source TEXT DEFAULT 'manual',
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    geocoded_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- הוספת אינדקסים לביצועים טובים יותר
CREATE INDEX idx_addresses_coordinates ON addresses(latitude, longitude);
CREATE INDEX idx_addresses_city ON addresses(city);
CREATE INDEX idx_addresses_created_at ON addresses(created_at);

-- הוספת RLS (Row Level Security) - אופציונלי
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;

-- מדיניות גישה - אפשר הכל לשרת (service role)
CREATE POLICY "Enable all for service role" ON addresses
FOR ALL USING (auth.role() = 'service_role');

-- מדיניות גישה - אפשר קריאה לכולם (אופציונלי)
CREATE POLICY "Enable read access for all users" ON addresses
FOR SELECT USING (true);

-- הוספת trigger לעדכון אוטומטי של updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_addresses_updated_at
    BEFORE UPDATE ON addresses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- הערות:
-- 1. הכנס את הקוד הזה ב-Supabase Dashboard -> SQL Editor
-- 2. הרץ את הסקריפט
-- 3. הטבלאות ייווצרו אוטומטית
-- 4. תוכל לראות את הנתונים ב-Table Editor
