/**
 * Smart Notifications System for StockMaster Pro
 * Provides real-time alerts for inventory, orders, and system events
 */

// Notification types and priorities
const NOTIFICATION_TYPES = {
    LOW_STOCK: 'low_stock',
    NEW_ORDER: 'new_order',
    SYSTEM_WARNING: 'system_warning',
    EXPIRY_ALERT: 'expiry_alert',
    PAYMENT_RECEIVED: 'payment_received',
    TASK_COMPLETED: 'task_completed',
    SECURITY_ALERT: 'security_alert'
};

const NOTIFICATION_PRIORITIES = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
};

// Notification sounds
const NOTIFICATION_SOUNDS = {
    [NOTIFICATION_TYPES.LOW_STOCK]: 'notification-soft.mp3',
    [NOTIFICATION_TYPES.NEW_ORDER]: 'notification-order.mp3',
    [NOTIFICATION_TYPES.SYSTEM_WARNING]: 'notification-alert.mp3',
    [NOTIFICATION_TYPES.EXPIRY_ALERT]: 'notification-soft.mp3',
    [NOTIFICATION_TYPES.PAYMENT_RECEIVED]: 'notification-cash.mp3',
    [NOTIFICATION_TYPES.SECURITY_ALERT]: 'notification-alert.mp3',
    default: 'notification-soft.mp3'
};

// Notification icons
const NOTIFICATION_ICONS = {
    [NOTIFICATION_TYPES.LOW_STOCK]: 'ri-store-2-line',
    [NOTIFICATION_TYPES.NEW_ORDER]: 'ri-shopping-cart-line',
    [NOTIFICATION_TYPES.SYSTEM_WARNING]: 'ri-error-warning-line',
    [NOTIFICATION_TYPES.EXPIRY_ALERT]: 'ri-calendar-event-line',
    [NOTIFICATION_TYPES.PAYMENT_RECEIVED]: 'ri-money-dollar-circle-line',
    [NOTIFICATION_TYPES.TASK_COMPLETED]: 'ri-check-double-line',
    [NOTIFICATION_TYPES.SECURITY_ALERT]: 'ri-shield-keyhole-line',
    default: 'ri-notification-3-line'
};

// Notification colors
const NOTIFICATION_COLORS = {
    [NOTIFICATION_PRIORITIES.LOW]: {
        bg: 'bg-blue-100 dark:bg-blue-900',
        text: 'text-blue-800 dark:text-blue-200',
        border: 'border-blue-300 dark:border-blue-700'
    },
    [NOTIFICATION_PRIORITIES.MEDIUM]: {
        bg: 'bg-yellow-100 dark:bg-yellow-900',
        text: 'text-yellow-800 dark:text-yellow-200',
        border: 'border-yellow-300 dark:border-yellow-700'
    },
    [NOTIFICATION_PRIORITIES.HIGH]: {
        bg: 'bg-orange-100 dark:bg-orange-900',
        text: 'text-orange-800 dark:text-orange-200',
        border: 'border-orange-300 dark:border-orange-700'
    },
    [NOTIFICATION_PRIORITIES.CRITICAL]: {
        bg: 'bg-red-100 dark:bg-red-900',
        text: 'text-red-800 dark:text-red-200',
        border: 'border-red-300 dark:border-red-700'
    }
};

// Notification state
let notifications = [];
let unreadCount = 0;
let notificationSettings = {
    sound: true,
    desktop: true,
    inApp: true,
    lowStockThreshold: 10, // Percentage
    autoRefresh: true,
    refreshInterval: 60000, // 1 minute
    groupSimilar: true,
    maxVisible: 5
};

// Initialize notification system
function initNotificationSystem() {
    // Load notification settings from localStorage
    loadNotificationSettings();
    
    // Create notification container if it doesn't exist
    createNotificationContainer();
    
    // Initialize notification badge
    updateNotificationBadge();
    
    // Set up polling for new notifications if enabled
    if (notificationSettings.autoRefresh) {
        startNotificationPolling();
    }
    
    // Set up notification button click handler
    setupNotificationButton();
    
    // Register service worker for push notifications if supported
    registerServiceWorker();
    
    console.log('Smart Notification System initialized');
}

// Load notification settings from localStorage
function loadNotificationSettings() {
    const savedSettings = localStorage.getItem('notificationSettings');
    if (savedSettings) {
        try {
            const parsedSettings = JSON.parse(savedSettings);
            notificationSettings = { ...notificationSettings, ...parsedSettings };
        } catch (e) {
            console.error('Error parsing notification settings:', e);
        }
    }
}

