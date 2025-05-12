/**
 * Floating Action Button for StockMaster Pro
 * Provides quick access to common actions on mobile and tablet devices
 */

// Initialize floating action button
document.addEventListener('DOMContentLoaded', function() {
    initFloatingActionButton();
});

// Initialize floating action button
function initFloatingActionButton() {
    const floatingBtn = document.getElementById('floatingActionBtn');
    const floatingMenu = document.getElementById('floatingActionMenu');
    
    if (!floatingBtn || !floatingMenu) return;
    
    // Show floating button on mobile/tablet
    if (window.innerWidth <= 768) {
        floatingBtn.classList.remove('hidden');
    }
    
    // Toggle menu on button click
    floatingBtn.addEventListener('click', function() {
        toggleFloatingMenu();
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!floatingBtn.contains(e.target) && !floatingMenu.contains(e.target) && !floatingMenu.classList.contains('hidden')) {
            hideFloatingMenu();
        }
    });
    
    // Apply role-based permissions to menu items
    applyRolePermissionsToMenu();
    
    // Add swipe gesture support if available
    if (window.GestureSupport && window.GestureSupport.register) {
        addGestureSupport();
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            floatingBtn.classList.remove('hidden');
        } else {
            floatingBtn.classList.add('hidden');
            hideFloatingMenu();
        }
    });
}

// Toggle floating menu
function toggleFloatingMenu() {
    const floatingBtn = document.getElementById('floatingActionBtn');
    const floatingMenu = document.getElementById('floatingActionMenu');
    
    if (!floatingBtn || !floatingMenu) return;
    
    if (floatingMenu.classList.contains('hidden')) {
        showFloatingMenu();
    } else {
        hideFloatingMenu();
    }
}

// Show floating menu
function showFloatingMenu() {
    const floatingBtn = document.getElementById('floatingActionBtn');
    const floatingMenu = document.getElementById('floatingActionMenu');
    
    if (!floatingBtn || !floatingMenu) return;
    
    // Show menu
    floatingMenu.classList.remove('hidden');
    
    // Animate menu items
    const menuItems = floatingMenu.querySelectorAll('.floating-action-item');
    menuItems.forEach((item, index) => {
        item.style.transitionDelay = `${index * 0.05}s`;
        setTimeout(() => {
            item.classList.add('show');
        }, 10);
    });
    
    // Rotate button icon
    floatingBtn.classList.add('active');
}

// Hide floating menu
function hideFloatingMenu() {
    const floatingBtn = document.getElementById('floatingActionBtn');
    const floatingMenu = document.getElementById('floatingActionMenu');
    
    if (!floatingBtn || !floatingMenu) return;
    
    // Hide menu items with animation
    const menuItems = floatingMenu.querySelectorAll('.floating-action-item');
    menuItems.forEach((item, index) => {
        const reverseIndex = menuItems.length - 1 - index;
        item.style.transitionDelay = `${reverseIndex * 0.05}s`;
        item.classList.remove('show');
    });
    
    // Hide menu after animation
    setTimeout(() => {
        floatingMenu.classList.add('hidden');
    }, menuItems.length * 50 + 100);
    
    // Rotate button icon back
    floatingBtn.classList.remove('active');
}

// Apply role-based permissions to menu items
function applyRolePermissionsToMenu() {
    const menuItems = document.querySelectorAll('.floating-action-item[data-requires-permission]');
    
    menuItems.forEach(item => {
        const requiredPermission = item.getAttribute('data-requires-permission');
        
        // Check if user has permission
        if (window.userRolesData && window.userRolesData.permissions) {
            const hasPermission = window.userRolesData.permissions.includes(requiredPermission);
            
            if (!hasPermission) {
                item.classList.add('hidden');
            }
        }
    });
}

// Add gesture support
function addGestureSupport() {
    // Register swipe up gesture to show menu
    window.GestureSupport.register(window.GestureSupport.types.SWIPE_UP, (data) => {
        if (data.distance > 100 && window.innerWidth <= 768) {
            showFloatingMenu();
        }
    });
    
    // Register swipe down gesture to hide menu
    window.GestureSupport.register(window.GestureSupport.types.SWIPE_DOWN, (data) => {
        if (data.distance > 100 && !document.getElementById('floatingActionMenu').classList.contains('hidden')) {
            hideFloatingMenu();
        }
    });
}

// Add CSS styles for floating action button and menu
function addFloatingActionStyles() {
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .floating-action-btn {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            z-index: 100;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        [dir="rtl"] .floating-action-btn {
            right: auto;
            left: 2rem;
        }
        
        .floating-action-btn i {
            font-size: 1.75rem;
            transition: transform 0.3s ease;
        }
        
        .floating-action-btn.active i {
            transform: rotate(45deg);
        }
        
        .floating-action-menu {
            position: fixed;
            bottom: 7rem;
            right: 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            z-index: 99;
        }
        
        [dir="rtl"] .floating-action-menu {
            right: auto;
            left: 2rem;
        }
        
        .floating-action-item {
            display: flex;
            align-items: center;
            background-color: var(--card-bg);
            border-radius: 2rem;
            padding: 0.75rem 1.25rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            color: var(--text-color);
            text-decoration: none;
            transform: scale(0.5) translateY(20px);
            opacity: 0;
            transition: all 0.3s ease;
        }
        
        .floating-action-item.show {
            transform: scale(1) translateY(0);
            opacity: 1;
        }
        
        .floating-action-item i {
            margin-right: 0.5rem;
            font-size: 1.25rem;
            color: var(--primary-color);
        }
        
        [dir="rtl"] .floating-action-item i {
            margin-right: 0;
            margin-left: 0.5rem;
        }
    `;
    
    document.head.appendChild(styleElement);
}

// Add styles on load
addFloatingActionStyles();
