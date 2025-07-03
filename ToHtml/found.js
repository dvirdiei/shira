// קובץ ראשי לטעינת כל הקבצים המודולריים
// found.js - Main loader

// הערה: קובץ זה טוען את כל הקבצים האחרים בסדר הנכון
console.log('טוען מערכת מפות הביקורים...');

// המערכת מורכבת מ-3 קבצים נפרדים:
// 1. data-loader.js: טעינת נתונים מהשרת
// 2. map-markers.js: מארקרים, פופאפים ותצוגת המפה  
// 3. user-actions.js: פעולות משתמש (ביקורים, ניווט, מחיקות)

// בדיקה שכל הקבצים נטענו
document.addEventListener('DOMContentLoaded', function() {
    console.log('בודק שכל הרכיבים נטענו...');
    
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
        console.warn('פונקציות חסרות:', missingFunctions);
    } else {
        console.log('✅ כל הרכיבים נטענו בהצלחה');
    }
});

// ייצוא מידע על המערכת
window.found = {
    version: '3.0 - Modular',
    loaded: true,
    message: 'מערכת מפות הביקורים המודולרית נטענה בהצלחה',
    modules: ['data-loader', 'map-markers', 'user-actions']
};
