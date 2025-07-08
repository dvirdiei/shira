-- יצירת טבלאות עבור מערכת הנוסע המתמיד
-- יש להריץ את הקוד הזה ב-Supabase SQL Editor

-- טבלה 1: כתובות עם קואורדינטות (הצלחה ב-Geocoding)
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    neighborhood TEXT,
    visited BOOLEAN DEFAULT false,
    source TEXT DEFAULT 'geocoded', -- 'geocoded', 'manual', 'manual_corrected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- טבלה 2: כתובות ללא קואורדינטות (כישלון ב-Geocoding) + אפשרות הזנה ידנית
CREATE TABLE IF NOT EXISTS addresses_missing_coordinates (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    reason TEXT DEFAULT 'geocoding_failed', -- 'geocoding_failed', 'invalid_address', 'api_error'
    -- קואורדינטות ידניות (NULL אם עדיין לא הוזנו)
    manual_lat REAL DEFAULT NULL,
    manual_lon REAL DEFAULT NULL,
    manual_neighborhood TEXT DEFAULT NULL,
    -- סטטוס הזנה ידנית
    manual_coordinates_added BOOLEAN DEFAULT false,
    manual_coordinates_needed BOOLEAN DEFAULT true,
    -- מטא-דאטה
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    attempts INTEGER DEFAULT 1, -- מספר ניסיונות geocoding
    -- מי הזין את הקואורדינטות הידניות
    manual_added_by TEXT DEFAULT NULL,
    manual_added_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- הוספת אינדקסים לביצועים טובים יותר
CREATE INDEX IF NOT EXISTS idx_addresses_lat_lon ON addresses(lat, lon);
CREATE INDEX IF NOT EXISTS idx_addresses_neighborhood ON addresses(neighborhood);
CREATE INDEX IF NOT EXISTS idx_addresses_visited ON addresses(visited);
CREATE INDEX IF NOT EXISTS idx_missing_coordinates_reason ON addresses_missing_coordinates(reason);
CREATE INDEX IF NOT EXISTS idx_missing_coordinates_manual_needed ON addresses_missing_coordinates(manual_coordinates_needed);
CREATE INDEX IF NOT EXISTS idx_missing_coordinates_manual_added ON addresses_missing_coordinates(manual_coordinates_added);
CREATE INDEX IF NOT EXISTS idx_missing_coordinates_manual_lat_lon ON addresses_missing_coordinates(manual_lat, manual_lon);

-- הוספת Trigger לעדכון updated_at אוטומטי
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

-- הוספת Trigger לעדכון updated_at גם לטבלת missing_coordinates
CREATE TRIGGER update_missing_coordinates_updated_at 
    BEFORE UPDATE ON addresses_missing_coordinates 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- הוספת Row Level Security (RLS) - אופציונלי
ALTER TABLE addresses ENABLE ROW LEVEL SECURITY;
ALTER TABLE addresses_missing_coordinates ENABLE ROW LEVEL SECURITY;

-- פוליסות גישה (אופציונלי - תלוי במדיניות האבטחה שלך)
CREATE POLICY "Enable read access for all users" ON addresses FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON addresses FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON addresses FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON addresses FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON addresses_missing_coordinates FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON addresses_missing_coordinates FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update access for all users" ON addresses_missing_coordinates FOR UPDATE USING (true);
CREATE POLICY "Enable delete access for all users" ON addresses_missing_coordinates FOR DELETE USING (true);
