/**
 * Enhanced POS (Point of Sale) JavaScript for StockMaster Pro
 */

// Global variables
let posData = null;
let currentOrder = {
    id: generateOrderId(),
    items: [],
    type: 'dine_in',
    customer: null,
    client_id: null,
    table_number: null,
    delivery_address: null,
    subtotal: 0,
    tax: 0,
    total: 0,
    discount: 0,
    notes: ''
};

let selectedClient = null;
let activeShift = null;
let taxRate = 15; // Default tax rate (%)

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize POS
    initPOS();
});

// Initialize POS
async function initPOS() {
    // Load POS data
    await loadPOSData();

    // Initialize event listeners
    initEventListeners();

    // Initialize UI
    updateOrderSummary();

    // Check if there's an active shift
    checkActiveShift();
}

// Load POS data
async function loadPOSData() {
    try {
        // Show loading state
        document.getElementById('productsGrid').innerHTML = `
            <div class="pos-loading">
                <div class="spinner"></div>
                <p>${document.documentElement.lang === 'ar' ? 'جاري التحميل...' : 'Loading...'}</p>
            </div>
        `;

        // Fetch POS data from API
        const response = await fetch('/pos/data');
        if (!response.ok) {
            throw new Error('Failed to load POS data');
        }

        posData = await response.json();

        // Update tax rate
        taxRate = posData.branch.tax_rate || 15;

        // Initialize categories
        initCategories();

        // Initialize products
        initProducts();

        // Update shift status
        if (posData.shift.active) {
            activeShift = posData.shift;
            updateShiftUI(true);
        }

    } catch (error) {
        console.error('Error loading POS data:', error);
        showToast(error.message, 'error');
    }
}

// Initialize categories
function initCategories() {
    const categoryTabs = document.getElementById('categoryTabs');

    // Clear existing tabs except "All"
    const allTab = categoryTabs.querySelector('[data-category="all"]');
    categoryTabs.innerHTML = '';
    categoryTabs.appendChild(allTab);

    // Add category tabs
    if (posData.categories && posData.categories.length > 0) {
        posData.categories.forEach(category => {
            const tab = document.createElement('button');
            tab.className = 'pos-category-tab';
            tab.setAttribute('data-category', category);
            tab.textContent = category;
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                document.querySelectorAll('.pos-category-tab').forEach(t => t.classList.remove('active'));
                // Add active class to clicked tab
                this.classList.add('active');
                // Filter products
                filterProducts(category);
            });
            categoryTabs.appendChild(tab);
        });
    }

    // Set "All" tab as active
    allTab.addEventListener('click', function() {
        // Remove active class from all tabs
        document.querySelectorAll('.pos-category-tab').forEach(t => t.classList.remove('active'));
        // Add active class to clicked tab
        this.classList.add('active');
        // Show all products
        filterProducts('all');
    });
    allTab.classList.add('active');
}

// Initialize products
function initProducts() {
    const productsGrid = document.getElementById('productsGrid');
    productsGrid.innerHTML = '';

    if (posData.products && posData.products.length > 0) {
        posData.products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'pos-product-card';
            card.setAttribute('data-product-id', product.id);
            card.setAttribute('data-category', product.category || 'uncategorized');

            // Generate random background color based on category
            const bgColors = {
                coffee: '#f0f9ff',
                tea: '#f0fdf4',
                desserts: '#fef2f2',
                snacks: '#fdf4ff',
                uncategorized: '#f9fafb'
            };

            const bgColor = bgColors[product.category] || bgColors.uncategorized;

            // Generate icon based on category
            const icons = {
                coffee: 'cup-line',
                tea: 'tea-cup-line',
                desserts: 'cake-3-line',
                snacks: 'sandwich-line',
                uncategorized: 'store-2-line'
            };

            const icon = icons[product.category] || icons.uncategorized;

            card.innerHTML = `
                <div class="pos-product-img" style="background-color: ${bgColor}">
                    ${product.image ? `<img src="${product.image}" alt="${product.name}">` : `<i class="ri-${icon} text-3xl"></i>`}
                </div>
                <div class="pos-product-info">
                    <h3 class="pos-product-name">${product.name}</h3>
                    <p class="pos-product-price">${product.price} ${posData.branch.currency || 'SAR'}</p>
                </div>
            `;

            // Add click event
            card.addEventListener('click', function() {
                addProductToOrder(product);
            });

            productsGrid.appendChild(card);
        });
    } else {
        productsGrid.innerHTML = `
            <div class="pos-empty-state">
                <i class="ri-shopping-basket-line text-5xl mb-2"></i>
                <p>${document.documentElement.lang === 'ar' ? 'لا توجد منتجات' : 'No products available'}</p>
            </div>
        `;
    }
}

