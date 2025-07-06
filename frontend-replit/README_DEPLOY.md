# הנוסע המתמיד - פרונט אנד 🌐

## הפעלה מהירה ב-Replit:

1. **העלה את כל הקבצים ל-Replit**
2. **לחץ על כפתור "Run"** 
3. **זהו! האתר יעבוד מיד** 🚀

## מה יקרה כשתלחץ Run:
- השרת יתחיל על פורט 3000 
- האתר יהיה זמין ב-URL של Replit
- החיבור לבאק אנד יעבוד אוטומטית

## הפעלה מקומית (אופציונלי):
```bash
python main.py
```

## תכונות:
- 📱 מותאם לטלפון נייד
- 🗺️ מפה אינטראקטיבית של ירושלים  
- 📁 העלאת קובץ TXT עם כתובות
- 📊 סיכום נתונים
- 🗑️ איפוס נתונים
- 🌐 חיבור אוטומטי לבאק אנד: https://shira-bf24.onrender.com

## קבצים חשובים:
- `main.py` - שרת הפרונט אנד ✨ **חדש!**
- `index.html` - דף ראשי
- `js/config.js` - הגדרות API (מוגדר אוטומטית)
- `.replit` - הגדרות Replit

---

# מדריך פריסה מלא 📋

## מבנה הפרויקט
```
📦 אתר/
├── 🖥️ backend-render/          # Backend Flask ל-Render ✅ פועל
│   └── URL: https://shira-bf24.onrender.com/
└── 🌐 frontend-replit/         # Frontend סטטי ל-Replit ✨ מוכן!
    ├── main.py                 # שרת Python פשוט
    ├── index.html              # דף ראשי
    ├── .replit                 # הגדרות Replit
    └── js/                     # קבצי JavaScript
```

## 🔧 הגדרות אוטומטיות
- ✅ הקוד מזהה אוטומטית אם הוא רץ ב-localhost או ב-production
- ✅ ב-localhost: משתמש ב-`http://localhost:5000`
- ✅ ב-production: משתמש ב-`https://shira-bf24.onrender.com`
- ✅ שרת Python פשוט ומותאם ל-Replit

## 🎮 תכונות הפרונט אנד

### כפתורי ניהול (מותאמים לטלפון):
- 📊 **סיכום**: הצגת סטטיסטיקות נתונים
- 📁 **העלאת קובץ**: העלאת קובץ TXT עם כתובות
- 🗑️ **איפוס**: מחיקת כל הנתונים

### תכונות המפה:
- 🗺️ מפה אינטראקטיבית של ירושלים
- 📍 סמנים צבעוניים לכתובות
- 🎯 זום וניווט
- 📱 מותאם לטלפון נייד

## 📡 API Endpoints זמינים

### קריאת נתונים:
- `GET /api/all-addresses` - כל הכתובות
- `GET /api/missing-coordinates` - כתובות ללא קואורדינטות

### ניהול כתובות:
- `POST /api/add-address` - הוספת כתובת חדשה
- `POST /api/batch-geocode` - הוספת כתובות מרובות
- `PUT /api/toggle-visited` - סימון ביקור
- `DELETE /api/delete-address` - מחיקת כתובת

### פונקציות מתקדמות:
- `POST /api/retry-geocoding` - ניסיון חוזר לחיפוש קואורדינטות
- `DELETE /api/reset-data` - איפוס כל הנתונים

## 🔐 אבטחה
- ✅ מפתח ה-API ב-.env (לא עולה לגיט)
- ✅ CORS מוגדר נכון
- ✅ Headers אבטחה

## 🚀 פריסה מהירה

### Frontend ל-Replit:
1. העלה את תיקיית `frontend-replit/` ל-Replit
2. לחץ "Run"
3. זהו! האתר יעבוד מיד

### Backend ב-Render:
- כבר פועל ב: https://shira-bf24.onrender.com/

## 📱 מותאם לטלפון
- כפתורים גדולים ונוחים
- עיצוב responsive
- מהירות טעינה מיטבית

---
**הכל מוכן לשימוש מיידי! פשוט לחץ Run ב-Replit** 🎉
