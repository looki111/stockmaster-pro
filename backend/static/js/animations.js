/**
 * StockMaster Pro Animations
 * Advanced animations and micro-interactions for a premium UI experience
 */

// Animation Configuration
const AnimationConfig = {
  // Timing
  duration: {
    fast: 150,
    normal: 300,
    slow: 500,
    verySlow: 800
  },
  
  // Easing Functions
  easing: {
    linear: 'linear',
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    // Cubic Bezier Curves
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
    smooth: 'cubic-bezier(0.4, 0, 0.2, 1)',
    accelerate: 'cubic-bezier(0.4, 0, 1, 1)',
    decelerate: 'cubic-bezier(0, 0, 0.2, 1)'
  },
  
  // Animation Presets
  presets: {
    fadeIn: [
      { opacity: 0 },
      { opacity: 1 }
    ],
    fadeOut: [
      { opacity: 1 },
      { opacity: 0 }
    ],
    slideInUp: [
      { transform: 'translateY(20px)', opacity: 0 },
      { transform: 'translateY(0)', opacity: 1 }
    ],
    slideInDown: [
      { transform: 'translateY(-20px)', opacity: 0 },
      { transform: 'translateY(0)', opacity: 1 }
    ],
    slideInLeft: [
      { transform: 'translateX(-20px)', opacity: 0 },
      { transform: 'translateX(0)', opacity: 1 }
    ],
    slideInRight: [
      { transform: 'translateX(20px)', opacity: 0 },
      { transform: 'translateX(0)', opacity: 1 }
    ],
    zoomIn: [
      { transform: 'scale(0.95)', opacity: 0 },
      { transform: 'scale(1)', opacity: 1 }
    ],
    zoomOut: [
      { transform: 'scale(1)', opacity: 1 },
      { transform: 'scale(0.95)', opacity: 0 }
    ],
    pulse: [
      { transform: 'scale(1)' },
      { transform: 'scale(1.05)' },
      { transform: 'scale(1)' }
    ],
    shake: [
      { transform: 'translateX(0)' },
      { transform: 'translateX(-5px)' },
      { transform: 'translateX(5px)' },
      { transform: 'translateX(-5px)' },
      { transform: 'translateX(5px)' },
      { transform: 'translateX(0)' }
    ],
    bounce: [
      { transform: 'translateY(0)' },
      { transform: 'translateY(-10px)' },
      { transform: 'translateY(0)' },
      { transform: 'translateY(-5px)' },
      { transform: 'translateY(0)' }
    ],
    flip: [
      { transform: 'perspective(400px) rotateY(0)' },
      { transform: 'perspective(400px) rotateY(180deg)' }
    ],
    rotate: [
      { transform: 'rotate(0deg)' },
      { transform: 'rotate(360deg)' }
    ]
  }
};

/**
 * Animation Controller
 * Handles all animations in the application
 */
class AnimationController {
  constructor() {
    this.initAnimations();
    this.setupEventListeners();
  }
  
  /**
   * Initialize animations on page load
   */
  initAnimations() {
    // Add entrance animations to elements with data-animate attribute
    this.setupEntranceAnimations();
    
    // Initialize 3D tilt effect
    this.setup3DTiltEffect();
    
    // Initialize hover animations
    this.setupHoverAnimations();
    
    // Initialize scroll animations
    this.setupScrollAnimations();
    
    console.log('Animation system initialized');
  }
  
  /**
   * Set up event listeners
   */
  setupEventListeners() {
    // Listen for page transitions
    document.addEventListener('page:transition', this.handlePageTransition.bind(this));
    
    // Listen for modal open/close
    document.addEventListener('modal:open', this.handleModalOpen.bind(this));
    document.addEventListener('modal:close', this.handleModalClose.bind(this));
    
    // Listen for form submissions
    document.addEventListener('form:submit', this.handleFormSubmit.bind(this));
    
    // Listen for data loading
    document.addEventListener('data:loading', this.handleDataLoading.bind(this));
    document.addEventListener('data:loaded', this.handleDataLoaded.bind(this));
  }
  
  /**
   * Set up entrance animations
   */
  setupEntranceAnimations() {
    const animatedElements = document.querySelectorAll('[data-animate]');
    
    animatedElements.forEach((element, index) => {
      const animationType = element.dataset.animate || 'fadeIn';
      const delay = element.dataset.animateDelay || index * 100;
      const duration = element.dataset.animateDuration || AnimationConfig.duration.normal;
      const easing = element.dataset.animateEasing || AnimationConfig.easing.easeOut;
      
      // Set initial state
      element.style.opacity = '0';
      element.style.transition = `all ${duration}ms ${easing}`;
      
      // Animate after delay
      setTimeout(() => {
        this.animate(element, animationType);
      }, delay);
    });
  }
  
  /**
   * Set up 3D tilt effect
   */
  setup3DTiltEffect() {
    const tiltElements = document.querySelectorAll('[data-tilt]');
    
    tiltElements.forEach(element => {
      element.addEventListener('mousemove', e => {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const deltaX = (x - centerX) / centerX;
        const deltaY = (y - centerY) / centerY;
        
        const tiltAmount = element.dataset.tiltAmount || 10;
        
        element.style.transform = `perspective(1000px) rotateX(${-deltaY * tiltAmount}deg) rotateY(${deltaX * tiltAmount}deg) scale3d(1.05, 1.05, 1.05)`;
      });
      
      element.addEventListener('mouseleave', () => {
        element.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
      });
    });
  }
  