// Filter products by category
function filterProducts(category) {
    const products = document.querySelectorAll('.pos-product-card');

    products.forEach(product => {
        if (category === 'all' || product.getAttribute('data-category') === category) {
            product.style.display = 'block';
        } else {
            product.style.display = 'none';
        }
    });
}

// Initialize event listeners
function initEventListeners() {
    // Search input
    const searchInput = document.getElementById('posSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const products = document.querySelectorAll('.pos-product-card');

            products.forEach(product => {
                const productName = product.querySelector('.pos-product-name').textContent.toLowerCase();

                if (productName.includes(searchTerm)) {
                    product.style.display = 'block';
                } else {
                    product.style.display = 'none';
                }
            });
        });
    }

    // Order type select
    const orderTypeSelect = document.getElementById('orderTypeSelect');
    if (orderTypeSelect) {
        orderTypeSelect.addEventListener('change', function() {
            currentOrder.type = this.value;
        });
    }

    // Client search
    const clientSearch = document.getElementById('clientSearch');
    if (clientSearch) {
        clientSearch.addEventListener('input', debounce(searchClients, 300));
    }

    // Checkout button
    const checkoutBtn = document.getElementById('checkoutBtn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            if (currentOrder.items.length === 0) {
                showToast(document.documentElement.lang === 'ar' ? 'أضف منتجات إلى الطلب أولاً' : 'Add products to order first', 'error');
                return;
            }

            if (!activeShift) {
                showToast(document.documentElement.lang === 'ar' ? 'يجب بدء وردية أولاً' : 'You must start a shift first', 'error');
                toggleShiftModal();
                return;
            }

            showCheckoutModal();
        });
    }

    // New order button
    const newOrderBtn = document.getElementById('newOrderBtn');
    if (newOrderBtn) {
        newOrderBtn.addEventListener('click', function() {
            if (currentOrder.items.length > 0) {
                if (confirm(document.documentElement.lang === 'ar' ? 'هل أنت متأكد من إنشاء طلب جديد؟ سيتم مسح الطلب الحالي.' : 'Are you sure you want to create a new order? Current order will be cleared.')) {
                    resetOrder();
                }
            } else {
                resetOrder();
            }
        });
    }

    // Fullscreen toggle
    const toggleFullscreenBtn = document.getElementById('toggleFullscreenBtn');
    if (toggleFullscreenBtn) {
        toggleFullscreenBtn.addEventListener('click', toggleFullscreen);
    }

    // Exit POS button
    const exitPosBtn = document.getElementById('exitPosBtn');
    if (exitPosBtn) {
        exitPosBtn.addEventListener('click', function() {
            if (currentOrder.items.length > 0) {
                if (confirm(document.documentElement.lang === 'ar' ? 'هل أنت متأكد من الخروج؟ سيتم فقدان الطلب الحالي.' : 'Are you sure you want to exit? Current order will be lost.')) {
                    window.location.href = '/dashboard';
                }
            } else {
                window.location.href = '/dashboard';
            }
        });
    }
}

