/**
 * Role-based UI Adaptation for StockMaster Pro
 * This module handles dynamic UI changes based on user roles and permissions
 */

// StockMaster namespace
window.StockMaster = window.StockMaster || {};

// Role-based UI module
StockMaster.RoleUI = (function() {
    // Private variables
    let _userRoles = [];
    let _userPermissions = [];
    let _primaryRole = '';
    
    /**
     * Initialize the role-based UI system
     * @param {Object} config Configuration object with roles and permissions
     */
    function init(config) {
        _userRoles = config.roles || [];
        _userPermissions = config.permissions || [];
        _primaryRole = config.primaryRole || '';
        
        console.log('Role UI initialized with roles:', _userRoles);
        console.log('User permissions:', _userPermissions);
        
        // Apply role-based UI adaptations
        applyRoleBasedUI();
        
        // Listen for dynamic content changes
        observeContentChanges();
    }
    
    /**
     * Apply role-based UI adaptations to the current page
     */
    function applyRoleBasedUI() {
        // Add role-specific body class
        if (_primaryRole) {
            document.body.classList.add(`role-${_primaryRole}`);
        }
        
        // Hide elements based on permissions
        hideUnauthorizedElements();
        
        // Adapt dashboard based on role
        adaptDashboard();
        
        // Adapt sidebar based on role
        adaptSidebar();
        
        // Apply role-specific styles
        applyRoleStyles();
    }
    
    /**
     * Hide elements that the user doesn't have permission to see
     */
    function hideUnauthorizedElements() {
        // Find all elements with data-requires-permission attribute
        const restrictedElements = document.querySelectorAll('[data-requires-permission]');
        
        restrictedElements.forEach(element => {
            const requiredPermission = element.getAttribute('data-requires-permission');
            if (!hasPermission(requiredPermission)) {
                element.style.display = 'none';
            }
        });
        
        // Find all elements with data-requires-role attribute
        const roleRestrictedElements = document.querySelectorAll('[data-requires-role]');
        
        roleRestrictedElements.forEach(element => {
            const requiredRole = element.getAttribute('data-requires-role');
            if (!hasRole(requiredRole)) {
                element.style.display = 'none';
            }
        });
    }
    
    /**
     * Adapt dashboard based on user role
     */
    function adaptDashboard() {
        const dashboardContainer = document.querySelector('.dashboard-container');
        if (!dashboardContainer) return;
        
        // Apply role-specific dashboard layouts
        if (hasRole('manager')) {
            dashboardContainer.classList.add('manager-dashboard');
            // Show all dashboard sections
        } else if (hasRole('cashier')) {
            dashboardContainer.classList.add('cashier-dashboard');
            // Hide inventory management, show POS and sales sections prominently
            hideElementsBySelector('.dashboard-inventory-management');
            prioritizeElementsBySelector('.dashboard-pos, .dashboard-sales');
        } else if (hasRole('inventory_manager')) {
            dashboardContainer.classList.add('inventory-dashboard');
            // Highlight inventory sections, hide sales reports
            hideElementsBySelector('.dashboard-financial-reports');
            prioritizeElementsBySelector('.dashboard-inventory, .dashboard-stock-alerts');
        } else if (hasRole('accountant')) {
            dashboardContainer.classList.add('accountant-dashboard');
            // Show financial reports prominently, hide inventory management
            hideElementsBySelector('.dashboard-inventory-management, .dashboard-marketing');
            prioritizeElementsBySelector('.dashboard-financial-reports, .dashboard-sales-summary');
        }
    }
    
    /**
     * Adapt sidebar based on user role
     */
    function adaptSidebar() {
        const sidebar = document.querySelector('#sidebar');
        if (!sidebar) return;
        
        // Hide sidebar links based on permissions
        const sidebarLinks = sidebar.querySelectorAll('.sidebar-link');
        
        sidebarLinks.forEach(link => {
            const href = link.getAttribute('href');
            
            // Hide inventory links for cashiers
            if (hasRole('cashier') && (href.includes('inventory') || href.includes('raw_materials'))) {
                if (!hasPermission('manage_inventory')) {
                    link.style.display = 'none';
                }
            }
            
            // Hide financial reports for non-accountants and non-managers
            if (!hasRole('accountant') && !hasRole('manager') && href.includes('reports')) {
                if (!hasPermission('view_reports')) {
                    link.style.display = 'none';
                }
            }
        });
    }
    
    /**
     * Apply role-specific styles
     */
    function applyRoleStyles() {
        // Apply role-specific accent colors
        let accentColor = '#4A90E2'; // Default blue
        
        if (hasRole('manager')) {
            accentColor = '#4A90E2'; // Blue for managers
        } else if (hasRole('cashier')) {
            accentColor = '#4CAF50'; // Green for cashiers
        } else if (hasRole('inventory_manager')) {
            accentColor = '#FF9800'; // Orange for inventory managers
        } else if (hasRole('accountant')) {
            accentColor = '#9C27B0'; // Purple for accountants
        }
        
        document.documentElement.style.setProperty('--role-accent-color', accentColor);
    }
    
    /**
     * Prioritize certain elements by adding a class and moving them up
     * @param {string} selector CSS selector for elements to prioritize
     */
    function prioritizeElementsBySelector(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.classList.add('role-prioritized');
            // Move to the top if it has a parent
            if (el.parentNode) {
                el.parentNode.prepend(el);
            }
        });
    }
    
    /**
     * Hide elements matching a selector
     * @param {string} selector CSS selector for elements to hide
     */
    function hideElementsBySelector(selector) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
            el.style.display = 'none';
        });
    }
    
    /**
     * Check if user has a specific permission
     * @param {string} permission Permission name to check
     * @returns {boolean} True if user has the permission
     */
    function hasPermission(permission) {
        return _userPermissions.includes(permission);
    }
    
    /**
     * Check if user has a specific role
     * @param {string} role Role name to check
     * @returns {boolean} True if user has the role
     */
    function hasRole(role) {
        return _userRoles.includes(role);
    }
    
    /**
     * Observe DOM changes to apply role-based UI to dynamically added content
     */
    function observeContentChanges() {
        // Create a MutationObserver to watch for DOM changes
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                    // Check if we need to apply permissions to new elements
                    hideUnauthorizedElements();
                }
            });
        });
        
        // Start observing the document with the configured parameters
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    // Public API
    return {
        init: init,
        hasPermission: hasPermission,
        hasRole: hasRole,
        applyRoleBasedUI: applyRoleBasedUI
    };
})();

// Initialize on page load if the user data is available
document.addEventListener('DOMContentLoaded', function() {
    // The user roles and permissions will be injected by the template
    if (window.userRolesData) {
        StockMaster.RoleUI.init(window.userRolesData);
    }
});
