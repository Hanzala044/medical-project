// Staff Dashboard JavaScript for MEDicos Pharmacy Management System
// Created by: Mohammed Hanzala

// Google Drive API integration (frontend-only upload)
// Add this to your HTML: <script src="https://apis.google.com/js/api.js"></script>

var CLIENT_ID = '104664795256266494944';
var API_KEY = '65d87663e049b9db9568b7f17d77cc9c30759541';
var FOLDER_ID = 'medicos-drive-uploader-340@medicos-466420.iam.gserviceaccount.com';
var SCOPES = 'https://www.googleapis.com/auth/drive.file';

function startGapi() {
  gapi.load('client:auth2', () => {
    gapi.client.init({
      apiKey: '65d87663e049b9db9568b7f17d77cc9c30759541',
      clientId: '787506116104-dkv3c43kpoma453jtmhh34sj7hfiahfe.apps.googleusercontent.com',
      discoveryDocs: ["https://www.googleapis.com/discovery/v1/apis/drive/v3/rest"],
      scope: SCOPES
    });
  });
}

async function authenticateGapi() {
  await gapi.auth2.getAuthInstance().signIn();
}

async function uploadPrescriptionToDrive() {
  await authenticateGapi();
  var fileInput = document.getElementById('prescriptionFile');
  var file = fileInput.files[0];
  if (!file) {
    alert('Please select a file to upload.');
    return;
  }
  var metadata = {
    'name': file.name,
    'mimeType': file.type,
    'parents': ['1HUQ_O8mSB0jrirZarLOy1ct8fYW1B-PE']
  };
  var upload = new FormData();
  upload.append('metadata', new Blob([JSON.stringify(metadata)], { type: 'application/json' }));
  upload.append('file', file);
  fetch('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart', {
    method: 'POST',
    headers: new Headers({ 'Authorization': 'Bearer ' + gapi.auth.getToken().access_token }),
    body: upload,
  }).then((res) => {
    if (res.ok) {
      alert('Upload successful!');
    } else {
      alert('Upload failed.');
    }
  });
}

// Call startGapi() on page load
if (typeof gapi !== 'undefined') {
  startGapi();
}

class StaffDashboard {
    constructor() {
        this.currentStaff = null;
        this.initializeEventListeners();
        this.loadCurrentStaffInfo();
        this.loadAvailableMedicines();
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
    }

    async loadCurrentStaffInfo() {
        try {
            const response = await fetch('/api/current-staff');
            if (response.ok) {
                const data = await response.json();
                this.currentStaff = data.staff;
                this.displayStaffName();
            } else {
                console.error('Failed to load staff info');
            }
        } catch (error) {
            console.error('Error loading staff info:', error);
        }
    }

    displayStaffName() {
        if (this.currentStaff) {
            document.getElementById('staffName').textContent = this.currentStaff.full_name;
        }
    }

    initializeEventListeners() {
        // Form submissions
        document.getElementById('sellForm').addEventListener('submit', (e) => this.handleAddSale(e));
        
        // Medicine selection
        document.getElementById('medicineSelect').addEventListener('change', (e) => this.handleMedicineSelection(e));
        
        // Prescription upload
        document.getElementById('prescriptionFile').addEventListener('change', (e) => this.handlePrescriptionUpload(e));
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
        
        document.getElementById('clock').textContent = timeString;
        document.getElementById('date').textContent = dateString;
    }

