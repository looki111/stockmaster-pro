// StockMaster Pro - Main JavaScript File

// Initialize AOS (Animate On Scroll)
document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
});

// --- THEME & LANGUAGE ---
// Note: These functions are now imported from main.js
// This section is kept for backward compatibility
// but all functionality is delegated to main.js

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Apply theme and language using main.js functions
    if (typeof window.StockMaster !== 'undefined') {
        if (typeof window.StockMaster.applyThemeOnLoad === 'function') {
            window.StockMaster.applyThemeOnLoad();
        }

        if (typeof window.StockMaster.applyLangOnLoad === 'function') {
            window.StockMaster.applyLangOnLoad();
        }
    } else {
        console.error('StockMaster object not found. Make sure main.js is loaded before app.js');
    }

    // Initialize any components that need setup
    initSidebar();
    initUserMenu();
});

// --- SIDEBAR & MOBILE ---
function initSidebar() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => toggleSidebar());
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', () => toggleSidebar(false));
    }
}

function toggleSidebar(force) {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (!sidebar || !backdrop) return;

    if (typeof force === 'boolean') {
        sidebar.classList.toggle('open', force);
        backdrop.style.display = force ? 'block' : 'none';
    } else {
        sidebar.classList.toggle('open');
        backdrop.style.display = sidebar.classList.contains('open') ? 'block' : 'none';
    }
}

// --- USER MENU ---
function initUserMenu() {
    document.addEventListener('click', function(event) {
        const menu = document.getElementById('userMenu');
        if (!menu) return;

        const button = event.target.closest('button[onclick="toggleUserMenu()"]');

        if (!button && !menu.contains(event.target)) {
            menu.classList.add('hidden');
        }
    });
}

function toggleUserMenu() {
    const menu = document.getElementById('userMenu');
    if (menu) {
        menu.classList.toggle('hidden');
    }
}

