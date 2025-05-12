/**
 * Enhanced POS (Point of Sale) JavaScript for StockMaster Pro - Part 2
 * Contains client management, checkout, and shift management functions
 */

// Client management functions
async function searchClients(event) {
    const searchTerm = event.target.value;
    if (searchTerm.length < 2) return;
    
    try {
        const response = await fetch(`/pos/clients?search=${encodeURIComponent(searchTerm)}`);
        if (!response.ok) {
            throw new Error('Failed to search clients');
        }
        
        const clients = await response.json();
        displayClientSearchResults(clients);
    } catch (error) {
        console.error('Error searching clients:', error);
        showToast(error.message, 'error');
    }
}

function displayClientSearchResults(clients) {
    const clientList = document.getElementById('clientList');
    clientList.innerHTML = '';
    
    if (clients.length === 0) {
        clientList.innerHTML = `
            <div class="pos-empty-state">
                <i class="ri-user-search-line text-3xl mb-2"></i>
                <p>${document.documentElement.lang === 'ar' ? 'لا توجد نتائج' : 'No results found'}</p>
            </div>
        `;
        return;
    }
    
    clients.forEach(client => {
        const clientItem = document.createElement('div');
        clientItem.className = 'client-item';
        clientItem.innerHTML = `
            <div class="client-info">
                <div class="client-name">${client.name}</div>
                <div class="client-details">
                    ${client.phone ? `<span><i class="ri-phone-line"></i> ${client.phone}</span>` : ''}
                    ${client.email ? `<span><i class="ri-mail-line"></i> ${client.email}</span>` : ''}
                </div>
            </div>
            <div class="client-loyalty">
                <i class="ri-award-line"></i>
                <span>${client.loyalty_points || 0}</span>
            </div>
        `;
        
        clientItem.addEventListener('click', function() {
            selectClient(client);
        });
        
        clientList.appendChild(clientItem);
    });
}

function selectClient(client) {
    selectedClient = client;
    currentOrder.client_id = client.id;
    
    // Update UI
    document.getElementById('selectedClientName').textContent = client.name;
    document.getElementById('orderClientName').textContent = client.name;
    
    // Hide client modal
    hideClientModal();
    
    // Show toast
    showToast(`${document.documentElement.lang === 'ar' ? 'تم اختيار العميل' : 'Customer selected'}: ${client.name}`, 'success');
}

async function addNewClient() {
    const name = document.getElementById('newClientName').value;
    const phone = document.getElementById('newClientPhone').value;
    const email = document.getElementById('newClientEmail').value;
    const notes = document.getElementById('newClientNotes').value;
    
    if (!name) {
        showToast(document.documentElement.lang === 'ar' ? 'الاسم مطلوب' : 'Name is required', 'error');
        return;
    }
    
    try {
        const response = await fetch('/pos/client/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                phone,
                email,
                notes
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to add client');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Select the new client
            selectClient(result.client);
            
            // Reset form
            document.getElementById('newClientName').value = '';
            document.getElementById('newClientPhone').value = '';
            document.getElementById('newClientEmail').value = '';
            document.getElementById('newClientNotes').value = '';
            
            // Hide add client form
            hideAddClientForm();
            
            // Show toast
            showToast(document.documentElement.lang === 'ar' ? 'تمت إضافة العميل بنجاح' : 'Client added successfully', 'success');
        } else {
            throw new Error(result.error || 'Failed to add client');
        }
    } catch (error) {
        console.error('Error adding client:', error);
        showToast(error.message, 'error');
    }
}

// Checkout functions
function showCheckoutModal() {
    // Update checkout items
    updateCheckoutItems();
    
    // Show modal
    document.getElementById('checkoutModal').style.display = 'flex';
}

function hideCheckoutModal() {
    document.getElementById('checkoutModal').style.display = 'none';
}

