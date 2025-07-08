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
 * מטפל בהעלאת קובץ TXT עם שירות הגיאוקודינג המתקדם
 */
async function handleFileUpload(event) {
    const file = event.target.files[0];
    
    if (!file) {
        alert('לא נבחר קובץ');
        return;
    }
    
    if (!file.name.toLowerCase().endsWith('.txt') && !file.name.toLowerCase().endsWith('.csv')) {
        alert('רק קבצי טקסט (.txt) או CSV (.csv) מותרים');
        return;
    }
    
    // הצגת מסך הטעינה
    showLoadingOverlay();
    updateLoadingMessage(`מעבד קובץ: ${file.name}`);
    
    try {
        updateDebug('📁 מעלה קובץ: ' + file.name);
        
        // יצירת FormData לשליחת הקובץ
        const formData = new FormData();
        formData.append('file', file);
        
        console.log('📤 שולח קובץ לשרת:', file.name);
        
        // שליחת הקובץ לשרת
        const response = await fetch(`${API_BASE_URL}/api/upload-addresses-file`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ הקובץ עובד בהצלחה:', result);
            updateDebug(`✅ הקובץ עובד: ${result.addresses_count} כתובות`);
            
            // הצגת תוצאות
            showUploadSuccess(result);
            
            // רענון המפה
            setTimeout(() => {
                hideLoadingOverlay();
                if (typeof initializeAddressMap === 'function' && typeof map !== 'undefined') {
                    initializeAddressMap(map);
                } else {
                    // אם אין מפה, פשוט רענן את הדף
                    location.reload();
                }
            }, 2000);
            
        } else {
            console.error('❌ שגיאה בעיבוד הקובץ:', result.error);
            updateDebug(`❌ שגיאה: ${result.error}`);
            showUploadError(result.error);
        }
        
    } catch (error) {
        console.error('❌ שגיאה בשליחת הקובץ:', error);
        updateDebug(`❌ שגיאה בשליחה: ${error.message}`);
        showUploadError('שגיאה בשליחת הקובץ: ' + error.message);
    }
    
    // איפוס שדה העלאת הקובץ
    event.target.value = '';
}

/**
 * הצגת מסך הטעינה
 */
function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    const status = document.getElementById('uploadStatus');
    
    if (overlay) {
        overlay.style.display = 'flex';
    }
    if (status) {
        status.style.display = 'none';
        status.className = 'upload-status';
    }
}

/**
 * הסתרת מסך הטעינה
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

/**
 * עדכון הודעת הטעינה
 */
function updateLoadingMessage(message) {
    const messageElement = document.getElementById('loadingMessage');
    if (messageElement) {
        messageElement.textContent = message;
    }
}

/**
 * הצגת הודעת הצלחה
 */
function showUploadSuccess(result) {
    const status = document.getElementById('uploadStatus');
    
    if (!status) return;
    
    let message = `✅ הקובץ עובד בהצלחה!\n`;
    message += `📄 קובץ: ${result.filename}\n`;
    message += `📊 כתובות שנמצאו: ${result.addresses_count}\n`;
    
    if (result.geocoding_result) {
        message += `✅ הצלחה: ${result.geocoding_result.successful || 0}\n`;
        message += `💾 נשמרו: ${result.geocoding_result.saved || 0}\n`;
        
        if (result.geocoding_result.failed > 0) {
            message += `❌ כשלון: ${result.geocoding_result.failed}\n`;
        }
    }
    
    status.className = 'upload-status success';
    status.style.display = 'block';
    status.innerHTML = message.replace(/\n/g, '<br>');
    
    updateLoadingMessage('הושלם בהצלחה! רענון המפה...');
}

/**
 * הצגת הודעת שגיאה
 */
function showUploadError(error) {
    const status = document.getElementById('uploadStatus');
    
    if (!status) return;
    
    status.className = 'upload-status error';
    status.style.display = 'block';
    status.innerHTML = `❌ שגיאה בעיבוד הקובץ:<br>${error}`;
    
    updateLoadingMessage('עיבוד נכשל');
    
    // הסתרה אוטומטית לאחר 5 שניות
    setTimeout(() => {
        hideLoadingOverlay();
    }, 5000);
}

/**
 * מציג דף סיכום
 */
function showSummary() {
    updateDebug('📊 פותח דף סיכום');
    
    // לעתיד - נוכל לפתוח דף סיכום נפרד
    alert('📊 פונקציית סיכום עדיין לא מוכנה');
}

/**
 * איפוס כל הנתונים
 */
async function resetAllData() {
    const confirmed = confirm('⚠️ האם אתה בטוח שברצונך למחוק את כל הנתונים?\n\nפעולה זו תמחק:\n• את כל הכתובות\n• את כל הקואורדינטות\n• את כל ההיסטוריה\n\nהפעולה בלתי הפיכה!');
    
    if (!confirmed) {
        return;
    }
    
    try {
        updateDebug('🗑️ מבצע איפוס נתונים...');
        
        // שליחה לשרת לאיפוס
        const response = await fetch(`${API_BASE_URL}/api/reset-all-data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת שרת: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ כל הנתונים נמחקו בהצלחה!');
            updateDebug('✅ איפוס הושלם');
            
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
