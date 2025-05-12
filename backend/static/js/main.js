// main.js - StockMaster Pro UI/UX helpers

/**
 * Theme Management
 * Handles dark/light mode switching and persistence with improved aesthetics
 */

// Set the theme (dark or light) with enhanced styling
function setTheme(theme) {
    // Apply theme to body class
    if (theme === 'dark') {
        document.body.classList.add('dark');
        document.body.classList.remove('light');

        // Update CSS variables for softer dark mode
        document.documentElement.style.setProperty('--bg-dark', '#2c2c2c');
        document.documentElement.style.setProperty('--text-dark', '#d4d4d4');
        document.documentElement.style.setProperty('--card-dark', '#363636');
    } else {
        document.body.classList.remove('dark');
        document.body.classList.add('light');

        // Reset CSS variables for light mode
        document.documentElement.style.setProperty('--bg-color-light', '#ffffff');
        document.documentElement.style.setProperty('--text-color-light', '#111111');
        document.documentElement.style.setProperty('--card-bg-light', '#ffffff');
        document.documentElement.style.setProperty('--input-bg-light', '#f5f5f5');
        document.documentElement.style.setProperty('--border-color-light', 'rgba(0, 0, 0, 0.1)');
    }

    // Store theme preference
    localStorage.setItem('theme', theme);

    // Update any theme toggle checkboxes
    const themeToggles = document.querySelectorAll('#darkModeToggle, #darkModeToggleTopbar');
    themeToggles.forEach(toggle => {
        if (toggle) toggle.checked = theme === 'dark';
    });

    // Apply smooth transition to all elements
    document.querySelectorAll('*').forEach(el => {
        if (!el.style.transition) {
            el.style.transition = 'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease';
        }
    });

    // Dispatch theme change event for charts and other components
    const themeChangedEvent = new CustomEvent('themeChanged', {
        detail: { theme: theme }
    });
    window.dispatchEvent(themeChangedEvent);

    // Update sidebar styling based on theme
    updateSidebarStyling(theme);
}

// Enhanced sidebar styling based on theme
function updateSidebarStyling(theme) {
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    const sidebar = document.querySelector('.sidebar');

    if (!sidebar) return;

    if (theme === 'dark') {
        sidebar.style.boxShadow = '0 0 20px rgba(0, 0, 0, 0.3)';
    } else {
        sidebar.style.boxShadow = '0 0 20px rgba(0, 0, 0, 0.1)';
    }

    // Enhance sidebar links with modern styling
    sidebarLinks.forEach(link => {
        // Add icon containers if they don't exist
        if (!link.querySelector('.icon-container')) {
            const icon = link.querySelector('i');
            if (icon) {
                const iconContainer = document.createElement('div');
                iconContainer.className = 'icon-container';
                iconContainer.style.width = '32px';
                iconContainer.style.height = '32px';
                iconContainer.style.borderRadius = '50%';
                iconContainer.style.display = 'flex';
                iconContainer.style.alignItems = 'center';
                iconContainer.style.justifyContent = 'center';
                iconContainer.style.marginRight = '10px';
                iconContainer.style.transition = 'all 0.3s ease';

                // Move the icon into the container
                link.removeChild(icon);
                iconContainer.appendChild(icon);
                link.prepend(iconContainer);
            }
        }

        // Update active link styling
        if (link.classList.contains('active')) {
            const iconContainer = link.querySelector('.icon-container');
            if (iconContainer) {
                iconContainer.style.backgroundColor = theme === 'dark' ? 'rgba(255, 167, 38, 0.2)' : 'rgba(255, 167, 38, 0.1)';
                iconContainer.style.color = '#ffa726';
            }
            link.style.borderRight = '3px solid #ffa726';
            link.style.backgroundColor = theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)';
        } else {
            // Reset non-active links
            const iconContainer = link.querySelector('.icon-container');
            if (iconContainer) {
                iconContainer.style.backgroundColor = 'transparent';
                iconContainer.style.color = 'inherit';
            }
            link.style.borderRight = 'none';
            link.style.backgroundColor = 'transparent';
        }

        // Enhance hover effect
        link.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.backgroundColor = theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)';
                const iconContainer = this.querySelector('.icon-container');
                if (iconContainer) {
                    iconContainer.style.backgroundColor = theme === 'dark' ? 'rgba(255, 167, 38, 0.1)' : 'rgba(255, 167, 38, 0.05)';
                    iconContainer.style.transform = 'scale(1.1)';
                }
            }
        });

        link.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.backgroundColor = 'transparent';
                const iconContainer = this.querySelector('.icon-container');
                if (iconContainer) {
                    iconContainer.style.backgroundColor = 'transparent';
                    iconContainer.style.transform = 'scale(1)';
                }
            }
        });
    });
}

