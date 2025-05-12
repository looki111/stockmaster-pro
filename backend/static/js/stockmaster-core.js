/**
 * StockMaster Pro - Core JavaScript
 * Handles core functionality like sidebar, theme switching, and responsive behavior
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize sidebar toggle
  initSidebar();

  // Initialize theme toggle
  initThemeToggle();

  // Initialize dropdowns
  initDropdowns();

  // Initialize responsive behavior
  initResponsiveBehavior();
});

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const appContainer = document.querySelector('.app-container');

  // Check if sidebar state is stored in localStorage
  const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';

  if (sidebarCollapsed) {
    appContainer.classList.add('sidebar-collapsed');
    updateSidebarToggleIcon(true);
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      appContainer.classList.toggle('sidebar-collapsed');

      const isCollapsed = appContainer.classList.contains('sidebar-collapsed');
      localStorage.setItem('sidebar-collapsed', isCollapsed);

      updateSidebarToggleIcon(isCollapsed);
    });
  }
}

/**
 * Update sidebar toggle icon based on sidebar state
 * @param {boolean} isCollapsed - Whether the sidebar is collapsed
 */
function updateSidebarToggleIcon(isCollapsed) {
  const sidebarToggle = document.getElementById('sidebar-toggle');

  if (sidebarToggle) {
    const icon = sidebarToggle.querySelector('i');

    if (icon) {
      if (isCollapsed) {
        icon.classList.remove('ri-menu-fold-line');
        icon.classList.add('ri-menu-unfold-line');
      } else {
        icon.classList.remove('ri-menu-unfold-line');
        icon.classList.add('ri-menu-fold-line');
      }
    }
  }
}

/**
 * Initialize theme toggle functionality
 */
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  const htmlElement = document.documentElement;

  // Check if theme is stored in localStorage
  const darkMode = localStorage.getItem('dark-mode') === 'true';

  if (darkMode) {
    htmlElement.classList.add('dark');
    updateThemeToggleIcon(true);
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      htmlElement.classList.toggle('dark');

      const isDarkMode = htmlElement.classList.contains('dark');
      localStorage.setItem('dark-mode', isDarkMode);

      updateThemeToggleIcon(isDarkMode);
    });
  }
}

/**
 * Update theme toggle icon based on theme state
 * @param {boolean} isDarkMode - Whether dark mode is enabled
 */
function updateThemeToggleIcon(isDarkMode) {
  const themeToggle = document.getElementById('theme-toggle');

  if (themeToggle) {
    const icon = themeToggle.querySelector('i');

    if (icon) {
      if (isDarkMode) {
        icon.classList.remove('ri-moon-line');
        icon.classList.add('ri-sun-line');
      } else {
        icon.classList.remove('ri-sun-line');
        icon.classList.add('ri-moon-line');
      }
    }
  }
}

/**
 * Initialize dropdown functionality
 */
