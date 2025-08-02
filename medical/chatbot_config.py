import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't exist
try:
    load_dotenv()
except:
    pass

class ChatbotConfig:
    """Configuration class for the medical chatbot"""
    
    # AI Model Configuration
    # You can add your API keys directly here instead of using .env file
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or "your_openai_api_key_here"
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') or "AIzaSyAwukn5kBLRqszJflBSYoRG-pTL9q2lR2I"
    OPENAI_MODEL = "gpt-3.5-turbo"
    GEMINI_MODEL = "gemini-pro"
    
    # Medical Database Configuration
    OPENFDA_BASE_URL = "https://api.fda.gov/drug"
    RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    DRUGBANK_BASE_URL = "https://api.drugbank.com/v1"
    
    # API Configuration
    API_HOST = "localhost"
    API_PORT = 5001
    API_DEBUG = True
    CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000"]
    
    # Privacy and Compliance
    DATA_RETENTION_DAYS = 30  # How long to keep chat history
    ANONYMIZE_DATA = True     # Remove personal information
    HIPAA_COMPLIANT = True    # Ensure HIPAA compliance
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_HOUR = 1000
    
    # Medical Disclaimer
    MEDICAL_DISCLAIMER = """
    ⚠️ IMPORTANT MEDICAL DISCLAIMER:
    
    This chatbot provides general information about medicines for educational purposes only. 
    The information provided is not intended to:
    - Replace professional medical advice
    - Diagnose medical conditions
    - Prescribe medications
    - Treat medical conditions
    
    Always consult with:
    - Your healthcare provider
    - A licensed pharmacist
    - Your doctor
    
    For medical emergencies, call emergency services immediately.
    
    MEDicos is not responsible for any decisions made based on this information.
    """
    
    # Supported Medicine Categories
    MEDICINE_CATEGORIES = [
        "Pain Relief",
        "Antibiotics",
        "Antihistamines",
        "Antacids",
        "Vitamins",
        "Supplements",
        "Prescription Drugs",
        "Over-the-Counter"
    ]
    
    # Common Medicine Names (for local database)
    COMMON_MEDICINES = {
        "paracetamol": {
            "generic_name": "Acetaminophen",
            "category": "Pain Relief",
            "otc": True
        },
        "ibuprofen": {
            "generic_name": "Ibuprofen",
            "category": "Pain Relief",
            "otc": True
        },
        "aspirin": {
            "generic_name": "Acetylsalicylic Acid",
            "category": "Pain Relief",
            "otc": True
        },
        "amoxicillin": {
            "generic_name": "Amoxicillin",
            "category": "Antibiotics",
            "otc": False
        },
        "cetirizine": {
            "generic_name": "Cetirizine",
            "category": "Antihistamines",
            "otc": True
        },
        "omeprazole": {
            "generic_name": "Omeprazole",
            "category": "Antacids",
            "otc": True
        }
    }
    
    # Response Templates
    RESPONSE_TEMPLATES = {
        "welcome": "Hello! I'm your MEDicos medical assistant. I can help you with information about medicines, their uses, side effects, and dosages. ⚠️ Important: This information is for educational purposes only. Always consult healthcare professionals for medical advice.",
        "not_found": "I couldn't find specific information about that medicine. Please check the spelling or try a different name. For accurate medical information, please consult a healthcare professional.",
        "error": "I apologize, but I encountered an error. Please try again or consult a healthcare professional for immediate assistance.",
        "disclaimer": "⚠️ Disclaimer: This information is for educational purposes only. Always consult healthcare professionals for medical advice.",
        "emergency": "🚨 If you're experiencing a medical emergency, please call emergency services immediately. This chatbot cannot provide emergency medical assistance."
    }
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "chatbot.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate_config(cls):
        """Validate the configuration"""
        errors = []
        
        if not cls.OPENAI_API_KEY and not cls.GOOGLE_API_KEY:
            errors.append("At least one AI API key (OpenAI or Google) is required")
        
        if cls.API_PORT < 1024 or cls.API_PORT > 65535:
            errors.append("API port must be between 1024 and 65535")
        
        if cls.MAX_REQUESTS_PER_MINUTE <= 0:
            errors.append("Rate limiting must be positive")
        
        return errors
    
    @classmethod
    def get_ai_config(cls):
        """Get AI configuration"""
        return {
            "openai": {
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "enabled": bool(cls.OPENAI_API_KEY)
            },
            "gemini": {
                "api_key": cls.GOOGLE_API_KEY,
                "model": cls.GEMINI_MODEL,
                "enabled": bool(cls.GOOGLE_API_KEY)
            }
        }
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration"""
        return {
            "openfda": {
                "base_url": cls.OPENFDA_BASE_URL,
                "enabled": True
            },
            "rxnorm": {
                "base_url": cls.RXNORM_BASE_URL,
                "enabled": True
            },
            "drugbank": {
                "base_url": cls.DRUGBANK_BASE_URL,
                "enabled": False  # Requires API key
            }
        } 