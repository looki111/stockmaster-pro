/**
 * StockMaster Pro - Theme Manager
 * Handles theme switching (light/dark) and remembers user preferences
 */

(function() {
  'use strict';

  // Theme constants
  const THEME_STORAGE_KEY = 'stockmaster-theme';
  const THEME_LIGHT = 'theme-light';
  const THEME_DARK = 'theme-dark';
  
  // DOM elements
  let themeToggleBtn;
  
  /**
   * Initialize the theme manager
   */
  function init() {
    // Get theme toggle button
    themeToggleBtn = document.getElementById('theme-toggle');
    
    // Apply saved theme or use system preference
    applyTheme(getSavedTheme() || getSystemTheme());
    
    // Set up event listeners
    setupEventListeners();
    
    // Watch for system theme changes
    watchSystemThemeChanges();
  }
  
  /**
   * Set up event listeners
   */
  function setupEventListeners() {
    // Theme toggle button click
    if (themeToggleBtn) {
      themeToggleBtn.addEventListener('click', toggleTheme);
    }
  }
  
  /**
   * Toggle between light and dark themes
   */
  function toggleTheme() {
    const currentTheme = document.documentElement.classList.contains(THEME_DARK) ? THEME_DARK : THEME_LIGHT;
    const newTheme = currentTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
    
    applyTheme(newTheme);
    saveTheme(newTheme);
    updateThemeToggleIcon(newTheme);
  }
  
  /**
   * Apply the specified theme
   * @param {string} theme - The theme to apply (THEME_LIGHT or THEME_DARK)
   */
  function applyTheme(theme) {
    // Remove both theme classes
    document.documentElement.classList.remove(THEME_LIGHT, THEME_DARK);
    
    // Add the new theme class
    document.documentElement.classList.add(theme);
    
    // Update the theme toggle icon
    updateThemeToggleIcon(theme);
    
    // Update meta theme-color for mobile browsers
    updateMetaThemeColor(theme);
  }
  
  /**
   * Update the theme toggle icon based on the current theme
   * @param {string} theme - The current theme
   */
  function updateThemeToggleIcon(theme) {
    if (!themeToggleBtn) return;
    
    const iconElement = themeToggleBtn.querySelector('i') || themeToggleBtn;
    
    if (theme === THEME_DARK) {
      // In dark mode, show sun icon
      iconElement.className = iconElement.className.replace('ri-moon-line', 'ri-sun-line');
    } else {
      // In light mode, show moon icon
      iconElement.className = iconElement.className.replace('ri-sun-line', 'ri-moon-line');
    }
  }
  
  /**
   * Update the meta theme-color for mobile browsers
   * @param {string} theme - The current theme
   */
  function updateMetaThemeColor(theme) {
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) return;
    
    if (theme === THEME_DARK) {
      metaThemeColor.setAttribute('content', '#1f2937'); // Neutral-800
    } else {
      metaThemeColor.setAttribute('content', '#ffffff'); // White
    }
  }
  
  /**
   * Get the saved theme from localStorage
   * @returns {string|null} The saved theme or null if none is saved
   */
  function getSavedTheme() {
    return localStorage.getItem(THEME_STORAGE_KEY);
  }
  
  /**
   * Save the theme to localStorage
   * @param {string} theme - The theme to save
   */
  function saveTheme(theme) {
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }
  
  /**
   * Get the system theme preference
   * @returns {string} The system theme (THEME_LIGHT or THEME_DARK)
   */
  function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? THEME_DARK : THEME_LIGHT;
  }
  
  /**
   * Watch for system theme changes
   */
  function watchSystemThemeChanges() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', (e) => {
        // Only apply system theme if user hasn't set a preference
        if (!getSavedTheme()) {
          applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
        }
      });
    }
    // Older browsers
    else if (mediaQuery.addListener) {
      mediaQuery.addListener((e) => {
        // Only apply system theme if user hasn't set a preference
        if (!getSavedTheme()) {
          applyTheme(e.matches ? THEME_DARK : THEME_LIGHT);
        }
      });
    }
  }
  
  // Initialize when the DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
