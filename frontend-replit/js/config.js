// קובץ הגדרות Frontend
// config.js

// 🌐 כתובת ה-Backend API
// לפרודקשן ב-Render: 
const RENDER_API_URL = 'https://shira-bf24.onrender.com';  // ✅ הקישור האמיתי של הבאק אנד

// לפיתוח מקומי:
const LOCAL_API_URL = 'http://localhost:5000';

// בחירה אוטומטית של ה-API על בסיס המיקום
// בגלל שה-RENDER API עובד מעולה, נשתמש בו תמיד
const API_BASE_URL = RENDER_API_URL;

console.log('🌐 משתמש ב-API:', API_BASE_URL);
console.log('🔍 hostname:', window.location.hostname);
console.log('🔍 port:', window.location.port);

// 🔧 הגדרות API
const API_ENDPOINTS = {
    // קריאה וניהול כתובות קיימות
    allAddresses: `${API_BASE_URL}/api/all-addresses`,
    missingCoordinates: `${API_BASE_URL}/api/missing-coordinates`,
    toggleVisited: `${API_BASE_URL}/api/toggle-visited`,
    deleteAddress: `${API_BASE_URL}/api/delete-address`,
    
    // הוספת כתובות חדשות וגיאוקודינג
    addAddress: `${API_BASE_URL}/api/add-address`,
    batchGeocode: `${API_BASE_URL}/api/batch-geocode`,
    retryGeocoding: `${API_BASE_URL}/api/retry-geocoding`,
    
    // איפוס נתונים
    resetData: `${API_BASE_URL}/api/reset-data`
};

// 🗺️ הגדרות מפה
const MAP_CONFIG = {
    center: [31.7683, 35.2137], // ירושלים
    zoom: 13,
    zoomControl: false // ללא כפתורי + ו -
};

// 🎨 הגדרות עיצוב
const UI_CONFIG = {
    popupMaxWidth: 300,
    notificationDuration: 3000, // 3 שניות
    summaryAutoHide: true
};

console.log('⚙️ Frontend config טעון - API Base:', API_BASE_URL);
console.log('🗺️ MAP_CONFIG זמין:', typeof MAP_CONFIG !== 'undefined');
console.log('📡 API_ENDPOINTS זמין:', typeof API_ENDPOINTS !== 'undefined');

// הגדרה גלובלית כדי לוודא שזמין לכל הקבצים
window.API_BASE_URL = API_BASE_URL;
window.API_ENDPOINTS = API_ENDPOINTS;
window.MAP_CONFIG = MAP_CONFIG;
window.UI_CONFIG = UI_CONFIG;
