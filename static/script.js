// המתנה לטעינת הדף
document.addEventListener('DOMContentLoaded', function() {
    console.log("דף נטען, מנסה להציג מפה...");
    
    try {
        // בדיקה אם הספרייה נטענה
        if (typeof L === 'undefined') {
            throw new Error("ספריית Leaflet לא נטענה");
        }
        
        // בדיקה אם אלמנט המפה קיים
        const mapElement = document.getElementById('map');
        if (!mapElement) {
            throw new Error("לא נמצא אלמנט עם ID 'map'");
        }
        
        console.log("יוצר מפה...");
        // יצירת המפה וקביעת המרכז לירושלים
        var map = L.map('map').setView([31.7683, 35.2137], 13);
        
        console.log("מוסיף שכבת מפה...");
        // הוספת שכבת מפה בסיסית
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        
        // טעינת הכתובות מה-CSV והצגתן על המפה
        if (typeof initializeAddressMap === 'function') {
            initializeAddressMap(map).then(markers => {
                console.log("כתובות נטענו בהצלחה על המפה");
            }).catch(error => {
                console.error("שגיאה בטעינת הכתובות:", error);
            });
        } else {
            console.warn("פונקציית initializeAddressMap לא נמצאה - נטען את found.js");
        }
        
        // אירוע לחיצה על המפה
        function onMapClick(e) {
            L.popup()
                .setLatLng(e.latlng)
                .setContent("לחצת על המפה בנקודה: " + e.latlng.toString())
                .openOn(map);
        }
        
        map.on('click', onMapClick);
        console.log("המפה נטענה בהצלחה");
        
    } catch (error) {
        // טיפול בשגיאות
        console.error("שגיאה בטעינת המפה:", error);
        
        // נסה ליצור אלמנט שגיאה אם הוא לא קיים
        let errorElement = document.getElementById('map-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.id = 'map-error';
            errorElement.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: red; color: white; padding: 20px; border-radius: 5px; z-index: 9999;';
            document.body.appendChild(errorElement);
        }
        
        errorElement.style.display = 'block';
        errorElement.innerHTML = 'שגיאה בטעינת המפה: ' + error.message;
    }
});
