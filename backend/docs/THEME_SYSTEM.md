# StockMaster Pro Theme System Documentation

## Overview

The StockMaster Pro theme system provides a comprehensive theming solution that supports:

- Light and dark mode themes
- Custom user theme colors
- Smooth transitions between themes
- RTL/LTR layout support
- Persistent preferences saved to both localStorage and database
- Mobile theme-color meta tag support

## Quick Usage Guide

### How to Toggle Theme

The theme toggle is handled automatically by the theme manager. Just make sure your HTML includes:

```html
<button id="themeToggle" aria-label="Toggle Theme">
  <i class="ri-moon-line"></i>
</button>
```

The ThemeManager will:
1. Initialize on page load
2. Apply the saved theme from localStorage
3. Attach event listeners to the theme toggle button
4. Update the toggle button's icon based on the current theme
5. Save user theme preference to the database (if authenticated)

### CSS Variables

The theme system is built around CSS variables. Use these variables in your CSS instead of hardcoded colors:

```css
.my-component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
```

## Implementation Details

### Files Structure

The theme system consists of the following files:

1. `static/js/theme-manager.js`: JavaScript class that handles theme switching and persistence
2. `static/css/theme-variables.css`: CSS variables for both light and dark themes
3. `routes/user_preferences.py`: API endpoints for saving user preferences to the database
4. `database/models.py`: UserPreference model for storing theme preferences
5. `migrations/versions/add_user_preferences.py`: Database migration for the UserPreference table

### Theme Manager API

The ThemeManager class provides the following methods:

```javascript
// Initialize the theme manager (done automatically)
window.themeManager = new ThemeManager();

// Toggle between light and dark theme
window.themeManager.toggleTheme();

// Directly apply a specific theme ('light' or 'dark')
window.themeManager.applyTheme('dark');

// Apply custom theme color
window.themeManager.applyUserThemeColor('#3498db');

// Diagnose theme issues
window.diagnoseTheme();
```

### Theme CSS Variables

The theme system defines CSS variables for both light and dark themes. A few key variables include:

| Variable | Light Theme Default | Dark Theme Default | Description |
|----------|---------------------|-------------------|-------------|
| `--bg-primary` | `#ffffff` | `#1a1a2e` | Primary background color |
| `--bg-secondary` | `#f5f7fa` | `#16213e` | Secondary background color |
| `--text-primary` | `#333333` | `#e6e6e6` | Primary text color |
| `--text-secondary` | `#6b7280` | `#b3b3b3` | Secondary text color |
| `--border-color` | `#e1e4e8` | `#2a3752` | Border color |
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | `0 1px 2px rgba(0,0,0,0.3)` | Small shadow |

See `theme-variables.css` for the complete list of variables.

## User Preferences API

### Endpoints

- **GET /api/user/preferences**: Retrieve all preferences for the current user
- **POST /api/user/preferences**: Save a preference
- **DELETE /api/user/preferences/:key**: Delete a preference

### Example: Saving a Preference

```javascript
fetch('/api/user/preferences', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
  },
  body: JSON.stringify({
    key: 'theme',
    value: 'dark'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Customizing the Theme System

### Adding Custom Color Schemes

You can extend the theme system with custom color schemes:

1. Add new CSS variables to theme-variables.css:

```css
:root {
  /* Existing variables */
  
  /* Coffee theme variables */
  --coffee-primary: #6f4e37;
  --coffee-secondary: #b9936c;
  --coffee-accent: #e6b89c;
}

.theme-dark {
  /* Existing variables */
  
  /* Coffee theme variables - darker versions */
  --coffee-primary: #5a3d2b;
  --coffee-secondary: #8c6e4a;
  --coffee-accent: #c69c7b;
}
```

2. Create a theme class that extends the base theme:

```css
.coffee-theme {
  --primary-600: var(--coffee-primary);
  --accent-color: var(--coffee-secondary);
  --highlight-color: var(--coffee-accent);
}
```

### Adding Custom Theme Types

To add a completely new theme type (beyond light/dark):

1. Extend the ThemeManager class:

```javascript
class ExtendedThemeManager extends ThemeManager {
  constructor() {
    super();
    this.themeType = localStorage.getItem('themeType') || 'default';
    this.initializeThemeType();
  }
  
  initializeThemeType() {
    document.documentElement.classList.add(`theme-type-${this.themeType}`);
    
    // Add theme type toggle handler
    document.getElementById('themeTypeToggle')?.addEventListener('click', () => {
      this.cycleThemeType();
    });
  }
  
  cycleThemeType() {
    const types = ['default', 'coffee', 'ocean'];
    let currentIndex = types.indexOf(this.themeType);
    let nextIndex = (currentIndex + 1) % types.length;
    this.setThemeType(types[nextIndex]);
  }
  
  setThemeType(type) {
    // Remove existing type classes
    document.documentElement.classList.remove(...types.map(t => `theme-type-${t}`));
    
    // Add new type class
    document.documentElement.classList.add(`theme-type-${type}`);
    
    // Save to localStorage
    localStorage.setItem('themeType', type);
    this.themeType = type;
    
    // Save to server if authenticated
    this.saveUserPreference('theme_type', type);
  }
}

// Override theme manager with extended version
window.themeManager = new ExtendedThemeManager();
```

## Troubleshooting

### Common Issues

1. **Theme not persisting after page reload:**
   - Check localStorage using the browser console:
     ```javascript
     console.log(localStorage.getItem('theme'));
     ```
   - Ensure theme toggle button has id="themeToggle"

2. **Theme toggle not working:**
   - Check console for JavaScript errors
   - Verify that theme-manager.js is loaded
   - Confirm that the theme toggle button has id="themeToggle"

3. **Theme variables not applying:**
   - Verify that theme-variables.css is loaded before your other CSS
   - Check if the CSS is using hardcoded colors instead of variables
   - Use browser inspector to see if variables are being overridden

### Diagnosing Issues

Use the built-in diagnostic function to check theme system status:

```javascript
window.diagnoseTheme();
```

This will output current theme status to the console:

```
{
  "Current theme (localStorage)": "dark",
  "User theme color": "#4f9cf9",
  "Body classes": "user-authenticated",
  "HTML classes": "theme-dark",
  "--bg-primary": "#1a1a2e",
  "--text-primary": "#e6e6e6",
  "--user-theme-color": "#4f9cf9"
}
```

### Fixing Common Issues

1. **Reset theme to default:**
   ```javascript
   localStorage.removeItem('theme');
   localStorage.removeItem('userThemeColor');
   window.location.reload();
   ```

2. **Check if theme toggle has correct ID:**
   ```javascript
   console.log(document.getElementById('themeToggle'));
   ```

3. **Manually toggle theme:**
   ```javascript
   window.themeManager.toggleTheme();
   ```

## Best Practices

1. **Always use CSS variables for styling**
   ```css
   /* Good */
   color: var(--text-primary);
   
   /* Bad */
   color: #333333;
   ```

2. **Test all components in both themes**
   - Check contrast ratios for accessibility
   - Ensure all UI elements are visible in both themes

3. **Handle transitions smoothly**
   - Use the provided transition variables:
   ```css
   transition: background-color var(--theme-transition-duration) var(--theme-transition-timing);
   ```

4. **Consider adding prefers-color-scheme media query support**
   ```javascript
   // In theme-manager.js constructor
   if (!localStorage.getItem('theme')) {
     const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
     this.currentTheme = prefersDark ? 'dark' : 'light';
   }
   ```

## Further Resources

- [CSS Variables on MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [prefers-color-scheme Media Query](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) 