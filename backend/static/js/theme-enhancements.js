/**
 * Enhanced Theme Management for StockMaster Pro
 * Adds auto theme switching based on time and system preferences
 */

// Theme constants
const THEME = {
    LIGHT: 'light',
    DARK: 'dark',
    AUTO: 'auto'
};

// Time-based theme settings
const TIME_BASED = {
    MORNING_HOUR: 6,   // 6 AM - Switch to light mode
    EVENING_HOUR: 18   // 6 PM - Switch to dark mode
};

// Initialize theme system with enhanced features
function initEnhancedThemeSystem() {
    // Add auto theme option to localStorage if not present
    if (!localStorage.getItem('themeMode')) {
        localStorage.setItem('themeMode', THEME.AUTO);
    }

    // Apply theme based on current settings
    applyThemeBasedOnSettings();

    // Listen for system preference changes
    if (window.matchMedia) {
        const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // Add change listener with compatibility check
        if (darkModeMediaQuery.addEventListener) {
            darkModeMediaQuery.addEventListener('change', handleSystemThemeChange);
        } else if (darkModeMediaQuery.addListener) {
            // For older browsers
            darkModeMediaQuery.addListener(handleSystemThemeChange);
        }
    }

    // Set up time-based theme switching
    scheduleNextThemeChange();
}

// Apply theme based on current settings
function applyThemeBasedOnSettings() {
    const themeMode = localStorage.getItem('themeMode') || THEME.AUTO;
    
    if (themeMode === THEME.AUTO) {
        applyAutoTheme();
    } else {
        // Use StockMaster's existing theme function
        if (typeof window.StockMaster !== 'undefined' && typeof window.StockMaster.setTheme === 'function') {
            window.StockMaster.setTheme(themeMode);
        } else {
            // Fallback if StockMaster object is not available
            document.body.classList.toggle('dark', themeMode === THEME.DARK);
            document.body.classList.toggle('light', themeMode === THEME.LIGHT);
        }
    }
}

// Apply theme automatically based on time and system preferences
function applyAutoTheme() {
    const currentHour = new Date().getHours();
    const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Determine theme based on time of day
    let isDarkTheme = false;
    
    // First check time of day
    if (currentHour < TIME_BASED.MORNING_HOUR || currentHour >= TIME_BASED.EVENING_HOUR) {
        isDarkTheme = true;
    } else {
        // During day time, respect system preference
        isDarkTheme = systemPrefersDark;
    }
    
    // Apply the determined theme
    if (typeof window.StockMaster !== 'undefined' && typeof window.StockMaster.setTheme === 'function') {
        window.StockMaster.setTheme(isDarkTheme ? THEME.DARK : THEME.LIGHT);
    } else {
        // Fallback
        document.body.classList.toggle('dark', isDarkTheme);
        document.body.classList.toggle('light', !isDarkTheme);
    }
}

// Handle system theme preference change
function handleSystemThemeChange(e) {
    const themeMode = localStorage.getItem('themeMode');
    
    // Only react to system changes if in AUTO mode
    if (themeMode === THEME.AUTO) {
        applyAutoTheme();
    }
}

// Schedule next theme change based on time
function scheduleNextThemeChange() {
    const now = new Date();
    const currentHour = now.getHours();
    let nextChangeHour;
    
    // Determine next change time
    if (currentHour < TIME_BASED.MORNING_HOUR) {
        nextChangeHour = TIME_BASED.MORNING_HOUR;
    } else if (currentHour < TIME_BASED.EVENING_HOUR) {
        nextChangeHour = TIME_BASED.EVENING_HOUR;
    } else {
        nextChangeHour = TIME_BASED.MORNING_HOUR + 24; // Next day morning
    }
    
    // Calculate milliseconds until next change
    const nextChange = new Date(now);
    nextChange.setHours(nextChangeHour, 0, 0, 0);
    const timeUntilChange = nextChange - now;
    
    // Schedule the change
    setTimeout(() => {
        const themeMode = localStorage.getItem('themeMode');
        if (themeMode === THEME.AUTO) {
            applyAutoTheme();
        }
        // Schedule the next change
        scheduleNextThemeChange();
    }, timeUntilChange);
}

// Toggle between light, dark, and auto modes
function toggleEnhancedTheme() {
    const currentMode = localStorage.getItem('themeMode') || THEME.AUTO;
    let newMode;
    
    // Cycle through modes: auto -> light -> dark -> auto
    switch (currentMode) {
        case THEME.AUTO:
            newMode = THEME.LIGHT;
            break;
        case THEME.LIGHT:
            newMode = THEME.DARK;
            break;
        case THEME.DARK:
            newMode = THEME.AUTO;
            break;
        default:
            newMode = THEME.AUTO;
    }
    
    // Save new mode
    localStorage.setItem('themeMode', newMode);
    
    // Apply the new theme
    applyThemeBasedOnSettings();
    
    // Send to server if user is logged in
    if (typeof window.StockMaster !== 'undefined') {
        fetch('/switch-theme', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        });
    }
    
    // Show toast notification
    const toastMessage = getThemeModeMessage(newMode);
    if (typeof window.StockMaster !== 'undefined' && typeof window.StockMaster.showToast === 'function') {
        window.StockMaster.showToast(toastMessage, 'info');
    } else if (typeof showToast === 'function') {
        showToast(toastMessage, 'info');
    }
    
    return newMode;
}

// Get localized message for theme mode
function getThemeModeMessage(mode) {
    const lang = document.documentElement.lang || 'en';
    const isArabic = lang === 'ar';
    
    switch (mode) {
        case THEME.AUTO:
            return isArabic ? 'تم تفعيل الوضع التلقائي' : 'Auto mode enabled';
        case THEME.LIGHT:
            return isArabic ? 'تم تفعيل الوضع الفاتح' : 'Light mode enabled';
        case THEME.DARK:
            return isArabic ? 'تم تفعيل الوضع المظلم' : 'Dark mode enabled';
        default:
            return '';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initEnhancedThemeSystem);

// Export functions to global scope
window.ThemeEnhancements = {
    toggleEnhancedTheme,
    applyAutoTheme,
    getThemeMode: () => localStorage.getItem('themeMode') || THEME.AUTO
};
