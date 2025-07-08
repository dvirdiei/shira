// קובץ הגדרות Frontend
// config.js

// 🌐 כתובת ה-Backend API
// לפרודקשן ב-Render (עדכן את זה לשם השרת שלך): 
const RENDER_API_URL = 'https://shira-bf24.onrender.com';  // 🔄 עדכן את זה!

// לפיתוח מקומי:
const LOCAL_API_URL = 'http://localhost:5000';

// בחירה אוטומטית של ה-API על בסיס המיקום
// עבור פיתוח מקומי - השתמש ב-localhost
const isLocalDevelopment = window.location.hostname === 'localhost' || 
                           window.location.hostname === '127.0.0.1' || 
                           window.location.port === '3000';

const API_BASE_URL = isLocalDevelopment ? LOCAL_API_URL : RENDER_API_URL;

console.log('🌐 משתמש ב-API:', API_BASE_URL);
console.log('🔍 hostname:', window.location.hostname);
console.log('🔍 port:', window.location.port);
console.log('🏠 מצב מקומי:', isLocalDevelopment);

// 🔧 הגדרות API
const API_ENDPOINTS = {
    // === מערכת שתי הטבלאות החדשה ===
    // קריאה וניהול כתובות - פורמט חדש
    addressesForMap: `${API_BASE_URL}/api/addresses-for-map`,        // 🆕 כל הכתובות למפה (משתי הטבלאות)
    addressesNeedingManual: `${API_BASE_URL}/api/addresses-needing-manual`, // 🆕 כתובות שצריכות הזנה ידנית
    addManualCoordinates: `${API_BASE_URL}/api/add-manual-coordinates`,     // 🆕 הוספת קואורדינטות ידניות
    processNewAddress: `${API_BASE_URL}/api/process-new-address`,           // 🆕 עיבוד כתובת חדשה
    
    // endpoints ישנים (תואמות לאחור)
    allAddresses: `${API_BASE_URL}/api/addresses-array`,            
    addresses: `${API_BASE_URL}/api/addresses`,                 
    missingCoordinates: `${API_BASE_URL}/api/missing-coordinates`,
    toggleVisited: `${API_BASE_URL}/api/toggle-visited`,
    deleteAddress: `${API_BASE_URL}/api/delete-address`,
    
    // הוספת כתובות חדשות וגיאוקודינג
    addAddress: `${API_BASE_URL}/api/add-address`,
    batchGeocode: `${API_BASE_URL}/api/batch-geocode`,
    retryGeocoding: `${API_BASE_URL}/api/retry-geocoding`,
    
    // איפוס נתונים וסטטיסטיקות
    resetData: `${API_BASE_URL}/api/reset-data`,
    statistics: `${API_BASE_URL}/api/statistics`,
    testConnection: `${API_BASE_URL}/api/test-connection`,
    health: `${API_BASE_URL}/api/health`
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
console.log('🔍 Testing connection to:', API_ENDPOINTS.health);

// בדיקת חיבור אוטומטית לBackend
fetch(API_ENDPOINTS.health)
    .then(response => {
        console.log('✅ Backend connection test:', response.status);
        if (response.ok) {
            console.log('🚀 Backend זמין ומוכן!');
        }
        return response.json();
    })
    .then(data => {
        console.log('📊 Backend response:', data);
    })
    .catch(error => {
        console.error('❌ Backend connection failed:', error);
        console.error('💡 Tip: ודא שהBackend רץ על:', API_BASE_URL);
    });

// הגדרה גלובלית כדי לוודא שזמין לכל הקבצים
window.API_BASE_URL = API_BASE_URL;
window.API_ENDPOINTS = API_ENDPOINTS;
window.MAP_CONFIG = MAP_CONFIG;
window.UI_CONFIG = UI_CONFIG;
