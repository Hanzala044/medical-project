// Staff Dashboard JavaScript for MEDicos Pharmacy Management System
// Created by: Mohammed Hanzala

// Google Drive API integration (frontend-only upload)
// Add this to your HTML: <script src="https://apis.google.com/js/api.js"></script>

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
        
        // Initialize all UI components
        this.initializeUIComponents();
        
        // Show Twilio integration is loaded
        this.showNotification('Twilio WhatsApp integration loaded!', 'info');
    }
    
    initializeUIComponents() {
        // Initialize form animations
        const formInputs = document.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.02)';
                this.parentElement.style.borderColor = '#10b981';
            });
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
                this.parentElement.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            });
        });
        
        // Initialize button hover effects
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.2)';
            });
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
            });
        });
        
        // Initialize table row hover effects
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        // Initialize modal animations
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                this.style.animation = 'fadeIn 0.3s ease-in-out';
            });
        });
        
        // Initialize floating elements
        const floatingElements = document.querySelectorAll('.animate-pulse, .animate-bounce');
        floatingElements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.2}s`;
        });
        
        // Initialize Razorpay integration
        if (typeof Razorpay !== 'undefined') {
            // Razorpay SDK loaded
        }
        
        // Initialize real-time calculations
        const quantityInput = document.getElementById('quantity');
        const rateInput = document.getElementById('ratePerTablet');
        const totalInput = document.getElementById('totalAmount');
        
        if (quantityInput && rateInput && totalInput) {
            [quantityInput, rateInput].forEach(input => {
                input.addEventListener('input', () => this.calculateTotal());
            });
        }
        
        // Initialize prescription upload preview
        const prescriptionInput = document.getElementById('prescriptionFile');
        if (prescriptionInput) {
            prescriptionInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        // Create preview if needed
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
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
        
        // Quantity and rate calculation
        document.getElementById('quantity').addEventListener('input', (e) => this.calculateTotal());
        document.getElementById('ratePerTablet').addEventListener('input', (e) => this.calculateTotal());
        
        // Razorpay payment
        document.getElementById('payWithRazorpayBtn').addEventListener('click', (e) => this.handleRazorpayPayment(e));
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
                        <td class="px-4 py-3">₹${sale.rate_per_tablet || sale.unit_price || 'N/A'}</td>
                        <td class="px-4 py-3">₹${sale.total_amount}</td>
                        <td class="px-4 py-3">
                            <span class="px-2 py-1 rounded text-xs ${sale.payment_status === 'completed' ? 'bg-green-500' : sale.payment_status === 'pending' ? 'bg-yellow-500' : 'bg-red-500'}">
                                ${sale.payment_status || 'N/A'}
                            </span>
                        </td>
                        <td class="px-4 py-3">${sale.doctor_name}</td>
                        <td class="px-4 py-3">${sale.sold_by_name || 'N/A'}</td>
                        <td class="px-4 py-3">
                            <button onclick="staffDashboard.viewSaleDetails(${sale.sale_id})" class="bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded text-sm">View</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="10" class="px-4 py-3 text-center text-gray-400">No sales records found</td></tr>';
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
                    <div class="flex flex-col items-end space-y-2">
                        ${sale.prescription_photo_url ? 
                            `<div class="flex flex-col items-center space-y-1">
                                <img src="${sale.prescription_photo_url}" alt="Prescription" class="w-16 h-16 object-cover rounded border cursor-pointer hover:scale-110 transition-transform" onclick="window.open('${sale.prescription_photo_url}', '_blank')">
                                <a href="${sale.prescription_photo_url}" target="_blank" class="text-blue-600 hover:text-blue-900 text-xs">View Full</a>
                            </div>` : 
                            '<span class="text-gray-400">No prescription</span>'
                        }
                        <div class="flex flex-col space-y-1">
                            <button onclick="staffDashboard.sendWhatsAppReceipt(${sale.sale_id})" 
                                    class="bg-green-500 hover:bg-green-600 text-white text-xs px-2 py-1 rounded transition-colors">
                                📱 Send Receipt
                            </button>
                            <button onclick="staffDashboard.sendTwilioReceipt(${sale.sale_id})" 
                                    class="bg-blue-500 hover:bg-blue-600 text-white text-xs px-2 py-1 rounded transition-colors">
                                📱 Send Receipt (Twilio)
                            </button>
                        </div>
                    </div>
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

    // WhatsApp receipt functionality
    async sendWhatsAppReceipt(saleId) {
        try {
            this.showNotification('Sending receipt via WhatsApp...', 'info');
            
            const response = await fetch(`/api/send-receipt/${saleId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showNotification('✅ Receipt sent successfully via WhatsApp!', 'success');
                // Refresh the sales list to show updated status
                this.loadSales();
            } else {
                this.showNotification(`❌ Failed to send receipt: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Error sending WhatsApp receipt:', error);
            this.showNotification('❌ Error sending receipt. Please try again.', 'error');
        }
    }

    // Check WhatsApp receipt status
    async checkWhatsAppStatus(saleId) {
        try {
            const response = await fetch(`/api/twilio-status/${saleId}`);
            const result = await response.json();
            
            if (result.success) {
                console.log('WhatsApp status:', result);
                return result;
            } else {
                console.error('Failed to check WhatsApp status:', result.message);
                return null;
            }
        } catch (error) {
            console.error('Error checking WhatsApp status:', error);
            return null;
        }
    }

    // Add sendTwilioReceipt method to StaffDashboard class
    async sendTwilioReceipt(saleId) {
        try {
            this.showNotification('Sending receipt via Twilio WhatsApp...', 'info');
            const response = await fetch(`/api/send-receipt-twilio/${saleId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (result.success) {
                this.showNotification('✅ Receipt sent successfully via Twilio WhatsApp!', 'success');
                this.loadSales();
            } else {
                this.showNotification(`❌ Failed to send receipt: ${result.message}`, 'error');
            }
        } catch (error) {
            console.error('Error sending Twilio WhatsApp receipt:', error);
            this.showNotification('❌ Error sending receipt. Please try again.', 'error');
        }
    }

    // Send WhatsApp receipt directly from form data
    async sendWhatsAppReceiptFromForm(saleData) {
        try {
            this.showNotification('Sending receipt via Twilio WhatsApp...', 'info');
            
            // Create a temporary sale object for receipt generation
            const tempSale = {
                sale_id: Date.now(), // Temporary ID
                sale_date: new Date().toISOString(),
                customer_name: saleData.customer_name,
                customer_phone: saleData.customer_phone,
                quantity_sold: saleData.quantity_sold,
                total_amount: saleData.total_amount || 0,
                doctor_name: saleData.doctor_name,
                doctor_phone: saleData.doctor_phone,
                medicine_name: saleData.medicine_name || 'Medicine',
                unit_price: saleData.unit_price || 0,
                manufacturer: saleData.manufacturer || 'Pharmacy',
                sold_by_name: this.currentStaff ? this.currentStaff.full_name : 'Staff'
            };
            
            // Send via Twilio
            const response = await fetch('/api/send-receipt-twilio-direct', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(tempSale)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('✅ Receipt sent successfully via Twilio WhatsApp!', 'success');
                return true;
            } else {
                this.showNotification(`❌ Failed to send receipt: ${result.message}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Error sending Twilio WhatsApp receipt:', error);
            this.showNotification('❌ Error sending receipt. Please try again.', 'error');
            return false;
        }
    }

    // Calculate total amount based on quantity and rate per tablet
    calculateTotal() {
        const quantity = parseFloat(document.getElementById('quantity').value) || 0;
        const ratePerTablet = parseFloat(document.getElementById('ratePerTablet').value) || 0;
        const totalAmount = quantity * ratePerTablet;
        
        document.getElementById('totalAmount').value = totalAmount.toFixed(2);
        return totalAmount;
    }

    // Handle Razorpay payment
    async handleRazorpayPayment(event) {
        event.preventDefault();
        
        // Validate form
        const form = document.getElementById('sellForm');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const totalAmount = this.calculateTotal();
        if (totalAmount <= 0) {
            alert('Please enter valid quantity and rate per tablet.');
            return;
        }

        // Get form data
        const formData = {
            customer_name: document.getElementById('customerName').value,
            customer_phone: document.getElementById('customerPhone').value,
            medicine_id: parseInt(document.getElementById('medicineSelect').value),
            quantity_sold: parseInt(document.getElementById('quantity').value),
            doctor_name: document.getElementById('doctorName').value,
            rate_per_tablet: parseFloat(document.getElementById('ratePerTablet').value),
            total_amount: totalAmount
        };

        try {
            // Create Razorpay order
            const orderResponse = await fetch('/api/create-razorpay-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: Math.round(totalAmount * 100), // Convert to paise
                    currency: 'INR',
                    receipt: 'receipt_' + Date.now(),
                    notes: {
                        customer_name: formData.customer_name,
                        medicine_id: formData.medicine_id,
                        quantity: formData.quantity_sold
                    }
                })
            });

            if (!orderResponse.ok) {
                throw new Error('Failed to create payment order');
            }

            const orderData = await orderResponse.json();
            
            // Check if we're in mock mode
            if (orderData.key_id === 'rzp_test_YOUR_KEY_ID' || orderData.key_id === 'mock_key') {
                // Mock payment flow for testing
                // Using Mock Payment Flow
                
                // Simulate payment success after 2 seconds
                setTimeout(async () => {
                    const mockResponse = {
                        razorpay_payment_id: 'pay_mock_' + Date.now(),
                        razorpay_order_id: orderData.id,
                        razorpay_signature: 'mock_signature_' + Date.now()
                    };
                    
                    await this.handlePaymentSuccess(mockResponse, formData);
                }, 2000);
                
                // Show mock payment modal
                alert('🔧 Mock Payment Mode\n\nSimulating payment process...\n\nPayment will be completed automatically in 2 seconds.');
                
            } else {
                // Real Razorpay payment flow
                const options = {
                    key: orderData.key_id,
                    amount: orderData.amount,
                    currency: orderData.currency,
                    name: 'MEDicos Pharmacy',
                    description: `Medicine Purchase - ${formData.customer_name}`,
                    order_id: orderData.id,
                    handler: async (response) => {
                        await this.handlePaymentSuccess(response, formData);
                    },
                    prefill: {
                        name: formData.customer_name,
                        contact: formData.customer_phone,
                        email: 'customer@medicos.com'
                    },
                    notes: {
                        address: 'MEDicos Pharmacy'
                    },
                    theme: {
                        color: '#10b981'
                    },
                    modal: {
                        ondismiss: () => {
                            // Payment modal closed
                        }
                    }
                };

                // Open Razorpay payment modal
                const rzp = new Razorpay(options);
                rzp.open();
            }

        } catch (error) {
            console.error('Payment error:', error);
            alert('Payment initialization failed: ' + error.message);
        }
    }

    // Handle successful payment
    async handlePaymentSuccess(paymentResponse, formData) {
        try {
            // Verify payment on backend
            const verifyResponse = await fetch('/api/verify-razorpay-payment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    payment_id: paymentResponse.razorpay_payment_id,
                    order_id: paymentResponse.razorpay_order_id,
                    signature: paymentResponse.razorpay_signature,
                    form_data: formData
                })
            });

            if (!verifyResponse.ok) {
                throw new Error('Payment verification failed');
            }

            const result = await verifyResponse.json();
            
            if (result.success) {
                alert('✅ Payment successful! Sale recorded and receipt sent.');
                
                // Send WhatsApp receipt
                if (formData.customer_phone) {
                    try {
                        const success = await this.sendWhatsAppReceiptFromForm(formData);
                        if (success) {
                            // WhatsApp receipt sent successfully
                        }
                    } catch (error) {
                        console.error('WhatsApp receipt failed:', error);
                    }
                }
                
                // Reset form
                document.getElementById('sellForm').reset();
                document.getElementById('totalAmount').value = '';
                
                // Refresh records
                this.refreshRecords();
                
            } else {
                alert('❌ Payment verification failed: ' + result.error);
            }

        } catch (error) {
            console.error('Payment verification error:', error);
            alert('Payment verification failed: ' + error.message);
        }
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
                    rate_per_tablet: parseFloat(document.getElementById('ratePerTablet').value),
                    total_amount: parseFloat(document.getElementById('totalAmount').value),
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
                    const saleResult = await saleResponse.json();
                    alert('Saved to database and image available in records!');
                    
                    // Automatically send WhatsApp receipt to customer
                    if (saleData.customer_phone) {
                        try {
                            // Try to send via sale ID first
                            if (saleResult.sale_id) {
                                const twilioResponse = await fetch(`/api/send-receipt-twilio/${saleResult.sale_id}`, {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' }
                                });
                                const twilioResult = await twilioResponse.json();
                                
                                if (twilioResult.success) {
                                    alert('✅ Receipt sent successfully to customer via WhatsApp!');
                                } else {
                                    // Fallback to direct method
                                    const success = await window.staffDashboard.sendWhatsAppReceiptFromForm(saleData);
                                    if (success) {
                                        alert('✅ Receipt sent successfully to customer via WhatsApp!');
                                    } else {
                                        alert('⚠️ Sale saved but WhatsApp receipt failed.');
                                    }
                                }
                            } else {
                                // Use direct method if no sale ID
                                const success = await window.staffDashboard.sendWhatsAppReceiptFromForm(saleData);
                                if (success) {
                                    alert('✅ Receipt sent successfully to customer via WhatsApp!');
                                } else {
                                    alert('⚠️ Sale saved but WhatsApp receipt failed.');
                                }
                            }
                        } catch (error) {
                            alert('⚠️ Sale saved but WhatsApp receipt failed: ' + error.message);
                        }
                    }
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