// קובץ לטעינת נתונים ומידע מהשרת
// data-loader.js

console.log('📊 data-loader.js נטען בהצלחה');

// פונקציה לטעינת נתוני הכתובות מקובץ CSV ומיפוי על המפה
async function loadAddressesFromCSV() {
    try {
        console.log("טוען נתוני כתובות...");
        
        // קריאה לנתוני ה-CSV דרך Flask API (כולל כתובות ידניות)
        const response = await fetch('/api/all-addresses');
        
        if (!response.ok) {
            throw new Error(`שגיאת שרת: ${response.status}`);
        }
        
        const addresses = await response.json();
        console.log(`נטענו ${addresses.length} כתובות`);
        
        return addresses;
        
    } catch (error) {
        console.error("שגיאה בטעינת הכתובות:", error);
        throw error;
    }
}

// פונקציה לטעינת כתובות ללא קואורדינטות
async function loadMissingCoordinates() {
    try {
        const response = await fetch('/api/missing-coordinates');
        
        if (!response.ok) {
            throw new Error(`שגיאת שרת: ${response.status}`);
        }
        
        const missingAddresses = await response.json();
        console.log(`נטענו ${missingAddresses.length} כתובות ללא קואורדינטות`);
        
        return missingAddresses;
        
    } catch (error) {
        console.error("שגיאה בטעינת כתובות חסרות:", error);
        return [];
    }
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
    
    const geocodedVisited = geocoded.filter(addr => addr.visited).length;
    const manualVisited = manual.filter(addr => addr.visited).length;
    const correctedVisited = corrected.filter(addr => addr.visited).length;
    
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
            
          
            <hr style="margin: 15px 0; border: 1px solid #eee;">
            
            <p>🚫 ללא קואורדינטות: <strong style="color: #e74c3c;">${missingCount}</strong></p>
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
