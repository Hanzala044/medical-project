import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import google.generativeai as genai
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure AI models
openai.api_key = os.getenv('OPENAI_API_KEY')
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Medical databases configuration
OPENFDA_BASE_URL = "https://api.fda.gov/drug"
RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

class MedicalChatbot:
    def __init__(self):
        self.conversation_history = []
        self.medicine_database = self._load_medicine_database()
        
    def _load_medicine_database(self):
        """Load local medicine database with common medications"""
        return {
            "paracetamol": {
                "generic_name": "Acetaminophen",
                "brand_names": ["Tylenol", "Panadol", "Calpol"],
                "uses": ["Pain relief", "Fever reduction"],
                "dosage": {
                    "adults": "500-1000mg every 4-6 hours, max 4000mg/day",
                    "children": "10-15mg/kg every 4-6 hours"
                },
                "side_effects": ["Nausea", "Liver problems (high doses)", "Allergic reactions"],
                "warnings": ["Do not exceed recommended dose", "Avoid alcohol", "Consult doctor if pregnant"],
                "interactions": ["Blood thinners", "Alcohol", "Other pain medications"]
            },
            "ibuprofen": {
                "generic_name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin", "Brufen"],
                "uses": ["Pain relief", "Inflammation reduction", "Fever"],
                "dosage": {
                    "adults": "200-400mg every 4-6 hours, max 1200mg/day",
                    "children": "5-10mg/kg every 6-8 hours"
                },
                "side_effects": ["Stomach upset", "Dizziness", "Increased bleeding risk"],
                "warnings": ["Take with food", "Avoid if stomach ulcers", "Consult doctor if pregnant"],
                "interactions": ["Blood thinners", "Aspirin", "ACE inhibitors"]
            },
            "amoxicillin": {
                "generic_name": "Amoxicillin",
                "brand_names": ["Amoxil", "Trimox"],
                "uses": ["Bacterial infections", "Respiratory infections", "Ear infections"],
                "dosage": {
                    "adults": "250-500mg every 8 hours",
                    "children": "20-40mg/kg/day divided every 8 hours"
                },
                "side_effects": ["Diarrhea", "Nausea", "Rash", "Yeast infection"],
                "warnings": ["Complete full course", "Take on empty stomach", "Avoid if allergic to penicillin"],
                "interactions": ["Birth control pills", "Blood thinners", "Probenecid"]
            }
        }
    
    def search_openfda(self, drug_name):
        """Search FDA database for drug information"""
        try:
            url = f"{OPENFDA_BASE_URL}/label.json"
            params = {
                "search": f"openfda.generic_name:{drug_name} OR openfda.brand_name:{drug_name}",
                "limit": 1
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    return data['results'][0]
            return None
        except Exception as e:
            logger.error(f"Error searching OpenFDA: {e}")
            return None
    
    def search_rxnorm(self, drug_name):
        """Search RxNorm database for drug information"""
        try:
            # Search for drug concepts
            url = f"{RXNORM_BASE_URL}/drugs.json"
            params = {"name": drug_name}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('drugGroup', {}).get('conceptGroup'):
                    return data['drugGroup']['conceptGroup']
            return None
        except Exception as e:
            logger.error(f"Error searching RxNorm: {e}")
            return None
    
    def get_medicine_info(self, drug_name):
        """Get comprehensive medicine information from multiple sources"""
        drug_name_lower = drug_name.lower()
        
        # Check local database first
        if drug_name_lower in self.medicine_database:
            return self.medicine_database[drug_name_lower]
        
        # Search external databases
        fda_data = self.search_openfda(drug_name)
        rxnorm_data = self.search_rxnorm(drug_name)
        
        # Combine and format data
        medicine_info = {
            "name": drug_name,
            "sources": []
        }
        
        if fda_data:
            medicine_info["sources"].append("FDA")
            # Extract relevant FDA information
            if 'openfda' in fda_data:
                openfda = fda_data['openfda']
                medicine_info.update({
                    "generic_name": openfda.get('generic_name', [drug_name])[0] if openfda.get('generic_name') else drug_name,
                    "brand_names": openfda.get('brand_name', []),
                    "manufacturer": openfda.get('manufacturer_name', [])[0] if openfda.get('manufacturer_name') else "Unknown"
                })
        
        if rxnorm_data:
            medicine_info["sources"].append("RxNorm")
        
        return medicine_info
    
    def generate_ai_response(self, user_message, medicine_info=None):
        """Generate AI-powered response using OpenAI or Google Gemini"""
        try:
            # Prepare context for AI
            context = f"""
            You are a medical chatbot assistant for MEDicos pharmacy. 
            Provide helpful, accurate, and safe information about medicines.
            Always remind users to consult healthcare professionals for medical advice.
            
            User question: {user_message}
            """
            
            if medicine_info:
                context += f"\nMedicine information: {json.dumps(medicine_info, indent=2)}"
            
            # Try OpenAI first, fallback to Google Gemini
            try:
                if openai.api_key:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful medical assistant. Always provide accurate information and recommend consulting healthcare professionals."},
                            {"role": "user", "content": context}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI error: {e}")
            
            # Fallback to Google Gemini
            try:
                if os.getenv('GOOGLE_API_KEY'):
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(context)
                    return response.text
            except Exception as e:
                logger.warning(f"Google Gemini error: {e}")
            
            # Fallback response
            return self._generate_fallback_response(user_message, medicine_info)
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble processing your request. Please try again or consult a healthcare professional."
    
    def _generate_fallback_response(self, user_message, medicine_info):
        """Generate a fallback response when AI services are unavailable"""
        if medicine_info and isinstance(medicine_info, dict):
            if "uses" in medicine_info:
                return f"""
                Based on available information about {medicine_info.get('generic_name', 'this medication')}:
                
                **Uses:** {', '.join(medicine_info['uses'])}
                **Dosage:** {medicine_info['dosage'].get('adults', 'Consult healthcare provider')}
                **Side Effects:** {', '.join(medicine_info['side_effects'])}
                **Warnings:** {', '.join(medicine_info['warnings'])}
                
                ⚠️ **Important:** This information is for educational purposes only. Always consult a healthcare professional for medical advice.
                """
        
        return f"""
        I understand you're asking about: "{user_message}"
        
        While I can provide general information, for specific medical advice, please:
        1. Consult a healthcare professional
        2. Speak with a pharmacist
        3. Contact your doctor
        
        For immediate medical concerns, please seek professional medical attention.
        """
    
    def process_message(self, user_message):
        """Process user message and return appropriate response"""
        try:
            # Extract medicine names from user message
            medicine_names = self._extract_medicine_names(user_message)
            
            # Get medicine information
            medicine_info = None
            if medicine_names:
                medicine_info = self.get_medicine_info(medicine_names[0])
            
            # Generate AI response
            ai_response = self.generate_ai_response(user_message, medicine_info)
            
            # Store conversation
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "bot_response": ai_response,
                "medicine_info": medicine_info
            }
            self.conversation_history.append(conversation_entry)
            
            return {
                "response": ai_response,
                "medicine_info": medicine_info,
                "timestamp": conversation_entry["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again or consult a healthcare professional.",
                "medicine_info": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_medicine_names(self, text):
        """Extract potential medicine names from text"""
        # Simple extraction - can be enhanced with NLP
        words = text.lower().split()
        medicine_names = []
        
        for word in words:
            # Check if word exists in our database
            if word in self.medicine_database:
                medicine_names.append(word)
        
        return medicine_names

# Initialize chatbot
chatbot = MedicalChatbot()

@app.route('/api/chatbot/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Process message
        result = chatbot.process_message(user_message)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/chatbot/medicines', methods=['GET'])
def search_medicines():
    """Search for medicines"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        medicine_info = chatbot.get_medicine_info(query)
        
        return jsonify({
            "query": query,
            "medicine_info": medicine_info
        })
        
    except Exception as e:
        logger.error(f"Error in medicines endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/chatbot/history', methods=['GET'])
def get_chat_history():
    """Get chat history"""
    try:
        return jsonify({
            "history": chatbot.conversation_history[-10:]  # Last 10 messages
        })
        
    except Exception as e:
        logger.error(f"Error in history endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/chatbot/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "openai": bool(openai.api_key),
            "google_gemini": bool(os.getenv('GOOGLE_API_KEY')),
            "openfda": True,
            "rxnorm": True
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 