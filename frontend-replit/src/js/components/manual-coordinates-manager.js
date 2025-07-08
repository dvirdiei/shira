// ניהול כתובות עם קואורדינטות ידניות
// manual-coordinates-manager.js

console.log('🎯 Manual Coordinates Manager נטען בהצלחה');

// משתנים גלובליים
let addressesNeedingManual = [];
let isLoadingManualAddresses = false;

// טעינת כתובות שצריכות קואורדינטות ידניות
async function loadManualAddressesManager() {
    if (isLoadingManualAddresses) {
        console.log('⏳ טעינה כבר בתהליך...');
        return;
    }
    
    try {
        isLoadingManualAddresses = true;
        console.log('🔍 טוען כתובות שצריכות קואורדינטות ידניות...');
        
        // שימוש בפונקציה מdata-loader.js
        if (typeof loadAddressesNeedingManual === 'function') {
            addressesNeedingManual = await loadAddressesNeedingManual();
            displayManualAddressesList();
        } else {
            console.error('❌ loadAddressesNeedingManual לא זמין - ודא שdata-loader.js נטען');
        }
        
    } catch (error) {
        console.error('❌ שגיאה בטעינת כתובות ידניות:', error);
    } finally {
        isLoadingManualAddresses = false;
    }
}

// הצגת רשימת כתובות שצריכות קואורדינטות ידניות
function displayManualAddressesList() {
    console.log(`📋 מציג ${addressesNeedingManual.length} כתובות שצריכות קואורדינטות ידניות`);
    
    // יצירת HTML לרשימה
    const listHtml = addressesNeedingManual.map(addr => `
        <div class="manual-address-item" data-id="${addr.id}">
            <div class="address-info">
                <h4>${addr.address}</h4>
                <p><small>סיבה: ${addr.reason || 'לא צוין'}</small></p>
                <p><small>נוצר: ${new Date(addr.created_at).toLocaleString('he-IL')}</small></p>
            </div>
            <div class="coordinates-form">
                <input type="number" step="any" placeholder="קו רוחב (lat)" class="lat-input" data-id="${addr.id}">
                <input type="number" step="any" placeholder="קו אורך (lon)" class="lon-input" data-id="${addr.id}">
                <input type="text" placeholder="שכונה (אופציונלי)" class="neighborhood-input" data-id="${addr.id}">
                <button onclick="submitManualCoordinates(${addr.id})" class="btn-add-coords">הוסף קואורדינטות</button>
            </div>
        </div>
    `).join('');
    
    // הכנסת HTML לעמוד
    const container = document.getElementById('manual-addresses-container');
    if (container) {
        container.innerHTML = `
            <h3>כתובות שצריכות קואורדינטות ידניות (${addressesNeedingManual.length})</h3>
            ${listHtml || '<p>אין כתובות שצריכות קואורדינטות ידניות כרגע</p>'}
        `;
    } else {
        console.warn('⚠️ לא נמצא container עם ID: manual-addresses-container');
    }
}

// שליחת קואורדינטות ידניות
async function submitManualCoordinates(missingId) {
    try {
        // קבלת הנתונים מהטופס
        const latInput = document.querySelector(`.lat-input[data-id="${missingId}"]`);
        const lonInput = document.querySelector(`.lon-input[data-id="${missingId}"]`);
        const neighborhoodInput = document.querySelector(`.neighborhood-input[data-id="${missingId}"]`);
        
        if (!latInput || !lonInput) {
            throw new Error('לא נמצאו שדות הקלט');
        }
        
        const lat = parseFloat(latInput.value);
        const lon = parseFloat(lonInput.value);
        const neighborhood = neighborhoodInput.value.trim() || null;
        
        // בדיקת תקינות
        if (isNaN(lat) || isNaN(lon)) {
            throw new Error('יש להזין קואורדינטות תקינות');
        }
        
        if (lat < -90 || lat > 90) {
            throw new Error('קו רוחב חייב להיות בין -90 ל-90');
        }
        
        if (lon < -180 || lon > 180) {
            throw new Error('קו אורך חייב להיות בין -180 ל-180');
        }
        
        console.log(`🎯 שולח קואורדינטות ידניות עבור ID: ${missingId}`);
        console.log(`📍 קואורדינטות: ${lat}, ${lon}`);
        
        // שימוש בפונקציה מdata-loader.js
        if (typeof addManualCoordinates === 'function') {
            const result = await addManualCoordinates(missingId, lat, lon, neighborhood, 'frontend-user');
            
            if (result.success) {
                // הסרת הכתובת מהרשימה
                addressesNeedingManual = addressesNeedingManual.filter(addr => addr.id !== missingId);
                displayManualAddressesList();
                
                // עדכון המפה
                if (typeof loadAndDisplayAddresses === 'function') {
                    await loadAndDisplayAddresses();
                }
                
                console.log('✅ קואורדינטות נוספו בהצלחה ומפה עודכנה');
            }
        } else {
            console.error('❌ addManualCoordinates לא זמין - ודא שdata-loader.js נטען');
        }
        
    } catch (error) {
        console.error('❌ שגיאה בשליחת קואורדינטות ידניות:', error);
        if (typeof showNotification === 'function') {
            showNotification(`שגיאה: ${error.message}`, 'error');
        } else {
            alert(`שגיאה: ${error.message}`);
        }
    }
}

// הוספת כתובת חדשה עם עיבוד אוטומטי
async function addNewAddressWithProcessing() {
    try {
        const addressInput = document.getElementById('new-address-input');
        if (!addressInput) {
            throw new Error('לא נמצא שדה הכנסת כתובת חדשה');
        }
        
        const address = addressInput.value.trim();
        if (!address) {
            throw new Error('יש להזין כתובת');
        }
        
        console.log('🔄 מעבד כתובת חדשה:', address);
        
        // שימוש בפונקציה מdata-loader.js
        if (typeof processNewAddress === 'function') {
            const result = await processNewAddress(address);
            
            if (result.success) {
                // ניקוי שדה הקלט
                addressInput.value = '';
                
                // עדכון רשימת כתובות ידניות
                await loadManualAddressesManager();
                
                // עדכון המפה
                if (typeof loadAndDisplayAddresses === 'function') {
                    await loadAndDisplayAddresses();
                }
                
                console.log('✅ כתובת חדשה עובדה והמפה עודכנה');
            }
        } else {
            console.error('❌ processNewAddress לא זמין - ודא שdata-loader.js נטען');
        }
        
    } catch (error) {
        console.error('❌ שגיאה בהוספת כתובת חדשה:', error);
        if (typeof showNotification === 'function') {
            showNotification(`שגיאה: ${error.message}`, 'error');
        } else {
            alert(`שגיאה: ${error.message}`);
        }
    }
}

// אתחול בטעינת העמוד
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Manual Coordinates Manager מאותחל');
    
    // טעינה ראשונית של כתובות ידניות
    setTimeout(() => {
        loadManualAddressesManager();
    }, 1000); // המתנה לטעינת dependencies
});

// Export functions for global use
window.loadManualAddressesManager = loadManualAddressesManager;
window.submitManualCoordinates = submitManualCoordinates;
window.addNewAddressWithProcessing = addNewAddressWithProcessing;
