/**
 * Notification System Fixes for StockMaster Pro
 * This file adds missing functionality to the smart-notifications.js system
 */

// Render notification list (if not already defined)
if (typeof renderNotificationList !== 'function') {
    function renderNotificationList() {
        const listContainer = document.getElementById('notificationList');
        if (!listContainer) return;

        // If we don't have notifications yet, try to fetch them
        if (!window.SmartNotifications.notifications || window.SmartNotifications.notifications.length === 0) {
            listContainer.innerHTML = `<div class="px-4 py-2 text-center text-gray-500 dark:text-gray-400">No notifications</div>`;
            return;
        }

        // Sort notifications by date (newest first)
        const sortedNotifications = [...window.SmartNotifications.notifications].sort((a, b) =>
            new Date(b.created_at) - new Date(a.created_at)
        );

        // Limit to a reasonable number
        const displayNotifications = sortedNotifications.slice(0, 20);

        // Generate HTML
        let html = '';
        displayNotifications.forEach(notification => {
            const type = notification.type || 'system_warning';
            const priority = notification.priority || 'medium';

            html += `
                <div class="notification-item px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${notification.read ? 'opacity-60' : ''}" data-id="${notification.id}">
                    <div class="flex items-start">
                        <div class="flex-shrink-0 mr-3">
                            <i class="ri-notification-3-line text-xl"></i>
                        </div>
                        <div class="flex-1">
                            <h4 class="font-semibold text-sm">${notification.title}</h4>
                            <p class="text-xs opacity-90">${notification.message}</p>
                            <div class="mt-1 text-xs opacity-75 flex justify-between">
                                <span>${formatNotificationTime(notification.created_at)}</span>
                                ${!notification.read ? `<button class="mark-read hover:underline">Mark read</button>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        listContainer.innerHTML = html;

        // Add event listeners
        listContainer.querySelectorAll('.mark-read').forEach(button => {
            button.addEventListener('click', (e) => {
                const item = e.target.closest('.notification-item');
                if (item) {
                    const id = item.dataset.id;
                    window.SmartNotifications.markRead(id);
                    item.classList.add('opacity-60');
                    e.target.remove();
                }
            });
        });
    }
}

// Format notification time helper
if (typeof formatNotificationTime !== 'function') {
    function formatNotificationTime(timestamp) {
        if (!timestamp) return 'Unknown';

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
}

// Mark all notifications as read
if (typeof markAllNotificationsRead !== 'function') {
    function markAllNotificationsRead() {
        if (window.SmartNotifications && window.SmartNotifications.notifications) {
            window.SmartNotifications.notifications.forEach(n => n.read = true);
            if (window.SmartNotifications.updateNotificationBadge) {
                window.SmartNotifications.updateNotificationBadge(0);
            }
            renderNotificationList();
        }
    }
}

// Show notification settings
if (typeof showNotificationSettings !== 'function') {
    function showNotificationSettings() {
        const panel = document.getElementById('notificationPanel');
        if (!panel) return;

        // Create settings panel
        const settingsPanel = document.createElement('div');
        settingsPanel.id = 'notificationSettingsPanel';
        settingsPanel.className = 'absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg py-2 z-50';

        const settings = window.SmartNotifications.getSettings ? window.SmartNotifications.getSettings() : {
            sound: true,
            desktop: true,
            inApp: true,
            autoRefresh: true,
            refreshInterval: 60000
        };

        settingsPanel.innerHTML = `
            <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h3 class="font-semibold">Notification Settings</h3>
                <button id="closeSettingsBtn" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                    <i class="ri-close-line"></i>
                </button>
            </div>
            <div class="p-4">
                <div class="mb-3">
                    <label class="flex items-center">
                        <input type="checkbox" id="soundEnabled" class="mr-2" ${settings.sound ? 'checked' : ''}>
                        <span>Sound notifications</span>
                    </label>
                </div>
                <div class="mb-3">
                    <label class="flex items-center">
                        <input type="checkbox" id="desktopEnabled" class="mr-2" ${settings.desktop ? 'checked' : ''}>
                        <span>Desktop notifications</span>
                    </label>
                </div>
                <div class="mb-3">
                    <label class="flex items-center">
                        <input type="checkbox" id="inAppEnabled" class="mr-2" ${settings.inApp ? 'checked' : ''}>
                        <span>In-app notifications</span>
                    </label>
                </div>
                <div class="mb-3">
                    <label class="flex items-center">
                        <input type="checkbox" id="autoRefreshEnabled" class="mr-2" ${settings.autoRefresh ? 'checked' : ''}>
                        <span>Auto-refresh notifications</span>
                    </label>
                </div>
                <div class="mb-3">
                    <label class="block mb-1">Refresh interval (seconds)</label>
                    <input type="number" id="refreshInterval" class="w-full p-2 border rounded" value="${settings.refreshInterval / 1000}" min="10" max="300">
                </div>
                <button id="saveSettingsBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">
                    Save Settings
                </button>
            </div>
        `;

        // Hide notification panel and show settings
        panel.classList.add('hidden');
        panel.parentNode.appendChild(settingsPanel);

        // Add event listeners
        document.getElementById('closeSettingsBtn').addEventListener('click', () => {
            settingsPanel.remove();
            panel.classList.remove('hidden');
        });

        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            // Get values
            const sound = document.getElementById('soundEnabled').checked;
            const desktop = document.getElementById('desktopEnabled').checked;
            const inApp = document.getElementById('inAppEnabled').checked;
            const autoRefresh = document.getElementById('autoRefreshEnabled').checked;
            const refreshInterval = Math.max(10, Math.min(300, parseInt(document.getElementById('refreshInterval').value))) * 1000;

            // Update settings
            if (window.SmartNotifications && window.SmartNotifications.updateSettings) {
                window.SmartNotifications.updateSettings({
                    sound,
                    desktop,
                    inApp,
                    autoRefresh,
                    refreshInterval
                });
            }

            // Close settings
            settingsPanel.remove();
            panel.classList.remove('hidden');
        });
    }
}

// Toggle notification panel
if (typeof toggleNotificationPanel !== 'function') {
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
}

// Create notification panel
if (typeof createNotificationPanel !== 'function') {
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
                <div class="px-4 py-2 text-center text-gray-500 dark:text-gray-400">No notifications</div>
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
        document.getElementById('markAllReadBtn').addEventListener('click', () => {
            if (window.SmartNotifications && window.SmartNotifications.markAllRead) {
                window.SmartNotifications.markAllRead();
            } else {
                markAllNotificationsRead();
            }
        });

        document.getElementById('notificationSettingsBtn').addEventListener('click', () => {
            if (window.SmartNotifications && window.SmartNotifications.showSettings) {
                window.SmartNotifications.showSettings();
            } else {
                showNotificationSettings();
            }
        });

        // Render notifications
        renderNotificationList();

        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (panel && !panel.contains(e.target) && !e.target.closest('.notification-button')) {
                panel.classList.add('hidden');
            }
        });
    }
}

// Extend SmartNotifications with missing functions
document.addEventListener('DOMContentLoaded', function() {
    // Wait for SmartNotifications to be initialized
    setTimeout(() => {
        if (window.SmartNotifications) {
            // Add missing functions
            if (!window.SmartNotifications.markAllRead) {
                window.SmartNotifications.markAllRead = markAllNotificationsRead;
            }

            if (!window.SmartNotifications.renderList) {
                window.SmartNotifications.renderList = renderNotificationList;
            }

            if (!window.SmartNotifications.showSettings) {
                window.SmartNotifications.showSettings = showNotificationSettings;
            }

            if (!window.SmartNotifications.togglePanel) {
                window.SmartNotifications.togglePanel = toggleNotificationPanel;
            }

            // Add notifications array if missing
            if (!window.SmartNotifications.notifications) {
                window.SmartNotifications.notifications = [];
            }

            console.log('Notification fixes applied');
        }
    }, 500);
});