// --- TOAST NOTIFICATIONS ---
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type} animate-fade-in`;
    toast.innerHTML = `<span>${message}</span>`;

    const container = document.getElementById('toastContainer');
    if (container) {
        container.appendChild(toast);
    } else {
        document.body.appendChild(toast);
    }

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// --- SHOW/HIDE PASSWORD ---
function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input || !btn) return;

    const icon = btn.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        if (icon) {
            icon.classList.remove('ri-eye-line');
            icon.classList.add('ri-eye-off-line');
        }
    } else {
        input.type = 'password';
        if (icon) {
            icon.classList.remove('ri-eye-off-line');
            icon.classList.add('ri-eye-line');
        }
    }
}

// --- FORM VALIDATION ---
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const requiredInputs = form.querySelectorAll('[required]');
    let isValid = true;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('border-red-500');
            isValid = false;
        } else {
            input.classList.remove('border-red-500');
        }
    });

    if (!isValid) {
        form.classList.add('animate-shake');
        setTimeout(() => form.classList.remove('animate-shake'), 500);
    }

    return isValid;
}

// --- RESPONSIVE DESIGN ---
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (window.innerWidth >= 900) {
        if (sidebar) sidebar.classList.remove('open');
        if (backdrop) backdrop.style.display = 'none';
    }
});

// --- ANIMATIONS ---
document.addEventListener('DOMContentLoaded', function() {
    const fadeElements = document.querySelectorAll('.animate-fade-in');
    fadeElements.forEach(el => {
        el.style.opacity = '0';
        setTimeout(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100);
    });
});

// --- EXPORT UTILITIES ---
window.StockMaster = {
    showToast,
    toggleSidebar,
    toggleUserMenu,
    togglePassword,
    validateForm
};

// API Request Handler
class API {
    static async request(endpoint, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };

        try {
            const response = await fetch(endpoint, { ...defaultOptions, ...options });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'An error occurred');
            }

            return data;
        } catch (error) {
            showToast(error.message, 'error');
            throw error;
        }
    }
}

// Data Table Handler
class DataTable {
    constructor(table, options = {}) {
        this.table = table;
        this.options = {
            searchable: true,
            sortable: true,
            pagination: true,
            perPage: 10,
            ...options
        };

        this.init();
    }

    init() {
        if (this.options.searchable) {
            this.addSearch();
        }

        if (this.options.sortable) {
            this.addSorting();
        }

        if (this.options.pagination) {
            this.addPagination();
        }
    }

    addSearch() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'mb-4';
        searchContainer.innerHTML = `
            <input type="text"
                   class="custom-input w-full"
                   placeholder="Search..."
                   data-table-search>
        `;

        this.table.parentElement.insertBefore(searchContainer, this.table);

        const searchInput = searchContainer.querySelector('input');
        searchInput.addEventListener('input', (e) => this.filterTable(e.target.value));
    }

    filterTable(query) {
        const rows = this.table.querySelectorAll('tbody tr');
        const searchTerm = query.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    addSorting() {
        const headers = this.table.querySelectorAll('th[data-sort]');

        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => this.sortTable(header));
        });
    }

    sortTable(header) {
        const index = Array.from(header.parentElement.children).indexOf(header);
        const rows = Array.from(this.table.querySelectorAll('tbody tr'));
        const direction = header.getAttribute('data-direction') === 'asc' ? -1 : 1;

        rows.sort((a, b) => {
            const aValue = a.children[index].textContent;
            const bValue = b.children[index].textContent;
            return direction * aValue.localeCompare(bValue);
        });

        header.setAttribute('data-direction', direction === 1 ? 'asc' : 'desc');

        const tbody = this.table.querySelector('tbody');
        rows.forEach(row => tbody.appendChild(row));
    }

    addPagination() {
        const rows = this.table.querySelectorAll('tbody tr');
        const totalPages = Math.ceil(rows.length / this.options.perPage);

        const paginationContainer = document.createElement('div');
        paginationContainer.className = 'flex justify-center mt-4';
        paginationContainer.innerHTML = this.createPaginationHTML(totalPages);

        this.table.parentElement.appendChild(paginationContainer);

        this.showPage(1);

        paginationContainer.addEventListener('click', (e) => {
            if (e.target.matches('[data-page]')) {
                const page = parseInt(e.target.dataset.page);
                this.showPage(page);
            }
        });
    }

    createPaginationHTML(totalPages) {
        let html = '<div class="flex space-x-2">';

        for (let i = 1; i <= totalPages; i++) {
            html += `
                <button class="px-3 py-1 rounded-md bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700"
                        data-page="${i}">
                    ${i}
                </button>
            `;
        }

        html += '</div>';
        return html;
    }

    showPage(page) {
        const rows = this.table.querySelectorAll('tbody tr');
        const start = (page - 1) * this.options.perPage;
        const end = start + this.options.perPage;

        rows.forEach((row, index) => {
            row.style.display = index >= start && index < end ? '' : 'none';
        });
    }
}

// Initialize DataTables
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-table]').forEach(table => {
        new DataTable(table);
    });
});

// Real-time Updates
class RealTimeUpdates {
    constructor() {
        this.socket = null;
        this.initializeWebSocket();
    }

    initializeWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleUpdate(data);
        };

        this.socket.onclose = () => {
            setTimeout(() => this.initializeWebSocket(), 1000);
        };
    }

    handleUpdate(data) {
        switch (data.type) {
            case 'order':
                this.updateOrderStatus(data);
                break;
            case 'inventory':
                this.updateInventoryLevel(data);
                break;
            case 'notification':
                showToast(data.message, data.level);
                break;
        }
    }

    updateOrderStatus(data) {
        const orderElement = document.querySelector(`[data-order-id="${data.orderId}"]`);
        if (orderElement) {
            orderElement.querySelector('.status-badge').textContent = data.status;
            orderElement.querySelector('.status-badge').className =
                `status-badge status-${data.status.toLowerCase()}`;
        }
    }

    updateInventoryLevel(data) {
        const inventoryElement = document.querySelector(`[data-product-id="${data.productId}"]`);
        if (inventoryElement) {
            inventoryElement.querySelector('.quantity').textContent = data.quantity;

            if (data.quantity <= data.lowStockThreshold) {
                showToast(`Low stock alert: ${data.productName}`, 'warning');
            }
        }
    }
}

// Initialize Real-time Updates
const realTimeUpdates = new RealTimeUpdates();

// Export utilities
window.StockMaster = {
    ...window.StockMaster,
    API,
    DataTable,
    RealTimeUpdates
};