/**
 * POS (Point of Sale) JavaScript for StockMaster Pro
 */

// Global variables
let currentOrder = {
    id: generateOrderId(),
    items: [],
    type: 'dine-in',
    customer: null,
    deliveryAddress: '',
    subtotal: 0,
    tax: 0,
    total: 0
};

let currentProductId = null;

// DOM Elements
const posContainer = document.getElementById('posContainer');
const productsGrid = document.getElementById('productsGrid');
const orderItems = document.getElementById('orderItems');
const subtotalElement = document.getElementById('subtotal');
const taxElement = document.getElementById('tax');
const totalElement = document.getElementById('total');
const checkoutModal = document.getElementById('checkoutModal');
const newOrderModal = document.getElementById('newOrderModal');
const quantityModal = document.getElementById('quantityModal');
const checkoutItems = document.getElementById('checkoutItems');
const checkoutSubtotal = document.getElementById('checkoutSubtotal');
const checkoutTax = document.getElementById('checkoutTax');
const checkoutTotal = document.getElementById('checkoutTotal');
const amountReceived = document.getElementById('amountReceived');
const changeAmount = document.getElementById('changeAmount');
const quantityInput = document.getElementById('quantityInput');
const quantityProductName = document.getElementById('quantityProductName');
const quantityProductPrice = document.getElementById('quantityProductPrice');
const productNotes = document.getElementById('productNotes');
const deliveryDetails = document.getElementById('deliveryDetails');
const deliveryAddress = document.getElementById('deliveryAddress');
const posSearch = document.getElementById('posSearch');

// Initialize POS
document.addEventListener('DOMContentLoaded', function() {
    // Load CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/css/pos.css';
    document.head.appendChild(link);

    // Initialize event listeners
    initEventListeners();

    // Initialize product cards
    initProductCards();

    // Initialize category tabs
    initCategoryTabs();

    // Initialize payment methods
    initPaymentMethods();

    // Initialize order types
    initOrderTypes();

    // Initialize search
    initSearch();

    // Update order summary
    updateOrderSummary();
});

// Initialize event listeners
function initEventListeners() {
    // Amount received input
    if (amountReceived) {
        amountReceived.addEventListener('input', calculateChange);
    }
}

// Initialize product cards
function initProductCards() {
    const productCards = document.querySelectorAll('.pos-product-card');

    productCards.forEach(card => {
        card.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const productName = this.querySelector('.pos-product-name').textContent;
            const productPrice = this.querySelector('.pos-product-price').textContent;

            // Set current product
            currentProductId = productId;

            // Update quantity modal
            quantityProductName.textContent = productName;
            quantityProductPrice.textContent = productPrice;
            quantityInput.value = 1;
            productNotes.value = '';

            // Show quantity modal
            showQuantityModal();
        });
    });
}

// Initialize category tabs
function initCategoryTabs() {
    const categoryTabs = document.querySelectorAll('.pos-category-tab');

    categoryTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            categoryTabs.forEach(t => t.classList.remove('active'));

            // Add active class to clicked tab
            this.classList.add('active');

            // Filter products
            const category = this.getAttribute('data-category');
            filterProducts(category);
        });
    });
}

// Filter products by category
function filterProducts(category) {
    const productCards = document.querySelectorAll('.pos-product-card');

    productCards.forEach(card => {
        if (category === 'all' || card.getAttribute('data-category') === category) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Initialize payment methods
function initPaymentMethods() {
    const paymentMethods = document.querySelectorAll('.payment-method');

    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            // Remove active class from all methods
            paymentMethods.forEach(m => m.classList.remove('active'));

            // Add active class to clicked method
            this.classList.add('active');

            // Update payment method
            currentOrder.paymentMethod = this.getAttribute('data-method');
        });
    });
}

// Initialize order types
function initOrderTypes() {
    const orderTypes = document.querySelectorAll('.order-type');

    orderTypes.forEach(type => {
        type.addEventListener('click', function() {
            // Remove active class from all types
            orderTypes.forEach(t => t.classList.remove('active'));

            // Add active class to clicked type
            this.classList.add('active');

            // Update order type
            const orderType = this.getAttribute('data-type');
            currentOrder.type = orderType;

            // Show/hide delivery details
            if (orderType === 'delivery') {
                deliveryDetails.classList.remove('hidden');
            } else {
                deliveryDetails.classList.add('hidden');
            }
        });
    });
}

