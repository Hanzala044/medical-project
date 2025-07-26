// Admin Dashboard JavaScript for MEDicos Pharmacy Management System
// Created by: Mohammed Hanzala

class AdminDashboard {
    constructor() {
        this.initializeEventListeners();
        this.loadDashboardStats();
        this.loadMedicines();
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
    }

    initializeEventListeners() {
        // Modal controls
        document.getElementById('addMedicineBtn').addEventListener('click', () => this.showAddMedicineModal());
        document.getElementById('closeAddModal').addEventListener('click', () => this.hideAddMedicineModal());
        document.getElementById('closeEditModal').addEventListener('click', () => this.hideEditMedicineModal());
        
        // Form submissions
        document.getElementById('addMedicineForm').addEventListener('submit', (e) => this.handleAddMedicine(e));
        document.getElementById('editMedicineForm').addEventListener('submit', (e) => this.handleEditMedicine(e));
        
        // Search functionality
        document.getElementById('searchMedicine').addEventListener('input', (e) => this.handleSearch(e.target.value));
        
        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());
    }

    updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        const dateString = now.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        document.getElementById('currentTime').textContent = timeString;
        document.getElementById('currentDate').textContent = dateString;
    }

    async loadDashboardStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('totalMedicines').textContent = data.total_medicines;
                document.getElementById('lowStock').textContent = data.low_stock;
                document.getElementById('expiringSoon').textContent = data.expiring_soon;
                document.getElementById('salesToday').textContent = data.sales_today;
                document.getElementById('revenueToday').textContent = `$${data.revenue_today.toFixed(2)}`;
            } else {
                console.error('Failed to load dashboard stats:', data.error);
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    async loadMedicines() {
        try {
            const response = await fetch('/api/medicines');
            const data = await response.json();
            
            if (response.ok) {
                this.displayMedicines(data.medicines);
            } else {
                console.error('Failed to load medicines:', data.error);
                this.showNotification('Failed to load medicines', 'error');
            }
        } catch (error) {
            console.error('Error loading medicines:', error);
            this.showNotification('Error loading medicines', 'error');
        }
    }

    displayMedicines(medicines) {
        const tbody = document.getElementById('medicinesTableBody');
        tbody.innerHTML = '';
        
        medicines.forEach(medicine => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            
            const expiryDate = new Date(medicine.expiry_date);
            const today = new Date();
            const daysUntilExpiry = Math.ceil((expiryDate - today) / (1000 * 60 * 60 * 24));
            
            let expiryClass = 'text-green-600';
            if (daysUntilExpiry <= 30 && daysUntilExpiry > 0) {
                expiryClass = 'text-yellow-600';
            } else if (daysUntilExpiry <= 0) {
                expiryClass = 'text-red-600';
            }
            
            let stockClass = 'text-green-600';
            if (medicine.quantity_available < 50) {
                stockClass = 'text-red-600';
            } else if (medicine.quantity_available < 100) {
                stockClass = 'text-yellow-600';
            }
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${medicine.medicine_name}</div>
                    <div class="text-sm text-gray-500">${medicine.batch_number}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${stockClass}">
                        ${medicine.quantity_available} units
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    $${medicine.unit_price}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="text-sm ${expiryClass}">${medicine.expiry_date}</span>
                    <div class="text-xs text-gray-500">${daysUntilExpiry > 0 ? `${daysUntilExpiry} days left` : 'Expired'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${medicine.manufacturer || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${medicine.category || 'N/A'}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button onclick="adminDashboard.editMedicine(${medicine.medicine_id})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                        Edit
                    </button>
                    <button onclick="adminDashboard.deleteMedicine(${medicine.medicine_id})" class="text-red-600 hover:text-red-900">
                        Delete
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    showAddMedicineModal() {
        document.getElementById('addMedicineModal').classList.remove('hidden');
        document.getElementById('addMedicineForm').reset();
    }

    hideAddMedicineModal() {
        document.getElementById('addMedicineModal').classList.add('hidden');
    }

    showEditMedicineModal() {
        document.getElementById('editMedicineModal').classList.remove('hidden');
    }

    hideEditMedicineModal() {
        document.getElementById('editMedicineModal').classList.add('hidden');
    }

    async handleAddMedicine(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const medicineData = {
            medicine_name: formData.get('medicine_name'),
            batch_number: formData.get('batch_number'),
            expiry_date: formData.get('expiry_date'),
            date_of_purchase: formData.get('date_of_purchase'),
            quantity_available: parseInt(formData.get('quantity_available')),
            unit_price: parseFloat(formData.get('unit_price')),
            manufacturer: formData.get('manufacturer'),
            category: formData.get('category'),
            description: formData.get('description')
        };
        
        try {
            const response = await fetch('/api/medicines', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(medicineData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Medicine added successfully!', 'success');
                this.hideAddMedicineModal();
                this.loadMedicines();
                this.loadDashboardStats();
            } else {
                this.showNotification(data.error || 'Failed to add medicine', 'error');
            }
        } catch (error) {
            console.error('Error adding medicine:', error);
            this.showNotification('Error adding medicine', 'error');
        }
    }

    async editMedicine(medicineId) {
        try {
            const response = await fetch(`/api/medicines/${medicineId}`);
            const medicine = await response.json();
            
            if (response.ok) {
                // Populate edit form
                document.getElementById('edit_medicine_id').value = medicine.medicine_id;
                document.getElementById('edit_medicine_name').value = medicine.medicine_name;
                document.getElementById('edit_batch_number').value = medicine.batch_number;
                document.getElementById('edit_expiry_date').value = medicine.expiry_date;
                document.getElementById('edit_date_of_purchase').value = medicine.date_of_purchase;
                document.getElementById('edit_quantity_available').value = medicine.quantity_available;
                document.getElementById('edit_unit_price').value = medicine.unit_price;
                document.getElementById('edit_manufacturer').value = medicine.manufacturer || '';
                document.getElementById('edit_category').value = medicine.category || '';
                document.getElementById('edit_description').value = medicine.description || '';
                
                this.showEditMedicineModal();
            } else {
                this.showNotification('Failed to load medicine details', 'error');
            }
        } catch (error) {
            console.error('Error loading medicine details:', error);
            this.showNotification('Error loading medicine details', 'error');
        }
    }

    async handleEditMedicine(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const medicineId = formData.get('medicine_id');
        const medicineData = {
            medicine_name: formData.get('medicine_name'),
            batch_number: formData.get('batch_number'),
            expiry_date: formData.get('expiry_date'),
            date_of_purchase: formData.get('date_of_purchase'),
            quantity_available: parseInt(formData.get('quantity_available')),
            unit_price: parseFloat(formData.get('unit_price')),
            manufacturer: formData.get('manufacturer'),
            category: formData.get('category'),
            description: formData.get('description')
        };
        
        try {
            const response = await fetch(`/api/medicines/${medicineId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(medicineData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Medicine updated successfully!', 'success');
                this.hideEditMedicineModal();
                this.loadMedicines();
                this.loadDashboardStats();
            } else {
                this.showNotification(data.error || 'Failed to update medicine', 'error');
            }
        } catch (error) {
            console.error('Error updating medicine:', error);
            this.showNotification('Error updating medicine', 'error');
        }
    }

    async deleteMedicine(medicineId) {
        if (!confirm('Are you sure you want to delete this medicine? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/medicines/${medicineId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Medicine deleted successfully!', 'success');
                this.loadMedicines();
                this.loadDashboardStats();
            } else {
                this.showNotification(data.error || 'Failed to delete medicine', 'error');
            }
        } catch (error) {
            console.error('Error deleting medicine:', error);
            this.showNotification('Error deleting medicine', 'error');
        }
    }

    handleSearch(searchTerm) {
        const rows = document.querySelectorAll('#medicinesTableBody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }

    async handleLogout() {
        try {
            const response = await fetch('/api/logout', {
                method: 'POST'
            });
            
            if (response.ok) {
                window.location.href = 'auth-admin.html';
            }
        } catch (error) {
            console.error('Error logging out:', error);
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});

// Export for global access
window.AdminDashboard = AdminDashboard; 