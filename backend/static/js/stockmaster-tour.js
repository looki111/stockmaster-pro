/**
 * StockMaster Pro - Guided Tour
 * A guided tour component for onboarding new users
 */

class GuidedTour {
  constructor(options = {}) {
    this.options = {
      steps: options.steps || [],
      onStart: options.onStart || null,
      onEnd: options.onEnd || null,
      onSkip: options.onSkip || null,
      onStep: options.onStep || null,
      showProgress: options.showProgress !== undefined ? options.showProgress : true,
      showSkip: options.showSkip !== undefined ? options.showSkip : true,
      showClose: options.showClose !== undefined ? options.showClose : true,
      showPulse: options.showPulse !== undefined ? options.showPulse : true,
      scrollIntoView: options.scrollIntoView !== undefined ? options.scrollIntoView : true,
      scrollPadding: options.scrollPadding || 20,
      spotlightPadding: options.spotlightPadding || 10,
      rtl: document.documentElement.dir === 'rtl',
      labels: {
        next: options.labels?.next || 'Next',
        prev: options.labels?.prev || 'Previous',
        skip: options.labels?.skip || 'Skip',
        finish: options.labels?.finish || 'Finish',
        close: options.labels?.close || 'Close',
        step: options.labels?.step || 'Step',
        of: options.labels?.of || 'of'
      }
    };

    this.currentStep = 0;
    this.isActive = false;
    this.elements = {
      overlay: null,
      spotlight: null,
      tooltip: null,
      pulse: null
    };

    // Bind methods
    this.start = this.start.bind(this);
    this.end = this.end.bind(this);
    this.skip = this.skip.bind(this);
    this.next = this.next.bind(this);
    this.prev = this.prev.bind(this);
    this.goToStep = this.goToStep.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleResize = this.handleResize.bind(this);
    this.handleScroll = this.handleScroll.bind(this);
    this.updateTooltipPosition = this.updateTooltipPosition.bind(this);
  }

  /**
   * Start the tour
   * @param {number} startAt - Step to start at (0-based index)
   */
  start(startAt = 0) {
    if (this.isActive || !this.options.steps.length) return;

    this.isActive = true;
    this.currentStep = startAt;

    // Create overlay
    this.createOverlay();

    // Add event listeners
    window.addEventListener('keydown', this.handleKeyDown);
    window.addEventListener('resize', this.handleResize);
    window.addEventListener('scroll', this.handleScroll, true);

    // Show first step
    this.showStep(this.currentStep);

    // Call onStart callback
    if (this.options.onStart) {
      this.options.onStart();
    }
  }

  /**
   * End the tour
   */
  end() {
    if (!this.isActive) return;

    this.isActive = false;

    // Remove elements
    this.removeElements();

    // Remove event listeners
    window.removeEventListener('keydown', this.handleKeyDown);
    window.removeEventListener('resize', this.handleResize);
    window.removeEventListener('scroll', this.handleScroll, true);

    // Call onEnd callback
    if (this.options.onEnd) {
      this.options.onEnd();
    }
  }

  /**
   * Skip the tour
   */
  skip() {
    if (!this.isActive) return;

    // Call onSkip callback
    if (this.options.onSkip) {
      this.options.onSkip(this.currentStep);
    }

    this.end();
  }

  /**
   * Go to the next step
   */
  next() {
    if (!this.isActive) return;

    const nextStep = this.currentStep + 1;
    if (nextStep >= this.options.steps.length) {
      this.end();
      return;
    }

    this.goToStep(nextStep);
  }

  /**
   * Go to the previous step
   */
  prev() {
    if (!this.isActive) return;

    const prevStep = this.currentStep - 1;
    if (prevStep < 0) return;

    this.goToStep(prevStep);
  }

  /**
   * Go to a specific step
   * @param {number} stepIndex - Step index (0-based)
   */
  goToStep(stepIndex) {
    if (!this.isActive || stepIndex < 0 || stepIndex >= this.options.steps.length) return;

    this.currentStep = stepIndex;
    this.showStep(this.currentStep);
  }

  /**
   * Show a step
   * @param {number} stepIndex - Step index (0-based)
   */
  showStep(stepIndex) {
    const step = this.options.steps[stepIndex];
    if (!step) return;

    // Get target element
    const target = this.getTargetElement(step.target);
    if (!target) {
      console.warn(`Target element not found: ${step.target}`);
      this.next();
      return;
    }

    // Scroll target into view if needed
    if (this.options.scrollIntoView) {
      this.scrollToTarget(target);
    }

    // Update spotlight
    this.updateSpotlight(target);

    // Update tooltip
    this.updateTooltip(step, target, stepIndex);

    // Update pulse
    if (this.options.showPulse) {
      this.updatePulse(target);
    }

    // Call onStep callback
    if (this.options.onStep) {
      this.options.onStep(stepIndex, step);
    }
  }