  /**
   * Set up hover animations
   */
  setupHoverAnimations() {
    const hoverElements = document.querySelectorAll('[data-hover-animate]');
    
    hoverElements.forEach(element => {
      const animationType = element.dataset.hoverAnimate;
      const duration = element.dataset.hoverDuration || AnimationConfig.duration.fast;
      const easing = element.dataset.hoverEasing || AnimationConfig.easing.easeOut;
      
      element.addEventListener('mouseenter', () => {
        this.animate(element, animationType, duration, easing);
      });
      
      element.addEventListener('mouseleave', () => {
        this.resetAnimation(element);
      });
    });
  }
  
  /**
   * Set up scroll animations
   */
  setupScrollAnimations() {
    const scrollElements = document.querySelectorAll('[data-scroll-animate]');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const element = entry.target;
          const animationType = element.dataset.scrollAnimate;
          const duration = element.dataset.scrollDuration || AnimationConfig.duration.normal;
          const easing = element.dataset.scrollEasing || AnimationConfig.easing.easeOut;
          
          this.animate(element, animationType, duration, easing);
          
          // Unobserve after animation if not repeating
          if (!element.dataset.scrollRepeat) {
            observer.unobserve(element);
          }
        } else if (element.dataset.scrollRepeat) {
          this.resetAnimation(entry.target);
        }
      });
    }, {
      threshold: 0.1
    });
    
    scrollElements.forEach(element => {
      observer.observe(element);
    });
  }
  
  /**
   * Animate an element with a preset animation
   */
  animate(element, animationType, duration = AnimationConfig.duration.normal, easing = AnimationConfig.easing.easeOut) {
    if (!element) return;
    
    const preset = AnimationConfig.presets[animationType];
    
    if (!preset) {
      console.warn(`Animation preset "${animationType}" not found`);
      return;
    }
    
    // Use Web Animations API
    const animation = element.animate(preset, {
      duration: duration,
      easing: easing,
      fill: 'forwards'
    });
    
    // Store animation reference
    element._currentAnimation = animation;
    
    return animation;
  }
  
  /**
   * Reset an element's animation
   */
  resetAnimation(element) {
    if (!element || !element._currentAnimation) return;
    
    element._currentAnimation.cancel();
    element.style.transform = '';
    element.style.opacity = '';
  }
  
  /**
   * Handle page transition
   */
  handlePageTransition(event) {
    const { from, to } = event.detail;
    
    // Animate out current page
    if (from) {
      this.animate(from, 'fadeOut', AnimationConfig.duration.fast)
        .onfinish = () => {
          from.style.display = 'none';
          
          // Animate in new page
          if (to) {
            to.style.display = 'block';
            this.animate(to, 'fadeIn', AnimationConfig.duration.fast);
          }
        };
    } else if (to) {
      to.style.display = 'block';
      this.animate(to, 'fadeIn', AnimationConfig.duration.fast);
    }
  }
  
  /**
   * Handle modal open
   */
  handleModalOpen(event) {
    const { modal, backdrop } = event.detail;
    
    if (backdrop) {
      backdrop.style.display = 'flex';
      this.animate(backdrop, 'fadeIn', AnimationConfig.duration.fast);
    }
    
    if (modal) {
      this.animate(modal, 'zoomIn', AnimationConfig.duration.normal);
    }
  }
  
  /**
   * Handle modal close
   */
  handleModalClose(event) {
    const { modal, backdrop } = event.detail;
    
    if (modal) {
      this.animate(modal, 'zoomOut', AnimationConfig.duration.fast)
        .onfinish = () => {
          if (backdrop) {
            this.animate(backdrop, 'fadeOut', AnimationConfig.duration.fast)
              .onfinish = () => {
                backdrop.style.display = 'none';
              };
          }
        };
    } else if (backdrop) {
      this.animate(backdrop, 'fadeOut', AnimationConfig.duration.fast)
        .onfinish = () => {
          backdrop.style.display = 'none';
        };
    }
  }
  
  /**
   * Handle form submit
   */
  handleFormSubmit(event) {
    const { form, success } = event.detail;
    
    if (success) {
      this.animate(form, 'pulse', AnimationConfig.duration.fast);
    } else {
      this.animate(form, 'shake', AnimationConfig.duration.fast);
    }
  }
  
  /**
   * Handle data loading
   */
  handleDataLoading(event) {
    const { container } = event.detail;
    
    if (container) {
      // Add loading state
      container.classList.add('is-loading');
      
      // Create and append loader if it doesn't exist
      if (!container.querySelector('.loader')) {
        const loader = document.createElement('div');
        loader.className = 'loader';
        container.appendChild(loader);
        
        this.animate(loader, 'fadeIn', AnimationConfig.duration.fast);
      }
    }
  }
  
  /**
   * Handle data loaded
   */
  handleDataLoaded(event) {
    const { container, data } = event.detail;
    
    if (container) {
      // Remove loading state
      container.classList.remove('is-loading');
      
      // Remove loader
      const loader = container.querySelector('.loader');
      if (loader) {
        this.animate(loader, 'fadeOut', AnimationConfig.duration.fast)
          .onfinish = () => {
            loader.remove();
          };
      }
      
      // Animate new content
      const content = container.querySelector('.content');
      if (content) {
        this.animate(content, 'fadeIn', AnimationConfig.duration.normal);
      }
    }
  }
}

// Initialize animation controller when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.AnimationController = new AnimationController();
});

// Export animation utilities
window.StockMasterAnimations = {
  animate: (element, animationType, duration, easing) => {
    if (window.AnimationController) {
      return window.AnimationController.animate(element, animationType, duration, easing);
    }
  },
  config: AnimationConfig
};
