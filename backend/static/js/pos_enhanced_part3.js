/**
 * Enhanced POS (Point of Sale) JavaScript for StockMaster Pro - Part 3
 * Contains utility functions and modal management
 */

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

function toggleFullscreen() {
    const posContainer = document.getElementById('posContainer');
    
    if (!document.fullscreenElement) {
        // Enter fullscreen
        if (posContainer.requestFullscreen) {
            posContainer.requestFullscreen();
        } else if (posContainer.mozRequestFullScreen) { /* Firefox */
            posContainer.mozRequestFullScreen();
        } else if (posContainer.webkitRequestFullscreen) { /* Chrome, Safari & Opera */
            posContainer.webkitRequestFullscreen();
        } else if (posContainer.msRequestFullscreen) { /* IE/Edge */
            posContainer.msRequestFullscreen();
        }
        
        document.getElementById('toggleFullscreenBtn').innerHTML = '<i class="ri-fullscreen-exit-line"></i>';
    } else {
        // Exit fullscreen
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { /* Firefox */
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { /* Chrome, Safari & Opera */
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { /* IE/Edge */
            document.msExitFullscreen();
        }
        
        document.getElementById('toggleFullscreenBtn').innerHTML = '<i class="ri-fullscreen-line"></i>';
    }
}

function resetOrder() {
    // Reset order data
    currentOrder = {
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
    
    // Reset selected client
    selectedClient = null;
    
    // Update UI
    document.getElementById('selectedClientName').textContent = document.documentElement.lang === 'ar' ? 'اختر العميل' : 'Select Customer';
    document.getElementById('orderClientName').textContent = document.documentElement.lang === 'ar' ? 'عميل عادي' : 'Walk-in Customer';
    document.getElementById('orderNumberValue').textContent = currentOrder.id.replace('ORD-', '');
    document.getElementById('orderTypeSelect').value = 'dine_in';
    
    // Update order summary
    updateOrderSummary();
    
    // Show toast
    showToast(document.documentElement.lang === 'ar' ? 'تم إنشاء طلب جديد' : 'New order created', 'success');
}

function updateShiftUI(isActive) {
    const shiftBtn = document.getElementById('shiftBtn');
    const shiftBtnText = document.getElementById('shiftBtnText');
    
    if (isActive) {
        shiftBtn.classList.remove('btn-primary');
        shiftBtn.classList.add('btn-success');
        shiftBtnText.textContent = document.documentElement.lang === 'ar' ? 'الوردية نشطة' : 'Shift Active';
    } else {
        shiftBtn.classList.remove('btn-success');
        shiftBtn.classList.add('btn-primary');
        shiftBtnText.textContent = document.documentElement.lang === 'ar' ? 'بدء الوردية' : 'Start Shift';
    }
}

function checkActiveShift() {
    if (posData && posData.shift && posData.shift.active) {
        activeShift = {
            id: posData.shift.id,
            start_time: posData.shift.start_time,
            initial_cash: posData.shift.initial_cash,
            total_sales: posData.shift.total_sales || 0,
            total_orders: posData.shift.total_orders || 0
        };
        updateShiftUI(true);
    } else {
        activeShift = null;
        updateShiftUI(false);
    }
}

// Modal management functions
function showClientModal() {
    document.getElementById('clientModal').style.display = 'flex';
    document.getElementById('clientSearch').focus();
    
    // Load recent clients
    if (posData && posData.recent_clients) {
        displayClientSearchResults(posData.recent_clients);
    }
}

function hideClientModal() {
    document.getElementById('clientModal').style.display = 'none';
}

function showAddClientForm() {
    document.getElementById('addClientForm').style.display = 'block';
    document.getElementById('newClientName').focus();
}

function hideAddClientForm() {
    document.getElementById('addClientForm').style.display = 'none';
}

function showNewOrderModal() {
    document.getElementById('newOrderModal').style.display = 'flex';
}

function hideNewOrderModal() {
    document.getElementById('newOrderModal').style.display = 'none';
}

// Apply discount
function applyDiscount() {
    const discountType = document.getElementById('discountType').value;
    const discountValue = parseFloat(document.getElementById('discountValue').value);
    
    if (isNaN(discountValue) || discountValue <= 0) {
        showToast(document.documentElement.lang === 'ar' ? 'أدخل قيمة خصم صالحة' : 'Enter a valid discount value', 'error');
        return;
    }
    
    if (discountType === 'percentage') {
        if (discountValue > 100) {
            showToast(document.documentElement.lang === 'ar' ? 'نسبة الخصم لا يمكن أن تتجاوز 100%' : 'Discount percentage cannot exceed 100%', 'error');
            return;
        }
        
        currentOrder.discount = (currentOrder.subtotal * discountValue) / 100;
    } else {
        if (discountValue > currentOrder.subtotal) {
            showToast(document.documentElement.lang === 'ar' ? 'قيمة الخصم لا يمكن أن تتجاوز المجموع الفرعي' : 'Discount amount cannot exceed subtotal', 'error');
            return;
        }
        
        currentOrder.discount = discountValue;
    }
    
    // Update total
    currentOrder.total = currentOrder.subtotal + currentOrder.tax - currentOrder.discount;
    
    // Update UI
    updateOrderSummary();
    
    // Show toast
    showToast(document.documentElement.lang === 'ar' ? 'تم تطبيق الخصم' : 'Discount applied', 'success');
    
    // Hide discount modal
    hideDiscountModal();
}

function removeDiscount() {
    currentOrder.discount = 0;
    currentOrder.total = currentOrder.subtotal + currentOrder.tax;
    
    // Update UI
    updateOrderSummary();
    
    // Show toast
    showToast(document.documentElement.lang === 'ar' ? 'تم إزالة الخصم' : 'Discount removed', 'success');
}

function showDiscountModal() {
    document.getElementById('discountModal').style.display = 'flex';
    document.getElementById('discountValue').focus();
}

function hideDiscountModal() {
    document.getElementById('discountModal').style.display = 'none';
}

// Table selection
function selectTable(tableNumber) {
    currentOrder.table_number = tableNumber;
    
    // Update UI
    document.getElementById('selectedTable').textContent = tableNumber;
    
    // Hide table modal
    hideTableModal();
    
    // Show toast
    showToast(`${document.documentElement.lang === 'ar' ? 'تم اختيار الطاولة' : 'Table selected'}: ${tableNumber}`, 'success');
}

function showTableModal() {
    document.getElementById('tableModal').style.display = 'flex';
}

function hideTableModal() {
    document.getElementById('tableModal').style.display = 'none';
}

// Delivery address
function setDeliveryAddress() {
    const address = document.getElementById('deliveryAddress').value;
    
    if (!address) {
        showToast(document.documentElement.lang === 'ar' ? 'أدخل عنوان التوصيل' : 'Enter delivery address', 'error');
        return;
    }
    
    currentOrder.delivery_address = address;
    
    // Hide delivery modal
    hideDeliveryModal();
    
    // Show toast
    showToast(document.documentElement.lang === 'ar' ? 'تم تعيين عنوان التوصيل' : 'Delivery address set', 'success');
}

function showDeliveryModal() {
    document.getElementById('deliveryModal').style.display = 'flex';
    document.getElementById('deliveryAddress').focus();
}

function hideDeliveryModal() {
    document.getElementById('deliveryModal').style.display = 'none';
}

// Order type selection
function selectOrderType(type) {
    currentOrder.type = type;
    
    // Update UI
    document.getElementById('orderTypeSelect').value = type;
    
    // Show relevant modals based on order type
    if (type === 'dine_in') {
        showTableModal();
    } else if (type === 'delivery') {
        showDeliveryModal();
    }
    
    // Hide new order modal
    hideNewOrderModal();
}