// Save notification settings to localStorage
function saveNotificationSettings() {
    localStorage.setItem('notificationSettings', JSON.stringify(notificationSettings));
}

// Create notification container
function createNotificationContainer() {
    let container = document.getElementById('smartNotificationContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'smartNotificationContainer';
        container.className = 'fixed bottom-4 right-4 z-50 flex flex-col-reverse gap-2 max-h-[80vh] overflow-hidden';
        document.body.appendChild(container);
    }
}

// Update notification badge
function updateNotificationBadge() {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (unreadCount > 0) {
            badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    }
}

// Start polling for new notifications
function startNotificationPolling() {
    // Clear any existing interval
    if (window.notificationInterval) {
        clearInterval(window.notificationInterval);
    }
    
    // Set up new interval
    window.notificationInterval = setInterval(() => {
        fetchNotifications();
    }, notificationSettings.refreshInterval);
}

// Fetch notifications from server
function fetchNotifications() {
    fetch('/api/notifications', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            processNewNotifications(data.notifications);
        }
    })
    .catch(error => {
        console.error('Error fetching notifications:', error);
    });
}

// Process new notifications
function processNewNotifications(newNotifications) {
    // Filter out notifications we already have
    const existingIds = notifications.map(n => n.id);
    const actuallyNew = newNotifications.filter(n => !existingIds.includes(n.id));
    
    // Update our notifications array
    notifications = [...actuallyNew, ...notifications];
    
    // Update unread count
    unreadCount += actuallyNew.filter(n => !n.read).length;
    updateNotificationBadge();
    
    // Show new notifications
    if (notificationSettings.inApp) {
        actuallyNew.forEach(notification => {
            showNotification(notification);
        });
    }
    
    // Play sound for new notifications if enabled
    if (notificationSettings.sound && actuallyNew.length > 0) {
        playNotificationSound(actuallyNew[0].type);
    }
    
    // Show desktop notifications if enabled
    if (notificationSettings.desktop && actuallyNew.length > 0) {
        showDesktopNotifications(actuallyNew);
    }
}

