// Frontend Map Markers - ניהול מארקרים ומפה
// map-markers.js

console.log('🗺️ Frontend map-markers.js נטען בהצלחה');

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
        }),
        manualVisited: L.divIcon({
            className: 'custom-marker manual-visited-marker',
            html: '<div class="marker-pin manual-visited">✅</div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        }),
        manualNotVisited: L.divIcon({
            className: 'custom-marker manual-not-visited-marker', 
            html: '<div class="marker-pin manual-not-visited">📌</div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        }),
        correctedVisited: L.divIcon({
            className: 'custom-marker corrected-visited-marker',
            html: '<div class="marker-pin corrected-visited">✅</div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        }),
        correctedNotVisited: L.divIcon({
            className: 'custom-marker corrected-not-visited-marker', 
            html: '<div class="marker-pin corrected-not-visited">🔧</div>',
            iconSize: [30, 42],
            iconAnchor: [15, 42],
            popupAnchor: [0, -42]
        }),
        demo: L.divIcon({
            className: 'custom-marker demo-marker',
            html: '<div class="marker-pin demo">🧪</div>',
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
    
    let sourceText, sourceIcon;
    switch(address.source) {
        case 'manual':
            sourceText = "הוספה ידנית";
            sourceIcon = "✋";
            break;
        case 'manual_corrected':
            sourceText = "תיקון ידני";
            sourceIcon = "🔧";
            break;
        case 'demo':
            sourceText = "נתוני דמו";
            sourceIcon = "🧪";
            break;
        default:
            sourceText = "גיאוקודינג אוטומטי";
            sourceIcon = "🤖";
            break;
    }
    
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
                <p><strong>🔍 מקור:</strong> 
                    <span class="source-${address.source}">
                        ${sourceIcon} ${sourceText}
                    </span>
                </p>
                <div class="coordinates">
                    <small>🌍 קואורדינטות: ${address.lat.toFixed(6)}, ${address.lon.toFixed(6)}</small>
                </div>
            </div>
            <div class="popup-actions">
                ${address.source !== 'demo' ? `
                    <button onclick="toggleVisitStatus('${address.address}', ${address.visited})" 
                            class="btn-visit ${address.visited ? 'cancel' : ''}">
                        ${address.visited ? 'בטל ביקור' : 'סמן כביקור'}
                    </button>
                    <button onclick="deleteAddress('${address.address}')" 
                            class="btn-delete">
                        🗑️ מחק נקודה
                    </button>
                ` : `
                    <p style="color: orange; font-size: 12px;">⚠️ נתוני דמו - לא ניתן לעדכן</p>
                `}
                <button onclick="openInGoogleMaps(${address.lat}, ${address.lon})" 
                        class="btn-navigate">
                    נווט ב-Google Maps
                </button>
                <button onclick="openInWaze(${address.lat}, ${address.lon})" 
                        class="btn-navigate btn-waze">
                    נווט ב-Waze
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
        let icon;
        
        // בחירת אייקון לפי מקור וסטטוס
        if (address.source === 'demo') {
            icon = icons.demo;
        } else if (address.source === 'manual') {
            icon = address.visited ? icons.manualVisited : icons.manualNotVisited;
        } else if (address.source === 'manual_corrected') {
            icon = address.visited ? icons.correctedVisited : icons.correctedNotVisited;
        } else {
            icon = address.visited ? icons.visited : icons.notVisited;
        }
        
        const marker = L.marker([address.lat, address.lon], { 
            icon: icon,
            title: address.address
        }).addTo(map);
        
        // הוספת פופאפ
        marker.bindPopup(createPopupContent(address), {
            maxWidth: UI_CONFIG.popupMaxWidth,
            className: 'custom-popup'
        });
        
        // שמירת המידע במארקר לשימוש עתידי
        marker.addressData = address;
        markers.push(marker);
        
        console.log(`נוסף מארקר ${index + 1}: ${address.address} (${address.source})`);
    });
    
    // התאמת התצוגה כך שכל המארקרים יהיו נראים
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
    
    return markers;
}

// פונקציה עיקרית לאתחול המפה
async function initializeAddressMap(mapInstance) {
    try {
        console.log('🚀 מתחיל אתחול מפה עם חיבור ל-Backend...');
        
        // טעינת נתוני הכתובות מה-Backend
        const addresses = await loadAddressesFromCSV();
        const missingAddresses = await loadMissingCoordinates();
        
        if (addresses.length === 0) {
            console.warn("⚠️ לא נמצאו כתובות להצגה");
            showNotification('לא נמצאו כתובות להצגה', 'warning');
            return;
        }
        
        // הוספת הכתובות למפה
        const markers = addAddressesToMap(mapInstance, addresses);
        
        // הוספת מידע סיכום למפה
        const summaryInfo = createSummaryInfo(addresses, missingAddresses);
        
        // יצירת קונטרול מותאם אישית לסיכום
        const summaryControl = L.control({position: 'topright'});
        summaryControl.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'info summary-control');
            div.innerHTML = summaryInfo;
            return div;
        };
        summaryControl.addTo(mapInstance);
        
        console.log(`✅ הוצגו בהצלחה ${markers.length} כתובות על המפה`);
        console.log(`📊 ${missingAddresses.length} כתובות ללא קואורדינטות`);
        
        // הודעת הצלחה למשתמש
        const demoCount = addresses.filter(addr => addr.source === 'demo').length;
        if (demoCount > 0) {
            showNotification(`נטענו ${addresses.length} כתובות (${demoCount} נתוני דמו)`, 'warning');
        } else {
            showNotification(`נטענו ${addresses.length} כתובות מהשרת`, 'success');
        }
        
        // החזרת המארקרים לשימוש נוסף
        return markers;
        
    } catch (error) {
        console.error("❌ שגיאה באתחול מפת הכתובות:", error);
        
        // הצגת הודעת שגיאה על המפה
        const errorPopup = L.popup()
            .setLatLng(MAP_CONFIG.center)
            .setContent(`
                <div class="error-message" dir="rtl">
                    <h4 style="color: red;">❌ שגיאה בטעינת הכתובות</h4>
                    <p>${error.message}</p>
                    <p><small>בדוק את החיבור לשרת Backend</small></p>
                    <p><small>או עדכן את כתובת ה-API ב-config.js</small></p>
                </div>
            `)
            .openOn(mapInstance);
            
        showNotification('שגיאה בחיבור לשרת Backend', 'error');
    }
}

// ייצוא הפונקציות
window.createCustomIcons = createCustomIcons;
window.createPopupContent = createPopupContent;
window.addAddressesToMap = addAddressesToMap;
window.initializeAddressMap = initializeAddressMap;