// Get the current theme from localStorage or system preference
function getTheme() {
    return localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}

// Toggle between dark and light themes with animation
function toggleTheme() {
    const newTheme = document.body.classList.contains('dark') ? 'light' : 'dark';

    // Add transition effect to body
    document.body.style.transition = 'background-color 0.5s ease';

    // Apply theme with slight delay for visual effect
    setTimeout(() => {
        setTheme(newTheme);
    }, 50);

    // Send request to server to update theme preference
    fetch('/switch-theme', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            console.error('Failed to update theme preference');
        }
    })
    .catch(error => {
        console.error('Error updating theme preference:', error);
    });

    // Show toast notification
    showToast(
        newTheme === 'dark'
            ? (getLang() === 'ar' ? 'تم تفعيل الوضع المظلم' : 'Dark mode enabled')
            : (getLang() === 'ar' ? 'تم تفعيل الوضع الفاتح' : 'Light mode enabled'),
        'info',
        1500
    );
}

// Apply the saved theme on page load with animation
function applyThemeOnLoad() {
    const theme = getTheme();
    document.body.style.opacity = '0';
    setTheme(theme);
    setTimeout(() => {
        document.body.style.opacity = '1';
        document.body.style.transition = 'opacity 0.5s ease';
    }, 50);
}

/**
 * Language Management
 * Handles Arabic/English switching and persistence with translations
 */

// Translation dictionary
const translations = {
    'ar': {
        'search': 'بحث...',
        'add': 'إضافة',
        'edit': 'تعديل',
        'delete': 'حذف',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'back': 'رجوع',
        'loading': 'جاري التحميل...',
        'success': 'تم بنجاح',
        'error': 'حدث خطأ',
        'confirm': 'تأكيد',
        'yes': 'نعم',
        'no': 'لا',
        'welcome': 'مرحبًا بك في ستوك ماستر برو',
        'inventory': 'المخزون',
        'sales': 'المبيعات',
        'reports': 'التقارير',
        'settings': 'الإعدادات',
        'logout': 'تسجيل الخروج',
        'profile': 'الملف الشخصي'
    },
    'en': {
        'search': 'Search...',
        'add': 'Add',
        'edit': 'Edit',
        'delete': 'Delete',
        'save': 'Save',
        'cancel': 'Cancel',
        'back': 'Back',
        'loading': 'Loading...',
        'success': 'Success',
        'error': 'Error',
        'confirm': 'Confirm',
        'yes': 'Yes',
        'no': 'No',
        'welcome': 'Welcome to StockMaster Pro',
        'inventory': 'Inventory',
        'sales': 'Sales',
        'reports': 'Reports',
        'settings': 'Settings',
        'logout': 'Logout',
        'profile': 'Profile'
    }
};

// Translate function to get text based on current language
function __(key) {
    const lang = getLang();
    return translations[lang][key] || key;
}

// Set the language (ar or en) with enhanced RTL support
function setLang(lang) {
    const html = document.documentElement;
    html.lang = lang;
    html.dir = lang === 'ar' ? 'rtl' : 'ltr';
    localStorage.setItem('lang', lang);

    // Apply RTL/LTR specific styling
    if (lang === 'ar') {
        document.body.classList.add('rtl');
        document.body.classList.remove('ltr');
    } else {
        document.body.classList.add('ltr');
        document.body.classList.remove('rtl');
    }

    // Update placeholders and static text elements
    updateTextElements(lang);
}

// Update text elements based on language
function updateTextElements(lang) {
    // Update placeholders
    document.querySelectorAll('input[placeholder], textarea[placeholder]').forEach(el => {
        const placeholderKey = el.dataset.placeholderKey;
        if (placeholderKey && translations[lang][placeholderKey]) {
            el.placeholder = translations[lang][placeholderKey];
        }
    });

    // Update buttons and static text
    document.querySelectorAll('[data-text-key]').forEach(el => {
        const textKey = el.dataset.textKey;
        if (textKey && translations[lang][textKey]) {
            el.textContent = translations[lang][textKey];
        }
    });
}

// Get the current language from localStorage or default to Arabic
function getLang() {
    return localStorage.getItem('lang') || 'ar';
}

