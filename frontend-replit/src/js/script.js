// Frontend Script - אתחול המפה
// script.js

console.log('🗺️ Frontend script.js נטען - מכין מפה...');

// המתנה לטעינת הדף
document.addEventListener('DOMContentLoaded', function() {
    console.log("📱 דף נטען, מנסה להציג מפה...");
    if (typeof updateDebug === 'function') {
        updateDebug("📱 DOM נטען, מתחיל יצירת מפה...");
    }
    
    try {
        // בדיקה אם הספרייה נטענה
        if (typeof L === 'undefined') {
            throw new Error("ספריית Leaflet לא נטענה");
        }
        if (typeof updateDebug === 'function') {
            updateDebug("✅ ספריית Leaflet נטענה");
        }
        
        // בדיקה אם אלמנט המפה קיים
        const mapElement = document.getElementById('map');
        if (!mapElement) {
            throw new Error("לא נמצא אלמנט עם ID 'map'");
        }
        if (typeof updateDebug === 'function') {
            updateDebug("✅ אלמנט המפה נמצא");
        }
        
        // בדיקה שהקונפיג נטען
        if (typeof MAP_CONFIG === 'undefined') {
            throw new Error("קובץ config.js לא נטען או MAP_CONFIG לא מוגדר");
        }
        if (typeof updateDebug === 'function') {
            updateDebug("✅ MAP_CONFIG זמין: " + JSON.stringify(MAP_CONFIG));
        }
        
        console.log("🗺️ יוצר מפה...");
        if (typeof updateDebug === 'function') {
            updateDebug("🗺️ יוצר מפה עם המפתח...");
        }
        // יצירת המפה עם הגדרות מ-config
        var map = L.map('map', {
            zoomControl: MAP_CONFIG.zoomControl  // ללא כפתורי zoom
        }).setView(MAP_CONFIG.center, MAP_CONFIG.zoom);
        
        // שמירת המפה כמשתנה גלובלי לגישה מפונקציות אחרות
        window.map = map;
        
        if (typeof updateDebug === 'function') {
            updateDebug("✅ מפה נוצרה בהצלחה!");
        }
        
        console.log("🌍 מוסיף שכבת מפה...");
        if (typeof updateDebug === 'function') {
            updateDebug("🌍 מוסיף שכבת מפה...");
        }
        // הוספת שכבת מפה בסיסית
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        
        if (typeof updateDebug === 'function') {
            updateDebug("✅ שכבת מפה נוספה!");
        }
        
        // טעינת הכתובות והצגתן על המפה
        if (typeof initializeAddressMap === 'function') {
            console.log('🚀 מתחיל טעינת כתובות מ-Backend...');
            initializeAddressMap(map).then(markers => {
                console.log("✅ כתובות נטענו בהצלחה על המפה");
            }).catch(error => {
                console.error("❌ שגיאה בטעינת הכתובות:", error);
                showNotification('שגיאה בטעינת הכתובות מ-Backend', 'error');
            });
        } else {
            console.warn("⚠️ פונקציית initializeAddressMap לא נמצאה");
            showNotification('שגיאה בטעינת רכיבי המערכת', 'error');
        }
        
        // אירוע לחיצה על המפה (לפיתוח)
        function onMapClick(e) {
            console.log('🖱️ לחיצה על המפה:', e.latlng.toString());
            L.popup()
                .setLatLng(e.latlng)
                .setContent(`
                    <div dir="rtl">
                        <p><strong>📍 נקודה על המפה</strong></p>
                        <p>קואורדינטות: ${e.latlng.lat.toFixed(6)}, ${e.latlng.lng.toFixed(6)}</p>
                        <small>לחיצה לפיתוח</small>
                    </div>
                `)
                .openOn(map);
        }
        
        map.on('click', onMapClick);
        console.log("✅ המפה נטענה בהצלחה");
        
        // הצגת מידע על הגרסה
        console.log('ℹ️ Frontend מוכן:', window.found);
        
    } catch (error) {
        // טיפול בשגיאות
        console.error("❌ שגיאה בטעינת המפה:", error);
        
        // נסה ליצור אלמנט שגיאה אם הוא לא קיים
        let errorElement = document.getElementById('map-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'map-error';
            errorElement.style.cssText = `
                position: fixed; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%); 
                background: #f8d7da; 
                color: #721c24; 
                padding: 20px; 
                border-radius: 8px; 
                border: 1px solid #f5c6cb;
                z-index: 9999;
                direction: rtl;
                text-align: center;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            document.body.appendChild(errorElement);
        }
        
        errorElement.style.display = 'block';
        errorElement.innerHTML = `
            <h3>❌ שגיאה בטעינת המפה</h3>
            <p>${error.message}</p>
            <small>בדוק את הקונסול למידע נוסף</small>
            <br><br>
            <button onclick="location.reload()" style="
                background: #dc3545; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                cursor: pointer;
            ">רענן דף</button>
        `;
        
        // הודעה למשתמש אם הפונקציה זמינה
        if (typeof showNotification === 'function') {
            showNotification('שגיאה בטעינת המפה', 'error');
        }
    }
});