// Initialize search
function initSearch() {
    posSearch.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const productCards = document.querySelectorAll('.pos-product-card');

        productCards.forEach(card => {
            const productName = card.querySelector('.pos-product-name').textContent.toLowerCase();

            if (productName.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// Show checkout modal
function showCheckoutModal() {
    if (currentOrder.items.length === 0) {
        showToast('Please add items to the order', 'error');
        return;
    }

    // Update checkout items
    updateCheckoutItems();

    // Show modal
    checkoutModal.classList.add('show');
}

// Hide checkout modal
function hideCheckoutModal() {
    checkoutModal.classList.remove('show');
}

// Show new order modal
function showNewOrderModal() {
    newOrderModal.classList.add('show');
}

// Hide new order modal
function hideNewOrderModal() {
    newOrderModal.classList.remove('show');
}

// Show quantity modal
function showQuantityModal() {
    quantityModal.classList.add('show');
}

// Hide quantity modal
function hideQuantityModal() {
    quantityModal.classList.remove('show');
}

// Update checkout items
function updateCheckoutItems() {
    // Clear checkout items
    checkoutItems.innerHTML = '';

    // Add items to checkout
    currentOrder.items.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'checkout-item';

        itemElement.innerHTML = `
            <div class="checkout-item-name">
                <span class="checkout-item-quantity">${item.quantity}</span>
                <span>${item.name}</span>
            </div>
            <div>${item.total} ${item.currency}</div>
        `;

        checkoutItems.appendChild(itemElement);
    });

    // Update totals
    checkoutSubtotal.textContent = `${currentOrder.subtotal} ${currentOrder.items[0]?.currency || 'SAR'}`;
    checkoutTax.textContent = `${currentOrder.tax} ${currentOrder.items[0]?.currency || 'SAR'}`;
    checkoutTotal.textContent = `${currentOrder.total} ${currentOrder.items[0]?.currency || 'SAR'}`;
}

// Calculate change
function calculateChange() {
    const received = parseFloat(amountReceived.value) || 0;
    const total = currentOrder.total;
    const change = received - total;

    changeAmount.value = change >= 0 ? `${change.toFixed(2)} ${currentOrder.items[0]?.currency || 'SAR'}` : '';
}

// Add to order
function addToOrder() {
    const quantity = parseInt(quantityInput.value) || 1;
    const notes = productNotes.value;

    // Get product details
    const productCard = document.querySelector(`.pos-product-card[data-product-id="${currentProductId}"]`);
    const productName = productCard.querySelector('.pos-product-name').textContent;
    const productPriceText = productCard.querySelector('.pos-product-price').textContent;
    const productPriceParts = productPriceText.split(' ');
    const productPrice = parseFloat(productPriceParts[0]);
    const currency = productPriceParts[1] || 'SAR';

    // Create item object
    const item = {
        id: currentProductId,
        name: productName,
        price: productPrice,
        quantity: quantity,
        notes: notes,
        total: productPrice * quantity,
        currency: currency
    };

    // Add to order
    currentOrder.items.push(item);

    // Update order summary
    updateOrderSummary();

    // Hide quantity modal
    hideQuantityModal();

    // Show success message
    showToast(`${productName} added to order`, 'success');
}

// Update order summary
function updateOrderSummary() {
    // Clear order items
    orderItems.innerHTML = '';

    if (currentOrder.items.length === 0) {
        // Show empty message
        const emptyElement = document.createElement('div');
        emptyElement.className = 'pos-order-empty';

        emptyElement.innerHTML = `
            <i class="ri-shopping-cart-line text-4xl mb-2"></i>
            <p>${document.documentElement.lang === 'ar' ? 'لا توجد منتجات في السلة' : 'No items in cart'}</p>
        `;

        orderItems.appendChild(emptyElement);

        // Update totals
        subtotalElement.textContent = `0 ${document.documentElement.lang === 'ar' ? 'ريال' : 'SAR'}`;
        taxElement.textContent = `0 ${document.documentElement.lang === 'ar' ? 'ريال' : 'SAR'}`;
        totalElement.textContent = `0 ${document.documentElement.lang === 'ar' ? 'ريال' : 'SAR'}`;

        return;
    }

    // Calculate totals
    let subtotal = 0;

    // Add items to order
    currentOrder.items.forEach((item, index) => {
        subtotal += item.total;

        const itemElement = document.createElement('div');
        itemElement.className = 'pos-order-item';

        itemElement.innerHTML = `
            <div class="pos-item-details">
                <div class="pos-item-name">${item.name}</div>
                <div class="pos-item-price">${item.price} ${item.currency} x ${item.quantity}</div>
                ${item.notes ? `<div class="pos-item-notes">${item.notes}</div>` : ''}
            </div>
            <div class="pos-item-total">${item.total} ${item.currency}</div>
        `;

        orderItems.appendChild(itemElement);
    });

    // Calculate tax and total
    const tax = subtotal * 0.15; // 15% tax
    const total = subtotal + tax;

    // Update order object
    currentOrder.subtotal = subtotal;
    currentOrder.tax = tax;
    currentOrder.total = total;

    // Update totals
    const currency = currentOrder.items[0]?.currency || 'SAR';
    subtotalElement.textContent = `${subtotal.toFixed(2)} ${currency}`;
    taxElement.textContent = `${tax.toFixed(2)} ${currency}`;
    totalElement.textContent = `${total.toFixed(2)} ${currency}`;
}

// Clear order
function clearOrder() {
    // Confirm clear
    if (!confirm(document.documentElement.lang === 'ar' ? 'هل أنت متأكد من مسح الطلب؟' : 'Are you sure you want to clear the order?')) {
        return;
    }

    // Clear order
    currentOrder.items = [];

    // Update order summary
    updateOrderSummary();

    // Show success message
    showToast(document.documentElement.lang === 'ar' ? 'تم مسح الطلب' : 'Order cleared', 'success');
}

// Complete order
function completeOrder() {
    // Validate payment
    const received = parseFloat(amountReceived.value) || 0;

    if (received < currentOrder.total && currentOrder.paymentMethod === 'cash') {
        showToast(document.documentElement.lang === 'ar' ? 'المبلغ المستلم أقل من إجمالي الطلب' : 'Amount received is less than total', 'error');
        return;
    }

    // TODO: Send order to server

    // Show success message
    showToast(document.documentElement.lang === 'ar' ? 'تم إتمام الطلب بنجاح' : 'Order completed successfully', 'success');

    // Hide checkout modal
    hideCheckoutModal();

    // Clear order
    currentOrder.items = [];
    currentOrder.id = generateOrderId();

    // Update order summary
    updateOrderSummary();
}

// Start new order
function startNewOrder() {
    // Get customer
    const customerSelect = document.getElementById('customerSelect');
    const customerId = customerSelect.value;

    // Get delivery address
    const address = deliveryAddress.value;

    // Validate delivery address
    if (currentOrder.type === 'delivery' && !address) {
        showToast(document.documentElement.lang === 'ar' ? 'يرجى إدخال عنوان التوصيل' : 'Please enter delivery address', 'error');
        return;
    }

    // Update order
    currentOrder.customer = customerId;
    currentOrder.deliveryAddress = address;

    // Hide new order modal
    hideNewOrderModal();

    // Show success message
    showToast(document.documentElement.lang === 'ar' ? 'تم بدء طلب جديد' : 'New order started', 'success');
}

// Increment quantity
function incrementQuantity() {
    const currentValue = parseInt(quantityInput.value) || 0;
    quantityInput.value = currentValue + 1;
}

// Decrement quantity
function decrementQuantity() {
    const currentValue = parseInt(quantityInput.value) || 0;
    if (currentValue > 1) {
        quantityInput.value = currentValue - 1;
    }
}

// Toggle fullscreen
function toggleFullscreen() {
    posContainer.classList.toggle('pos-fullscreen');
}

// Exit POS mode
function exitPosMode() {
    // Confirm exit if there are items in the order
    if (currentOrder.items.length > 0) {
        if (!confirm(document.documentElement.lang === 'ar' ? 'هناك طلب قيد التقدم. هل أنت متأكد من الخروج؟' : 'There is an order in progress. Are you sure you want to exit?')) {
            return;
        }
    }

    // Redirect to dashboard
    window.location.href = '/dashboard';
}

// Generate order ID
function generateOrderId() {
    return Math.floor(10000 + Math.random() * 90000);
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');

    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    toast.innerHTML = `
        <div class="toast-icon">
            <i class="ri-${type === 'error' ? 'error-warning' : type === 'success' ? 'check-line' : 'information-line'}"></i>
        </div>
        <div class="toast-content">${message}</div>
        <button class="toast-close" onclick="this.parentNode.remove()">
            <i class="ri-close-line"></i>
        </button>
    `;

    toastContainer.appendChild(toast);

    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}