    // Section management
    showSection(sectionName) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('hidden');
            section.classList.remove('active');
        });
        
        if (sectionName === 'sales') {
            document.getElementById('salesSection').classList.remove('hidden');
            document.getElementById('salesSection').classList.add('active');
        } else if (sectionName === 'records') {
            document.getElementById('recordsSection').classList.remove('hidden');
            document.getElementById('recordsSection').classList.add('active');
            this.loadSalesRecords();
        }
    }

    // Load sales records
    async loadSalesRecords() {
        try {
            const response = await fetch('/api/sales');
            const data = await response.json();
            
            const tbody = document.getElementById('recordsTable');
            tbody.innerHTML = '';
            
            if (data.sales && data.sales.length > 0) {
                data.sales.forEach(sale => {
                    const row = document.createElement('tr');
                    row.className = 'border-b border-white/10 hover:bg-white/5';
                    row.innerHTML = `
                        <td class="px-4 py-3">${new Date(sale.sale_date).toLocaleDateString()}</td>
                        <td class="px-4 py-3">${sale.customer_name}</td>
                        <td class="px-4 py-3">${sale.medicine_name}</td>
                        <td class="px-4 py-3">${sale.quantity_sold}</td>
                        <td class="px-4 py-3">$${sale.total_amount}</td>
                        <td class="px-4 py-3">${sale.doctor_name}</td>
                        <td class="px-4 py-3">${sale.sold_by_name || 'N/A'}</td>
                        <td class="px-4 py-3">
                            <button onclick="staffDashboard.viewSaleDetails(${sale.sale_id})" class="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-sm">View</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="8" class="px-4 py-3 text-center text-gray-400">No sales records found</td></tr>';
            }
        } catch (error) {
            console.error('Error loading sales records:', error);
            document.getElementById('recordsMessage').textContent = 'Error loading records';
            document.getElementById('recordsMessage').className = 'mt-4 text-center text-sm text-red-400';
        }
    }

    refreshRecords() {
        this.loadSalesRecords();
    }

    viewSaleDetails(saleId) {
        // Implement sale details view
        alert(`Viewing sale details for ID: ${saleId}`);
    }

    logout() {
        fetch('/api/logout', { method: 'POST' })
            .then(() => {
                window.location.href = 'auth-admin.html';
            })
            .catch(error => {
                console.error('Logout error:', error);
                window.location.href = 'auth-admin.html';
            });
    }

    async loadDashboardStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('totalSales').textContent = data.sales_today;
                document.getElementById('totalRevenue').textContent = `$${data.revenue_today.toFixed(2)}`;
                document.getElementById('totalMedicines').textContent = data.total_medicines;
                document.getElementById('lowStock').textContent = data.low_stock;
            } else {
                console.error('Failed to load dashboard stats:', data.error);
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    async loadSales() {
        try {
            const response = await fetch('/api/sales');
            const data = await response.json();
            
            if (response.ok) {
                this.displaySales(data.sales);
            } else {
                console.error('Failed to load sales:', data.error);
                this.showNotification('Failed to load sales', 'error');
            }
        } catch (error) {
            console.error('Error loading sales:', error);
            this.showNotification('Error loading sales', 'error');
        }
    }

    displaySales(sales) {
        const tbody = document.getElementById('salesTableBody');
        tbody.innerHTML = '';
        
        sales.forEach(sale => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            
            const saleDate = new Date(sale.sale_date);
            const formattedDate = saleDate.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900">${sale.medicine_name}</div>
                    <div class="text-sm text-gray-500">Batch: ${sale.batch_number || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${sale.quantity_sold} units
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    $${sale.total_amount}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${sale.doctor_name || 'N/A'}</div>
                    <div class="text-sm text-gray-500">${sale.doctor_phone || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900">${sale.customer_name || 'N/A'}</div>
                    <div class="text-sm text-gray-500">${sale.customer_phone || 'N/A'}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${formattedDate}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${sale.sold_by_name}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    ${sale.prescription_photo_url ? 
                        `<a href="${sale.prescription_photo_url}" target="_blank" class="text-blue-600 hover:text-blue-900">View Prescription</a>` : 
                        '<span class="text-gray-400">No prescription</span>'
                    }
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }

    async loadAvailableMedicines() {
        try {
            const response = await fetch('/api/medicines/available');
            const data = await response.json();
            
            if (response.ok) {
                this.populateMedicineSelect(data.medicines);
            } else {
                console.error('Failed to load available medicines:', data.error);
            }
        } catch (error) {
            console.error('Error loading available medicines:', error);
        }
    }

    populateMedicineSelect(medicines) {
        const select = document.getElementById('medicineSelect');
        select.innerHTML = '<option value="">Select Medicine</option>';
        
        medicines.forEach(medicine => {
            const option = document.createElement('option');
            option.value = medicine.medicine_id;
            option.textContent = `${medicine.medicine_name} (${medicine.quantity_available} available) - $${medicine.unit_price}`;
            option.dataset.price = medicine.unit_price;
            option.dataset.available = medicine.quantity_available;
            select.appendChild(option);
        });
    }

    showAddSaleModal() {
        document.getElementById('addSaleModal').classList.remove('hidden');
        document.getElementById('addSaleForm').reset();
        document.getElementById('prescriptionPreview').style.display = 'none';
        document.getElementById('prescriptionUrl').value = '';
    }

    hideAddSaleModal() {
        document.getElementById('addSaleModal').classList.add('hidden');
    }

    handleMedicineSelection(event) {
        const selectedOption = event.target.options[event.target.selectedIndex];
        const quantityInput = document.getElementById('quantitySold');
        const totalAmountSpan = document.getElementById('totalAmount');
        
        if (selectedOption.value) {
            const price = parseFloat(selectedOption.dataset.price);
            const available = parseInt(selectedOption.dataset.available);
            
            quantityInput.max = available;
            quantityInput.addEventListener('input', () => {
                const quantity = parseInt(quantityInput.value) || 0;
                const total = quantity * price;
                totalAmountSpan.textContent = `$${total.toFixed(2)}`;
            });
        } else {
            totalAmountSpan.textContent = '$0.00';
        }
    }

    async handlePrescriptionUpload(event) {
        // Use Google Drive upload instead of backend
        await uploadPrescriptionToDrive();
    }

    async handleAddSale(event) {
        event.preventDefault();
        
        if (!this.currentStaff) {
            this.showNotification('Staff information not loaded. Please refresh the page.', 'error');
            return;
        }
        
        const form = event.target;
        const saleData = {
            medicine_id: parseInt(document.getElementById('medicineSelect').value),
            quantity_sold: parseInt(document.getElementById('quantity').value),
            doctor_name: document.getElementById('doctorName').value,
            doctor_phone: document.getElementById('doctorPhone').value,
            prescription_photo_url: '', // Will be set after upload
            customer_name: document.getElementById('customerName').value,
            customer_phone: document.getElementById('customerPhone').value,
            sold_by: this.currentStaff.staff_id // Add the staff ID
        };
        
        // Validation
        if (!saleData.medicine_id) {
            this.showNotification('Please select a medicine', 'error');
            return;
        }
        
        if (saleData.quantity_sold <= 0) {
            this.showNotification('Quantity must be greater than 0', 'error');
            return;
        }
        
        // Handle prescription upload first
        const prescriptionFile = document.getElementById('prescriptionFile').files[0];
        if (prescriptionFile) {
            try {
                const formData = new FormData();
                formData.append('prescription', prescriptionFile);
                
                const uploadResponse = await fetch('/api/upload-prescription', {
                    method: 'POST',
                    body: formData
                });
                
                const uploadData = await uploadResponse.json();
                
                if (uploadResponse.ok) {
                    saleData.prescription_photo_url = uploadData.file_url;
                } else {
                    this.showNotification(uploadData.error || 'Failed to upload prescription', 'error');
                    return;
                }
            } catch (error) {
                console.error('Error uploading prescription:', error);
                this.showNotification('Error uploading prescription', 'error');
                return;
            }
        }
        
        try {
            const response = await fetch('/api/sales', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(saleData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Sale recorded successfully!', 'success');
                form.reset();
                this.loadAvailableMedicines(); // Refresh medicine list
                document.getElementById('saleMessage').textContent = 'Sale recorded successfully!';
                document.getElementById('saleMessage').className = 'mt-4 text-center text-sm text-green-400';
            } else {
                this.showNotification(data.error || 'Failed to record sale', 'error');
                document.getElementById('saleMessage').textContent = data.error || 'Failed to record sale';
                document.getElementById('saleMessage').className = 'mt-4 text-center text-sm text-red-400';
            }
        } catch (error) {
            console.error('Error recording sale:', error);
            this.showNotification('Error recording sale', 'error');
            document.getElementById('saleMessage').textContent = 'Error recording sale';
            document.getElementById('saleMessage').className = 'mt-4 text-center text-sm text-red-400';
        }
    }

    handleSearch(searchTerm) {
        const rows = document.querySelectorAll('#salesTableBody tr');
        
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

    // Utility function to format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    // Utility function to validate phone number
    validatePhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.staffDashboard = new StaffDashboard();
    // Add Save button event
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async function() {
            const form = document.getElementById('sellForm');
            const formData = new FormData(form);
            const fileInput = document.getElementById('prescriptionFile');
            const file = fileInput.files[0];
            if (file) {
                formData.append('prescription', file);
            }
            // Upload image to backend
            const uploadResponse = await fetch('/api/upload-prescription', {
                method: 'POST',
                body: formData
            });
            const uploadData = await uploadResponse.json();
            if (uploadResponse.ok) {
                // Save sale data to backend (include image URL)
                const saleData = {
                    medicine_id: parseInt(document.getElementById('medicineSelect').value),
                    quantity_sold: parseInt(document.getElementById('quantity').value),
                    doctor_name: document.getElementById('doctorName').value,
                    doctor_phone: document.getElementById('doctorPhone').value,
                    prescription_photo_url: uploadData.file_url,
                    customer_name: document.getElementById('customerName').value,
                    customer_phone: document.getElementById('customerPhone').value
                };
                const saleResponse = await fetch('/api/sales', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(saleData)
                });
                if (saleResponse.ok) {
                    alert('Saved to database and image available in records!');
                } else {
                    alert('Sale save failed.');
                }
            } else {
                alert('Image upload failed: ' + (uploadData.error || 'Unknown error'));
            }
        });
    }
    // Add Push to Drive button event
    const pushDriveBtn = document.getElementById('pushDriveBtn');
    if (pushDriveBtn) {
        pushDriveBtn.addEventListener('click', async function() {
            await uploadPrescriptionToDrive();
        });
    }
});

// Export for global access
window.StaffDashboard = StaffDashboard; 