function initDropdowns() {
  const userDropdown = document.querySelector('.user-dropdown');

  if (userDropdown) {
    const toggle = userDropdown.querySelector('.user-dropdown-toggle');

    if (toggle) {
      // Create dropdown menu if it doesn't exist
      if (!userDropdown.querySelector('.user-dropdown-menu')) {
        const menu = document.createElement('div');
        menu.className = 'user-dropdown-menu';
        menu.style.position = 'absolute';
        menu.style.top = '100%';
        menu.style.right = '0';
        menu.style.marginTop = '0.5rem';
        menu.style.width = '200px';
        menu.style.backgroundColor = 'var(--bg-primary)';
        menu.style.borderRadius = 'var(--radius-lg)';
        menu.style.boxShadow = 'var(--shadow-lg)';
        menu.style.overflow = 'hidden';
        menu.style.zIndex = 'var(--z-30)';
        menu.style.display = 'none';

        // Add dropdown items
        menu.innerHTML = `
          <a href="#profile" class="user-dropdown-item">
            <i class="ri-user-line"></i>
            <span>${document.documentElement.lang === 'ar' ? 'الملف الشخصي' : 'Profile'}</span>
          </a>
          <a href="#settings" class="user-dropdown-item">
            <i class="ri-settings-3-line"></i>
            <span>${document.documentElement.lang === 'ar' ? 'الإعدادات' : 'Settings'}</span>
          </a>
          <div class="user-dropdown-divider"></div>
          <a href="/auth/logout" class="user-dropdown-item text-error">
            <i class="ri-logout-box-line"></i>
            <span>${document.documentElement.lang === 'ar' ? 'تسجيل الخروج' : 'Logout'}</span>
          </a>
        `;

        // Style dropdown items
        const items = menu.querySelectorAll('.user-dropdown-item');
        items.forEach(item => {
          item.style.display = 'flex';
          item.style.alignItems = 'center';
          item.style.padding = '0.75rem 1rem';
          item.style.color = 'var(--text-primary)';
          item.style.textDecoration = 'none';
          item.style.transition = 'background-color var(--transition-fast) ease-in-out';

          item.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'var(--bg-tertiary)';
          });

          item.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
          });

          const icon = item.querySelector('i');
          if (icon) {
            icon.style.marginRight = '0.75rem';

            if (document.documentElement.dir === 'rtl') {
              icon.style.marginRight = '0';
              icon.style.marginLeft = '0.75rem';
            }
          }
        });

        // Style dropdown divider
        const divider = menu.querySelector('.user-dropdown-divider');
        if (divider) {
          divider.style.height = '1px';
          divider.style.backgroundColor = 'var(--border-color)';
          divider.style.margin = '0.5rem 0';
        }

        userDropdown.appendChild(menu);
      }

      const menu = userDropdown.querySelector('.user-dropdown-menu');

      toggle.addEventListener('click', function(e) {
        e.stopPropagation();
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', function() {
        if (menu) {
          menu.style.display = 'none';
        }
      });
    }
  }
}

/**
 * Initialize responsive behavior
 */
function initResponsiveBehavior() {
  const appContainer = document.querySelector('.app-container');
  const sidebar = document.querySelector('.sidebar');

  // Handle mobile sidebar
  function handleMobileView() {
    if (window.innerWidth < 768) {
      appContainer.classList.remove('sidebar-collapsed');
      appContainer.classList.add('sidebar-mobile');

      // Create mobile overlay if it doesn't exist
      if (!document.querySelector('.sidebar-overlay')) {
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.right = '0';
        overlay.style.bottom = '0';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.zIndex = 'var(--z-20)';
        overlay.style.display = 'none';

        overlay.addEventListener('click', function() {
          appContainer.classList.remove('sidebar-open');
          overlay.style.display = 'none';
        });

        document.body.appendChild(overlay);
      }

      // Create mobile toggle if it doesn't exist
      if (!document.querySelector('.mobile-sidebar-toggle')) {
        const mobileToggle = document.createElement('button');
        mobileToggle.className = 'mobile-sidebar-toggle';
        mobileToggle.style.position = 'fixed';
        mobileToggle.style.bottom = '1rem';
        mobileToggle.style.right = '1rem';
        mobileToggle.style.width = '3rem';
        mobileToggle.style.height = '3rem';
        mobileToggle.style.borderRadius = '50%';
        mobileToggle.style.backgroundColor = 'var(--primary-600)';
        mobileToggle.style.color = 'white';
        mobileToggle.style.display = 'flex';
        mobileToggle.style.alignItems = 'center';
        mobileToggle.style.justifyContent = 'center';
        mobileToggle.style.boxShadow = 'var(--shadow-lg)';
        mobileToggle.style.zIndex = 'var(--z-30)';
        mobileToggle.style.border = 'none';
        mobileToggle.style.cursor = 'pointer';

        mobileToggle.innerHTML = '<i class="ri-menu-line" style="font-size: 1.5rem;"></i>';

        mobileToggle.addEventListener('click', function() {
          appContainer.classList.toggle('sidebar-open');
          const overlay = document.querySelector('.sidebar-overlay');
          if (overlay) {
            overlay.style.display = appContainer.classList.contains('sidebar-open') ? 'block' : 'none';
          }
        });

        document.body.appendChild(mobileToggle);
      }
    } else {
      appContainer.classList.remove('sidebar-mobile');

      // Hide mobile elements
      const overlay = document.querySelector('.sidebar-overlay');
      if (overlay) {
        overlay.style.display = 'none';
      }

      const mobileToggle = document.querySelector('.mobile-sidebar-toggle');
      if (mobileToggle) {
        mobileToggle.style.display = 'none';
      }
    }
  }

  // Initial check
  handleMobileView();

  // Listen for window resize
  window.addEventListener('resize', handleMobileView);
}
