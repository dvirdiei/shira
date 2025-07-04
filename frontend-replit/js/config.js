// קובץ הגדרות Frontend
// config.js

// 🌐 כתובת ה-Backend API ב-Render
const API_BASE_URL = 'http://localhost:5000'; // 🔥 להרצה מקומית!

// 🔧 הגדרות API
const API_ENDPOINTS = {
    allAddresses: `${API_BASE_URL}/api/all-addresses`,
    missingCoordinates: `${API_BASE_URL}/api/missing-coordinates`,
    toggleVisited: `${API_BASE_URL}/api/toggle-visited`,
    deleteAddress: `${API_BASE_URL}/api/delete-address`
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
