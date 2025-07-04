// Frontend Data Loader - קריאות API לBackend
// data-loader.js

console.log('📊 Frontend data-loader.js נטען בהצלחה');
console.log('🔗 API_BASE_URL:', API_BASE_URL);
console.log('🔗 API_ENDPOINTS:', API_ENDPOINTS);

// פונקציה לטעינת נתוני הכתובות מה-Backend API
async function loadAddressesFromCSV() {
    try {
        console.log("🚀 טוען נתוני כתובות מה-Backend...");
        console.log("📡 URL לקריאה:", API_ENDPOINTS.allAddresses);
        
        // קריאה ל-Backend API ב-Render
        const response = await fetch(API_ENDPOINTS.allAddresses, {
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
        
        const addresses = await response.json();
        console.log(`✅ נטענו ${addresses.length} כתובות מה-Backend`);
        console.log("📋 דוגמה לנתונים:", addresses.slice(0, 2));
        
        return addresses;
        
    } catch (error) {
        console.error("❌ שגיאה בטעינת הכתובות מה-Backend:", error);
        console.error("❌ פרטי השגיאה:", error.message);
        console.error("❌ סוג השגיאה:", error.name);
        
        // הצגת הודעת שגיאה למשתמש
        showNotification(`שגיאה בחיבור לשרת: ${error.message}`, 'error');
        
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

// ייצוא הפונקציות
window.loadAddressesFromCSV = loadAddressesFromCSV;
window.loadMissingCoordinates = loadMissingCoordinates;
window.createSummaryInfo = createSummaryInfo;
window.toggleSummary = toggleSummary;