// Show in-app notification
function showNotification(notification) {
    const container = document.getElementById('smartNotificationContainer');
    if (!container) return;
    
    // Get notification type and priority
    const type = notification.type || NOTIFICATION_TYPES.SYSTEM_WARNING;
    const priority = notification.priority || NOTIFICATION_PRIORITIES.MEDIUM;
    
    // Create notification element
    const notificationEl = document.createElement('div');
    notificationEl.className = `notification-item ${NOTIFICATION_COLORS[priority].bg} ${NOTIFICATION_COLORS[priority].text} ${NOTIFICATION_COLORS[priority].border} rounded-lg shadow-lg p-4 max-w-sm w-full transform transition-all duration-300 translate-x-full opacity-0`;
    notificationEl.dataset.id = notification.id;
    
    // Add notification content
    notificationEl.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0 mr-3">
                <i class="${NOTIFICATION_ICONS[type] || NOTIFICATION_ICONS.default} text-2xl"></i>
            </div>
            <div class="flex-1">
                <h4 class="font-semibold">${notification.title}</h4>
                <p class="text-sm opacity-90">${notification.message}</p>
                <div class="mt-2 text-xs opacity-75 flex justify-between">
                    <span>${formatNotificationTime(notification.created_at)}</span>
                    <button class="mark-read hover:underline">Mark as read</button>
                </div>
            </div>
            <button class="ml-2 text-lg close-notification">&times;</button>
        </div>
    `;
    
    // Add to container
    container.appendChild(notificationEl);
    
    // Animate in
    setTimeout(() => {
        notificationEl.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    // Add event listeners
    notificationEl.querySelector('.close-notification').addEventListener('click', () => {
        removeNotification(notificationEl);
    });
    
    notificationEl.querySelector('.mark-read').addEventListener('click', () => {
        markNotificationRead(notification.id);
        removeNotification(notificationEl);
    });
    
    // Auto-hide after delay based on priority
    const delays = {
        [NOTIFICATION_PRIORITIES.LOW]: 5000,
        [NOTIFICATION_PRIORITIES.MEDIUM]: 8000,
        [NOTIFICATION_PRIORITIES.HIGH]: 12000,
        [NOTIFICATION_PRIORITIES.CRITICAL]: 0 // Don't auto-hide critical notifications
    };
    
    if (delays[priority] > 0) {
        setTimeout(() => {
            removeNotification(notificationEl);
        }, delays[priority]);
    }
}

// Remove notification element with animation
function removeNotification(element) {
    element.classList.add('translate-x-full', 'opacity-0');
    setTimeout(() => {
        if (element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }, 300);
}

// Format notification time
function formatNotificationTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) {
        return 'Just now';
    } else if (diffMins < 60) {
        return `${diffMins} min ago`;
    } else if (diffMins < 1440) {
        const hours = Math.floor(diffMins / 60);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
        const days = Math.floor(diffMins / 1440);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
}

// Play notification sound
function playNotificationSound(type) {
    const soundFile = NOTIFICATION_SOUNDS[type] || NOTIFICATION_SOUNDS.default;
    const audio = new Audio(`/static/sounds/${soundFile}`);
    audio.volume = 0.5;
    audio.play().catch(e => {
        console.log('Could not play notification sound:', e);
    });
}

// Show desktop notifications
function showDesktopNotifications(notifications) {
    if (!('Notification' in window)) {
        console.log('Desktop notifications not supported');
        return;
    }
    
    if (Notification.permission === 'granted') {
        notifications.forEach(notification => {
            const desktopNotification = new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/logo.png'
            });
            
            desktopNotification.onclick = function() {
                window.focus();
                markNotificationRead(notification.id);
            };
        });
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showDesktopNotifications(notifications);
            }
        });
    }
}

// Mark notification as read
function markNotificationRead(id) {
    fetch(`/api/notifications/${id}/read`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update local state
            const notification = notifications.find(n => n.id === id);
            if (notification && !notification.read) {
                notification.read = true;
                unreadCount = Math.max(0, unreadCount - 1);
                updateNotificationBadge();
            }
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Register service worker for push notifications
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/notification-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful with scope:', registration.scope);
            })
            .catch(error => {
                console.log('ServiceWorker registration failed:', error);
            });
    }
}

// Set up notification button click handler
function setupNotificationButton() {
    const notificationButton = document.querySelector('.notification-button');
    if (notificationButton) {
        notificationButton.addEventListener('click', toggleNotificationPanel);
    }
}

// Toggle notification panel
function toggleNotificationPanel() {
    const panel = document.getElementById('notificationPanel');
    if (!panel) {
        createNotificationPanel();
    } else {
        panel.classList.toggle('hidden');
        if (!panel.classList.contains('hidden')) {
            renderNotificationList();
        }
    }
}

// Create notification panel
function createNotificationPanel() {
    const panel = document.createElement('div');
    panel.id = 'notificationPanel';
    panel.className = 'absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg py-2 z-50';
    panel.innerHTML = `
        <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h3 class="font-semibold">Notifications</h3>
            <div>
                <button id="markAllReadBtn" class="text-xs text-blue-600 dark:text-blue-400 hover:underline">Mark all read</button>
                <button id="notificationSettingsBtn" class="ml-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                    <i class="ri-settings-3-line"></i>
                </button>
            </div>
        </div>
        <div id="notificationList" class="max-h-80 overflow-y-auto py-2">
            <div class="px-4 py-2 text-center text-gray-500 dark:text-gray-400">Loading notifications...</div>
        </div>
    `;
    
    // Add to DOM
    const notificationButton = document.querySelector('.notification-button');
    if (notificationButton) {
        notificationButton.parentNode.appendChild(panel);
    } else {
        document.body.appendChild(panel);
    }
    
    // Add event listeners
    document.getElementById('markAllReadBtn').addEventListener('click', markAllNotificationsRead);
    document.getElementById('notificationSettingsBtn').addEventListener('click', showNotificationSettings);
    
    // Render notifications
    renderNotificationList();
    
    // Close when clicking outside
    document.addEventListener('click', function(e) {
        if (panel && !panel.contains(e.target) && !e.target.closest('.notification-button')) {
            panel.classList.add('hidden');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initNotificationSystem);

// Export functions to global scope
window.SmartNotifications = {
    show: showNotification,
    markRead: markNotificationRead,
    markAllRead: markAllNotificationsRead,
    fetchNew: fetchNotifications,
    getSettings: () => ({ ...notificationSettings }),
    updateSettings: (newSettings) => {
        notificationSettings = { ...notificationSettings, ...newSettings };
        saveNotificationSettings();
        if (notificationSettings.autoRefresh) {
            startNotificationPolling();
        } else if (window.notificationInterval) {
            clearInterval(window.notificationInterval);
        }
    }
};
