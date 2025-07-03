// פונקציה לטעינת נתוני הכתובות מקובץ CSV ומיפוי על המפה
async function loadAddressesFromCSV() {
    try {
        console.log("טוען נתוני כתובות...");
        
        // קריאה לנתוני ה-CSV דרך Flask API
        const response = await fetch('/api/addresses');
        
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

// פונקציה ליצירת אייקונים מותאמים אישית
function createCustomIcons() {
    return {
        visited: L.divIcon({
            className: 'custom-marker visited-marker',
            html: '<div class="marker-pin visited">✅</div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        }),
        notVisited: L.divIcon({
            className: 'custom-marker not-visited-marker', 
            html: '<div class="marker-pin not-visited">📍</div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        })
    };
}

// פונקציה ליצירת תוכן פופאפ
function createPopupContent(address) {
    const statusText = address.visited ? "ביקרנו" : "לא ביקרנו";
    const statusIcon = address.visited ? "✅" : "❌";
    const statusClass = address.visited ? "status-visited" : "status-not-visited";
    
    return `
        <div class="popup-content" dir="rtl">
            <h3 class="popup-title">${address.address}</h3>
            <div class="popup-info">
                <p><strong>🏘️ שכונה:</strong> ${address.neighborhood}</p>
                <p><strong>📍 סטטוס:</strong> 
                    <span class="${statusClass}">
                        ${statusIcon} ${statusText}
                    </span>
                </p>
                <div class="coordinates">
                    <small>🌍 קואורדינטות: ${address.lat.toFixed(6)}, ${address.lon.toFixed(6)}</small>
                </div>
            </div>
            <div class="popup-actions">
                <button onclick="markAsVisited('${address.address}')" 
                        class="btn-visit ${address.visited ? 'disabled' : ''}">
                    ${address.visited ? 'כבר ביקרת' : 'סמן כביקור'}
                </button>
                <button onclick="openInGoogleMaps(${address.lat}, ${address.lon})" 
                        class="btn-navigate">
                    נווט ב-Google Maps
                </button>
            </div>
        </div>
    `;
}

// פונקציה להוספת כל הכתובות למפה
function addAddressesToMap(map, addresses) {
    const icons = createCustomIcons();
    const markers = [];
    
    addresses.forEach(function(address, index) {
        const icon = address.visited ? icons.visited : icons.notVisited;
        
        const marker = L.marker([address.lat, address.lon], { 
            icon: icon,
            title: address.address
        }).addTo(map);
        
        // הוספת פופאפ
        marker.bindPopup(createPopupContent(address), {
            maxWidth: 300,
            className: 'custom-popup'
        });
        
        // שמירת המידע במארקר לשימוש עתידי
        marker.addressData = address;
        markers.push(marker);
        
        console.log(`נוסף מארקר ${index + 1}: ${address.address}`);
    });
    
    // התאמת התצוגה כך שכל המארקרים יהיו נראים
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
    
    return markers;
}

// פונקציה ליצירת מפת סיכום
function createSummaryInfo(addresses) {
    const visited = addresses.filter(addr => addr.visited).length;
    const total = addresses.length;
    const notVisited = total - visited;
    
    const summaryHTML = `
        <div class="summary-info" dir="rtl">
            <h4>סיכום הביקורים</h4>
            <p>📍 סך הכל כתובות: <strong>${total}</strong></p>
            <p>✅ ביקרנו: <strong>${visited}</strong></p>
            <p>❌ לא ביקרנו: <strong>${notVisited}</strong></p>
            <div class="progress-bar">
                <div class="progress" style="width: ${(visited/total*100)}%"></div>
            </div>
            <p class="progress-text">${Math.round(visited/total*100)}% הושלם</p>
        </div>
    `;
    
    return summaryHTML;
}

// פונקציה עיקרית לטעינת והצגת הכתובות
async function initializeAddressMap(mapInstance) {
    try {
        // טעינת נתוני הכתובות
        const addresses = await loadAddressesFromCSV();
        
        if (addresses.length === 0) {
            console.warn("לא נמצאו כתובות להצגה");
            return;
        }
        
        // הוספת הכתובות למפה
        const markers = addAddressesToMap(mapInstance, addresses);
        
        // הוספת מידע סיכום למפה
        const summaryInfo = createSummaryInfo(addresses);
        
        // יצירת קונטרול מותאם אישית לסיכום
        const summaryControl = L.control({position: 'topright'});
        summaryControl.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'info summary-control');
            div.innerHTML = summaryInfo;
            return div;
        };
        summaryControl.addTo(mapInstance);
        
        console.log(`הוצגו בהצלחה ${markers.length} כתובות על המפה`);
        
        // החזרת המארקרים לשימוש נוסף
        return markers;
        
    } catch (error) {
        console.error("שגיאה באתחול מפת הכתובות:", error);
        
        // הצגת הודעת שגיאה על המפה
        const errorPopup = L.popup()
            .setLatLng([31.7683, 35.2137])
            .setContent(`
                <div class="error-message" dir="rtl">
                    <h4 style="color: red;">❌ שגיאה בטעינת הכתובות</h4>
                    <p>${error.message}</p>
                    <p><small>נסה לרענן את הדף או בדוק את החיבור לשרת</small></p>
                </div>
            `)
            .openOn(mapInstance);
    }
}

// פונקציות עזר לפעולות על הכתובות
function markAsVisited(address) {
    // כאן תוכל להוסיף לוגיקה לעדכון הסטטוס בשרת
    console.log(`מסמן את ${address} כביקור`);
    alert(`תכונה זו תתווסף בגרסה הבאה!\nכתובת: ${address}`);
}

function openInGoogleMaps(lat, lon) {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
    window.open(url, '_blank');
}

// ייצוא הפונקציות לשימוש גלובלי
window.initializeAddressMap = initializeAddressMap;
window.markAsVisited = markAsVisited;
window.openInGoogleMaps = openInGoogleMaps;
