/**
 * Bidirectional (RTL/LTR) Support for StockMaster Pro
 * This file contains JavaScript functions to enhance bidirectional support
 */

// Initialize bidirectional support when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initBidirectionalSupport();
});

/**
 * Initialize bidirectional support
 */
function initBidirectionalSupport() {
    // Set CSS variables based on current direction
    updateDirectionVariables();
    
    // Mirror directional icons
    mirrorDirectionalIcons();
    
    // Fix input groups for RTL
    fixInputGroups();
    
    // Enhance form layouts
    enhanceFormLayouts();
    
    // Fix tables for RTL
    fixTables();
    
    // Add ARIA attributes for screen readers
    addDirectionAriaAttributes();
    
    // Initialize language toggle
    initLanguageToggle();
}

/**
 * Update CSS variables based on current direction
 */
function updateDirectionVariables() {
    const isRTL = document.documentElement.dir === 'rtl';
    const root = document.documentElement;
    
    // Set direction variables
    root.style.setProperty('--reverse-direction', isRTL ? '-1' : '1');
    root.style.setProperty('--start-direction', isRTL ? 'right' : 'left');
    root.style.setProperty('--end-direction', isRTL ? 'left' : 'right');
    
    // Set text alignment
    root.style.setProperty('--text-align', isRTL ? 'right' : 'left');
    
    // Add a class to the body for easier styling
    document.body.classList.toggle('rtl-active', isRTL);
}

/**
 * Mirror directional icons based on current direction
 */
function mirrorDirectionalIcons() {
    const isRTL = document.documentElement.dir === 'rtl';
    
    // Find all directional icons
    const directionalIcons = document.querySelectorAll('.ri-arrow-right-line, .ri-arrow-left-line, .ri-chevron-right, .ri-chevron-left');
    
    directionalIcons.forEach(icon => {
        if (isRTL) {
            // Swap right and left icons
            if (icon.classList.contains('ri-arrow-right-line')) {
                icon.classList.remove('ri-arrow-right-line');
                icon.classList.add('ri-arrow-left-line');
            } else if (icon.classList.contains('ri-arrow-left-line')) {
                icon.classList.remove('ri-arrow-left-line');
                icon.classList.add('ri-arrow-right-line');
            } else if (icon.classList.contains('ri-chevron-right')) {
                icon.classList.remove('ri-chevron-right');
                icon.classList.add('ri-chevron-left');
            } else if (icon.classList.contains('ri-chevron-left')) {
                icon.classList.remove('ri-chevron-left');
                icon.classList.add('ri-chevron-right');
            }
        }
    });
}

/**
 * Fix input groups for RTL layout
 */
function fixInputGroups() {
    const isRTL = document.documentElement.dir === 'rtl';
    
    if (isRTL) {
        // Find all input groups
        const inputGroups = document.querySelectorAll('.input-group');
        
        inputGroups.forEach(group => {
            // Reverse the order of children
            const children = Array.from(group.children);
            children.reverse().forEach(child => group.appendChild(child));
            
            // Fix border radius
            const addon = group.querySelector('.input-group-addon');
            const input = group.querySelector('input, select, textarea');
            
            if (addon && input) {
                addon.style.borderRadius = '0 0.375rem 0.375rem 0';
                input.style.borderRadius = '0.375rem 0 0 0.375rem';
            }
        });
    }
}

/**
 * Enhance form layouts for bidirectional support
 */
function enhanceFormLayouts() {
    const isRTL = document.documentElement.dir === 'rtl';
    
    // Find all form groups
    const formGroups = document.querySelectorAll('.form-group');
    
    formGroups.forEach(group => {
        // Set text alignment
        group.style.textAlign = isRTL ? 'right' : 'left';
        
        // Align labels
        const label = group.querySelector('label');
        if (label) {
            label.style.textAlign = isRTL ? 'right' : 'left';
        }
    });
}

/**
 * Fix tables for RTL layout
 */
function fixTables() {
    const isRTL = document.documentElement.dir === 'rtl';
    
    if (isRTL) {
        // Find all tables
        const tables = document.querySelectorAll('table');
        
        tables.forEach(table => {
            // Set text alignment for table cells
            const cells = table.querySelectorAll('th, td');
            cells.forEach(cell => {
                cell.style.textAlign = 'right';
            });
        });
    }
}

/**
 * Add ARIA attributes for screen readers
 */
function addDirectionAriaAttributes() {
    const isRTL = document.documentElement.dir === 'rtl';
    
    // Announce language direction to screen readers
    document.body.setAttribute('aria-orientation', isRTL ? 'rtl' : 'ltr');
    
    // Add language attribute
    document.documentElement.lang = isRTL ? 'ar' : 'en';
}

/**
 * Initialize language toggle with enhanced UX
 */
function initLanguageToggle() {
    const languageToggle = document.querySelector('.language-toggle');
    
    if (languageToggle) {
        // Add click event listener
        languageToggle.addEventListener('click', function(e) {
            // Add a visual feedback animation
            this.classList.add('animate-pulse');
            
            // Announce language change to screen readers
            const announcement = document.createElement('div');
            announcement.setAttribute('aria-live', 'polite');
            announcement.classList.add('visually-hidden');
            announcement.textContent = document.documentElement.dir === 'rtl' 
                ? 'Switching to English' 
                : 'جاري التبديل إلى العربية';
            document.body.appendChild(announcement);
            
            // Remove the announcement after 2 seconds
            setTimeout(() => {
                document.body.removeChild(announcement);
            }, 2000);
        });
    }
}

// Export functions to global scope
window.StockMasterBidirectional = {
    initBidirectionalSupport,
    updateDirectionVariables,
    mirrorDirectionalIcons,
    fixInputGroups,
    enhanceFormLayouts,
    fixTables,
    addDirectionAriaAttributes,
    initLanguageToggle
};
