/**
 * StockMaster Pro - Theme Customizer
 * A theme customization panel for personalized user experience
 */

class ThemeCustomizer {
  constructor() {
    this.settings = {
      theme: 'light',
      primaryColor: '#6366F1',
      fontSize: 16,
      layout: 'sidebar',
      rtl: document.documentElement.dir === 'rtl',
      reducedMotion: false,
      highContrast: false,
      glassmorphism: true,
      borderRadius: 'medium',
      compactMode: false
    };

    this.colors = {
      indigo: '#6366F1',
      blue: '#3B82F6',
      purple: '#8B5CF6',
      pink: '#EC4899',
      red: '#EF4444',
      orange: '#F59E0B',
      green: '#10B981',
      teal: '#14B8A6',
      cyan: '#06B6D4'
    };

    this.borderRadii = {
      none: {
        '--border-radius-sm': '0',
        '--border-radius': '0',
        '--border-radius-md': '0',
        '--border-radius-lg': '0',
        '--border-radius-xl': '0',
        '--border-radius-2xl': '0',
        '--border-radius-3xl': '0',
        '--border-radius-full': '9999px'
      },
      small: {
        '--border-radius-sm': '0.125rem',
        '--border-radius': '0.25rem',
        '--border-radius-md': '0.375rem',
        '--border-radius-lg': '0.5rem',
        '--border-radius-xl': '0.75rem',
        '--border-radius-2xl': '1rem',
        '--border-radius-3xl': '1.5rem',
        '--border-radius-full': '9999px'
      },
      medium: {
        '--border-radius-sm': '0.25rem',
        '--border-radius': '0.375rem',
        '--border-radius-md': '0.5rem',
        '--border-radius-lg': '0.75rem',
        '--border-radius-xl': '1rem',
        '--border-radius-2xl': '1.5rem',
        '--border-radius-3xl': '2rem',
        '--border-radius-full': '9999px'
      },
      large: {
        '--border-radius-sm': '0.375rem',
        '--border-radius': '0.5rem',
        '--border-radius-md': '0.75rem',
        '--border-radius-lg': '1rem',
        '--border-radius-xl': '1.5rem',
        '--border-radius-2xl': '2rem',
        '--border-radius-3xl': '3rem',
        '--border-radius-full': '9999px'
      }
    };

    this.fontSizes = {
      small: {
        '--font-size-xs': '0.625rem',
        '--font-size-sm': '0.75rem',
        '--font-size-base': '0.875rem',
        '--font-size-lg': '1rem',
        '--font-size-xl': '1.125rem',
        '--font-size-2xl': '1.25rem',
        '--font-size-3xl': '1.5rem',
        '--font-size-4xl': '1.875rem'
      },
      medium: {
        '--font-size-xs': '0.75rem',
        '--font-size-sm': '0.875rem',
        '--font-size-base': '1rem',
        '--font-size-lg': '1.125rem',
        '--font-size-xl': '1.25rem',
        '--font-size-2xl': '1.5rem',
        '--font-size-3xl': '1.875rem',
        '--font-size-4xl': '2.25rem'
      },
      large: {
        '--font-size-xs': '0.875rem',
        '--font-size-sm': '1rem',
        '--font-size-base': '1.125rem',
        '--font-size-lg': '1.25rem',
        '--font-size-xl': '1.5rem',
        '--font-size-2xl': '1.75rem',
        '--font-size-3xl': '2rem',
        '--font-size-4xl': '2.5rem'
      }
    };

    this.panel = null;
    this.isInitialized = false;

    // Bind methods
    this.init = this.init.bind(this);
    this.createPanel = this.createPanel.bind(this);
    this.togglePanel = this.togglePanel.bind(this);
    this.loadSettings = this.loadSettings.bind(this);
    this.saveSettings = this.saveSettings.bind(this);
    this.resetSettings = this.resetSettings.bind(this);
    this.applySettings = this.applySettings.bind(this);
    this.updateTheme = this.updateTheme.bind(this);
    this.updatePrimaryColor = this.updatePrimaryColor.bind(this);
    this.updateFontSize = this.updateFontSize.bind(this);
    this.updateLayout = this.updateLayout.bind(this);
    this.updateDirection = this.updateDirection.bind(this);
    this.updateReducedMotion = this.updateReducedMotion.bind(this);
    this.updateHighContrast = this.updateHighContrast.bind(this);
    this.updateGlassmorphism = this.updateGlassmorphism.bind(this);
    this.updateBorderRadius = this.updateBorderRadius.bind(this);
    this.updateCompactMode = this.updateCompactMode.bind(this);
    this.generateColorShades = this.generateColorShades.bind(this);
  }

