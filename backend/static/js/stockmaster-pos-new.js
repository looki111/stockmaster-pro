/**
 * StockMaster Pro - POS (Point of Sale) JavaScript
 * Handles POS functionality with cart management, search, checkout,
 * and modern UI interactions including dropdowns, tooltips, and animations
 */

(function() {
  'use strict';

  // DOM elements
  let searchInput;
  let searchClearButton;
  let searchFilterButton;
  let productsGrid;
  let categoryButtons;
  let cartItems;
  let cartSubtotal;
  let cartTax;
  let cartTotal;
  let checkoutButton;
  let clearCartButton;
  let fullscreenButton;
  let dropdownToggles;
  let emptyCartElement;
  let customerButton;
  let discountButton;

  // State
  const cart = [];
  let products = [];
  let currentCategory = 'all';
  let isFullscreen = false;
  let taxRate = 0.15; // 15% tax rate

  /**
   * Initialize the POS functionality
   */
  function init() {
    // Get DOM elements
    searchInput = document.getElementById('pos-search');
    searchClearButton = document.querySelector('.pos-search-actions button:first-child');
    searchFilterButton = document.querySelector('.pos-search-actions button:last-child');
    productsGrid = document.querySelector('.pos-products-grid');
    categoryButtons = document.querySelectorAll('.pos-category');
    cartItems = document.querySelector('.pos-cart-items');
    cartSubtotal = document.querySelectorAll('.pos-cart-row-value')[0];
    cartTax = document.querySelectorAll('.pos-cart-row-value')[1];
    cartTotal = document.querySelector('.pos-cart-total-value');
    checkoutButton = document.getElementById('pos-checkout');
    clearCartButton = document.getElementById('pos-clear-cart');
    fullscreenButton = document.getElementById('pos-fullscreen');
    dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    emptyCartElement = document.getElementById('empty-cart');
    customerButton = document.querySelector('.btn-outline-primary');
    discountButton = document.querySelector('.btn-glass');

    // Set up event listeners
    setupEventListeners();

    // Initialize dropdowns
    initializeDropdowns();

    // Initialize tooltips
    initializeTooltips();

    // Load products
    loadProducts();

    // Initialize cart
    updateCart();

    // Add animation classes
    addAnimationClasses();
  }

  /**
   * Set up event listeners
   */
  function setupEventListeners() {
    // Search input
    if (searchInput) {
      searchInput.addEventListener('input', handleSearch);
      searchInput.addEventListener('focus', () => {
        searchInput.parentElement.classList.add('focused');
      });
      searchInput.addEventListener('blur', () => {
        searchInput.parentElement.classList.remove('focused');
      });
    }

    // Search clear button
    if (searchClearButton) {
      searchClearButton.addEventListener('click', () => {
        searchInput.value = '';
        handleSearch();
        searchInput.focus();
      });
    }

    // Search filter button
    if (searchFilterButton) {
      searchFilterButton.addEventListener('click', () => {
        // In a real app, this would open an advanced search modal
        alert('Advanced search would be implemented here');
      });
    }

    // Category buttons
    if (categoryButtons) {
      categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
          const category = button.dataset.category;
          setActiveCategory(category);
          filterProducts();

          // Scroll the category into view
          button.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        });
      });
    }

    // Checkout button
    if (checkoutButton) {
      checkoutButton.addEventListener('click', handleCheckout);
    }

    // Clear cart button
    if (clearCartButton) {
      clearCartButton.addEventListener('click', clearCart);
    }

    // Fullscreen button
    if (fullscreenButton) {
      fullscreenButton.addEventListener('click', toggleFullscreen);
    }

    // Customer button
    if (customerButton) {
      customerButton.addEventListener('click', () => {
        // In a real app, this would open a customer selection modal
        alert('Customer selection would be implemented here');
      });
    }

    // Discount button
    if (discountButton) {
      discountButton.addEventListener('click', () => {
        // In a real app, this would open a discount modal
        alert('Discount application would be implemented here');
      });
    }

    // Close dropdowns when clicking outside
    document.addEventListener('click', (event) => {
      if (!event.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
          menu.classList.remove('show');
        });
      }
    });
  }

  /**
   * Initialize dropdowns
   */
  function initializeDropdowns() {
    if (dropdownToggles) {
      dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (event) => {
          event.stopPropagation();
          const dropdown = toggle.nextElementSibling;

          // Close all other dropdowns
          document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            if (menu !== dropdown) {
              menu.classList.remove('show');
            }
          });

          // Toggle current dropdown
          dropdown.classList.toggle('show');
        });
      });
    }

    // Add click handlers to dropdown items
    document.querySelectorAll('.dropdown-item').forEach(item => {
      item.addEventListener('click', () => {
        // Close the dropdown
        item.closest('.dropdown-menu').classList.remove('show');
      });
    });
  }

  /**
   * Initialize tooltips
   */
  function initializeTooltips() {
    // No additional initialization needed as we're using CSS tooltips
    // But we could add dynamic tooltips here if needed
  }

  /**
   * Add animation classes to elements
   */
  function addAnimationClasses() {
    // Add animation delay to product cards
    const productCards = document.querySelectorAll('.pos-product-card');
    productCards.forEach((card, index) => {
      card.style.animationDelay = `${index * 0.05}s`;
      card.classList.add('animate-fadeIn');
    });
  }

  /**
   * Load products from the server
   */
  function loadProducts() {
    // For demo purposes, we'll use dummy data
    // In a real application, you would fetch this from the server
    products = [
      { id: 1, name: 'Espresso', price: 12, category: 'coffee', image: 'ri-cup-line' },
      { id: 2, name: 'Cappuccino', price: 18, category: 'coffee', image: 'ri-cup-line' },
      { id: 3, name: 'Latte', price: 20, category: 'coffee', image: 'ri-cup-line' },
      { id: 4, name: 'Americano', price: 15, category: 'coffee', image: 'ri-cup-line' },
      { id: 5, name: 'Mocha', price: 22, category: 'coffee', image: 'ri-cup-line' },
      { id: 6, name: 'Green Tea', price: 14, category: 'tea', image: 'ri-cup-line' },
      { id: 7, name: 'Black Tea', price: 12, category: 'tea', image: 'ri-cup-line' },
      { id: 8, name: 'Herbal Tea', price: 16, category: 'tea', image: 'ri-cup-line' },
      { id: 9, name: 'Chocolate Cake', price: 25, category: 'dessert', image: 'ri-cake-3-line' },
      { id: 10, name: 'Cheesecake', price: 28, category: 'dessert', image: 'ri-cake-3-line' },
      { id: 11, name: 'Croissant', price: 10, category: 'bakery', image: 'ri-cake-2-line' },
      { id: 12, name: 'Sandwich', price: 22, category: 'food', image: 'ri-sandwich-line' }
    ];

    renderProducts();
  }

  /**
   * Render products in the grid
   */
  function renderProducts() {
    if (!productsGrid) return;

    productsGrid.innerHTML = '';

    const filteredProducts = filterProductsByCategory(filterProductsBySearch(products));

    if (filteredProducts.length === 0) {
      // Show no results message
      const noResults = document.createElement('div');
      noResults.className = 'text-center py-8 col-span-full';
      noResults.innerHTML = `
        <img src="/static/img/no-inventory.svg" alt="No products found" class="mx-auto mb-4" style="width: 120px; height: 120px; opacity: 0.7;">
        <p class="text-secondary-content mb-2">No products found</p>
        <p class="text-tertiary-content text-sm">Try a different search term or category</p>
      `;
      productsGrid.appendChild(noResults);
      return;
    }

    filteredProducts.forEach((product, index) => {
      const productCard = document.createElement('div');
      productCard.className = 'pos-product-card animate-fadeIn';
      productCard.dataset.id = product.id;
      productCard.style.animationDelay = `${index * 0.05}s`;

      // Add badge for new or sale items (randomly for demo)
      let badgeHTML = '';
      if (product.id % 5 === 0) {
        badgeHTML = `<div class="pos-product-badge pos-product-badge-new">New</div>`;
      } else if (product.id % 7 === 0) {
        badgeHTML = `<div class="pos-product-badge pos-product-badge-sale">Sale</div>`;
      }

      productCard.innerHTML = `
        <div class="pos-product-image">
          <i class="${product.image}"></i>
          ${badgeHTML}
        </div>
        <div class="pos-product-details">
          <div class="pos-product-name">${product.name}</div>
          <div class="pos-product-price">
            <span>${product.price} SAR</span>
            <button class="pos-product-add" aria-label="Add to cart">
              <i class="ri-add-line"></i>
            </button>
          </div>
        </div>
      `;

      productCard.addEventListener('click', () => {
        addToCart(product);

        // Add a ripple effect
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        productCard.appendChild(ripple);

        // Position the ripple
        const rect = productCard.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
        ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

        // Remove the ripple after animation
        setTimeout(() => {
          ripple.remove();
        }, 600);
      });

      productsGrid.appendChild(productCard);
    });
  }

  /**
   * Filter products by search term
   * @param {Array} products - The products to filter
   * @returns {Array} - Filtered products
   */
  function filterProductsBySearch(products) {
    if (!searchInput || !searchInput.value.trim()) {
      return products;
    }

    const searchTerm = searchInput.value.trim().toLowerCase();

    return products.filter(product => {
      return product.name.toLowerCase().includes(searchTerm);
    });
  }

  /**
   * Filter products by category
   * @param {Array} products - The products to filter
   * @returns {Array} - Filtered products
   */
  function filterProductsByCategory(products) {
    if (currentCategory === 'all') {
      return products;
    }

    return products.filter(product => {
      return product.category === currentCategory;
    });
  }

  /**
   * Handle search input
   */
  function handleSearch() {
    renderProducts();
  }

  /**
   * Set active category
   * @param {string} category - The category to set as active
   */
  function setActiveCategory(category) {
    currentCategory = category;

    categoryButtons.forEach(button => {
      if (button.dataset.category === category) {
        button.classList.add('active');
      } else {
        button.classList.remove('active');
      }
    });
  }

  /**
   * Filter products based on current search and category
   */
  function filterProducts() {
    renderProducts();
  }

  /**
   * Add a product to the cart
   * @param {Object} product - The product to add
   */
  function addToCart(product) {
    const existingItem = cart.find(item => item.product.id === product.id);

    if (existingItem) {
      existingItem.quantity += 1;
    } else {
      cart.push({
        product,
        quantity: 1
      });
    }

    updateCart();
  }

  /**
   * Remove a product from the cart
   * @param {number} productId - The ID of the product to remove
   */
  function removeFromCart(productId) {
    const index = cart.findIndex(item => item.product.id === productId);

    if (index !== -1) {
      cart.splice(index, 1);
      updateCart();
    }
  }

  /**
   * Update the quantity of a product in the cart
   * @param {number} productId - The ID of the product
   * @param {number} quantity - The new quantity
   */
  function updateCartItemQuantity(productId, quantity) {
    const item = cart.find(item => item.product.id === productId);

    if (item) {
      item.quantity = Math.max(1, quantity);
      updateCart();
    }
  }

  /**
   * Update the cart UI
   */
  function updateCart() {
    if (!cartItems || !cartTotal) return;

    cartItems.innerHTML = '';

    if (cart.length === 0) {
      // Show empty cart state
      cartItems.innerHTML = `
        <div id="empty-cart" class="text-center py-8">
          <img src="/static/img/empty-cart.svg" alt="Empty Cart" class="mb-4" style="width: 120px; height: 120px; opacity: 0.7;">
          <p class="text-secondary-content mb-2">Your cart is empty</p>
          <p class="text-tertiary-content text-sm">Add products to start a new order</p>
        </div>
      `;

      // Update totals
      if (cartSubtotal) cartSubtotal.textContent = '0 SAR';
      if (cartTax) cartTax.textContent = '0 SAR';
      cartTotal.textContent = '0 SAR';

      // Disable checkout button
      if (checkoutButton) {
        checkoutButton.disabled = true;
        checkoutButton.classList.add('disabled');
      }

      return;
    }

    // Enable checkout button
    if (checkoutButton) {
      checkoutButton.disabled = false;
      checkoutButton.classList.remove('disabled');
    }

    let subtotal = 0;

    cart.forEach((item, index) => {
      const { product, quantity } = item;
      const itemTotal = product.price * quantity;
      subtotal += itemTotal;

      const cartItem = document.createElement('div');
      cartItem.className = 'pos-cart-item animate-fadeIn';
      cartItem.style.animationDelay = `${index * 0.05}s`;
      cartItem.innerHTML = `
        <div class="pos-cart-item-details">
          <div class="pos-cart-item-name">${product.name}</div>
          <div class="pos-cart-item-price">${product.price} SAR × ${quantity} = ${itemTotal.toFixed(2)} SAR</div>
        </div>
        <div class="pos-cart-item-quantity">
          <button class="pos-quantity-btn" data-action="decrease" aria-label="Decrease quantity">
            <i class="ri-subtract-line"></i>
          </button>
          <div class="pos-quantity-value">${quantity}</div>
          <button class="pos-quantity-btn" data-action="increase" aria-label="Increase quantity">
            <i class="ri-add-line"></i>
          </button>
        </div>
        <div class="pos-cart-item-remove" data-id="${product.id}" aria-label="Remove item">
          <i class="ri-delete-bin-line"></i>
        </div>
      `;

      // Add event listeners
      cartItems.appendChild(cartItem);

      const decreaseBtn = cartItem.querySelector('[data-action="decrease"]');
      const increaseBtn = cartItem.querySelector('[data-action="increase"]');
      const removeBtn = cartItem.querySelector('.pos-cart-item-remove');

      decreaseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        updateCartItemQuantity(product.id, quantity - 1);
      });

      increaseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        updateCartItemQuantity(product.id, quantity + 1);
      });

      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        // Add fade out animation
        cartItem.classList.add('animate-fadeOut');

        // Remove after animation completes
        setTimeout(() => {
          removeFromCart(product.id);
        }, 300);
      });
    });

    // Calculate tax and total
    const tax = subtotal * taxRate;
    const total = subtotal + tax;

    // Update totals
    if (cartSubtotal) cartSubtotal.textContent = `${subtotal.toFixed(2)} SAR`;
    if (cartTax) cartTax.textContent = `${tax.toFixed(2)} SAR`;
    cartTotal.textContent = `${total.toFixed(2)} SAR`;
  }

  /**
   * Clear the cart
   */
  function clearCart() {
    cart.length = 0;
    updateCart();
  }

  /**
   * Handle checkout
   */
  function handleCheckout() {
    if (cart.length === 0) {
      alert('Your cart is empty');
      return;
    }

    // In a real application, you would send the cart to the server
    // and process the payment
    alert('Checkout functionality would be implemented here');

    // For demo purposes, we'll just clear the cart
    clearCart();
  }

  /**
   * Toggle fullscreen mode
   */
  function toggleFullscreen() {
    const posContainer = document.querySelector('.pos-container');

    if (!posContainer) return;

    isFullscreen = !isFullscreen;

    if (isFullscreen) {
      posContainer.classList.add('pos-fullscreen');
      fullscreenButton.innerHTML = '<i class="ri-fullscreen-exit-line"></i>';
    } else {
      posContainer.classList.remove('pos-fullscreen');
      fullscreenButton.innerHTML = '<i class="ri-fullscreen-line"></i>';
    }
  }

  // Initialize when the DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
