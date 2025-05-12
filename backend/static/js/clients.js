// Search functionality
const searchInput = document.getElementById('searchInput');
const clientList = document.getElementById('clientList');

if (searchInput && clientList) {
    searchInput.addEventListener('input', debounce(async (e) => {
        const query = e.target.value.trim();
        if (query.length < 2) {
            // Show all clients if search query is too short
            const clients = await fetch('/clients/search').then(res => res.json());
            updateClientList(clients);
            return;
        }

        const clients = await fetch(`/clients/search?q=${encodeURIComponent(query)}`).then(res => res.json());
        updateClientList(clients);
    }, 300));
}

// Sort functionality
const sortSelect = document.getElementById('sortSelect');
if (sortSelect) {
    sortSelect.addEventListener('change', async () => {
        const clients = await fetch('/clients/search').then(res => res.json());
        const sortBy = sortSelect.value;
        
        clients.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'points':
                    return b.loyalty_points - a.loyalty_points;
                case 'spent':
                    return b.total_spent - a.total_spent;
                default:
                    return 0;
            }
        });

        updateClientList(clients);
    });
}

// Update client list in the DOM
function updateClientList(clients) {
    if (!clientList) return;

    clientList.innerHTML = clients.length ? clients.map(client => `
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 backdrop-blur-lg bg-opacity-80 dark:bg-opacity-80 border border-gray-200 dark:border-gray-700">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-xl font-semibold text-gray-800 dark:text-white">${client.name}</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">${client.email || ''}</p>
                </div>
                <div class="flex space-x-2">
                    <button onclick="editClient(${client.id})" 
                            class="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                        ${lang === 'ar' ? 'تعديل' : 'Edit'}
                    </button>
                    <button onclick="deleteClient(${client.id})"
                            class="px-3 py-1 text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                        ${lang === 'ar' ? 'حذف' : 'Delete'}
                    </button>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <p class="text-gray-600 dark:text-gray-400">${lang === 'ar' ? 'رقم الهاتف' : 'Phone'}</p>
                    <p class="text-gray-800 dark:text-white">${client.phone || '-'}</p>
                </div>
                <div>
                    <p class="text-gray-600 dark:text-gray-400">${lang === 'ar' ? 'العنوان' : 'Address'}</p>
                    <p class="text-gray-800 dark:text-white">${client.address || '-'}</p>
                </div>
                <div>
                    <p class="text-gray-600 dark:text-gray-400">${lang === 'ar' ? 'نقاط الولاء' : 'Loyalty Points'}</p>
                    <p class="text-gray-800 dark:text-white">${client.loyalty_points}</p>
                </div>
                <div>
                    <p class="text-gray-600 dark:text-gray-400">${lang === 'ar' ? 'إجمالي المشتريات' : 'Total Spent'}</p>
                    <p class="text-gray-800 dark:text-white">${client.total_spent.toFixed(2)}</p>
                </div>
            </div>
        </div>
    `).join('') : `
        <div class="text-center text-gray-600 dark:text-gray-400 py-8">
            ${lang === 'ar' ? 'لا يوجد عملاء' : 'No clients found'}
        </div>
    `;
}

// Edit client
function editClient(clientId) {
    window.location.href = `/clients/${clientId}/edit`;
}

// Delete client
function deleteClient(clientId) {
    if (confirm(lang === 'ar' ? 'هل أنت متأكد من حذف هذا العميل؟' : 'Are you sure you want to delete this client?')) {
        fetch(`/clients/${clientId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(() => {
            window.location.reload();
        }).catch(error => {
            console.error('Error:', error);
            alert(lang === 'ar' ? 'حدث خطأ أثناء حذف العميل' : 'Error deleting client');
        });
    }
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
} 