  /**
   * Initialize the theme customizer
   */
  init() {
    if (this.isInitialized) return;

    // Load settings from local storage
    this.loadSettings();

    // Create customizer panel
    this.createPanel();

    // Apply current settings
    this.applySettings();

    this.isInitialized = true;
  }

  /**
   * Create the customizer panel
   */
  createPanel() {
    // Create panel element
    const panel = document.createElement('div');
    panel.className = 'customizer-panel';
    panel.innerHTML = this.createPanelContent();
    document.body.appendChild(panel);
    this.panel = panel;

    // Add toggle button
    const toggleButton = panel.querySelector('.customizer-toggle');
    toggleButton.addEventListener('click', this.togglePanel);

    // Add reset button
    const resetButton = panel.querySelector('.customizer-reset');
    resetButton.addEventListener('click', this.resetSettings);

    // Add theme toggle
    const themeToggle = panel.querySelector('#theme-toggle');
    themeToggle.checked = this.settings.theme === 'dark';
    themeToggle.addEventListener('change', (e) => {
      this.updateTheme(e.target.checked ? 'dark' : 'light');
    });

    // Add color options
    const colorOptions = panel.querySelectorAll('.color-option');
    colorOptions.forEach(option => {
      option.addEventListener('click', () => {
        this.updatePrimaryColor(option.dataset.color);
        
        // Update active state
        colorOptions.forEach(opt => opt.classList.remove('active'));
        option.classList.add('active');
      });
      
      // Set initial active state
      if (option.dataset.color === this.settings.primaryColor) {
        option.classList.add('active');
      }
    });

    // Add font size slider
    const fontSizeSlider = panel.querySelector('#font-size-slider');
    const fontSizeValue = panel.querySelector('#font-size-value');
    fontSizeSlider.value = this.settings.fontSize;
    fontSizeValue.textContent = `${this.settings.fontSize}px`;
    
    fontSizeSlider.addEventListener('input', (e) => {
      const value = parseInt(e.target.value);
      fontSizeValue.textContent = `${value}px`;
      this.updateFontSize(value);
    });

    // Add layout options
    const layoutOptions = panel.querySelectorAll('.layout-option');
    layoutOptions.forEach(option => {
      option.addEventListener('click', () => {
        this.updateLayout(option.dataset.layout);
        
        // Update active state
        layoutOptions.forEach(opt => opt.classList.remove('active'));
        option.classList.add('active');
      });
      
      // Set initial active state
      if (option.dataset.layout === this.settings.layout) {
        option.classList.add('active');
      }
    });

    // Add RTL toggle
    const rtlToggle = panel.querySelector('#rtl-toggle');
    rtlToggle.checked = this.settings.rtl;
    rtlToggle.addEventListener('change', (e) => {
      this.updateDirection(e.target.checked);
    });

    // Add reduced motion toggle
    const reducedMotionToggle = panel.querySelector('#reduced-motion-toggle');
    reducedMotionToggle.checked = this.settings.reducedMotion;
    reducedMotionToggle.addEventListener('change', (e) => {
      this.updateReducedMotion(e.target.checked);
    });

    // Add high contrast toggle
    const highContrastToggle = panel.querySelector('#high-contrast-toggle');
    highContrastToggle.checked = this.settings.highContrast;
    highContrastToggle.addEventListener('change', (e) => {
      this.updateHighContrast(e.target.checked);
    });

    // Add glassmorphism toggle
    const glassmorphismToggle = panel.querySelector('#glassmorphism-toggle');
    glassmorphismToggle.checked = this.settings.glassmorphism;
    glassmorphismToggle.addEventListener('change', (e) => {
      this.updateGlassmorphism(e.target.checked);
    });

    // Add border radius options
    const borderRadiusSelect = panel.querySelector('#border-radius-select');
    borderRadiusSelect.value = this.settings.borderRadius;
    borderRadiusSelect.addEventListener('change', (e) => {
      this.updateBorderRadius(e.target.value);
    });

    // Add compact mode toggle
    const compactModeToggle = panel.querySelector('#compact-mode-toggle');
    compactModeToggle.checked = this.settings.compactMode;
    compactModeToggle.addEventListener('change', (e) => {
      this.updateCompactMode(e.target.checked);
    });
  }

