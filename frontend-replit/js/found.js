// Frontend Main Loader - טעינת כל המודולים
// found.js

console.log('🚀 Frontend found.js נטען - מערכת מפות הביקורים');

// בדיקה שכל הרכיבים נטענו
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 בודק שכל הרכיבים נטענו...');
    
    const requiredFunctions = [
        'loadAddressesFromCSV',
        'createCustomIcons', 
        'initializeAddressMap',
        'toggleVisitStatus',
        'deleteAddress',
        'openInGoogleMaps',
        'showNotification'
    ];
    
    const missingFunctions = requiredFunctions.filter(func => typeof window[func] !== 'function');
    
    if (missingFunctions.length > 0) {
        console.warn('⚠️ פונקציות חסרות:', missingFunctions);
        showNotification('שגיאה בטעינת רכיבי המערכת', 'error');
    } else {
        console.log('✅ כל הרכיבים נטענו בהצלחה');
    }
    
    // בדיקת חיבור ל-Backend
    if (typeof API_BASE_URL !== 'undefined') {
        if (API_BASE_URL.includes('YOUR-BACKEND')) {
            console.warn('⚠️ כתובת Backend לא עודכנה ב-config.js');
            showNotification('נדרש לעדכן כתובת Backend ב-config.js', 'warning');
        } else {
            console.log('🌐 Backend מוגדר:', API_BASE_URL);
        }
    }
});

// ייצוא מידע על המערכת
window.found = {
    version: '4.0 - Frontend/Backend Split',
    loaded: true,
    message: 'מערכת מפות הביקורים - Frontend ב-Replit',
    modules: ['config', 'data-loader', 'map-markers', 'user-actions'],
    backend: typeof API_BASE_URL !== 'undefined' ? API_BASE_URL : 'לא מוגדר'
};