  /**
   * Create the overlay element
   */
  createOverlay() {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'tour-overlay';
    document.body.appendChild(overlay);
    this.elements.overlay = overlay;

    // Create spotlight
    const spotlight = document.createElement('div');
    spotlight.className = 'tour-spotlight';
    document.body.appendChild(spotlight);
    this.elements.spotlight = spotlight;

    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'tour-tooltip';
    document.body.appendChild(tooltip);
    this.elements.tooltip = tooltip;

    // Create pulse
    if (this.options.showPulse) {
      const pulse = document.createElement('div');
      pulse.className = 'tour-pulse';
      document.body.appendChild(pulse);
      this.elements.pulse = pulse;
    }
  }

  /**
   * Remove all tour elements
   */
  removeElements() {
    // Remove overlay
    if (this.elements.overlay && this.elements.overlay.parentNode) {
      this.elements.overlay.parentNode.removeChild(this.elements.overlay);
    }

    // Remove spotlight
    if (this.elements.spotlight && this.elements.spotlight.parentNode) {
      this.elements.spotlight.parentNode.removeChild(this.elements.spotlight);
    }

    // Remove tooltip
    if (this.elements.tooltip && this.elements.tooltip.parentNode) {
      this.elements.tooltip.parentNode.removeChild(this.elements.tooltip);
    }

    // Remove pulse
    if (this.elements.pulse && this.elements.pulse.parentNode) {
      this.elements.pulse.parentNode.removeChild(this.elements.pulse);
    }

    this.elements = {
      overlay: null,
      spotlight: null,
      tooltip: null,
      pulse: null
    };
  }

  /**
   * Update the spotlight position and size
   * @param {HTMLElement} target - Target element
   */
  updateSpotlight(target) {
    if (!this.elements.spotlight || !target) return;

    const rect = target.getBoundingClientRect();
    const padding = this.options.spotlightPadding;

    this.elements.spotlight.style.top = `${rect.top - padding}px`;
    this.elements.spotlight.style.left = `${rect.left - padding}px`;
    this.elements.spotlight.style.width = `${rect.width + padding * 2}px`;
    this.elements.spotlight.style.height = `${rect.height + padding * 2}px`;
  }

  /**
   * Update the tooltip content and position
   * @param {Object} step - Step configuration
   * @param {HTMLElement} target - Target element
   * @param {number} stepIndex - Step index (0-based)
   */
  updateTooltip(step, target, stepIndex) {
    if (!this.elements.tooltip || !target) return;

    // Update tooltip content
    this.elements.tooltip.innerHTML = this.createTooltipContent(step, stepIndex);

    // Add event listeners to buttons
    const skipButton = this.elements.tooltip.querySelector('.tour-tooltip-button-skip');
    if (skipButton) {
      skipButton.addEventListener('click', this.skip);
    }

    const prevButton = this.elements.tooltip.querySelector('.tour-tooltip-button-prev');
    if (prevButton) {
      prevButton.addEventListener('click', this.prev);
    }

    const nextButton = this.elements.tooltip.querySelector('.tour-tooltip-button-next');
    if (nextButton) {
      nextButton.addEventListener('click', this.next);
    }

    const finishButton = this.elements.tooltip.querySelector('.tour-tooltip-button-finish');
    if (finishButton) {
      finishButton.addEventListener('click', this.end);
    }

    const closeButton = this.elements.tooltip.querySelector('.tour-tooltip-close');
    if (closeButton) {
      closeButton.addEventListener('click', this.end);
    }

    // Update tooltip position
    this.updateTooltipPosition(target, step.position || 'bottom');
  }

  /**
   * Update the tooltip position
   * @param {HTMLElement} target - Target element
   * @param {string} position - Tooltip position (top, bottom, left, right)
   */
  updateTooltipPosition(target, position) {
    if (!this.elements.tooltip || !target) return;

    const targetRect = target.getBoundingClientRect();
    const tooltipRect = this.elements.tooltip.getBoundingClientRect();
    const padding = this.options.spotlightPadding;

    // Reset position classes
    this.elements.tooltip.classList.remove('top', 'bottom', 'left', 'right');
    this.elements.tooltip.classList.add(position);

    let top, left;

    switch (position) {
      case 'top':
        top = targetRect.top - tooltipRect.height - padding;
        left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
        break;
      case 'bottom':
        top = targetRect.bottom + padding;
        left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
        break;
      case 'left':
        top = targetRect.top + (targetRect.height - tooltipRect.height) / 2;
        left = targetRect.left - tooltipRect.width - padding;
        break;
      case 'right':
        top = targetRect.top + (targetRect.height - tooltipRect.height) / 2;
        left = targetRect.right + padding;
        break;
      default:
        top = targetRect.bottom + padding;
        left = targetRect.left + (targetRect.width - tooltipRect.width) / 2;
    }

    // Adjust if tooltip is outside viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    if (left < 0) {
      left = 0;
    } else if (left + tooltipRect.width > viewportWidth) {
      left = viewportWidth - tooltipRect.width;
    }

