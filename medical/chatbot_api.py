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

# Load environment variables (optional)
try:
    load_dotenv()
except:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for development

# Configure AI models (with fallback for missing keys)
openai_api_key = os.getenv('OPENAI_API_KEY') or "your_openai_api_key_here"
google_api_key = os.getenv('GOOGLE_API_KEY') or "your_google_api_key_here"

openai.api_key = openai_api_key
genai.configure(api_key=google_api_key)

# Medical databases configuration
OPENFDA_BASE_URL = "https://api.fda.gov/drug"
RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

class MedicalChatbot:
    def __init__(self):
        self.conversation_history = []
        self.medicine_database = self._load_medicine_database()
        
    def _load_medicine_database(self):
        """Load comprehensive local medicine database"""
        return {
            # Pain Relief & Anti-inflammatory Drugs
            "paracetamol": {
                "generic_name": "Acetaminophen",
                "brand_names": ["Tylenol", "Panadol", "Calpol"],
                "category": "Pain Relief & Anti-inflammatory",
                "uses": ["Fever", "Mild pain"],
                "dosage": {
                    "adults": "500mg–1g every 4–6 hours (max 4g/day)",
                    "children": "10-15mg/kg every 4-6 hours"
                },
                "side_effects": ["Liver damage (overdose)", "Rash"],
                "warnings": ["Do not exceed recommended dose", "Avoid alcohol", "Consult doctor if pregnant"],
                "interactions": ["Blood thinners", "Alcohol", "Other pain medications"]
            },
            "acetaminophen": {
                "generic_name": "Acetaminophen",
                "brand_names": ["Tylenol", "Panadol", "Calpol"],
                "category": "Pain Relief & Anti-inflammatory",
                "uses": ["Fever", "Mild pain"],
                "dosage": {
                    "adults": "500mg–1g every 4–6 hours (max 4g/day)",
                    "children": "10-15mg/kg every 4-6 hours"
                },
                "side_effects": ["Liver damage (overdose)", "Rash"],
                "warnings": ["Do not exceed recommended dose", "Avoid alcohol", "Consult doctor if pregnant"],
                "interactions": ["Blood thinners", "Alcohol", "Other pain medications"]
            },
            "ibuprofen": {
                "generic_name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin", "Brufen"],
                "category": "Pain Relief & Anti-inflammatory",
                "uses": ["Pain", "Inflammation", "Fever"],
                "dosage": {
                    "adults": "200–400mg every 4–6 hours",
                    "children": "5-10mg/kg every 6-8 hours"
                },
                "side_effects": ["Stomach ulcers", "Kidney issues"],
                "warnings": ["Take with food", "Avoid if stomach ulcers", "Consult doctor if pregnant"],
                "interactions": ["Blood thinners", "Aspirin", "ACE inhibitors"]
            },
            "aspirin": {
                "generic_name": "Acetylsalicylic Acid",
                "brand_names": ["Bayer", "Ecotrin"],
                "category": "Pain Relief & Anti-inflammatory",
                "uses": ["Pain", "Fever", "Blood thinner"],
                "dosage": {
                    "adults": "325–650mg every 4–6 hours",
                    "children": "Not recommended for children under 16"
                },
                "side_effects": ["Bleeding risk", "Stomach irritation"],
                "warnings": ["Avoid in children with viral infections", "Take with food", "Consult doctor before use"],
                "interactions": ["Blood thinners", "Other NSAIDs", "Alcohol"]
            },
            "naproxen": {
                "generic_name": "Naproxen",
                "brand_names": ["Aleve", "Naprosyn"],
                "category": "Pain Relief & Anti-inflammatory",
                "uses": ["Arthritis", "Menstrual pain"],
                "dosage": {
                    "adults": "250–500mg twice daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Heartburn", "Dizziness"],
                "warnings": ["Take with food", "Avoid if stomach ulcers", "Monitor for heart issues"],
                "interactions": ["Blood thinners", "Other NSAIDs", "ACE inhibitors"]
            },
            
            # Antibiotics
            "amoxicillin": {
                "generic_name": "Amoxicillin",
                "brand_names": ["Amoxil", "Trimox"],
                "category": "Antibiotics",
                "uses": ["Bacterial infections (ear, throat)"],
                "dosage": {
                    "adults": "250–500mg every 8 hours",
                    "children": "20-40mg/kg/day divided every 8 hours"
                },
                "side_effects": ["Diarrhea", "Allergic reactions"],
                "warnings": ["Complete full course", "Take on empty stomach", "Avoid if allergic to penicillin"],
                "interactions": ["Birth control pills", "Blood thinners", "Probenecid"]
            },
            "azithromycin": {
                "generic_name": "Azithromycin",
                "brand_names": ["Zithromax", "Z-Pak"],
                "category": "Antibiotics",
                "uses": ["Respiratory infections"],
                "dosage": {
                    "adults": "500mg once daily for 3 days",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Nausea", "Abdominal pain"],
                "warnings": ["Complete full course", "Take on empty stomach", "Avoid if allergic to macrolides"],
                "interactions": ["Antacids", "Blood thinners", "Other antibiotics"]
            },
            "ciprofloxacin": {
                "generic_name": "Ciprofloxacin",
                "brand_names": ["Cipro"],
                "category": "Antibiotics",
                "uses": ["UTI", "Bacterial diarrhea"],
                "dosage": {
                    "adults": "250–750mg twice daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Tendon rupture (rare)", "Nausea"],
                "warnings": ["Avoid sunlight", "Stay hydrated", "Complete full course"],
                "interactions": ["Antacids", "Iron supplements", "Calcium supplements"]
            },
            "doxycycline": {
                "generic_name": "Doxycycline",
                "brand_names": ["Vibramycin", "Doryx"],
                "category": "Antibiotics",
                "uses": ["Acne", "Malaria prophylaxis"],
                "dosage": {
                    "adults": "100mg twice daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Sun sensitivity", "Yeast infections"],
                "warnings": ["Avoid sunlight", "Take on empty stomach", "Use sunscreen"],
                "interactions": ["Antacids", "Iron supplements", "Calcium supplements"]
            },
            
            # Antihypertensives
            "losartan": {
                "generic_name": "Losartan",
                "brand_names": ["Cozaar"],
                "category": "Antihypertensives",
                "uses": ["High BP", "Kidney protection in diabetes"],
                "dosage": {
                    "adults": "25–100mg once daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Dizziness", "High potassium"],
                "warnings": ["Monitor blood pressure", "Avoid during pregnancy", "Regular kidney function tests"],
                "interactions": ["Potassium supplements", "Lithium", "NSAIDs"]
            },
            "amlodipine": {
                "generic_name": "Amlodipine",
                "brand_names": ["Norvasc"],
                "category": "Antihypertensives",
                "uses": ["Hypertension", "Angina"],
                "dosage": {
                    "adults": "5–10mg once daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Swelling in ankles", "Headache"],
                "warnings": ["Monitor blood pressure", "Gradual dose increase", "Avoid grapefruit"],
                "interactions": ["Grapefruit juice", "Other blood pressure medications", "Simvastatin"]
            },
            "metoprolol": {
                "generic_name": "Metoprolol",
                "brand_names": ["Lopressor", "Toprol XL"],
                "category": "Antihypertensives",
                "uses": ["High BP", "Heart rhythm disorders"],
                "dosage": {
                    "adults": "25–100mg twice daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Fatigue", "Cold hands/feet"],
                "warnings": ["Do not stop suddenly", "Monitor heart rate", "Avoid during pregnancy"],
                "interactions": ["Other beta-blockers", "Calcium channel blockers", "Digoxin"]
            },
            
            # Antidiabetics
            "metformin": {
                "generic_name": "Metformin",
                "brand_names": ["Glucophage", "Fortamet"],
                "category": "Antidiabetics",
                "uses": ["Type 2 diabetes"],
                "dosage": {
                    "adults": "500–2000mg/day in divided doses",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Diarrhea", "Vitamin B12 deficiency"],
                "warnings": ["Take with food", "Monitor blood sugar", "Avoid alcohol"],
                "interactions": ["Alcohol", "Other diabetes medications", "Contrast dye"]
            },
            "glimepiride": {
                "generic_name": "Glimepiride",
                "brand_names": ["Amaryl"],
                "category": "Antidiabetics",
                "uses": ["Lowers blood sugar"],
                "dosage": {
                    "adults": "1–4mg once daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Hypoglycemia", "Weight gain"],
                "warnings": ["Monitor blood sugar", "Take with food", "Carry glucose tablets"],
                "interactions": ["Other diabetes medications", "Alcohol", "Beta-blockers"]
            },
            
            # Antidepressants
            "sertraline": {
                "generic_name": "Sertraline",
                "brand_names": ["Zoloft"],
                "category": "Antidepressants",
                "uses": ["Depression", "Anxiety"],
                "dosage": {
                    "adults": "50–200mg once daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Insomnia", "Sexual dysfunction"],
                "warnings": ["Gradual dose increase", "Monitor for suicidal thoughts", "Avoid alcohol"],
                "interactions": ["MAO inhibitors", "Other antidepressants", "Blood thinners"]
            },
            "fluoxetine": {
                "generic_name": "Fluoxetine",
                "brand_names": ["Prozac"],
                "category": "Antidepressants",
                "uses": ["Depression", "OCD"],
                "dosage": {
                    "adults": "20–80mg once daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Headache", "Weight changes"],
                "warnings": ["Gradual dose increase", "Monitor for suicidal thoughts", "Long half-life"],
                "interactions": ["MAO inhibitors", "Other antidepressants", "Blood thinners"]
            },
            
            # Gastrointestinal Drugs
            "omeprazole": {
                "generic_name": "Omeprazole",
                "brand_names": ["Prilosec"],
                "category": "Gastrointestinal Drugs",
                "uses": ["Acid reflux", "Ulcers"],
                "dosage": {
                    "adults": "20–40mg once daily",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Headache", "Diarrhea"],
                "warnings": ["Take before meals", "Long-term use may affect bone health", "Monitor magnesium levels"],
                "interactions": ["Iron supplements", "Vitamin B12", "Blood thinners"]
            },
            
            # Antihistamines
            "cetirizine": {
                "generic_name": "Cetirizine",
                "brand_names": ["Zyrtec"],
                "category": "Antihistamines",
                "uses": ["Allergies", "Itching"],
                "dosage": {
                    "adults": "10mg once daily",
                    "children": "5mg once daily (6-12 years)"
                },
                "side_effects": ["Drowsiness (rare)", "Dry mouth"],
                "warnings": ["May cause drowsiness", "Avoid alcohol", "Take in evening if drowsy"],
                "interactions": ["Alcohol", "Other sedatives", "Antidepressants"]
            },
            "loratadine": {
                "generic_name": "Loratadine",
                "brand_names": ["Claritin"],
                "category": "Antihistamines",
                "uses": ["Non-drowsy allergy relief"],
                "dosage": {
                    "adults": "10mg once daily",
                    "children": "5mg once daily (2-12 years)"
                },
                "side_effects": ["Headache", "Nervousness"],
                "warnings": ["Generally non-drowsy", "Take with or without food", "Monitor for side effects"],
                "interactions": ["Few interactions", "Generally safe with most medications"]
            },
            
            # Steroids
            "prednisone": {
                "generic_name": "Prednisone",
                "brand_names": ["Deltasone", "Prednisone Intensol"],
                "category": "Steroids",
                "uses": ["Inflammation", "Autoimmune diseases"],
                "dosage": {
                    "adults": "5–60mg/day (tapered)",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Weight gain", "Osteoporosis"],
                "warnings": ["Do not stop suddenly", "Take with food", "Monitor blood sugar"],
                "interactions": ["Blood thinners", "Diabetes medications", "NSAIDs"]
            },
            
            # Antacids
            "aluminum hydroxide": {
                "generic_name": "Aluminum Hydroxide",
                "brand_names": ["Amphojel", "AlternaGEL"],
                "category": "Antacids",
                "uses": ["Heartburn", "Acid indigestion"],
                "dosage": {
                    "adults": "500–1500mg as needed",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Constipation"],
                "warnings": ["Take 1-2 hours after other medications", "Monitor for constipation", "Not for long-term use"],
                "interactions": ["Many medications", "Take separately from other drugs", "May affect absorption"]
            },
            
            # Antifungals
            "fluconazole": {
                "generic_name": "Fluconazole",
                "brand_names": ["Diflucan"],
                "category": "Antifungals",
                "uses": ["Yeast infections"],
                "dosage": {
                    "adults": "150mg single dose (for thrush)",
                    "children": "Consult healthcare provider"
                },
                "side_effects": ["Liver enzyme changes"],
                "warnings": ["Monitor liver function", "Take with or without food", "Complete full course"],
                "interactions": ["Blood thinners", "Diabetes medications", "Other antifungals"]
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
                if openai.api_key and openai.api_key != "your_openai_api_key_here":
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
                if google_api_key and google_api_key != "your_google_api_key_here":
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
        """Extract potential medicine names from text with flexible matching"""
        text_lower = text.lower()
        medicine_names = []
        
        # Direct matches
        for medicine_name in self.medicine_database.keys():
            if medicine_name in text_lower:
                medicine_names.append(medicine_name)
        
        # Brand name matches
        for medicine_name, medicine_data in self.medicine_database.items():
            if 'brand_names' in medicine_data:
                for brand_name in medicine_data['brand_names']:
                    if brand_name.lower() in text_lower:
                        medicine_names.append(medicine_name)
        
        # Generic name matches
        for medicine_name, medicine_data in self.medicine_database.items():
            if 'generic_name' in medicine_data:
                generic_name = medicine_data['generic_name'].lower()
                if generic_name in text_lower:
                    medicine_names.append(medicine_name)
        
        # Category-based matching
        category_keywords = {
            "pain": ["paracetamol", "acetaminophen", "ibuprofen", "aspirin", "naproxen"],
            "fever": ["paracetamol", "acetaminophen", "ibuprofen", "aspirin"],
            "antibiotic": ["amoxicillin", "azithromycin", "ciprofloxacin", "doxycycline"],
            "blood pressure": ["losartan", "amlodipine", "metoprolol"],
            "diabetes": ["metformin", "glimepiride"],
            "depression": ["sertraline", "fluoxetine"],
            "allergy": ["cetirizine", "loratadine"],
            "acid": ["omeprazole", "aluminum hydroxide"],
            "yeast": ["fluconazole"],
            "inflammation": ["prednisone", "ibuprofen", "naproxen"]
        }
        
        for keyword, medicines in category_keywords.items():
            if keyword in text_lower:
                for medicine in medicines:
                    if medicine not in medicine_names:
                        medicine_names.append(medicine)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_medicine_names = []
        for medicine in medicine_names:
            if medicine not in seen:
                seen.add(medicine)
                unique_medicine_names.append(medicine)
        
        return unique_medicine_names

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
    app.run(debug=True, host='0.0.0.0', port=5001) 