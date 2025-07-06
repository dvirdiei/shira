-- 🚀 מערכת הנוסע המתמיד - החלפת קבצי CSV בטבלאות Supabase
-- העתק והדבק את כל הקוד הזה ב-Supabase SQL Editor

-- 🗂️ טבלה 1: כתובות שנמצאו (found_addresses.csv)
CREATE TABLE IF NOT EXISTS found_addresses (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    neighborhood TEXT DEFAULT 'לא ידוע',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    visited BOOLEAN DEFAULT FALSE,
    source TEXT DEFAULT 'geocoded',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- � טבלה 2: כתובות שלא נמצאו (not_found_addresses.csv)
CREATE TABLE IF NOT EXISTS not_found_addresses (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    neighborhood TEXT DEFAULT 'לא ידוע',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    visited BOOLEAN DEFAULT FALSE,
    source TEXT DEFAULT 'manual_corrected',
    attempts INTEGER DEFAULT 1,
    last_attempt TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- �️ טבלה 3: כתובות שנמחקו (deleted_addresses.csv)
CREATE TABLE IF NOT EXISTS deleted_addresses (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    neighborhood TEXT DEFAULT 'לא ידוע',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    visited BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMPTZ DEFAULT NOW(),
    deletion_reason TEXT,
    original_source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- � טבלה 4: כתובות לשימוש עתידי (future_use.csv)
CREATE TABLE IF NOT EXISTS future_use_addresses (
    id BIGSERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    neighborhood TEXT DEFAULT 'לא ידוע',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    visited BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 1,
    planned_date DATE,
    notes TEXT,
    source TEXT DEFAULT 'manual',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- � טבלה 5: VIEW מאוחדת - כל הכתובות יחד (להחליף את ה-CSV logic)
CREATE OR REPLACE VIEW all_addresses AS
SELECT 
    'found' as status,
    id,
    address,
    neighborhood,
    latitude,
    longitude,
    visited,
    source,
    created_at,
    updated_at
FROM found_addresses
UNION ALL
SELECT 
    'not_found' as status,
    id,
    address,
    neighborhood,
    latitude,
    longitude,
    visited,
    source,
    created_at,
    updated_at
FROM not_found_addresses
UNION ALL
SELECT 
    'future_use' as status,
    id,
    address,
    neighborhood,
    latitude,
    longitude,
    visited,
    source,
    created_at,
    updated_at
FROM future_use_addresses;

-- 🔧 עדכון טבלת addresses הקיימת (אם יש נתונים)
ALTER TABLE addresses ADD COLUMN IF NOT EXISTS neighborhood TEXT DEFAULT 'לא ידוע';
ALTER TABLE addresses ADD COLUMN IF NOT EXISTS visited BOOLEAN DEFAULT FALSE;
ALTER TABLE addresses ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual';
ALTER TABLE addresses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 📋 טבלה 6: רשימות/קטגוריות
CREATE TABLE IF NOT EXISTS address_categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT DEFAULT '#007bff',
    icon TEXT DEFAULT '📍',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 🔗 טבלה 7: קישור כתובות לקטגוריות
CREATE TABLE IF NOT EXISTS address_category_links (
    id BIGSERIAL PRIMARY KEY,
    address_id BIGINT,
    category_id BIGINT REFERENCES address_categories(id) ON DELETE CASCADE,
    table_name TEXT NOT NULL, -- 'found_addresses', 'not_found_addresses', etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(address_id, category_id, table_name)
);

-- 📈 טבלה 8: לוג פעולות (לעקוב אחרי שינויים)
CREATE TABLE IF NOT EXISTS address_logs (
    id BIGSERIAL PRIMARY KEY,
    address_id BIGINT,
    table_name TEXT NOT NULL,
    action TEXT NOT NULL, -- 'insert', 'update', 'delete', 'move'
    old_values JSONB,
    new_values JSONB,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 📊 יצירת אינדקסים לביצועים מהירים
CREATE INDEX IF NOT EXISTS idx_found_addresses_coordinates ON found_addresses(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_found_addresses_visited ON found_addresses(visited);
CREATE INDEX IF NOT EXISTS idx_found_addresses_neighborhood ON found_addresses(neighborhood);

CREATE INDEX IF NOT EXISTS idx_not_found_addresses_attempts ON not_found_addresses(attempts);
CREATE INDEX IF NOT EXISTS idx_not_found_addresses_last_attempt ON not_found_addresses(last_attempt);

CREATE INDEX IF NOT EXISTS idx_deleted_addresses_date ON deleted_addresses(deleted_date);
CREATE INDEX IF NOT EXISTS idx_future_use_priority ON future_use_addresses(priority);
CREATE INDEX IF NOT EXISTS idx_future_use_planned_date ON future_use_addresses(planned_date);

CREATE INDEX IF NOT EXISTS idx_category_links_address ON address_category_links(address_id);
CREATE INDEX IF NOT EXISTS idx_category_links_category ON address_category_links(category_id);
CREATE INDEX IF NOT EXISTS idx_category_links_table ON address_category_links(table_name);

CREATE INDEX IF NOT EXISTS idx_logs_address ON address_logs(address_id);
CREATE INDEX IF NOT EXISTS idx_logs_table ON address_logs(table_name);
CREATE INDEX IF NOT EXISTS idx_logs_action ON address_logs(action);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON address_logs(created_at);

-- 🔒 הגדרת Row Level Security (RLS)
ALTER TABLE found_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE not_found_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE deleted_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE future_use_addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE address_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE address_category_links ENABLE ROW LEVEL SECURITY;
ALTER TABLE address_logs ENABLE ROW LEVEL SECURITY;

-- 🛡️ מדיניות גישה - אפשר הכל לשרת
CREATE POLICY "Enable all for service role on found_addresses" ON found_addresses FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable all for service role on not_found_addresses" ON not_found_addresses FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable all for service role on deleted_addresses" ON deleted_addresses FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable all for service role on future_use_addresses" ON future_use_addresses FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable all for service role on address_categories" ON address_categories FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable all for service role on address_category_links" ON address_category_links FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Enable all for service role on address_logs" ON address_logs FOR ALL USING (auth.role() = 'service_role');

-- 📝 הכנסת קטגוריות דוגמה
INSERT INTO address_categories (name, description, color, icon) VALUES 
('מקומות קדושים', 'בתי כנסת ומקומות קדושים בירושלים', '#28a745', '🕍'),
('מסעדות', 'מקומות אוכל טובים שכדאי לבקר', '#fd7e14', '🍽️'),
('אטרקציות', 'מקומות מעניינים לתיירים', '#6f42c1', '🎭'),
('קניות', 'חנויות ומרכזי קניות', '#17a2b8', '🛍️'),
('ביקרנו', 'מקומות שכבר ביקרנו בהם', '#dc3545', '✅'),
('לביקור עתידי', 'מקומות שמתוכננים לביקור', '#ffc107', '📅')
ON CONFLICT DO NOTHING;

-- 🚀 פונקציות עזר לניהול הנתונים

-- פונקציה להעברת כתובת בין טבלאות
CREATE OR REPLACE FUNCTION move_address(
    p_address_id BIGINT,
    p_from_table TEXT,
    p_to_table TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    address_record RECORD;
    result BOOLEAN := FALSE;
BEGIN
    -- שלוף את הכתובת מהטבלה המקורית
    EXECUTE format('SELECT * FROM %I WHERE id = %L', p_from_table, p_address_id) INTO address_record;
    
    IF address_record IS NOT NULL THEN
        -- הכנס לטבלה החדשה
        EXECUTE format('INSERT INTO %I (address, neighborhood, latitude, longitude, visited, source) VALUES (%L, %L, %L, %L, %L, %L)',
            p_to_table, 
            address_record.address, 
            address_record.neighborhood, 
            address_record.latitude, 
            address_record.longitude, 
            address_record.visited, 
            address_record.source
        );
        
        -- מחק מהטבלה המקורית
        EXECUTE format('DELETE FROM %I WHERE id = %L', p_from_table, p_address_id);
        
        result := TRUE;
    END IF;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- פונקציה לחיפוש בכל הטבלאות
CREATE OR REPLACE FUNCTION search_all_addresses(search_term TEXT)
RETURNS TABLE(
    status TEXT,
    id BIGINT,
    address TEXT,
    neighborhood TEXT,
    latitude DECIMAL,
    longitude DECIMAL,
    visited BOOLEAN,
    source TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM all_addresses 
    WHERE 
        address ILIKE '%' || search_term || '%' 
        OR neighborhood ILIKE '%' || search_term || '%'
    ORDER BY 
        CASE WHEN status = 'found' THEN 1
             WHEN status = 'future_use' THEN 2
             WHEN status = 'not_found' THEN 3
             ELSE 4 END,
        address;
END;
$$ LANGUAGE plpgsql;

-- ✅ בדיקה שהכל נוצר בהצלחה
SELECT 
    'found_addresses' as table_name, 
    COUNT(*) as row_count 
FROM found_addresses
UNION ALL
SELECT 
    'not_found_addresses' as table_name, 
    COUNT(*) as row_count 
FROM not_found_addresses
UNION ALL
SELECT 
    'deleted_addresses' as table_name, 
    COUNT(*) as row_count 
FROM deleted_addresses
UNION ALL
SELECT 
    'future_use_addresses' as table_name, 
    COUNT(*) as row_count 
FROM future_use_addresses
UNION ALL
SELECT 
    'address_categories' as table_name, 
    COUNT(*) as row_count 
FROM address_categories;

-- 📋 הצגת מבנה הטבלאות שנוצרו
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name IN (
    'found_addresses', 
    'not_found_addresses', 
    'deleted_addresses', 
    'future_use_addresses',
    'address_categories',
    'address_category_links',
    'address_logs'
)
ORDER BY table_name, ordinal_position;
