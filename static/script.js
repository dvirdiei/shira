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
        document.getElementById('map-error').style.display = 'block';
        document.getElementById('map-error').innerHTML = 'שגיאה בטעינת המפה: ' + error.message;
    }
});
