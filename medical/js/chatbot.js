class MedicalChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.conversationHistory = [];
        this.apiBaseUrl = 'http://localhost:5001/api/chatbot';
        
        this.init();
    }
    
    init() {
        this.createChatbotUI();
        this.bindEvents();
        this.loadChatHistory();
    }
    
    createChatbotUI() {
        // Create chatbot container
        const chatbotHTML = `
            <div id="medical-chatbot" class="fixed bottom-4 right-4 z-50">
                <!-- Chat Button -->
                <div id="chatbot-button" class="bg-emerald-500 hover:bg-emerald-600 text-white rounded-full p-4 shadow-lg cursor-pointer transition-all duration-300 transform hover:scale-110">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                    </svg>
                </div>
                
                <!-- Chat Window -->
                <div id="chatbot-window" class="hidden absolute bottom-16 right-0 w-96 h-[500px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col">
                    <!-- Header -->
                    <div class="bg-emerald-500 text-white p-4 rounded-t-lg flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div>
                                <h3 class="font-semibold">MEDicos Assistant</h3>
                                <p class="text-sm opacity-90">Medical Information & Support</p>
                            </div>
                        </div>
                        <button id="chatbot-close" class="text-white hover:text-gray-200 transition-colors">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    
                    <!-- Messages Container -->
                    <div id="chatbot-messages" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                        <!-- Welcome message -->
                        <div class="flex items-start space-x-3">
                            <div class="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
                                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="bg-white rounded-lg p-3 shadow-sm max-w-xs">
                                <p class="text-sm text-gray-800">
                                    Hello! I'm your MEDicos medical assistant. I can help you with information about medicines, their uses, side effects, and dosages. 
                                    <br><br>
                                    <strong>⚠️ Important:</strong> This information is for educational purposes only. Always consult healthcare professionals for medical advice.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Input Area -->
                    <div class="p-4 border-t border-gray-200 bg-white rounded-b-lg">
                        <div class="flex space-x-2">
                            <input 
                                id="chatbot-input" 
                                type="text" 
                                placeholder="Ask about medicines, side effects, dosages..." 
                                class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent text-sm"
                                disabled
                            >
                            <button 
                                id="chatbot-send" 
                                class="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                disabled
                            >
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                </svg>
                            </button>
                        </div>
                        <p class="text-xs text-gray-500 mt-2">
                            💡 Try: "What are the side effects of paracetamol?" or "How much ibuprofen should I take?"
                        </p>
                    </div>
                </div>
            </div>
        `;
        
        // Add to body
        document.body.insertAdjacentHTML('beforeend', chatbotHTML);
    }
    
    bindEvents() {
        // Toggle chatbot
        document.getElementById('chatbot-button').addEventListener('click', () => {
            this.toggleChatbot();
        });
        
        // Close chatbot
        document.getElementById('chatbot-close').addEventListener('click', () => {
            this.closeChatbot();
        });
        
        // Send message
        document.getElementById('chatbot-send').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key to send
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            const chatbot = document.getElementById('medical-chatbot');
            if (!chatbot.contains(e.target)) {
                this.closeChatbot();
            }
        });
    }
    
    toggleChatbot() {
        const window = document.getElementById('chatbot-window');
        const button = document.getElementById('chatbot-button');
        const input = document.getElementById('chatbot-input');
        const send = document.getElementById('chatbot-send');
        
        if (this.isOpen) {
            window.classList.add('hidden');
            button.classList.remove('bg-emerald-600');
            button.classList.add('bg-emerald-500');
            this.isOpen = false;
        } else {
            window.classList.remove('hidden');
            button.classList.remove('bg-emerald-500');
            button.classList.add('bg-emerald-600');
            input.disabled = false;
            send.disabled = false;
            input.focus();
            this.isOpen = true;
        }
    }
    
    closeChatbot() {
        const window = document.getElementById('chatbot-window');
        const button = document.getElementById('chatbot-button');
        const input = document.getElementById('chatbot-input');
        const send = document.getElementById('chatbot-send');
        
        window.classList.add('hidden');
        button.classList.remove('bg-emerald-600');
        button.classList.add('bg-emerald-500');
        input.disabled = true;
        send.disabled = true;
        this.isOpen = false;
    }
    
    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        input.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to API
            const response = await fetch(`${this.apiBaseUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Add bot response
                this.addMessage(data.response, 'bot', data.medicine_info);
                
                // Store in history
                this.conversationHistory.push({
                    timestamp: data.timestamp,
                    user_message: message,
                    bot_response: data.response,
                    medicine_info: data.medicine_info
                });
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.addMessage('Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'bot');
        } finally {
            this.hideTypingIndicator();
        }
    }
    
    addMessage(message, sender, medicineInfo = null) {
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start space-x-3';
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="flex-1"></div>
                <div class="bg-emerald-500 text-white rounded-lg p-3 shadow-sm max-w-xs">
                    <p class="text-sm">${this.escapeHtml(message)}</p>
                </div>
            `;
        } else {
            let messageContent = `<p class="text-sm text-gray-800">${this.escapeHtml(message)}</p>`;
            
            // Add medicine info if available
            if (medicineInfo && typeof medicineInfo === 'object') {
                messageContent += this.createMedicineInfoCard(medicineInfo);
            }
            
            messageDiv.innerHTML = `
                <div class="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div class="bg-white rounded-lg p-3 shadow-sm max-w-xs">
                    ${messageContent}
                </div>
            `;
        }
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    createMedicineInfoCard(medicineInfo) {
        if (!medicineInfo || typeof medicineInfo !== 'object') return '';
        
        let cardHTML = '<div class="mt-3 p-3 bg-emerald-50 rounded-lg border border-emerald-200">';
        cardHTML += '<h4 class="font-semibold text-emerald-800 text-sm mb-2">📋 Medicine Information</h4>';
        
        if (medicineInfo.generic_name) {
            cardHTML += `<p class="text-xs text-gray-700"><strong>Generic Name:</strong> ${medicineInfo.generic_name}</p>`;
        }
        
        if (medicineInfo.brand_names && medicineInfo.brand_names.length > 0) {
            cardHTML += `<p class="text-xs text-gray-700"><strong>Brand Names:</strong> ${medicineInfo.brand_names.join(', ')}</p>`;
        }
        
        if (medicineInfo.uses && medicineInfo.uses.length > 0) {
            cardHTML += `<p class="text-xs text-gray-700"><strong>Uses:</strong> ${medicineInfo.uses.join(', ')}</p>`;
        }
        
        if (medicineInfo.dosage && medicineInfo.dosage.adults) {
            cardHTML += `<p class="text-xs text-gray-700"><strong>Adult Dosage:</strong> ${medicineInfo.dosage.adults}</p>`;
        }
        
        if (medicineInfo.side_effects && medicineInfo.side_effects.length > 0) {
            cardHTML += `<p class="text-xs text-gray-700"><strong>Side Effects:</strong> ${medicineInfo.side_effects.join(', ')}</p>`;
        }
        
        if (medicineInfo.warnings && medicineInfo.warnings.length > 0) {
            cardHTML += `<p class="text-xs text-red-600"><strong>⚠️ Warnings:</strong> ${medicineInfo.warnings.join(', ')}</p>`;
        }
        
        cardHTML += '<p class="text-xs text-red-600 mt-2"><strong>⚠️ Disclaimer:</strong> Always consult healthcare professionals for medical advice.</p>';
        cardHTML += '</div>';
        
        return cardHTML;
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        const messagesContainer = document.getElementById('chatbot-messages');
        
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'flex items-start space-x-3';
        typingDiv.innerHTML = `
            <div class="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            <div class="bg-white rounded-lg p-3 shadow-sm">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                    <div class="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
            </div>
        `;
        
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/history`);
            const data = await response.json();
            
            if (response.ok && data.history) {
                this.conversationHistory = data.history;
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.medicalChatbot = new MedicalChatbot();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MedicalChatbot;
} 