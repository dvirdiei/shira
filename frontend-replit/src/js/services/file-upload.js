// קובץ לניהול העלאת קבצים ופונקציות ניהול
// file-upload.js

console.log('📁 Frontend file-upload.js נטען');

// בדיקת תלויות
setTimeout(() => {
    if (typeof API_ENDPOINTS === 'undefined') {
        console.error('❌ API_ENDPOINTS לא מוגדר - ודא שconfig.js נטען ראשון');
    } else {
        console.log('✅ API_ENDPOINTS זמין:', Object.keys(API_ENDPOINTS).join(', '));
    }
}, 100);

/**
 * מטפל בהעלאת קובץ TXT
 */
async function handleFileUpload(event) {
    const file = event.target.files[0];
    
    if (!file) {
        alert('לא נבחר קובץ');
        return;
    }
    
    if (!file.name.toLowerCase().endsWith('.txt')) {
        alert('יש לבחור קובץ TXT בלבד');
        return;
    }
    
    try {
        updateDebug('📁 מעלה קובץ: ' + file.name);
        
        // קריאת תוכן הקובץ
        const content = await readFileContent(file);
        
        // פיצול לשורות וניקוי
        const lines = content.split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0);
        
        if (lines.length === 0) {
            alert('הקובץ ריק או לא מכיל כתובות תקינות');
            return;
        }
        
        updateDebug(`📋 נמצאו ${lines.length} כתובות בקובץ`);
        
        // הכנת נתונים לשליחה
        const addresses = lines.map(line => ({ address: line }));
        
        // שליחה לשרת
        const success = await uploadAddressesToServer(addresses);
        
        if (success) {
            alert(`✅ הועלו בהצלחה ${lines.length} כתובות מהקובץ!`);
            updateDebug('✅ העלאת הקובץ הושלמה בהצלחה');
            
            // רענון המפה לטעינת הכתובות החדשות
            console.log('🔄 מנסה לרענן את המפה...');
            updateDebug('🔄 מרענן את המפה...');
            
            // אפשרות 1: רענון מלא של המפה
            if (typeof initializeAddressMap === 'function' && typeof map !== 'undefined') {
                try {
                    console.log('🔁 מרענן את המפה עם כתובות חדשות...');
                    await initializeAddressMap(map);
                    console.log('✅ המפה רוענה בהצלחה');
                    updateDebug('✅ המפה רוענה בהצלחה');
                } catch (err) {
                    console.error('❌ שגיאה ברענון המפה:', err);
                    updateDebug('❌ שגיאה ברענון המפה: ' + err.message);
                }
            } 
            // אפשרות 2: טעינת כתובות מחדש
            else if (typeof loadAddressesFromCSV === 'function') {
                try {
                    console.log('🔁 טוען כתובות מחדש...');
                    const newAddresses = await loadAddressesFromCSV();
                    console.log('✅ כתובות נטענו מחדש:', newAddresses.length);
                    updateDebug(`✅ נטענו ${newAddresses.length} כתובות מהשרת`);
                } catch (err) {
                    console.error('❌ שגיאה בטעינת כתובות:', err);
                    updateDebug('❌ שגיאה בטעינת כתובות: ' + err.message);
                }
            } 
            // אפשרות 3: רענון הדף
            else {
                console.warn('⚠️ לא נמצאה פונקציה לרענון המפה - מרענן את הדף');
                updateDebug('⚠️ מרענן את הדף לעדכון המפה...');
                setTimeout(() => {
                    location.reload();
                }, 2000);
            }
        } else {
            alert('❌ שגיאה בהעלאת הכתובות לשרת');
            updateDebug('❌ העלאת הקובץ נכשלה');
        }

        
    } catch (error) {
        console.error('שגיאה בהעלאת הקובץ:', error);
        alert('❌ שגיאה בעיבוד הקובץ: ' + error.message);
        updateDebug('❌ שגיאה: ' + error.message);
    }
    
    // איפוס ה-input
    event.target.value = '';
}

/**
 * קורא את תוכן קובץ טקסט
 */
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            resolve(e.target.result);
        };
        
        reader.onerror = function() {
            reject(new Error('שגיאה בקריאת הקובץ'));
        };
        
        reader.readAsText(file, 'utf-8');
    });
}

/**
 * שולח כתובות לשרת בבת אחת
 */