  /**
   * Create the panel content
   * @returns {string} - Panel HTML content
   */
  createPanelContent() {
    return `
      <button class="customizer-toggle" aria-label="Toggle customizer">
        <i class="ri-settings-4-line"></i>
      </button>
      <div class="customizer-header">
        <h2 class="customizer-title">Theme Customizer</h2>
        <button class="customizer-reset">
          <i class="ri-refresh-line"></i>
          <span>Reset</span>
        </button>
      </div>
      <div class="customizer-body">
        <!-- Theme Section -->
        <div class="customizer-section">
          <h3 class="customizer-section-title">
            <i class="ri-contrast-2-line"></i>
            Theme
          </h3>
          <div class="toggle-switch">
            <span class="toggle-switch-label">Dark Mode</span>
            <label class="toggle-switch-control">
              <input type="checkbox" class="toggle-switch-input" id="theme-toggle">
              <span class="toggle-switch-slider"></span>
            </label>
          </div>
        </div>

        <!-- Colors Section -->
        <div class="customizer-section">
          <h3 class="customizer-section-title">
            <i class="ri-palette-line"></i>
            Primary Color
          </h3>
          <div class="color-options">
            <div class="color-option" data-color="${this.colors.indigo}" style="background-color: ${this.colors.indigo};"></div>
            <div class="color-option" data-color="${this.colors.blue}" style="background-color: ${this.colors.blue};"></div>
            <div class="color-option" data-color="${this.colors.purple}" style="background-color: ${this.colors.purple};"></div>
            <div class="color-option" data-color="${this.colors.pink}" style="background-color: ${this.colors.pink};"></div>
            <div class="color-option" data-color="${this.colors.red}" style="background-color: ${this.colors.red};"></div>
            <div class="color-option" data-color="${this.colors.orange}" style="background-color: ${this.colors.orange};"></div>
            <div class="color-option" data-color="${this.colors.green}" style="background-color: ${this.colors.green};"></div>
            <div class="color-option" data-color="${this.colors.teal}" style="background-color: ${this.colors.teal};"></div>
            <div class="color-option" data-color="${this.colors.cyan}" style="background-color: ${this.colors.cyan};"></div>
          </div>
        </div>

        <!-- Font Size Section -->
        <div class="customizer-section">
          <h3 class="customizer-section-title">
            <i class="ri-font-size-2"></i>
            Font Size
          </h3>
          <div class="font-size-control">
            <span class="font-size-label">Base Size</span>
            <input type="range" min="12" max="20" step="1" class="font-size-slider" id="font-size-slider">
            <span class="font-size-value" id="font-size-value">16px</span>
          </div>
        </div>

        <!-- Layout Section -->
        <div class="customizer-section">
          <h3 class="customizer-section-title">
            <i class="ri-layout-2-line"></i>
            Layout
          </h3>
          <div class="layout-options">
            <div class="layout-option" data-layout="sidebar">
              <div class="layout-option-preview">
                <div class="layout-option-preview-sidebar"></div>
                <div class="layout-option-preview-content" style="left: 30%; width: 70%;">
                  <div class="layout-option-preview-card"></div>
                  <div class="layout-option-preview-card"></div>
                </div>
              </div>
              <div class="layout-option-label">Sidebar</div>
            </div>
            <div class="layout-option" data-layout="topbar">
              <div class="layout-option-preview">
                <div class="layout-option-preview-header"></div>
                <div class="layout-option-preview-content">
                  <div class="layout-option-preview-card"></div>
                  <div class="layout-option-preview-card"></div>
                </div>
              </div>
              <div class="layout-option-label">Topbar</div>
            </div>
          </div>
        </div>

        <!-- Accessibility Section -->
        <div class="customizer-section">
          <h3 class="customizer-section-title">
            <i class="ri-eye-line"></i>
            Accessibility
          </h3>
          <div class="toggle-switch">
            <span class="toggle-switch-label">RTL Layout</span>
            <label class="toggle-switch-control">
              <input type="checkbox" class="toggle-switch-input" id="rtl-toggle">
              <span class="toggle-switch-slider"></span>
            </label>
          </div>
          <div class="toggle-switch">
            <span class="toggle-switch-label">Reduced Motion</span>
            <label class="toggle-switch-control">
              <input type="checkbox" class="toggle-switch-input" id="reduced-motion-toggle">
              <span class="toggle-switch-slider"></span>
            </label>
          </div>
          <div class="toggle-switch">
            <span class="toggle-switch-label">High Contrast</span>
            <label class="toggle-switch-control">
              <input type="checkbox" class="toggle-switch-input" id="high-contrast-toggle">
              <span class="toggle-switch-slider"></span>
            </label>
          </div>
        </div>

        <!-- UI Effects Section -->
        <div class="customizer-section">
          <h3 class="customizer-section-title">
            <i class="ri-bubble-chart-line"></i>
            UI Effects
          </h3>
          <div class="toggle-switch">
            <span class="toggle-switch-label">Glassmorphism</span>
            <label class="toggle-switch-control">
              <input type="checkbox" class="toggle-switch-input" id="glassmorphism-toggle">
              <span class="toggle-switch-slider"></span>
            </label>
          </div>
          <div class="form-group mb-4">
            <label for="border-radius-select" class="form-label">Border Radius</label>
            <select id="border-radius-select" class="form-select">
              <option value="none">None</option>
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div>
          <div class="toggle-switch">
            <span class="toggle-switch-label">Compact Mode</span>
            <label class="toggle-switch-control">
              <input type="checkbox" class="toggle-switch-input" id="compact-mode-toggle">
              <span class="toggle-switch-slider"></span>
            </label>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Toggle the customizer panel
   */
  togglePanel() {
    if (!this.panel) return;
    this.panel.classList.toggle('open');
  }

  /**
   * Load settings from local storage
   */
  loadSettings() {
    const savedSettings = localStorage.getItem('stockmaster-theme-settings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        this.settings = { ...this.settings, ...parsedSettings };
      } catch (error) {
        console.error('Error loading theme settings:', error);
      }
    }
  }

  /**
   * Save settings to local storage
   */
  saveSettings() {
    try {
      localStorage.setItem('stockmaster-theme-settings', JSON.stringify(this.settings));
    } catch (error) {
      console.error('Error saving theme settings:', error);
    }
  }

  /**
   * Reset settings to defaults
   */
  resetSettings() {
    this.settings = {
      theme: 'light',
      primaryColor: '#6366F1',
      fontSize: 16,
      layout: 'sidebar',
      rtl: document.documentElement.dir === 'rtl',
      reducedMotion: false,
      highContrast: false,
      glassmorphism: true,
      borderRadius: 'medium',
      compactMode: false
    };

    this.applySettings();
    this.saveSettings();

    // Update UI
    if (this.panel) {
      // Theme toggle
      const themeToggle = this.panel.querySelector('#theme-toggle');
      themeToggle.checked = this.settings.theme === 'dark';

      // Color options
      const colorOptions = this.panel.querySelectorAll('.color-option');
      colorOptions.forEach(option => {
        option.classList.remove('active');
        if (option.dataset.color === this.settings.primaryColor) {
          option.classList.add('active');
        }
      });

      // Font size slider
      const fontSizeSlider = this.panel.querySelector('#font-size-slider');
      const fontSizeValue = this.panel.querySelector('#font-size-value');
      fontSizeSlider.value = this.settings.fontSize;
      fontSizeValue.textContent = `${this.settings.fontSize}px`;

      // Layout options
      const layoutOptions = this.panel.querySelectorAll('.layout-option');
      layoutOptions.forEach(option => {
        option.classList.remove('active');
        if (option.dataset.layout === this.settings.layout) {
          option.classList.add('active');
        }
      });

      // RTL toggle
      const rtlToggle = this.panel.querySelector('#rtl-toggle');
      rtlToggle.checked = this.settings.rtl;

      // Reduced motion toggle
      const reducedMotionToggle = this.panel.querySelector('#reduced-motion-toggle');
      reducedMotionToggle.checked = this.settings.reducedMotion;

      // High contrast toggle
      const highContrastToggle = this.panel.querySelector('#high-contrast-toggle');
      highContrastToggle.checked = this.settings.highContrast;

      // Glassmorphism toggle
      const glassmorphismToggle = this.panel.querySelector('#glassmorphism-toggle');
      glassmorphismToggle.checked = this.settings.glassmorphism;

      // Border radius select
      const borderRadiusSelect = this.panel.querySelector('#border-radius-select');
      borderRadiusSelect.value = this.settings.borderRadius;

      // Compact mode toggle
      const compactModeToggle = this.panel.querySelector('#compact-mode-toggle');
      compactModeToggle.checked = this.settings.compactMode;
    }

    // Show toast notification
    if (window.toast) {
      window.toast.success({
        title: 'Settings Reset',
        message: 'Theme settings have been reset to defaults.',
        duration: 3000
      });
    }
  }

  /**
   * Apply current settings
   */
  applySettings() {
    // Apply theme
    this.updateTheme(this.settings.theme, false);

    // Apply primary color
    this.updatePrimaryColor(this.settings.primaryColor, false);

    // Apply font size
    this.updateFontSize(this.settings.fontSize, false);

    // Apply layout
    this.updateLayout(this.settings.layout, false);

    // Apply direction
    this.updateDirection(this.settings.rtl, false);

    // Apply reduced motion
    this.updateReducedMotion(this.settings.reducedMotion, false);

    // Apply high contrast
    this.updateHighContrast(this.settings.highContrast, false);

    // Apply glassmorphism
    this.updateGlassmorphism(this.settings.glassmorphism, false);

    // Apply border radius
    this.updateBorderRadius(this.settings.borderRadius, false);

    // Apply compact mode
    this.updateCompactMode(this.settings.compactMode, false);
  }

  /**
   * Update theme
   * @param {string} theme - Theme name (light or dark)
   * @param {boolean} save - Whether to save settings
   */
  updateTheme(theme, save = true) {
    this.settings.theme = theme;

    // Update HTML class
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    document.documentElement.classList.add(`theme-${theme}`);

    // Dispatch theme change event
    document.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update primary color
   * @param {string} color - Primary color hex code
   * @param {boolean} save - Whether to save settings
   */
  updatePrimaryColor(color, save = true) {
    this.settings.primaryColor = color;

    // Generate color shades
    const shades = this.generateColorShades(color);

    // Apply color variables
    Object.entries(shades).forEach(([shade, value]) => {
      document.documentElement.style.setProperty(`--primary-${shade}`, value);
    });

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update font size
   * @param {number} size - Base font size in pixels
   * @param {boolean} save - Whether to save settings
   */
  updateFontSize(size, save = true) {
    this.settings.fontSize = size;

    // Set base font size
    document.documentElement.style.fontSize = `${size}px`;

    // Apply font size variables based on size category
    let fontSizeCategory = 'medium';
    if (size <= 14) {
      fontSizeCategory = 'small';
    } else if (size >= 18) {
      fontSizeCategory = 'large';
    }

    Object.entries(this.fontSizes[fontSizeCategory]).forEach(([variable, value]) => {
      document.documentElement.style.setProperty(variable, value);
    });

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update layout
   * @param {string} layout - Layout name (sidebar or topbar)
   * @param {boolean} save - Whether to save settings
   */
  updateLayout(layout, save = true) {
    this.settings.layout = layout;

    // Update body class
    document.body.classList.remove('layout-sidebar', 'layout-topbar');
    document.body.classList.add(`layout-${layout}`);

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update direction
   * @param {boolean} rtl - Whether to use RTL direction
   * @param {boolean} save - Whether to save settings
   */
  updateDirection(rtl, save = true) {
    this.settings.rtl = rtl;

    // Update HTML dir attribute
    document.documentElement.dir = rtl ? 'rtl' : 'ltr';

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update reduced motion
   * @param {boolean} reducedMotion - Whether to use reduced motion
   * @param {boolean} save - Whether to save settings
   */
  updateReducedMotion(reducedMotion, save = true) {
    this.settings.reducedMotion = reducedMotion;

    // Update body class
    document.body.classList.toggle('reduced-motion', reducedMotion);

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update high contrast
   * @param {boolean} highContrast - Whether to use high contrast
   * @param {boolean} save - Whether to save settings
   */
  updateHighContrast(highContrast, save = true) {
    this.settings.highContrast = highContrast;

    // Update body class
    document.body.classList.toggle('high-contrast', highContrast);

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update glassmorphism
   * @param {boolean} glassmorphism - Whether to use glassmorphism
   * @param {boolean} save - Whether to save settings
   */
  updateGlassmorphism(glassmorphism, save = true) {
    this.settings.glassmorphism = glassmorphism;

    // Update body class
    document.body.classList.toggle('no-glassmorphism', !glassmorphism);

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update border radius
   * @param {string} borderRadius - Border radius size (none, small, medium, large)
   * @param {boolean} save - Whether to save settings
   */
  updateBorderRadius(borderRadius, save = true) {
    this.settings.borderRadius = borderRadius;

    // Apply border radius variables
    Object.entries(this.borderRadii[borderRadius]).forEach(([variable, value]) => {
      document.documentElement.style.setProperty(variable, value);
    });

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Update compact mode
   * @param {boolean} compactMode - Whether to use compact mode
   * @param {boolean} save - Whether to save settings
   */
  updateCompactMode(compactMode, save = true) {
    this.settings.compactMode = compactMode;

    // Update body class
    document.body.classList.toggle('compact-mode', compactMode);

    if (save) {
      this.saveSettings();
    }
  }

  /**
   * Generate color shades from a base color
   * @param {string} baseColor - Base color hex code
   * @returns {Object} - Color shades object
   */
  generateColorShades(baseColor) {
    // Convert hex to RGB
    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null;
    };

    // Convert RGB to hex
    const rgbToHex = (r, g, b) => {
      return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    };

    // Lighten or darken color
    const adjustColor = (color, amount) => {
      const { r, g, b } = hexToRgb(color);
      return rgbToHex(
        Math.max(0, Math.min(255, Math.round(r + amount))),
        Math.max(0, Math.min(255, Math.round(g + amount))),
        Math.max(0, Math.min(255, Math.round(b + amount)))
      );
    };

    // Generate shades
    return {
      '50': adjustColor(baseColor, 150),
      '100': adjustColor(baseColor, 120),
      '200': adjustColor(baseColor, 90),
      '300': adjustColor(baseColor, 60),
      '400': adjustColor(baseColor, 30),
      '500': baseColor,
      '600': adjustColor(baseColor, -30),
      '700': adjustColor(baseColor, -60),
      '800': adjustColor(baseColor, -90),
      '900': adjustColor(baseColor, -120)
    };
  }
}

// Create global customizer instance
window.themeCustomizer = new ThemeCustomizer();

// Initialize customizer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.themeCustomizer.init();
});
