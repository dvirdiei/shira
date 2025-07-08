// Frontend Data Loader - קריאות API לBackend
// data-loader.js

console.log('📊 Frontend data-loader.js נטען בהצלחה');

// בדיקת תלויות
if (typeof API_BASE_URL === 'undefined') {
    console.error('❌ API_BASE_URL לא מוגדר - ודא שconfig.js נטען ראשון');
}
if (typeof API_ENDPOINTS === 'undefined') {
    console.error('❌ API_ENDPOINTS לא מוגדר - ודא שconfig.js נטען ראשון');
} else {
    console.log('🔗 API_BASE_URL:', API_BASE_URL);
    console.log('🔗 API_ENDPOINTS:', API_ENDPOINTS);
}

// פונקציה לטעינת נתוני הכתובות מה-Backend API - מערכת שתי טבלאות
async function loadAddressesFromCSV() {
    try {
        console.log("🚀 טוען נתוני כתובות מה-Backend (מערכת שתי טבלאות)...");
        console.log("📡 URL לקריאה:", API_ENDPOINTS.addressesForMap);
        
        // וידוא שAPI_ENDPOINTS מוגדר
        if (typeof API_ENDPOINTS === 'undefined' || !API_ENDPOINTS.addressesForMap) {
            throw new Error('API_ENDPOINTS לא מוגדר - ודא שconfig.js נטען ראשון');
        }
        
        // קריאה ל-Backend API ב-Render - endpoint חדש שמחזיר כתובות משתי הטבלאות
        const response = await fetch(API_ENDPOINTS.addressesForMap, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        console.log("📬 תגובה התקבלה:", response.status, response.statusText);
        
        if (!response.ok) {
            throw new Error(`שגיאת Backend: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // בדיקה שקיבלנו תגובה תקינה
        if (!result.success) {
            console.error('🔍 תגובה מהBackend:', result);
            throw new Error(`Backend error: ${result.error || 'Unknown error'}`);
        }
        
        const addresses = result.addresses;
        
        // בדיקה שקיבלנו מערך
        if (!Array.isArray(addresses)) {
            console.error('🔍 תגובה מהBackend:', result);
            throw new Error('Backend לא החזיר מערך כתובות (בדוק את הendpoint)');
        }
        
        console.log(`✅ נטענו ${addresses.length} כתובות מהBackend (משתי הטבלאות)`);
        console.log("📋 דוגמה לנתונים:", addresses.slice(0, 2));
        
        // מיון כתובות לפי מקור
        const geocodedAddresses = addresses.filter(addr => addr.source === 'geocoded');
        const manualAddresses = addresses.filter(addr => addr.source === 'manual');
        const correctedAddresses = addresses.filter(addr => addr.source === 'manual_corrected');
        
        console.log(`📍 ${geocodedAddresses.length} כתובות מגיאוקודינג`);
        console.log(`✋ ${manualAddresses.length} כתובות ידניות`);
        console.log(`🔧 ${correctedAddresses.length} כתובות מתוקנות`);
        
        return addresses;
        
    } catch (error) {
        console.error("❌ שגיאה בטעינת הכתובות מה-Backend:", error);
        console.error("❌ פרטי השגיאה:", error.message);
        console.error("❌ סוג השגיאה:", error.name);
        
        // הצגת הודעת שגיאה למשתמש
        if (typeof showNotification === 'function') {
            showNotification(`שגיאה בחיבור לשרת: ${error.message}`, 'error');
        } else {
            console.warn('🔍 showNotification לא זמין - ודא שuser-actions.js נטען');
        }
        
        // החזרת נתונים דמה לפיתוח (אופציונלי)
        return getDemoData();
    }
}

// פונקציה לטעינת כתובות ללא קואורדינטות
async function loadMissingCoordinates() {
    try {
        const response = await fetch(API_ENDPOINTS.missingCoordinates, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת Backend: ${response.status}`);
        }
        
        const missingAddresses = await response.json();
        console.log(`✅ נטענו ${missingAddresses.length} כתובות ללא קואורדינטות`);
        
        return missingAddresses;
        
    } catch (error) {
        console.error("❌ שגיאה בטעינת כתובות חסרות:", error);
        return [];
    }
}

// נתונים דמה למקרה של בעיות בחיבור (פיתוח בלבד)
function getDemoData() {
    return [
        {
            address: 'דמו - הרב ריינס ירושלים',
            lat: 31.7903429,
            lon: 35.1940735,
            neighborhood: 'Givat Shaul',
            visited: false,
            source: 'demo'
        },
        {
            address: 'דמו - חירם ירושלים', 
            lat: 31.7929006,
            lon: 35.2077533,
            neighborhood: 'Romema',
            visited: true,
            source: 'demo'
        }
    ];
}

// פונקציה ליצירת מפת סיכום
function createSummaryInfo(addresses, missingAddresses) {
    const visited = addresses.filter(addr => addr.visited).length;
    const total = addresses.length;
    const notVisited = total - visited;
    
    // סיכום לפי מקור
    const geocoded = addresses.filter(addr => addr.source === 'geocoded');
    const manual = addresses.filter(addr => addr.source === 'manual');
    const corrected = addresses.filter(addr => addr.source === 'manual_corrected');
    const demo = addresses.filter(addr => addr.source === 'demo');
    
    const missingCount = missingAddresses.length;
    
    const summaryHTML = `
        <div class="summary-header">
            <button onclick="toggleSummary()" id="summaryToggle" class="summary-toggle" title="סגור סיכום">
                📊
            </button>
        </div>
        <div class="summary-info" id="summaryContent" dir="rtl">
            <h4>סיכום הביקורים</h4>
            <p>📍 סך הכל כתובות: <strong>${total}</strong></p>
            <p>✅ ביקרנו: <strong>${visited}</strong></p>
            <p>❌ לא ביקרנו: <strong>${notVisited}</strong></p>
            <div class="progress-bar">
                <div class="progress" style="width: ${total > 0 ? (visited/total*100) : 0}%"></div>
            </div>
            <p class="progress-text">${total > 0 ? Math.round(visited/total*100) : 0}% הושלם</p>
            
            ${demo.length > 0 ? `<p style="color: orange;">⚠️ נתוני דמו: ${demo.length}</p>` : ''}
          
            <hr style="margin: 15px 0; border: 1px solid #eee;">
            
            <p>🚫 ללא קואורדינטות: <strong style="color: #e74c3c;">${missingCount}</strong></p>
            
            <hr style="margin: 15px 0; border: 1px solid #eee;">
            <p style="font-size: 12px; color: #666;">
                🌐 Backend: ${API_BASE_URL.includes('YOUR-BACKEND') ? '❌ לא מחובר' : '✅ מחובר'}
            </p>
        </div>
    `;
    
    return summaryHTML;
}

// פונקציה לפתיחה/סגירה של הסיכום
function toggleSummary() {
    const summaryContent = document.getElementById('summaryContent');
    const toggleButton = document.getElementById('summaryToggle');
    
    if (summaryContent.style.display === 'none') {
        summaryContent.style.display = 'block';
        toggleButton.textContent = '📊';
        toggleButton.title = 'סגור סיכום';
    } else {
        summaryContent.style.display = 'none';
        toggleButton.textContent = '📋';
        toggleButton.title = 'פתח סיכום';
    }
}

// סגירת הסיכום בטעינה ראשונית של הדף
document.addEventListener('DOMContentLoaded', function() {
    // המתנה קצרה לוודא שהאלמנטים נטענו
    setTimeout(() => {
        const summaryContent = document.getElementById('summaryContent');
        const toggleButton = document.getElementById('summaryToggle');
        
        if (summaryContent && toggleButton) {
            summaryContent.style.display = 'none';
            toggleButton.textContent = '📋';
            toggleButton.title = 'פתח סיכום';
            console.log('📋 סיכום הוסתר בטעינה ראשונית');
        }
    }, 500); // המתנה של חצי שנייה לאחר טעינת הדף
});

// === פונקציות חדשות למערכת שתי הטבלאות ===

// טעינת כתובות שצריכות קואורדינטות ידניות
async function loadAddressesNeedingManual() {
    try {
        console.log("🔍 טוען כתובות שצריכות קואורדינטות ידניות...");
        
        const response = await fetch(API_ENDPOINTS.addressesNeedingManual, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת Backend: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(`Backend error: ${result.error || 'Unknown error'}`);
        }
        
        console.log(`✅ נטענו ${result.addresses.length} כתובות שצריכות קואורדינטות ידניות`);
        return result.addresses;
        
    } catch (error) {
        console.error("❌ שגיאה בטעינת כתובות שצריכות קואורדינטות ידניות:", error);
        if (typeof showNotification === 'function') {
            showNotification(`שגיאה בטעינת כתובות: ${error.message}`, 'error');
        }
        return [];
    }
}

// עיבוד כתובת חדשה (גיאוקודינג אוטומטי)
async function processNewAddress(address) {
    try {
        console.log("🔄 מעבד כתובת חדשה:", address);
        
        const response = await fetch(API_ENDPOINTS.processNewAddress, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ address: address })
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת Backend: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            console.log(`✅ כתובת עובדה בהצלחה: ${result.message}`);
            if (typeof showNotification === 'function') {
                showNotification(`כתובת נוספה: ${result.message}`, 'success');
            }
        } else {
            console.error("❌ שגיאה בעיבוד כתובת:", result.error);
            if (typeof showNotification === 'function') {
                showNotification(`שגיאה: ${result.error}`, 'error');
            }
        }
        
        return result;
        
    } catch (error) {
        console.error("❌ שגיאה בעיבוד כתובת חדשה:", error);
        if (typeof showNotification === 'function') {
            showNotification(`שגיאה בעיבוד כתובת: ${error.message}`, 'error');
        }
        return { success: false, error: error.message };
    }
}

