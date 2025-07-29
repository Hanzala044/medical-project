// MEDicos Pharmacy Management System - Global Initialization Script
// Created by: Mohammed Hanzala

class MEDicosInitializer {
    constructor() {
        this.initTime = Date.now();
        console.log('🚀 MEDicos - Global Initialization Started');
        this.initializeAll();
    }

    async initializeAll() {
        try {
            // Initialize core components
            await this.initializeCore();
            
            // Initialize UI components
            this.initializeUI();
            
            // Initialize integrations
            this.initializeIntegrations();
            
            // Initialize animations
            this.initializeAnimations();
            
            // Initialize event listeners
            this.initializeEventListeners();
            
            console.log(`🎉 MEDicos initialization completed in ${Date.now() - this.initTime}ms`);
            
        } catch (error) {
            console.error('❌ MEDicos initialization failed:', error);
        }
    }

    async initializeCore() {
        console.log('🔧 Initializing core components...');
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
            console.log('✅ Lucide icons initialized');
        }
        
        // Initialize Tailwind CSS (if needed)
        if (typeof tailwind !== 'undefined') {
            console.log('✅ Tailwind CSS initialized');
        }
        
        // Check for required libraries
        this.checkRequiredLibraries();
        
        console.log('✅ Core components initialized');
    }

    initializeUI() {
        console.log('🎨 Initializing UI components...');
        
        // Initialize trust markers
        this.initializeTrustMarkers();
        
        // Initialize forms
        this.initializeForms();
        
        // Initialize buttons
        this.initializeButtons();
        
        // Initialize tables
        this.initializeTables();
        
        // Initialize modals
        this.initializeModals();
        
        // Initialize navigation
        this.initializeNavigation();
        
        console.log('✅ UI components initialized');
    }

    initializeTrustMarkers() {
        const trustMarkers = document.querySelectorAll('.TrustMarkerHeroComponent_gradientBorderBackground___42bi');
        trustMarkers.forEach(marker => {
            // Hover effects
            marker.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.3)';
            });
            
            marker.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.boxShadow = '';
            });
            
            // Click feedback
            marker.addEventListener('click', function() {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1.05)';
                }, 150);
            });
        });
        
        if (trustMarkers.length > 0) {
            console.log(`✅ ${trustMarkers.length} trust markers initialized`);
        }
    }

    initializeForms() {
        const formInputs = document.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            // Focus effects
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.02)';
                this.parentElement.style.borderColor = '#10b981';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
                this.parentElement.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            });
            
            // Real-time validation
            input.addEventListener('input', function() {
                this.classList.remove('border-red-500', 'border-green-500');
                if (this.checkValidity()) {
                    this.classList.add('border-green-500');
                } else if (this.value.length > 0) {
                    this.classList.add('border-red-500');
                }
            });
        });
        
        console.log(`✅ ${formInputs.length} form inputs initialized`);
    }

    initializeButtons() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            // Hover effects
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.2)';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
            });
            
            // Click feedback
            button.addEventListener('click', function() {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 150);
            });
        });
        
        console.log(`✅ ${buttons.length} buttons initialized`);
    }

    initializeTables() {
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
        
        if (tableRows.length > 0) {
            console.log(`✅ ${tableRows.length} table rows initialized`);
        }
    }

    initializeModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                this.style.animation = 'fadeIn 0.3s ease-in-out';
            });
        });
        
        if (modals.length > 0) {
            console.log(`✅ ${modals.length} modals initialized`);
        }
    }

    initializeNavigation() {
        // Smooth scrolling for anchor links
        const navLinks = document.querySelectorAll('a[href^="#"]');
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Mobile menu toggle
        const mobileMenuBtn = document.querySelector('[aria-label="Toggle menu"]');
        const mobileMenu = document.querySelector('.mobile-menu');
        
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', function() {
                mobileMenu.classList.toggle('hidden');
            });
        }
        
        console.log('✅ Navigation initialized');
    }

    initializeIntegrations() {
        console.log('🔌 Initializing integrations...');
        
        // Check Razorpay
        if (typeof Razorpay !== 'undefined') {
            console.log('✅ Razorpay SDK loaded');
        } else {
            console.log('⚠️ Razorpay SDK not loaded');
        }
        
        // Check Twilio (if applicable)
        if (typeof Twilio !== 'undefined') {
            console.log('✅ Twilio SDK loaded');
        }
        
        // Check Google APIs
        if (typeof gapi !== 'undefined') {
            console.log('✅ Google APIs loaded');
        }
        
        console.log('✅ Integrations checked');
    }

    initializeAnimations() {
        console.log('🎭 Initializing animations...');
        
        // Floating elements
        const floatingElements = document.querySelectorAll('.float-anim, .animate-pulse, .animate-bounce');
        floatingElements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.2}s`;
        });
        
        // Page transitions
        const pages = document.querySelectorAll('.page');
        pages.forEach(page => {
            if (page.classList.contains('active')) {
                page.style.animation = 'fadeIn 0.5s ease-in-out';
            }
        });
        
        // Add CSS animations
        this.addCSSAnimations();
        
        console.log(`✅ ${floatingElements.length} animated elements initialized`);
    }

    addCSSAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes slideIn {
                from { transform: translateX(-100%); }
                to { transform: translateX(0); }
            }
            
            @keyframes scaleIn {
                from { transform: scale(0.8); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
            
            .page.active {
                animation: fadeIn 0.5s ease-in-out;
            }
            
            .modal.show {
                animation: scaleIn 0.3s ease-in-out;
            }
            
            .float-anim {
                animation: float 6s ease-in-out infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
            }
        `;
        document.head.appendChild(style);
    }

    initializeEventListeners() {
        console.log('👂 Initializing event listeners...');
        
        // Global click handler for dropdowns
        document.addEventListener('click', function(e) {
            const dropdowns = document.querySelectorAll('.dropdown');
            dropdowns.forEach(dropdown => {
                if (!dropdown.contains(e.target) && !dropdown.previousElementSibling?.contains(e.target)) {
                    dropdown.classList.add('hidden');
                }
            });
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Escape key to close modals
            if (e.key === 'Escape') {
                const modals = document.querySelectorAll('.modal.show');
                modals.forEach(modal => {
                    modal.classList.remove('show');
                });
            }
        });
        
        console.log('✅ Event listeners initialized');
    }

    checkRequiredLibraries() {
        const requiredLibraries = [
            { name: 'lucide', check: () => typeof lucide !== 'undefined' },
            { name: 'Tailwind CSS', check: () => document.querySelector('[class*="bg-"]') !== null }
        ];
        
        requiredLibraries.forEach(lib => {
            if (lib.check()) {
                console.log(`✅ ${lib.name} loaded`);
            } else {
                console.warn(`⚠️ ${lib.name} not found`);
            }
        });
    }

    // Utility methods
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' :
            type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
        } text-white`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    validatePhone(phone) {
        const phoneRegex = /^[6-9]\d{9}$/;
        return phoneRegex.test(phone);
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.medicosInitializer = new MEDicosInitializer();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MEDicosInitializer;
} 