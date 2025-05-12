/**
 * StockMaster Pro Theme Manager
 * Handles theme switching, persistence, and custom user theme colors
 */

class ThemeManager {
  constructor() {
    this.currentTheme = localStorage.getItem('theme') || 'light';
    this.userThemeColor = localStorage.getItem('userThemeColor');
    this.initialize();
  }

  initialize() {
    // Apply saved theme on initial load
    this.applyTheme(this.currentTheme);
    
    // Apply custom color if exists
    if (this.userThemeColor) {
      this.applyUserThemeColor(this.userThemeColor);
    }
    
    // Set up event listeners for theme toggle when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
      const themeToggle = document.getElementById('themeToggle');
      if (themeToggle) {
        themeToggle.addEventListener('click', () => {
          this.toggleTheme();
        });
      }
    });

    // Handle theme changes from other tabs/windows
    window.addEventListener('storage', (event) => {
      if (event.key === 'theme') {
        this.applyTheme(event.newValue || 'light', false);
      } else if (event.key === 'userThemeColor' && event.newValue) {
        this.applyUserThemeColor(event.newValue, false);
      }
    });
  }

  applyTheme(theme, saveToStorage = true) {
    // Remove existing theme classes
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    
    // Add new theme class to html element (better for CSS variable scope)
    document.documentElement.classList.add(`theme-${theme}`);
    
    // Store in localStorage if needed
    if (saveToStorage) {
      localStorage.setItem('theme', theme);
    }
    
    // Update current theme
    this.currentTheme = theme;
    
    // Update theme toggle button appearance
    this.updateToggleButton();
    
    // Dispatch custom event for other components
    document.dispatchEvent(new CustomEvent('themeChanged', { 
      detail: { theme: theme } 
    }));

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', 
        theme === 'light' ? '#ffffff' : '#1a1a2e');
    }
  }

  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    // Try to save to server if authenticated
    this.saveUserPreference('theme', newTheme);
  }
  
  updateToggleButton() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.updateToggleButton());
      return;
    }

    const toggle = document.getElementById('themeToggle');
    if (toggle) {
      const iconElement = toggle.querySelector('i') || document.createElement('i');
      
      // Remove any existing icon classes
      iconElement.className = '';
      
      // Add appropriate icon class
      iconElement.classList.add('ri-' + (this.currentTheme === 'light' ? 'moon' : 'sun') + '-line');
      
      // Update aria-label for accessibility
      toggle.setAttribute('aria-label', 
        this.currentTheme === 'light' ? 'تبديل للوضع الداكن' : 'تبديل للوضع الفاتح');
      
      // Ensure icon is in the button
      if (!iconElement.parentNode) {
        toggle.innerHTML = '';
        toggle.appendChild(iconElement);
      }
    }
  }

  applyUserThemeColor(color, saveToStorage = true) {
    // Create style element for custom properties
    let style = document.getElementById('userThemeStyle') || document.createElement('style');
    if (!style.id) style.id = 'userThemeStyle';
    
    // Apply the custom color with different intensities for both themes
    style.innerHTML = `
      :root {
        --user-theme-color: ${color};
        --user-theme-light: ${this.lightenColor(color, 20)};
        --user-theme-dark: ${this.darkenColor(color, 20)};
      }
      .theme-dark {
        --user-theme-color: ${this.lightenColor(color, 10)};
        --user-theme-light: ${this.lightenColor(color, 30)};
        --user-theme-dark: ${color};
      }
    `;
    
    // Add style to document head if not already there
    if (!style.parentNode) document.head.appendChild(style);
    
    // Save to localStorage
    if (saveToStorage) {
      localStorage.setItem('userThemeColor', color);
      this.userThemeColor = color;
      
      // Try to save to server if authenticated
      this.saveUserPreference('theme_color', color);
    }
  }

  // Helper functions for color manipulation
  lightenColor(color, percent) {
    return this.adjustColor(color, percent);
  }

  darkenColor(color, percent) {
    return this.adjustColor(color, -percent);
  }

  adjustColor(color, percent) {
    // Convert hex to RGB
    let r = parseInt(color.substring(1, 3), 16);
    let g = parseInt(color.substring(3, 5), 16);
    let b = parseInt(color.substring(5, 7), 16);

    // Adjust by percentage
    r = Math.max(0, Math.min(255, r + (percent / 100) * 255));
    g = Math.max(0, Math.min(255, g + (percent / 100) * 255));
    b = Math.max(0, Math.min(255, b + (percent / 100) * 255));

    // Convert back to hex
    return "#" + 
      Math.round(r).toString(16).padStart(2, '0') +
      Math.round(g).toString(16).padStart(2, '0') +
      Math.round(b).toString(16).padStart(2, '0');
  }

  // Save user preference to server (if user is authenticated)
  saveUserPreference(key, value) {
    // Skip if we're not authenticated
    if (!document.body.classList.contains('user-authenticated')) {
      return;
    }

    // Use fetch to save preference to server
    fetch('/api/user/preferences', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': this.getCsrfToken()
      },
      body: JSON.stringify({
        key: key,
        value: value
      })
    }).catch(error => {
      console.error('Error saving user preference:', error);
    });
  }

  getCsrfToken() {
    // Try to get CSRF token from meta tag
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
      return metaToken.getAttribute('content');
    }
    return '';
  }

  // Static diagnostic method to help debug theme issues
  static diagnose() {
    console.log({
      "Current theme (localStorage)": localStorage.getItem('theme'),
      "User theme color": localStorage.getItem('userThemeColor'),
      "Body classes": document.body.classList.toString(),
      "HTML classes": document.documentElement.classList.toString(),
      "--bg-primary": getComputedStyle(document.documentElement).getPropertyValue('--bg-primary'),
      "--text-primary": getComputedStyle(document.documentElement).getPropertyValue('--text-primary'),
      "--user-theme-color": getComputedStyle(document.documentElement).getPropertyValue('--user-theme-color')
    });
  }
}

// Initialize theme manager when script loads
window.themeManager = new ThemeManager();

// Export diagnose function to global scope for debugging
window.diagnoseTheme = ThemeManager.diagnose; 