async function uploadAddressesToServer(addresses) {
    try {
        updateDebug('🌐 שולח כתובות לשרת...');
        
        // בדיקה שAPI_ENDPOINTS מוגדר
        if (typeof API_ENDPOINTS === 'undefined' || !API_ENDPOINTS.batchGeocode) {
            throw new Error('API_ENDPOINTS לא מוגדר - ודא שconfig.js נטען ראשון');
        }
        
        console.log('📡 שולח בקשה ל:', API_ENDPOINTS.batchGeocode);
        console.log('📋 נתונים לשליחה:', { addresses: addresses });
        
        const response = await fetch(API_ENDPOINTS.batchGeocode, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ addresses: addresses })
        });
        
        console.log('📬 סטטוס תגובה:', response.status, response.statusText);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('❌ שגיאת שרת מפורטת:', errorText);
            throw new Error(`שגיאת שרת: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        
        console.log('📋 תגובה מהשרת:', result); // לוג לדיבוג
        
        if (result.success) {
            // בדיקה אם יש summary
            if (result.summary) {
                updateDebug(`✅ הועלו בהצלחה: נמצאו ${result.summary.found || 0}, לא נמצאו ${result.summary.not_found || 0}`);
            } else {
                updateDebug(`✅ הועלו בהצלחה: ${result.message || 'פעולה הושלמה'}`);
            }
            return true;
        } else {
            updateDebug('❌ שגיאה מהשרת: ' + (result.message || result.error || 'שגיאה לא ידועה'));
            return false;
        }
        
    } catch (error) {
        console.error('שגיאה בשליחה לשרת:', error);
        updateDebug('❌ שגיאת רשת: ' + error.message);
        return false;
    }
}

/**
 * מציג דף סיכום
 */
function showSummary() {
    updateDebug('📊 פותח דף סיכום');
    
    // בדיקה אם יש דף סיכום נפרד
    const summaryPage = 'summary.html';
    
    // פתיחה בחלון/טאב חדש
    window.open(summaryPage, '_blank');
}

/**
 * איפוס כל הנתונים
 */
async function resetAllData() {
    const confirmed = confirm('⚠️ האם אתה בטוח שברצונך למחוק את כל הנתונים?\n\nפעולה זו תמחק:\n• את כל הכתובות\n• את כל הקואורדינטות\n• את כל ההיסטוריה\n\nהפעולה בלתי הפיכה!');
    
    if (!confirmed) {
        return;
    }
    
    // בקשת אישור נוסף
    const doubleConfirm = confirm('❗ אישור אחרון!\n\nלמחוק את כל הנתונים?');
    
    if (!doubleConfirm) {
        return;
    }
    
    try {
        updateDebug('🗑️ מבצע איפוס נתונים...');
        
        // בדיקה שAPI_ENDPOINTS מוגדר
        if (typeof API_ENDPOINTS === 'undefined' || !API_ENDPOINTS.resetData) {
            throw new Error('API_ENDPOINTS לא מוגדר - ודא שconfig.js נטען ראשון');
        }
        
        // שליחה לשרת לאיפוס
        const response = await fetch(API_ENDPOINTS.resetData, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת שרת: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ כל הנתונים נמחקו בהצלחה!');
            updateDebug('✅ איפוס הושלם');
            
            // רענון המפה
            if (typeof initializeAddressMap === 'function' && typeof map !== 'undefined') {
                try {
                    console.log('🔁 מרענן את המפה אחרי איפוס...');
                    await initializeAddressMap(map);
                    console.log('✅ המפה רוענה בהצלחה');
                } catch (err) {
                    console.error('❌ שגיאה ברענון המפה:', err);
                    updateDebug('❌ שגיאה ברענון המפה: ' + err.message);
                }
            } else if (typeof loadAddressesFromCSV === 'function') {
                try {
                    console.log('🔁 טוען כתובות מחדש אחרי איפוס...');
                    await loadAddressesFromCSV();
                    console.log('✅ כתובות נטענו מחדש');
                } catch (err) {
                    console.error('❌ שגיאה בטעינת כתובות:', err);
                    updateDebug('❌ שגיאה בטעינת כתובות: ' + err.message);
                }
            }
            
            // רענון הדף
            setTimeout(() => {
                location.reload();
            }, 1000);
            
        } else {
            alert('❌ שגיאה באיפוס הנתונים: ' + result.message);
            updateDebug('❌ שגיאה באיפוס: ' + result.message);
        }
        
    } catch (error) {
        console.error('שגיאה באיפוס:', error);
        alert('❌ שגיאה באיפוס הנתונים: ' + error.message);
        updateDebug('❌ שגיאת איפוס: ' + error.message);
    }
}

// פונקציה לעדכון המידע לדיבוג (אם לא קיימת)
if (typeof updateDebug === 'undefined') {
    function updateDebug(message) {
        console.log('🔧 Debug:', message);
        const debugElement = document.getElementById('debugInfo');
        if (debugElement) {
            const timestamp = new Date().toLocaleTimeString('he-IL');
            debugElement.innerHTML += `<br>[${timestamp}] ${message}`;
            // גלילה למטה
            debugElement.scrollTop = debugElement.scrollHeight;
        }
    }
}

// ייצוא פונקציות לגישה גלובלית
window.handleFileUpload = handleFileUpload;
window.showSummary = showSummary;
window.resetAllData = resetAllData;

// הודעת טעינה
console.log('📁 Frontend file-upload.js נטען בהצלחה');