// Toggle between Arabic and English with animation
function toggleLang() {
    const currentLang = getLang();
    const newLang = currentLang === 'ar' ? 'en' : 'ar';

    // Show loading indicator
    const loader = document.createElement('div');
    loader.className = 'language-transition-loader';
    loader.innerHTML = `<div class="spinner"></div><p>${newLang === 'ar' ? 'جاري التغيير للعربية...' : 'Switching to English...'}</p>`;
    loader.style.position = 'fixed';
    loader.style.top = '0';
    loader.style.left = '0';
    loader.style.width = '100%';
    loader.style.height = '100%';
    loader.style.backgroundColor = 'rgba(0,0,0,0.7)';
    loader.style.color = 'white';
    loader.style.display = 'flex';
    loader.style.flexDirection = 'column';
    loader.style.alignItems = 'center';
    loader.style.justifyContent = 'center';
    loader.style.zIndex = '9999';
    document.body.appendChild(loader);

    // Apply language change locally first
    setLang(newLang);

    // Use fetch API to call the switch-lang endpoint
    fetch('/switch-lang', {
        method: 'GET',
        headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.ok) {
            // Reload the page to apply changes from server
            window.location.reload();
        } else {
            console.error('Failed to switch language');
            // Remove loader if there's an error
            document.body.removeChild(loader);
        }
    })
    .catch(error => {
        console.error('Error switching language:', error);
        // Remove loader if there's an error
        document.body.removeChild(loader);
    });
}

// Apply the saved language on page load
function applyLangOnLoad() {
    const lang = getLang();
    setLang(lang);
}

// Function for language switching from the topbar
function toggleLanguage() {
    toggleLang();
}

/**
 * Sidebar Management
 * Handles sidebar collapse and mobile drawer
 */

// Toggle sidebar for mobile and desktop
function toggleSidebar(force) {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (!sidebar || !backdrop) return;

    const isOpen = sidebar.classList.contains('open');

    if (force === false || isOpen) {
        // Close sidebar
        sidebar.classList.remove('open');
        backdrop.classList.add('hidden');
        sidebar.style.transform = 'translateX(-100%)';
        setTimeout(() => {
            backdrop.style.opacity = '0';
        }, 50);
    } else {
        // Open sidebar
        sidebar.classList.add('open');
        backdrop.classList.remove('hidden');
        sidebar.style.transform = 'translateX(0)';
        backdrop.style.opacity = '1';
    }
}

// Initialize sidebar with proper styling and event listeners
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');

    if (!sidebar || !backdrop) return;

    // Add transition for smooth open/close
    sidebar.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
    backdrop.style.transition = 'opacity 0.3s ease';

    // Set initial state
    if (window.innerWidth < 768) {
        sidebar.style.transform = 'translateX(-100%)';
        backdrop.classList.add('hidden');
    }

    // Add event listeners
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => toggleSidebar());
    }

    backdrop.addEventListener('click', () => toggleSidebar(false));

    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) {
            sidebar.style.transform = 'translateX(0)';
            backdrop.classList.add('hidden');
        } else if (!sidebar.classList.contains('open')) {
            sidebar.style.transform = 'translateX(-100%)';
        }
    });
}

// Shake effect for error with improved animation
function shakeForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (form) {
        form.classList.remove('shake');
        void form.offsetWidth; // reflow
        form.classList.add('shake');

        // Add CSS if not already in document
        if (!document.getElementById('shake-animation')) {
            const style = document.createElement('style');
            style.id = 'shake-animation';
            style.textContent = `
                @keyframes shake {
                    0%, 100% { transform: translateX(0); }
                    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                    20%, 40%, 60%, 80% { transform: translateX(5px); }
                }
                .shake {
                    animation: shake 0.6s cubic-bezier(.36,.07,.19,.97) both;
                }
            `;
            document.head.appendChild(style);
        }

        setTimeout(() => form.classList.remove('shake'), 600);
    }
}

// Enhanced Toast/snackbar with theme-aware styling
function showToast(message, type = 'success', duration = 3000) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-message');
    existingToasts.forEach(toast => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    });

    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.position = 'fixed';
        toastContainer.style.bottom = '20px';
        toastContainer.style.right = '20px';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    let toast = document.createElement('div');
    toast.className = 'toast-message ' + type;
    toast.style.minWidth = '250px';
    toast.style.margin = '10px';
    toast.style.padding = '15px 20px';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.style.fontSize = '14px';
    toast.style.fontWeight = '500';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(20px)';
    toast.style.transition = 'all 0.3s ease';

    // Set theme-aware colors
    const isDark = document.body.classList.contains('dark');
    if (isDark) {
        toast.style.backgroundColor = type === 'success' ? '#2e7d32' :
                                     type === 'error' ? '#c62828' :
                                     type === 'warning' ? '#ef6c00' : '#0277bd';
        toast.style.color = '#ffffff';
    } else {
        toast.style.backgroundColor = type === 'success' ? '#e8f5e9' :
                                     type === 'error' ? '#ffebee' :
                                     type === 'warning' ? '#fff3e0' : '#e1f5fe';
        toast.style.color = type === 'success' ? '#2e7d32' :
                           type === 'error' ? '#c62828' :
                           type === 'warning' ? '#ef6c00' : '#0277bd';
    }

    // Add icon based on type
    const icon = type === 'success' ? '✓' :
                type === 'error' ? '✕' :
                type === 'warning' ? '⚠' : 'ℹ';

    toast.innerHTML = `<span style="margin-right: 8px;">${icon}</span> ${message}`;

    // Add to container
    toastContainer.appendChild(toast);

    // Show with animation
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 10);

    // Hide after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(20px)';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Password visibility toggle with improved UX