// Add product to order
function addProductToOrder(product) {
    // Check if product is already in order
    const existingItemIndex = currentOrder.items.findIndex(item => item.product_id === product.id);

    if (existingItemIndex !== -1) {
        // Increment quantity
        currentOrder.items[existingItemIndex].quantity += 1;
        currentOrder.items[existingItemIndex].total_price = currentOrder.items[existingItemIndex].quantity * currentOrder.items[existingItemIndex].unit_price;
    } else {
        // Add new item
        currentOrder.items.push({
            product_id: product.id,
            name: product.name,
            unit_price: product.price,
            quantity: 1,
            total_price: product.price,
            notes: ''
        });
    }

    // Update order summary
    updateOrderSummary();

    // Show toast
    showToast(`${product.name} ${document.documentElement.lang === 'ar' ? 'تمت إضافته' : 'added to order'}`, 'success');
}

// Update order summary
function updateOrderSummary() {
    const orderItems = document.getElementById('orderItems');
    const emptyOrderMessage = document.getElementById('emptyOrderMessage');
    const subtotalElement = document.getElementById('subtotal');
    const taxElement = document.getElementById('tax');
    const totalElement = document.getElementById('total');

    // Calculate totals
    currentOrder.subtotal = currentOrder.items.reduce((sum, item) => sum + item.total_price, 0);
    currentOrder.tax = (currentOrder.subtotal * taxRate) / 100;
    currentOrder.total = currentOrder.subtotal + currentOrder.tax - currentOrder.discount;

    // Update order items
    if (currentOrder.items.length > 0) {
        // Hide empty message
        if (emptyOrderMessage) {
            emptyOrderMessage.style.display = 'none';
        }

        // Clear order items
        orderItems.innerHTML = '';

        // Add items
        currentOrder.items.forEach((item, index) => {
            const itemElement = document.createElement('div');
            itemElement.className = 'pos-order-item';
            itemElement.innerHTML = `
                <div class="pos-item-details">
                    <div class="pos-item-name">${item.name}</div>
                    <div class="pos-item-price">${item.unit_price} ${posData.branch.currency || 'SAR'}</div>
                    ${item.notes ? `<div class="pos-item-notes">${item.notes}</div>` : ''}
                </div>
                <div class="pos-item-quantity">
                    <button class="pos-qty-btn" onclick="decrementQuantity(${index})">-</button>
                    <span>${item.quantity}</span>
                    <button class="pos-qty-btn" onclick="incrementQuantity(${index})">+</button>
                </div>
                <div class="pos-item-total">${item.total_price.toFixed(2)} ${posData.branch.currency || 'SAR'}</div>
                <button class="pos-item-remove" onclick="removeItem(${index})">
                    <i class="ri-delete-bin-line"></i>
                </button>
            `;

            orderItems.appendChild(itemElement);
        });
    } else {
        // Show empty message
        if (emptyOrderMessage) {
            emptyOrderMessage.style.display = 'flex';
        }
    }

    // Update totals
    if (subtotalElement) {
        subtotalElement.textContent = `${currentOrder.subtotal.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    }

    if (taxElement) {
        taxElement.textContent = `${currentOrder.tax.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    }

    if (totalElement) {
        totalElement.textContent = `${currentOrder.total.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    }
}

// Increment item quantity
function incrementQuantity(index) {
    currentOrder.items[index].quantity += 1;
    currentOrder.items[index].total_price = currentOrder.items[index].quantity * currentOrder.items[index].unit_price;
    updateOrderSummary();
}

// Decrement item quantity
function decrementQuantity(index) {
    if (currentOrder.items[index].quantity > 1) {
        currentOrder.items[index].quantity -= 1;
        currentOrder.items[index].total_price = currentOrder.items[index].quantity * currentOrder.items[index].unit_price;
    } else {
        removeItem(index);
    }
    updateOrderSummary();
}

// Remove item from order
function removeItem(index) {
    currentOrder.items.splice(index, 1);
    updateOrderSummary();
}

// Generate order ID
function generateOrderId() {
    return 'ORD-' + Math.random().toString(36).substr(2, 9).toUpperCase();
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <i class="ri-${type === 'success' ? 'check-line' : type === 'error' ? 'error-warning-line' : 'information-line'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}
