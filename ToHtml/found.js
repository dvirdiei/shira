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
        case 'manual_corrected':
            sourceText = "תיקון ידני";
            sourceIcon = "🔧";
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
                <button onclick="markAsVisited('${address.address}')" 
                        class="btn-visit ${address.visited ? 'disabled' : ''}">
                    ${address.visited ? 'כבר ביקרת' : 'סמן כביקור'}
                </button>
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
        if (address.source === 'manual') {
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
            maxWidth: 300,
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

// פונקציה עיקרית לטעינת והצגת הכתובות
async function initializeAddressMap(mapInstance) {
    try {
        // טעינת נתוני הכתובות
        const addresses = await loadAddressesFromCSV();
        const missingAddresses = await loadMissingCoordinates();
        
        if (addresses.length === 0) {
            console.warn("לא נמצאו כתובות להצגה");
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
        
        console.log(`הוצגו בהצלחה ${markers.length} כתובות על המפה`);
        console.log(`${missingAddresses.length} כתובות ללא קואורדינטות`);
        
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
async function markAsVisited(address) {
    try {
        console.log(`מסמן את ${address} כביקור`);
        
        // שליחת בקשה לשרת לעדכון הסטטוס
        const response = await fetch('/api/mark-visited', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ address: address })
        });
        
        if (!response.ok) {
            throw new Error(`שגיאה בעדכון: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // עדכון המפה באופן מיידי
            location.reload(); // רענון הדף להצגת השינויים
        } else {
            alert(`שגיאה בעדכון: ${result.message}`);
        }
        
    } catch (error) {
        console.error("שגיאה בעדכון הביקור:", error);
        alert(`שגיאה בעדכון הביקור: ${error.message}`);
    }
}

function openInGoogleMaps(lat, lon) {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
    window.open(url, '_blank');
}

function openInWaze(lat, lon) {
    const url = `https://waze.com/ul?ll=${lat},${lon}&navigate=yes`;
    window.open(url, '_blank');
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

// ייצוא הפונקציות לשימוש גלובלי
window.initializeAddressMap = initializeAddressMap;
window.markAsVisited = markAsVisited;
window.openInGoogleMaps = openInGoogleMaps;
window.openInWaze = openInWaze;
window.toggleSummary = toggleSummary;