function togglePassword(inputId, iconSelector) {
    const input = document.getElementById(inputId);
    const icon = document.querySelector(iconSelector);

    if (input && icon) {
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('ri-eye-line');
            icon.classList.add('ri-eye-off-line');

            // Auto-hide after 3 seconds for security
            setTimeout(() => {
                if (input.type === 'text') {
                    input.type = 'password';
                    icon.classList.remove('ri-eye-off-line');
                    icon.classList.add('ri-eye-line');
                }
            }, 3000);
        } else {
            input.type = 'password';
            icon.classList.remove('ri-eye-off-line');
            icon.classList.add('ri-eye-line');
        }
    }
}

// Page transition effect
function addPageTransitions() {
    // Add CSS for page transitions
    const style = document.createElement('style');
    style.textContent = `
        .page-transition-enter {
            opacity: 0;
            transform: translateY(20px);
        }
        .page-transition-enter-active {
            opacity: 1;
            transform: translateY(0);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        .page-transition-exit {
            opacity: 1;
        }
        .page-transition-exit-active {
            opacity: 0;
            transition: opacity 0.3s ease;
        }
    `;
    document.head.appendChild(style);

    // Add transition to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('page-transition-enter');
        setTimeout(() => {
            mainContent.classList.add('page-transition-enter-active');
        }, 10);
    }
}

// Dynamic breadcrumbs
function updateBreadcrumbs() {
    const breadcrumbContainer = document.querySelector('.breadcrumbs');
    if (!breadcrumbContainer) return;

    const path = window.location.pathname;
    const parts = path.split('/').filter(part => part);

    let breadcrumbHTML = `<a href="/" class="breadcrumb-item">Home</a>`;
    let currentPath = '';

    parts.forEach((part, index) => {
        currentPath += `/${part}`;
        const isLast = index === parts.length - 1;

        // Format the part name (replace dashes with spaces, capitalize)
        const formattedPart = part.replace(/-/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());

        if (isLast) {
            breadcrumbHTML += `<span class="breadcrumb-separator">/</span>
                              <span class="breadcrumb-item current">${formattedPart}</span>`;
        } else {
            breadcrumbHTML += `<span class="breadcrumb-separator">/</span>
                              <a href="${currentPath}" class="breadcrumb-item">${formattedPart}</a>`;
        }
    });

    breadcrumbContainer.innerHTML = breadcrumbHTML;
}

// On load, apply theme/lang and initialize UI
window.addEventListener('DOMContentLoaded', function() {
    // Apply theme and language
    applyThemeOnLoad();
    applyLangOnLoad();

    // Initialize UI components
    initSidebar();
    addPageTransitions();
    updateBreadcrumbs();

    // Add loader for initial page load
    const loader = document.getElementById('pageLoader');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 300);
        }, 500);
    }
});

// Toggle user menu
function toggleUserMenu() {
    const userMenu = document.getElementById('userMenu');
    if (userMenu) {
        userMenu.classList.toggle('hidden');

        // Close when clicking outside
        if (!userMenu.classList.contains('hidden')) {
            const closeMenu = function(e) {
                if (!userMenu.contains(e.target) && !e.target.closest('button[onclick*="toggleUserMenu"]')) {
                    userMenu.classList.add('hidden');
                    document.removeEventListener('click', closeMenu);
                }
            };

            // Add event listener with a slight delay to avoid immediate triggering
            setTimeout(() => {
                document.addEventListener('click', closeMenu);
            }, 10);
        }
    }
}

// Export theme and language functions to global scope
window.StockMaster = window.StockMaster || {};
Object.assign(window.StockMaster, {
    // Theme functions
    setTheme,
    getTheme,
    toggleTheme,
    applyThemeOnLoad,
    updateSidebarStyling,

    // Language functions
    setLang,
    getLang,
    toggleLang,
    toggleLanguage,
    applyLangOnLoad,
    __,  // Translation helper

    // Sidebar functions
    toggleSidebar,
    initSidebar,

    // User menu
    toggleUserMenu,

    // UI helpers
    showToast,
    shakeForm,
    togglePassword,
    addPageTransitions,
    updateBreadcrumbs
});