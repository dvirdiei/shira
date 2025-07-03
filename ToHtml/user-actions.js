// קובץ לפעולות משתמש - ביקורים, ניווט ומחיקות
// user-actions.js

console.log('👤 user-actions.js נטען בהצלחה');

// פונקציות עזר לפעולות על הכתובות
async function toggleVisitStatus(address, currentStatus) {
    try {
        const action = currentStatus ? 'unmark' : 'mark';
        const actionText = currentStatus ? 'מבטל ביקור' : 'מסמן כביקור';
        console.log(`${actionText} עבור ${address}`);
        
        // שליחת בקשה לשרת לעדכון הסטטוס
        const response = await fetch('/api/toggle-visited', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                address: address,
                action: action
            })
        });
        
        if (!response.ok) {
            throw new Error(`שגיאה בעדכון: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // עדכון המפה באופן מיידי
            showNotification(actionText === 'מסמן כביקור' ? 'הכתובת סומנה כביקור ✅' : 'הביקור בוטל ❌', 'success');
            location.reload(); // רענון הדף להצגת השינויים
        } else {
            showNotification(`שגיאה בעדכון: ${result.message}`, 'error');
        }
        
    } catch (error) {
        console.error("שגיאה בעדכון הביקור:", error);
        showNotification(`שגיאה בעדכון הביקור: ${error.message}`, 'error');
    }
}

// פונקציה ישנה לתאימות לאחור
async function markAsVisited(address) {
    return toggleVisitStatus(address, false);
}

// פונקציה למחיקת כתובת
async function deleteAddress(address) {
    // אישור מחיקה עם הודעה ברורה יותר
    const confirmMessage = `⚠️ אזהרה: פעולת מחיקה
    
האם אתה בטוח שברצונך למחוק את הכתובת:
"${address}"

הכתובת תועבר לקובץ המחוקים עם תאריך המחיקה.
פעולה זו ניתנת לביטול רק באופן ידני.`;
    
    const confirmDelete = confirm(confirmMessage);
    
    if (!confirmDelete) {
        return;
    }
    
    try {
        console.log(`מוחק את ${address}`);
        
        // שליחת בקשה לשרת למחיקת הכתובת
        const response = await fetch('/api/delete-address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                address: address
            })
        });
        
        if (!response.ok) {
            throw new Error(`שגיאה במחיקה: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`הכתובת "${address}" נמחקה בהצלחה 🗑️`, 'success');
            // עדכון המפה באופן מיידי
            location.reload(); // רענון הדף להצגת השינויים
        } else {
            showNotification(`שגיאה במחיקה: ${result.message}`, 'error');
        }
        
    } catch (error) {
        console.error("שגיאה במחיקת הכתובת:", error);
        showNotification(`שגיאה במחיקת הכתובת: ${error.message}`, 'error');
    }
}

// פונקציות ניווט
function openInGoogleMaps(lat, lon) {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}`;
    window.open(url, '_blank');
}

function openInWaze(lat, lon) {
    const url = `https://waze.com/ul?ll=${lat},${lon}&navigate=yes`;
    window.open(url, '_blank');
}

// פונקציות עזר להצגת הודעות למשתמש
function showNotification(message, type = 'success') {
    // יצירת אלמנט ההודעה
    const notification = document.createElement('div');
    notification.className = `alert-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        max-width: 500px;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        direction: rtl;
        font-weight: bold;
        animation: slideInRight 0.3s ease;
    `;
    notification.textContent = message;
    
    // הוספה לדף
    document.body.appendChild(notification);
    
    // הסרה אוטומטית אחרי 3 שניות
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// הוספת אנימציות CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ייצוא הפונקציות
window.toggleVisitStatus = toggleVisitStatus;
window.markAsVisited = markAsVisited;
window.deleteAddress = deleteAddress;
window.openInGoogleMaps = openInGoogleMaps;
window.openInWaze = openInWaze;
window.showNotification = showNotification;
window.showNotification = showNotification;
