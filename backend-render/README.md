# 🔧 Backend - הנוסע המתמיד
**Backend API ב-Render עם Database ו-CORS לFrontend**

## 📁 מבנה הקבצים
```
backend-render/
├── main.py             # שרת Flask ראשי
├── requirements.txt    # תלויות Python
├── Procfile           # הוראות Render
├── runtime.txt        # גרסת Python
├── PYTHON/
│   ├── __init__.py    # Package init
│   ├── api_handlers.py # לוגיקת API
│   └── routes.py      # נתבים
└── database/
    ├── found_addresses.csv
    ├── not_found_addresses.csv
    ├── future_use.csv
    └── deleted_addresses.csv
```

## 🚀 העלאה ל-Render

### שלב 1: GitHub Repository
```bash
# צור repository חדש ב-GitHub בשם: 
# הנוסע-המתמיד-backend

# העלה את כל התוכן של backend-render/
git init
git add .
git commit -m "Backend ready for Render"
git push origin main
```

### שלב 2: יצירת Web Service ב-Render
1. **היכנס ל-https://render.com**
2. **לחץ "New +" → "Web Service"**
3. **חבר את GitHub Repository**
4. **הגדרות:**
   ```
   Name: הנוסע-המתמיד-backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn main:app
   ```

### שלב 3: Deploy
- לחץ **"Create Web Service"**
- המתן 3-5 דקות לבנייה
- תקבל URL כמו: `https://הנוסע-המתמיד-backend.onrender.com`

### שלב 4: בדיקת תקינות
ביקור ב:
- `https://YOUR-BACKEND.onrender.com/` - דף הבית
- `https://YOUR-BACKEND.onrender.com/health` - בדיקת תקינות
- `https://YOUR-BACKEND.onrender.com/api/all-addresses` - נתוני כתובות

## 📡 API Endpoints

### GET /
```json
{
    "service": "הנוסע המתמיד Backend API",
    "status": "online",
    "endpoints": [...],
    "message": "Backend מוכן לשירות! 🚀"
}
```

### GET /api/all-addresses
מחזיר את כל הכתובות עם קואורדינטות
```json
[
    {
        "address": "הרב ריינס ירושלים",
        "lat": 31.7903429,
        "lon": 35.1940735,
        "neighborhood": "Givat Shaul",
        "visited": false,
        "source": "geocoded"
    }
]
```

### POST /api/toggle-visited
עדכון סטטוס ביקור
```json
{
    "address": "שם הכתובת",
    "action": "mark" // או "unmark"
}
```

### POST /api/delete-address
מחיקת כתובת
```json
{
    "address": "שם הכתובת"
}
```

## 🔒 אבטחה ו-CORS

Backend מוגדר עם:
- **CORS פתוח** לכל דומיין (`origins=['*']`)
- **Headers מותאמים** לעבודה עם Frontend
- **JSON responses** בלבד

### לשיפור האבטחה (Production):
```python
# במקום origins=['*'], הגדר:
CORS(app, origins=['https://YOUR-FRONTEND.repl.co'])
```

## 💾 Database (CSV Files)

### ⚠️ הגבלות Render חינמי:
- קבצי CSV נשמרים **זמנית בזיכרון**
- אחרי רענון שרת - שינויים **עלולים להיאבד**
- שרת "נרדם" אחרי 15 דקות חוסר פעילות

### 📊 קבצי נתונים:
- `found_addresses.csv` - כתובות עם קואורדינטות
- `not_found_addresses.csv` - כתובות ללא קואורדינטות
- `future_use.csv` - שימוש עתידי
- `deleted_addresses.csv` - נקודות שנמחקו (עם תאריך)

## 🔄 עדכון Database לשירות מאובטח

### אפשרות 1: PostgreSQL ב-Render
```bash
# הוסף PostgreSQL database ב-Render
# עדכן הקוד לעבוד עם SQL במקום CSV
```

### אפשרות 2: Supabase (מומלץ)
```bash
# עבור ל-Supabase.com
# יצור טבלאות PostgreSQL
# חיבור עם API מאובטח
```

### אפשרות 3: Firebase
```bash
# עבור ל-Firebase.google.com  
# יצור Firestore Database
# חיבור עם SDK
```

## 🔧 ניפוי שגיאות

### לוגים ב-Render:
1. היכנס ל-Dashboard
2. בחר את השירות
3. לחץ "Logs"

### בדיקות מקומיות:
```bash
# הרצה מקומית
python main.py

# בדיקת endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/all-addresses
```

## 📈 ביצועים

### Render חינמי:
- **זמן התעוררות**: 30 שניות מ"שינה"
- **זיכרון**: 512MB
- **CPU**: Shared
- **Storage**: זמני

### לשיפור ביצועים:
- שדרג לRender Pro ($7/חודש)
- עבור לDatabase חיצוני
- הוסף caching

---

**Backend מוכן לפעולה! העלה ל-Render וקבל URL לFrontend! 🚀**