function updateCheckoutItems() {
    const checkoutItems = document.getElementById('checkoutItems');
    const checkoutSubtotal = document.getElementById('checkoutSubtotal');
    const checkoutTax = document.getElementById('checkoutTax');
    const checkoutTotal = document.getElementById('checkoutTotal');
    const discountRow = document.getElementById('discountRow');
    const checkoutDiscount = document.getElementById('checkoutDiscount');
    
    // Clear checkout items
    checkoutItems.innerHTML = '';
    
    // Add items
    currentOrder.items.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'checkout-item';
        itemElement.innerHTML = `
            <div class="checkout-item-name">
                <span>${item.name}</span>
                <span class="checkout-item-qty">x${item.quantity}</span>
            </div>
            <div class="checkout-item-price">${item.total_price.toFixed(2)} ${posData.branch.currency || 'SAR'}</div>
        `;
        
        checkoutItems.appendChild(itemElement);
    });
    
    // Update totals
    checkoutSubtotal.textContent = `${currentOrder.subtotal.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    checkoutTax.textContent = `${currentOrder.tax.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    checkoutTotal.textContent = `${currentOrder.total.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    
    // Show/hide discount row
    if (currentOrder.discount > 0) {
        discountRow.style.display = 'flex';
        checkoutDiscount.textContent = `${currentOrder.discount.toFixed(2)} ${posData.branch.currency || 'SAR'}`;
    } else {
        discountRow.style.display = 'none';
    }
}

async function processPayment(paymentMethod) {
    try {
        // Prepare order data
        const orderData = {
            items: currentOrder.items,
            subtotal: currentOrder.subtotal,
            tax: currentOrder.tax,
            total: currentOrder.total,
            discount: currentOrder.discount,
            payment_method: paymentMethod,
            client_id: currentOrder.client_id,
            customer_name: selectedClient ? selectedClient.name : null,
            order_type: currentOrder.type,
            table_number: currentOrder.table_number,
            delivery_address: currentOrder.delivery_address,
            notes: currentOrder.notes
        };
        
        // Send order to server
        const response = await fetch('/pos/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to process order');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Hide checkout modal
            hideCheckoutModal();
            
            // Show success message
            showToast(document.documentElement.lang === 'ar' ? 'تم إنشاء الطلب بنجاح' : 'Order created successfully', 'success');
            
            // Reset order
            resetOrder();
            
            // Update shift data if active
            if (activeShift) {
                activeShift.total_sales += orderData.total;
                activeShift.total_orders += 1;
                updateShiftUI(true);
            }
            
            // Print receipt if needed
            if (result.invoice_path) {
                // Open invoice in new tab
                window.open(result.invoice_path, '_blank');
            }
        } else {
            throw new Error(result.error || 'Failed to process order');
        }
    } catch (error) {
        console.error('Error processing payment:', error);
        showToast(error.message, 'error');
    }
}

// Shift management functions
function toggleShiftModal() {
    const shiftModal = document.getElementById('shiftModal');
    const startShiftForm = document.getElementById('startShiftForm');
    const endShiftForm = document.getElementById('endShiftForm');
    const shiftModalTitle = document.getElementById('shiftModalTitle');
    
    if (activeShift) {
        // Show end shift form
        startShiftForm.style.display = 'none';
        endShiftForm.style.display = 'block';
        shiftModalTitle.textContent = document.documentElement.lang === 'ar' ? 'إنهاء الوردية' : 'End Shift';
        
        // Update shift summary
        document.getElementById('shiftStartTime').textContent = new Date(activeShift.start_time).toLocaleTimeString();
        document.getElementById('shiftInitialCash').textContent = `${activeShift.initial_cash} ${posData.branch.currency || 'SAR'}`;
        document.getElementById('shiftTotalSales').textContent = `${activeShift.total_sales} ${posData.branch.currency || 'SAR'}`;
        document.getElementById('shiftOrderCount').textContent = activeShift.total_orders;
        
        // Set suggested final cash
        document.getElementById('finalCash').value = (parseFloat(activeShift.initial_cash) + parseFloat(activeShift.total_sales)).toFixed(2);
    } else {
        // Show start shift form
        startShiftForm.style.display = 'block';
        endShiftForm.style.display = 'none';
        shiftModalTitle.textContent = document.documentElement.lang === 'ar' ? 'بدء الوردية' : 'Start Shift';
    }
    
    shiftModal.style.display = 'flex';
}

function hideShiftModal() {
    document.getElementById('shiftModal').style.display = 'none';
}

async function startShift() {
    const initialCash = document.getElementById('initialCash').value;
    const notes = document.getElementById('startShiftNotes').value;
    
    if (!initialCash) {
        showToast(document.documentElement.lang === 'ar' ? 'المبلغ الافتتاحي مطلوب' : 'Opening amount is required', 'error');
        return;
    }
    
    try {
        const response = await fetch('/pos/shift/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                initial_cash: parseFloat(initialCash),
                notes
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to start shift');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Update active shift
            activeShift = {
                id: result.shift.id,
                start_time: result.shift.start_time,
                initial_cash: parseFloat(initialCash),
                total_sales: 0,
                total_orders: 0
            };
            
            // Update UI
            updateShiftUI(true);
            
            // Hide modal
            hideShiftModal();
            
            // Show toast
            showToast(document.documentElement.lang === 'ar' ? 'تم بدء الوردية بنجاح' : 'Shift started successfully', 'success');
        } else {
            throw new Error(result.error || 'Failed to start shift');
        }
    } catch (error) {
        console.error('Error starting shift:', error);
        showToast(error.message, 'error');
    }
}

async function endShift() {
    const finalCash = document.getElementById('finalCash').value;
    const notes = document.getElementById('endShiftNotes').value;
    
    if (!finalCash) {
        showToast(document.documentElement.lang === 'ar' ? 'المبلغ النهائي مطلوب' : 'Closing amount is required', 'error');
        return;
    }
    
    try {
        const response = await fetch('/pos/shift/end', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                final_cash: parseFloat(finalCash),
                notes
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to end shift');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Clear active shift
            activeShift = null;
            
            // Update UI
            updateShiftUI(false);
            
            // Hide modal
            hideShiftModal();
            
            // Show toast
            showToast(document.documentElement.lang === 'ar' ? 'تم إنهاء الوردية بنجاح' : 'Shift ended successfully', 'success');
        } else {
            throw new Error(result.error || 'Failed to end shift');
        }
    } catch (error) {
        console.error('Error ending shift:', error);
        showToast(error.message, 'error');
    }
}