    if (top < 0) {
      top = 0;
    } else if (top + tooltipRect.height > viewportHeight) {
      top = viewportHeight - tooltipRect.height;
    }

    this.elements.tooltip.style.top = `${top}px`;
    this.elements.tooltip.style.left = `${left}px`;
  }

  /**
   * Update the pulse position
   * @param {HTMLElement} target - Target element
   */
  updatePulse(target) {
    if (!this.elements.pulse || !target) return;

    const rect = target.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height) * 1.5;

    this.elements.pulse.style.top = `${rect.top + rect.height / 2 - size / 2}px`;
    this.elements.pulse.style.left = `${rect.left + rect.width / 2 - size / 2}px`;
    this.elements.pulse.style.width = `${size}px`;
    this.elements.pulse.style.height = `${size}px`;
  }

  /**
   * Create the tooltip content
   * @param {Object} step - Step configuration
   * @param {number} stepIndex - Step index (0-based)
   * @returns {string} - Tooltip HTML content
   */
  createTooltipContent(step, stepIndex) {
    const isFirst = stepIndex === 0;
    const isLast = stepIndex === this.options.steps.length - 1;
    const { labels } = this.options;

    return `
      <div class="tour-tooltip-header">
        <div class="tour-tooltip-step">${stepIndex + 1}</div>
        <div class="tour-tooltip-title">${step.title || ''}</div>
        ${this.options.showClose ? `<button class="tour-tooltip-close" aria-label="${labels.close}"><i class="ri-close-line"></i></button>` : ''}
      </div>
      <div class="tour-tooltip-content">${step.content || ''}</div>
      <div class="tour-tooltip-footer">
        ${this.options.showProgress ? `<div class="tour-tooltip-progress">${labels.step} ${stepIndex + 1} ${labels.of} ${this.options.steps.length}</div>` : ''}
        <div class="tour-tooltip-buttons">
          ${this.options.showSkip && !isLast ? `<button class="tour-tooltip-button tour-tooltip-button-skip">${labels.skip}</button>` : ''}
          ${!isFirst ? `<button class="tour-tooltip-button tour-tooltip-button-prev">${labels.prev}</button>` : ''}
          ${!isLast ? `<button class="tour-tooltip-button tour-tooltip-button-next">${labels.next}</button>` : ''}
          ${isLast ? `<button class="tour-tooltip-button tour-tooltip-button-finish">${labels.finish}</button>` : ''}
        </div>
      </div>
    `;
  }

  /**
   * Get the target element
   * @param {string|HTMLElement} target - Target selector or element
   * @returns {HTMLElement|null} - Target element
   */
  getTargetElement(target) {
    if (!target) return null;

    if (typeof target === 'string') {
      return document.querySelector(target);
    }

    return target;
  }

  /**
   * Scroll to the target element
   * @param {HTMLElement} target - Target element
   */
  scrollToTarget(target) {
    if (!target) return;

    const rect = target.getBoundingClientRect();
    const isInViewport = (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    );

    if (!isInViewport) {
      const scrollPadding = this.options.scrollPadding;
      const scrollTop = window.pageYOffset + rect.top - scrollPadding;
      
      window.scrollTo({
        top: scrollTop,
        behavior: 'smooth'
      });
    }
  }

  /**
   * Handle keydown events
   * @param {KeyboardEvent} event - Keyboard event
   */
  handleKeyDown(event) {
    if (!this.isActive) return;

    switch (event.key) {
      case 'Escape':
        this.end();
        break;
      case 'ArrowRight':
        if (!this.options.rtl) {
          this.next();
        } else {
          this.prev();
        }
        break;
      case 'ArrowLeft':
        if (!this.options.rtl) {
          this.prev();
        } else {
          this.next();
        }
        break;
      case 'Enter':
        this.next();
        break;
    }
  }

  /**
   * Handle resize events
   */
  handleResize() {
    if (!this.isActive) return;

    const step = this.options.steps[this.currentStep];
    if (!step) return;

    const target = this.getTargetElement(step.target);
    if (!target) return;

    this.updateSpotlight(target);
    this.updateTooltipPosition(target, step.position || 'bottom');
    
    if (this.options.showPulse) {
      this.updatePulse(target);
    }
  }

  /**
   * Handle scroll events
   */
  handleScroll() {
    if (!this.isActive) return;

    const step = this.options.steps[this.currentStep];
    if (!step) return;

    const target = this.getTargetElement(step.target);
    if (!target) return;

    this.updateSpotlight(target);
    this.updateTooltipPosition(target, step.position || 'bottom');
    
    if (this.options.showPulse) {
      this.updatePulse(target);
    }
  }
}

// Create global tour instance
window.guidedTour = new GuidedTour();
