/**
 * StockMaster Pro - Core JavaScript
 * Core functionality for the StockMaster Pro application
 */

(function() {
  'use strict';

  // DOM elements
  let sidebarToggle;
  let sidebar;
  let userDropdownToggle;
  let userDropdownMenu;
  let alertCloseButtons;
  
  /**
   * Initialize the core functionality
   */
  function init() {
    // Get DOM elements
    sidebarToggle = document.getElementById('sidebar-toggle');
    sidebar = document.querySelector('.sidebar');
    userDropdownToggle = document.querySelector('.user-dropdown-toggle');
    userDropdownMenu = document.querySelector('.user-dropdown-menu');
    alertCloseButtons = document.querySelectorAll('.alert-close');
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize components
    initializeSidebar();
    initializeDropdowns();
    initializeAlerts();
    initializeTooltips();
    initializeModals();
    
    // Add body class when JavaScript is available
    document.body.classList.add('js-enabled');
  }
  
  /**
   * Set up event listeners
   */
  function setupEventListeners() {
    // Sidebar toggle
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', toggleSidebar);
    }
    
    // User dropdown toggle
    if (userDropdownToggle && userDropdownMenu) {
      userDropdownToggle.addEventListener('click', toggleUserDropdown);
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', closeDropdownsOnClickOutside);
    
    // Alert close buttons
    if (alertCloseButtons.length > 0) {
      alertCloseButtons.forEach(button => {
        button.addEventListener('click', closeAlert);
      });
    }
    
    // Handle responsive sidebar
    window.addEventListener('resize', handleResize);
  }
  
  /**
   * Initialize sidebar functionality
   */
  function initializeSidebar() {
    // Create sidebar backdrop for mobile
    if (sidebar && !document.querySelector('.sidebar-backdrop')) {
      const backdrop = document.createElement('div');
      backdrop.className = 'sidebar-backdrop';
      backdrop.addEventListener('click', closeSidebar);
      sidebar.parentNode.insertBefore(backdrop, sidebar.nextSibling);
    }
    
    // Check if sidebar should be collapsed based on saved preference
    const sidebarCollapsed = localStorage.getItem('stockmaster-sidebar-collapsed') === 'true';
    if (sidebarCollapsed && sidebar) {
      sidebar.classList.add('sidebar-collapsed');
      updateSidebarToggleIcon(true);
    }
    
    // Handle initial window size
    handleResize();
  }
  
  /**
   * Toggle sidebar expanded/collapsed state
   */
  function toggleSidebar() {
    if (!sidebar) return;
    
    const isCollapsed = sidebar.classList.contains('sidebar-collapsed');
    const isMobile = window.innerWidth < 1024;
    
    if (isMobile) {
      // On mobile, toggle open/closed
      sidebar.classList.toggle('sidebar-open');
    } else {
      // On desktop, toggle collapsed/expanded
      sidebar.classList.toggle('sidebar-collapsed');
      
      // Save preference
      localStorage.setItem('stockmaster-sidebar-collapsed', !isCollapsed);
    }
    
    // Update icon
    updateSidebarToggleIcon(!isCollapsed);
  }
  
  /**
   * Close the sidebar (mobile only)
   */
  function closeSidebar() {
    if (sidebar) {
      sidebar.classList.remove('sidebar-open');
    }
  }
  
  /**
   * Update the sidebar toggle icon based on the current state
   * @param {boolean} isCollapsed - Whether the sidebar is collapsed
   */
  function updateSidebarToggleIcon(isCollapsed) {
    if (!sidebarToggle) return;
    
    const iconElement = sidebarToggle.querySelector('i') || sidebarToggle;
    
    if (isCollapsed) {
      // When collapsed, show expand icon
      iconElement.className = iconElement.className.replace('ri-menu-fold-line', 'ri-menu-unfold-line');
    } else {
      // When expanded, show collapse icon
      iconElement.className = iconElement.className.replace('ri-menu-unfold-line', 'ri-menu-fold-line');
    }
  }
  
  /**
   * Handle window resize events
   */
  function handleResize() {
    const isMobile = window.innerWidth < 1024;
    
    if (sidebar) {
      if (isMobile) {
        // On mobile, remove collapsed class and add necessary mobile classes
        sidebar.classList.remove('sidebar-collapsed');
        document.body.classList.add('sidebar-mobile');
      } else {
        // On desktop, check saved preference
        const sidebarCollapsed = localStorage.getItem('stockmaster-sidebar-collapsed') === 'true';
        if (sidebarCollapsed) {
          sidebar.classList.add('sidebar-collapsed');
        }
        
        // Remove mobile classes
        sidebar.classList.remove('sidebar-open');
        document.body.classList.remove('sidebar-mobile');
      }
    }
  }
  
  /**
   * Initialize dropdown functionality
   */
  function initializeDropdowns() {
    // Add aria attributes for accessibility
    if (userDropdownToggle && userDropdownMenu) {
      userDropdownToggle.setAttribute('aria-expanded', 'false');
      userDropdownToggle.setAttribute('aria-controls', 'user-dropdown-menu');
      userDropdownMenu.setAttribute('id', 'user-dropdown-menu');
      userDropdownMenu.setAttribute('aria-hidden', 'true');
    }
  }
  
  /**
   * Toggle user dropdown menu
   * @param {Event} e - The click event
   */
  function toggleUserDropdown(e) {
    e.stopPropagation();
    
    if (!userDropdownMenu) return;
    
    const isOpen = userDropdownMenu.classList.contains('show');
    
    // Close all other dropdowns
    closeAllDropdowns();
    
    if (!isOpen) {
      // Open this dropdown
      userDropdownMenu.classList.add('show');
      userDropdownToggle.setAttribute('aria-expanded', 'true');
      userDropdownMenu.setAttribute('aria-hidden', 'false');
    }
  }
  
  /**
   * Close all dropdowns
   */
  function closeAllDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    const toggles = document.querySelectorAll('[aria-expanded="true"]');
    
    dropdowns.forEach(dropdown => {
      dropdown.classList.remove('show');
      dropdown.setAttribute('aria-hidden', 'true');
    });
    
    toggles.forEach(toggle => {
      toggle.setAttribute('aria-expanded', 'false');
    });
  }
  
  /**
   * Close dropdowns when clicking outside
   * @param {Event} e - The click event
   */
  function closeDropdownsOnClickOutside(e) {
    if (!e.target.closest('.dropdown')) {
      closeAllDropdowns();
    }
  }
  
  /**
   * Initialize alert functionality
   */
  function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds if they have the 'alert-auto-dismiss' class
    const autoDismissAlerts = document.querySelectorAll('.alert.alert-auto-dismiss');
    
    autoDismissAlerts.forEach(alert => {
      setTimeout(() => {
        dismissAlert(alert);
      }, 5000);
    });
  }
  
  /**
   * Close an alert
   * @param {Event} e - The click event
   */
  function closeAlert(e) {
    const alert = e.target.closest('.alert');
    if (alert) {
      dismissAlert(alert);
    }
  }
  
  /**
   * Dismiss an alert with animation
   * @param {HTMLElement} alert - The alert element to dismiss
   */
  function dismissAlert(alert) {
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
      alert.style.height = alert.offsetHeight + 'px';
      alert.style.marginTop = '0';
      alert.style.marginBottom = '0';
      alert.style.padding = '0';
      alert.style.overflow = 'hidden';
      
      setTimeout(() => {
        alert.style.height = '0';
        alert.style.marginTop = '0';
        alert.style.marginBottom = '0';
        
        setTimeout(() => {
          alert.remove();
        }, 300);
      }, 10);
    }, 300);
  }
  
  /**
   * Initialize tooltip functionality
   */
  function initializeTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(trigger => {
      trigger.addEventListener('mouseenter', showTooltip);
      trigger.addEventListener('mouseleave', hideTooltip);
      trigger.addEventListener('focus', showTooltip);
      trigger.addEventListener('blur', hideTooltip);
    });
  }
  
  /**
   * Show a tooltip
   * @param {Event} e - The mouseenter or focus event
   */
  function showTooltip(e) {
    const trigger = e.target;
    const tooltipText = trigger.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const triggerRect = trigger.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    tooltip.style.top = (triggerRect.top - tooltipRect.height - 10) + 'px';
    tooltip.style.left = (triggerRect.left + (triggerRect.width / 2) - (tooltipRect.width / 2)) + 'px';
    
    // Store reference to tooltip
    trigger._tooltip = tooltip;
    
    // Show tooltip with animation
    setTimeout(() => {
      tooltip.classList.add('tooltip-visible');
    }, 10);
  }
  
  /**
   * Hide a tooltip
   * @param {Event} e - The mouseleave or blur event
   */
  function hideTooltip(e) {
    const trigger = e.target;
    const tooltip = trigger._tooltip;
    
    if (!tooltip) return;
    
    // Hide tooltip with animation
    tooltip.classList.remove('tooltip-visible');
    
    // Remove tooltip after animation
    setTimeout(() => {
      if (tooltip.parentNode) {
        tooltip.parentNode.removeChild(tooltip);
      }
      delete trigger._tooltip;
    }, 300);
  }
  
  /**
   * Initialize modal functionality
   */
  function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modalCloseButtons = document.querySelectorAll('[data-modal-close]');
    
    modalTriggers.forEach(trigger => {
      trigger.addEventListener('click', openModal);
    });
    
    modalCloseButtons.forEach(button => {
      button.addEventListener('click', closeModal);
    });
    
    // Close modal when clicking on backdrop
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal')) {
        closeModal(e);
      }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
          e.preventDefault();
          closeModal({ target: openModal });
        }
      }
    });
  }
  
  /**
   * Open a modal
   * @param {Event} e - The click event
   */
  function openModal(e) {
    e.preventDefault();
    
    const modalId = e.target.getAttribute('data-modal');
    const modal = document.getElementById(modalId);
    
    if (!modal) return;
    
    // Show modal
    modal.classList.add('show');
    document.body.classList.add('modal-open');
    
    // Set focus to first focusable element
    const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length > 0) {
      focusable[0].focus();
    }
  }
  
  /**
   * Close a modal
   * @param {Event} e - The click event
   */
  function closeModal(e) {
    const modal = e.target.closest('.modal');
    
    if (!modal) return;
    
    // Hide modal
    modal.classList.remove('show');
    document.body.classList.remove('modal-open');
  }
  
  // Initialize when the DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