// הוספת קואורדינטות ידניות
async function addManualCoordinates(missingId, lat, lon, neighborhood = null, addedBy = 'user') {
    try {
        console.log(`🎯 מוסיף קואורדינטות ידניות לכתובת ID: ${missingId}`);
        
        const response = await fetch(API_ENDPOINTS.addManualCoordinates, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                missing_id: missingId,
                lat: lat,
                lon: lon,
                neighborhood: neighborhood,
                added_by: addedBy
            })
        });
        
        if (!response.ok) {
            throw new Error(`שגיאת Backend: ${response.status} - ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            console.log("✅ קואורדינטות ידניות נוספו בהצלחה");
            if (typeof showNotification === 'function') {
                showNotification("קואורדינטות ידניות נוספו בהצלחה!", 'success');
            }
        } else {
            console.error("❌ שגיאה בהוספת קואורדינטות ידניות:", result.error);
            if (typeof showNotification === 'function') {
                showNotification(`שגיאה: ${result.error}`, 'error');
            }
        }
        
        return result;
        
    } catch (error) {
        console.error("❌ שגיאה בהוספת קואורדינטות ידניות:", error);
        if (typeof showNotification === 'function') {
            showNotification(`שגיאה בהוספת קואורדינטות: ${error.message}`, 'error');
        }
        return { success: false, error: error.message };
    }
}
