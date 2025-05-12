/**
 * StockMaster Pro - Notification System
 * A comprehensive notification system for alerts, toasts, and badges
 */

class NotificationSystem {
  constructor(options = {}) {
    this.options = {
      position: options.position || 'top-right',
      duration: options.duration || 5000,
      maxToasts: options.maxToasts || 5,
      pauseOnHover: options.pauseOnHover !== undefined ? options.pauseOnHover : true,
      showCloseButton: options.showCloseButton !== undefined ? options.showCloseButton : true,
      showProgressBar: options.showProgressBar !== undefined ? options.showProgressBar : true,
      newestOnTop: options.newestOnTop !== undefined ? options.newestOnTop : true,
      escapeHTML: options.escapeHTML !== undefined ? options.escapeHTML : true,
      rtl: document.documentElement.dir === 'rtl'
    };

    this.container = null;
    this.toasts = [];
    this.toastCounter = 0;
    this.createContainer();
  }

  /**
   * Create the notification container
   */
  createContainer() {
    if (document.querySelector('.notification-container')) {
      this.container = document.querySelector('.notification-container');
      return;
    }

    this.container = document.createElement('div');
    this.container.className = `notification-container ${this.options.position}`;
    document.body.appendChild(this.container);
  }

  /**
   * Show a toast notification
   * @param {Object} options - Toast options
   * @returns {Object} - Toast instance
   */
  toast(options) {
    const toastOptions = {
      type: options.type || 'info',
      title: options.title || '',
      message: options.message || '',
      icon: options.icon || this.getDefaultIcon(options.type || 'info'),
      duration: options.duration || this.options.duration,
      onClick: options.onClick || null,
      onClose: options.onClose || null,
      glass: options.glass !== undefined ? options.glass : false,
      data: options.data || {}
    };

    // Create toast element
    const toast = document.createElement('div');
    const toastId = `toast-${this.toastCounter++}`;
    toast.id = toastId;
    toast.className = `toast toast-${toastOptions.type}${toastOptions.glass ? '-glass' : ''}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // Create toast content
    let content = `
      <div class="toast-icon">
        <i class="${toastOptions.icon}"></i>
      </div>
      <div class="toast-content">
        ${toastOptions.title ? `<div class="toast-title">${this.options.escapeHTML ? this.escapeHTML(toastOptions.title) : toastOptions.title}</div>` : ''}
        ${toastOptions.message ? `<div class="toast-message">${this.options.escapeHTML ? this.escapeHTML(toastOptions.message) : toastOptions.message}</div>` : ''}
      </div>
    `;

    // Add close button if enabled
    if (this.options.showCloseButton) {
      content += `
        <button type="button" class="toast-close" aria-label="Close">
          <i class="ri-close-line"></i>
        </button>
      `;
    }

    // Add progress bar if enabled
    if (this.options.showProgressBar) {
      content += `<div class="toast-progress" style="width: 100%;"></div>`;
    }

    toast.innerHTML = content;

    // Add event listeners
    if (toastOptions.onClick) {
      toast.addEventListener('click', (e) => {
        if (e.target.closest('.toast-close')) return;
        toastOptions.onClick(e, { id: toastId, ...toastOptions.data });
      });
    }

    if (this.options.showCloseButton) {
      const closeButton = toast.querySelector('.toast-close');
      closeButton.addEventListener('click', () => this.closeToast(toastId));
    }

    // Pause on hover if enabled
    if (this.options.pauseOnHover) {
      toast.addEventListener('mouseenter', () => this.pauseToast(toastId));
      toast.addEventListener('mouseleave', () => this.resumeToast(toastId));
    }

    // Add to container
    if (this.options.newestOnTop) {
      this.container.prepend(toast);
    } else {
      this.container.appendChild(toast);
    }

    // Manage max toasts
    this.manageToasts();

    // Store toast data
    const toastData = {
      id: toastId,
      element: toast,
      options: toastOptions,
      progress: 0,
      remaining: toastOptions.duration,
      startTime: Date.now(),
      pauseTime: null,
      timeoutId: null
    };

    this.toasts.push(toastData);

    // Start toast timer
    this.startToastTimer(toastId);

    // Return toast instance
    return {
      id: toastId,
      close: () => this.closeToast(toastId),
      update: (newOptions) => this.updateToast(toastId, newOptions)
    };
  }

  /**
   * Start the toast timer
   * @param {string} id - Toast ID
   */
  startToastTimer(id) {
    const toast = this.toasts.find(t => t.id === id);
    if (!toast) return;

    // Clear existing timeout
    if (toast.timeoutId) {
      clearTimeout(toast.timeoutId);
    }

    // Set new timeout
    toast.timeoutId = setTimeout(() => {
      this.closeToast(id);
    }, toast.remaining);

    // Start progress bar animation
    if (this.options.showProgressBar) {
      toast.startTime = Date.now();
      this.animateProgressBar(id);
    }
  }

  /**
   * Animate the progress bar
   * @param {string} id - Toast ID
   */
  animateProgressBar(id) {
    const toast = this.toasts.find(t => t.id === id);
    if (!toast || toast.pauseTime) return;

    const progressBar = toast.element.querySelector('.toast-progress');
    if (!progressBar) return;

    const elapsed = Date.now() - toast.startTime;
    const progress = Math.min(elapsed / toast.options.duration, 1);
    toast.progress = progress;

    progressBar.style.width = `${(1 - progress) * 100}%`;

    if (progress < 1) {
      requestAnimationFrame(() => this.animateProgressBar(id));
    }
  }

  /**
   * Pause a toast
   * @param {string} id - Toast ID
   */
  pauseToast(id) {
    const toast = this.toasts.find(t => t.id === id);
    if (!toast || toast.pauseTime) return;

    // Clear timeout
    clearTimeout(toast.timeoutId);
    toast.timeoutId = null;

    // Store pause time and remaining duration
    toast.pauseTime = Date.now();
    toast.remaining = toast.remaining - (toast.pauseTime - toast.startTime);
  }

  /**
   * Resume a toast
   * @param {string} id - Toast ID
   */
  resumeToast(id) {
    const toast = this.toasts.find(t => t.id === id);
    if (!toast || !toast.pauseTime) return;

    // Update start time
    toast.startTime = Date.now();
    toast.pauseTime = null;

    // Restart timer
    this.startToastTimer(id);
  }

  /**
   * Close a toast
   * @param {string} id - Toast ID
   */
  closeToast(id) {
    const toastIndex = this.toasts.findIndex(t => t.id === id);
    if (toastIndex === -1) return;

    const toast = this.toasts[toastIndex];
    
    // Clear timeout
    if (toast.timeoutId) {
      clearTimeout(toast.timeoutId);
    }

    // Add closing animation
    toast.element.classList.add('closing');

    // Remove after animation
    setTimeout(() => {
      if (toast.element.parentNode) {
        toast.element.parentNode.removeChild(toast.element);
      }
      
      // Call onClose callback if provided
      if (toast.options.onClose) {
        toast.options.onClose({ id, ...toast.options.data });
      }
      
      // Remove from toasts array
      this.toasts.splice(toastIndex, 1);
    }, 300);
  }

  /**
   * Update a toast
   * @param {string} id - Toast ID
   * @param {Object} newOptions - New toast options
   */
  updateToast(id, newOptions) {
    const toast = this.toasts.find(t => t.id === id);
    if (!toast) return;

    // Update title if provided
    if (newOptions.title !== undefined) {
      const titleEl = toast.element.querySelector('.toast-title');
      if (titleEl) {
        titleEl.innerHTML = this.options.escapeHTML ? this.escapeHTML(newOptions.title) : newOptions.title;
      } else if (newOptions.title) {
        const contentEl = toast.element.querySelector('.toast-content');
        const messageEl = toast.element.querySelector('.toast-message');
        
        const titleEl = document.createElement('div');
        titleEl.className = 'toast-title';
        titleEl.innerHTML = this.options.escapeHTML ? this.escapeHTML(newOptions.title) : newOptions.title;
        
        contentEl.insertBefore(titleEl, messageEl);
      }
    }

    // Update message if provided
    if (newOptions.message !== undefined) {
      const messageEl = toast.element.querySelector('.toast-message');
      if (messageEl) {
        messageEl.innerHTML = this.options.escapeHTML ? this.escapeHTML(newOptions.message) : newOptions.message;
      } else if (newOptions.message) {
        const contentEl = toast.element.querySelector('.toast-content');
        
        const messageEl = document.createElement('div');
        messageEl.className = 'toast-message';
        messageEl.innerHTML = this.options.escapeHTML ? this.escapeHTML(newOptions.message) : newOptions.message;
        
        contentEl.appendChild(messageEl);
      }
    }

    // Update type if provided
    if (newOptions.type !== undefined) {
      toast.element.className = `toast toast-${newOptions.type}${newOptions.glass ? '-glass' : ''}`;
      
      // Update icon if not explicitly provided
      if (newOptions.icon === undefined) {
        const iconEl = toast.element.querySelector('.toast-icon i');
        if (iconEl) {
          iconEl.className = this.getDefaultIcon(newOptions.type);
        }
      }
    }

    // Update icon if provided
    if (newOptions.icon !== undefined) {
      const iconEl = toast.element.querySelector('.toast-icon i');
      if (iconEl) {
        iconEl.className = newOptions.icon;
      }
    }

    // Update duration if provided
    if (newOptions.duration !== undefined) {
      toast.options.duration = newOptions.duration;
      toast.remaining = newOptions.duration;
      toast.startTime = Date.now();
      this.startToastTimer(id);
    }

    // Update data if provided
    if (newOptions.data !== undefined) {
      toast.options.data = { ...toast.options.data, ...newOptions.data };
    }

    // Update onClick if provided
    if (newOptions.onClick !== undefined) {
      toast.options.onClick = newOptions.onClick;
      
      // Remove existing click listener
      const newToast = toast.element.cloneNode(true);
      toast.element.parentNode.replaceChild(newToast, toast.element);
      toast.element = newToast;
      
      // Add new click listener
      if (newOptions.onClick) {
        newToast.addEventListener('click', (e) => {
          if (e.target.closest('.toast-close')) return;
          newOptions.onClick(e, { id, ...toast.options.data });
        });
      }
      
      // Re-add close button listener
      if (this.options.showCloseButton) {
        const closeButton = newToast.querySelector('.toast-close');
        if (closeButton) {
          closeButton.addEventListener('click', () => this.closeToast(id));
        }
      }
      
      // Re-add hover listeners
      if (this.options.pauseOnHover) {
        newToast.addEventListener('mouseenter', () => this.pauseToast(id));
        newToast.addEventListener('mouseleave', () => this.resumeToast(id));
      }
    }
  }

  /**
   * Manage the maximum number of toasts
   */
  manageToasts() {
    if (this.toasts.length > this.options.maxToasts) {
      const oldestToast = this.options.newestOnTop ? this.toasts[this.toasts.length - 1] : this.toasts[0];
      this.closeToast(oldestToast.id);
    }
  }

  /**
   * Get the default icon for a toast type
   * @param {string} type - Toast type
   * @returns {string} - Icon class
   */
  getDefaultIcon(type) {
    switch (type) {
      case 'success':
        return 'ri-check-line';
      case 'error':
        return 'ri-error-warning-line';
      case 'warning':
        return 'ri-alert-line';
      case 'info':
      default:
        return 'ri-information-line';
    }
  }

  /**
   * Escape HTML to prevent XSS
   * @param {string} html - HTML string
   * @returns {string} - Escaped HTML
   */
  escapeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
  }

  /**
   * Show an info toast
   * @param {string|Object} options - Toast options or message
   * @returns {Object} - Toast instance
   */
  info(options) {
    if (typeof options === 'string') {
      options = { message: options };
    }
    return this.toast({ ...options, type: 'info' });
  }

  /**
   * Show a success toast
   * @param {string|Object} options - Toast options or message
   * @returns {Object} - Toast instance
   */
  success(options) {
    if (typeof options === 'string') {
      options = { message: options };
    }
    return this.toast({ ...options, type: 'success' });
  }

  /**
   * Show a warning toast
   * @param {string|Object} options - Toast options or message
   * @returns {Object} - Toast instance
   */
  warning(options) {
    if (typeof options === 'string') {
      options = { message: options };
    }
    return this.toast({ ...options, type: 'warning' });
  }

  /**
   * Show an error toast
   * @param {string|Object} options - Toast options or message
   * @returns {Object} - Toast instance
   */
  error(options) {
    if (typeof options === 'string') {
      options = { message: options };
    }
    return this.toast({ ...options, type: 'error' });
  }

  /**
   * Clear all toasts
   */
  clear() {
    this.toasts.forEach(toast => this.closeToast(toast.id));
  }
}

// Create global notification instance
window.notifications = new NotificationSystem();

// Shorthand functions
window.toast = {
  info: (options) => window.notifications.info(options),
  success: (options) => window.notifications.success(options),
  warning: (options) => window.notifications.warning(options),
  error: (options) => window.notifications.error(options),
  clear: () => window.notifications.clear()
};
