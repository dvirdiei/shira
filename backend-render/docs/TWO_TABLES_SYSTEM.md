# 🗺️ מערכת שתי הטבלאות - הנוסע המתמיד

## סקירה כללית
המערכת עכשיו תומכת בשתי טבלאות:
1. **addresses** - כתובות שהגיאוקודינג הצליח להן (יש קווי אורך ורחב)
2. **addresses_missing_coordinates** - כתובות שהגיאוקודינג נכשל (צריכות הזנה ידנית)

## 🏗️ יצירת הטבלאות ב-Supabase

1. היכנס ל-Supabase Dashboard
2. לך ל-SQL Editor  
3. הריץ את הקובץ `database/create_tables.sql`

## 🔗 API Endpoints החדשים

### קבלת נתונים
- `GET /api/addresses-for-map` - כל הכתובות למפה (משתי הטבלאות)
- `GET /api/addresses-needing-manual` - כתובות שצריכות קואורדינטות ידניות
- `GET /api/missing-coordinates` - כל הכתובות ללא קואורדינטות

### הוספת נתונים
- `POST /api/process-new-address` - עיבוד כתובת חדשה (גיאוקודינג אוטומטי)
- `POST /api/add-manual-coordinates` - הוספת קואורדינטות ידניות

## 📊 תהליך עבודה

### הוספת כתובת חדשה:
```javascript
// Frontend
const response = await fetch('/api/process-new-address', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: 'רחוב הרצל 1 תל אביב' })
});

const result = await response.json();
// אם הגיאוקודינג הצליח -> טבלת addresses
// אם נכשל -> טבלת addresses_missing_coordinates
```

### הוספת קואורדינטות ידניות:
```javascript
// Frontend  
const response = await fetch('/api/add-manual-coordinates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        missing_id: 5,
        lat: 32.0853,
        lon: 34.7818,
        neighborhood: 'תל אביב',
        added_by: 'admin'
    })
});
```

### קבלת כל הכתובות למפה:
```javascript
// Frontend
const response = await fetch('/api/addresses-for-map');
const data = await response.json();
// מחזיר כתובות משתי הטבלאות בפורמט אחיד
```

## 🔄 לוגיקת העבודה

1. **כתובת חדשה מגיעה** → קריאה ל-`/api/process-new-address`
2. **Backend מנסה גיאוקודינג**:
   - **הצליח** → שמירה ב-`addresses` עם קואורדינטות
   - **נכשל** → שמירה ב-`addresses_missing_coordinates`
3. **מנהל רואה כתובות ללא קואורדינטות** → קריאה ל-`/api/addresses-needing-manual`
4. **מנהל מוסיף קואורדינטות ידניות** → קריאה ל-`/api/add-manual-coordinates`
5. **המפה מציגה הכל** → קריאה ל-`/api/addresses-for-map`

## 📱 עדכון Frontend

עדכן את `config.js`:
```javascript
const API_ENDPOINTS = {
    // מפת כל הכתובות
    addressesForMap: `${API_BASE_URL}/api/addresses-for-map`,
    
    // ניהול קואורדינטות ידניות
    needingManual: `${API_BASE_URL}/api/addresses-needing-manual`,
    addManualCoords: `${API_BASE_URL}/api/add-manual-coordinates`,
    
    // הוספת כתובת חדשה
    processNewAddress: `${API_BASE_URL}/api/process-new-address`,
    
    // אחרים...
    allAddresses: `${API_BASE_URL}/api/addresses-array`,
    missingCoordinates: `${API_BASE_URL}/api/missing-coordinates`
};
```

## 🧪 בדיקות

### בדיקת הטבלאות:
```bash
curl https://your-backend-url/api/test-connection
```

### בדיקת כתובות למפה:
```bash
curl https://your-backend-url/api/addresses-for-map
```

### הוספת כתובת לבדיקה:
```bash
curl -X POST https://your-backend-url/api/process-new-address \
  -H "Content-Type: application/json" \
  -d '{"address": "רחוב דיזנגוף 1 תל אביב"}'
```

## 🛠️ תחזוקה

- כתובות שנכשלו בגיאוקודינג יופיעו ב-`/api/addresses-needing-manual`
- ניתן להוסיף קואורדינטות ידניות דרך `/api/add-manual-coordinates`
- המפה תציג אוטומטית כתובות משתי הטבלאות דרך `/api/addresses-for-map`
