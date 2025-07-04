// קובץ לניהול העלאת קבצים ופונקציות ניהול
// file-upload.js

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
            // רענון המפה לטעינת הכתובות החדשות
            if (typeof loadAddresses === 'function') {
                loadAddresses();
            }
        } else {
            alert('❌ שגיאה בהעלאת הכתובות לשרת');
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
        
        const response = await fetch(`${API_BASE_URL}/api/batch-geocode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ addresses: addresses })
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת שרת: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            updateDebug(`✅ הועלו בהצלחה: נמצאו ${result.summary.found}, לא נמצאו ${result.summary.not_found}`);
            return true;
        } else {
            updateDebug('❌ שגיאה מהשרת: ' + result.message);
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
        
        // שליחה לשרת לאיפוס
        const response = await fetch(`${API_BASE_URL}/api/reset-all-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
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
            if (typeof loadAddresses === 'function') {
                loadAddresses();
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
        console.log(message);
        const debugElement = document.getElementById('debugInfo');
        if (debugElement) {
            debugElement.innerHTML += '<br>' + message;
        }
    }
}
