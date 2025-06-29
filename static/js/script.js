// Notification permission request
document.addEventListener('DOMContentLoaded', function() {
    if (Notification.permission !== "granted" && Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            console.log("Notification permission:", permission);
        });
    }
});

// Function to display notification
function showNotification(title, message) {
    if (Notification.permission === "granted") {
        new Notification(title, {
            body: message,
            icon: "/static/images/logo.png"
        });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                new Notification(title, {
                    body: message,
                    icon: "/static/images/logo.png"
                });
            }
        });
    }
}

// Example usage - you would call this from your notification system
// showNotification("Recovery Activity", "Time for your morning exercise!");