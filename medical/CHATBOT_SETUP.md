# MEDicos Medical Chatbot Setup Guide

## Overview

The MEDicos Medical Chatbot is an AI-powered assistant that provides detailed information about medicines, including their uses, side effects, dosages, and warnings. It integrates with medical databases like OpenFDA and RxNorm, and uses AI models (OpenAI GPT or Google Gemini) for natural language understanding.

## Features

- 🤖 **AI-Powered Responses**: Uses OpenAI GPT-3.5 or Google Gemini for natural language processing
- 💊 **Medical Database Integration**: Connects to OpenFDA and RxNorm for accurate medicine information
- 📱 **Professional UI**: Modern, responsive chat interface consistent with MEDicos theme
- 🔒 **Privacy Compliant**: HIPAA-compliant data handling with automatic data retention
- ⚡ **Real-time Responses**: Fast, accurate responses with typing indicators
- 📚 **Comprehensive Information**: Detailed medicine data including dosages, side effects, and warnings

## Prerequisites

- Python 3.8 or higher
- Node.js (for frontend development)
- API keys for AI services (OpenAI or Google Gemini)

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# AI Model API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Database Configuration
DATABASE_URL=your_database_url_here

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

### 3. Get API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

#### Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

## Configuration

### Chatbot Configuration

The chatbot configuration is managed in `chatbot_config.py`. Key settings include:

- **AI Models**: Choose between OpenAI and Google Gemini
- **Medical Databases**: Configure OpenFDA and RxNorm connections
- **Privacy Settings**: Data retention and anonymization settings
- **Rate Limiting**: Control API request limits

### Frontend Configuration

The frontend chatbot is configured in `js/chatbot.js`. Key settings:

- **API Base URL**: Default is `http://localhost:5001/api/chatbot`
- **UI Styling**: Matches MEDicos theme with emerald colors
- **Responsive Design**: Works on all device sizes

## Running the Chatbot

### 1. Start the Backend API

```bash
python chatbot_api.py
```

The API will start on `http://localhost:5001`

### 2. Start the Main Website

```bash
python app.py
```

The website will start on `http://localhost:5000`

### 3. Access the Chatbot

The chatbot will automatically appear as a floating button in the bottom-right corner of all pages.

## Testing

### Run Automated Tests

```bash
python test_chatbot.py
```

This will test:
- Health check endpoint
- Medicine search functionality
- Chat functionality
- Error handling
- Performance metrics

### Manual Testing

1. **Basic Functionality**:
   - Click the chatbot button
   - Ask: "What is paracetamol used for?"
   - Verify response includes medicine information

2. **Medicine Information**:
   - Ask about specific medicines: ibuprofen, amoxicillin, aspirin
   - Check for dosage, side effects, and warnings

3. **Error Handling**:
   - Try asking about non-existent medicines
   - Test with empty messages
   - Verify appropriate error responses

## API Endpoints

### Health Check
```
GET /api/chatbot/health
```
Returns system status and service availability.

### Chat
```
POST /api/chatbot/chat
Content-Type: application/json

{
  "message": "What are the side effects of paracetamol?"
}
```
Processes user messages and returns AI-generated responses.

### Medicine Search
```
GET /api/chatbot/medicines?q=paracetamol
```
Searches for medicine information in databases.

### Chat History
```
GET /api/chatbot/history
```
Returns recent conversation history.

## Medical Database Integration

### OpenFDA Integration
- **URL**: https://api.fda.gov/drug
- **Data**: Drug labels, adverse events, recalls
- **Rate Limit**: 1000 requests per hour
- **Authentication**: None required

### RxNorm Integration
- **URL**: https://rxnav.nlm.nih.gov/REST
- **Data**: Drug names, concepts, relationships
- **Rate Limit**: None specified
- **Authentication**: None required

### Local Database
The chatbot includes a local database of common medicines with:
- Generic and brand names
- Uses and indications
- Dosage information
- Side effects and warnings
- Drug interactions

## Privacy and Compliance

### HIPAA Compliance
- No personal health information is stored
- All data is anonymized
- Automatic data retention (30 days)
- Secure API communication

### Data Handling
- Chat history is stored temporarily
- No personal identifiers are logged
- All responses include medical disclaimers
- Users are advised to consult healthcare professionals

## Customization

### Adding New Medicines

To add medicines to the local database, edit the `_load_medicine_database()` method in `chatbot_api.py`:

```python
def _load_medicine_database(self):
    return {
        "new_medicine": {
            "generic_name": "Generic Name",
            "brand_names": ["Brand1", "Brand2"],
            "uses": ["Use 1", "Use 2"],
            "dosage": {
                "adults": "Dosage for adults",
                "children": "Dosage for children"
            },
            "side_effects": ["Side effect 1", "Side effect 2"],
            "warnings": ["Warning 1", "Warning 2"],
            "interactions": ["Interaction 1", "Interaction 2"]
        }
    }
```

### Customizing AI Responses

Modify the `generate_ai_response()` method to customize AI behavior:

```python
def generate_ai_response(self, user_message, medicine_info=None):
    # Custom system prompt
    system_prompt = "You are a medical assistant for MEDicos pharmacy..."
    
    # Custom response generation logic
    # ...
```

### Styling the Chatbot

Modify the CSS classes in `js/chatbot.js` to match your theme:

```javascript
// Change colors
const chatbotHTML = `
    <div id="medical-chatbot" class="fixed bottom-4 right-4 z-50">
        <div id="chatbot-button" class="bg-your-color hover:bg-your-color-dark">
        // ...
`;
```

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Check if the chatbot server is running
   - Verify API keys are set correctly
   - Check network connectivity

2. **No AI Responses**
   - Verify OpenAI or Google API keys
   - Check API quota limits
   - Review error logs

3. **Medicine Information Not Found**
   - Check spelling of medicine names
   - Verify database connections
   - Add medicines to local database

4. **Frontend Issues**
   - Check browser console for errors
   - Verify JavaScript is loaded
   - Clear browser cache

### Debug Mode

Enable debug logging by setting in `chatbot_config.py`:

```python
LOG_LEVEL = "DEBUG"
```

### Logs

Check the following log files:
- `chatbot.log`: Chatbot API logs
- Browser console: Frontend errors
- Flask logs: Main application logs

## Performance Optimization

### Caching
- Medicine information is cached locally
- AI responses can be cached (implement as needed)
- Database queries are optimized

### Rate Limiting
- Configure rate limits in `chatbot_config.py`
- Monitor API usage
- Implement request queuing if needed

### Database Optimization
- Use connection pooling
- Implement query caching
- Optimize database indexes

## Security Considerations

### API Security
- Validate all input data
- Implement rate limiting
- Use HTTPS in production
- Sanitize user inputs

### Data Protection
- Encrypt sensitive data
- Implement access controls
- Regular security audits
- Monitor for suspicious activity

## Deployment

### Production Setup

1. **Environment Variables**:
   ```env
   OPENAI_API_KEY=your_production_key
   GOOGLE_API_KEY=your_production_key
   LOG_LEVEL=WARNING
   ```

2. **Server Configuration**:
   - Use production WSGI server (Gunicorn)
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

3. **Database Setup**:
   - Use production database
   - Configure backups
   - Set up monitoring

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "chatbot_api.py"]
```

## Support and Maintenance

### Regular Maintenance
- Update dependencies regularly
- Monitor API usage and costs
- Review and update medicine database
- Check for security updates

### Monitoring
- Monitor API response times
- Track error rates
- Monitor user satisfaction
- Review chat logs for improvements

### Updates
- Keep AI models updated
- Add new medicines to database
- Improve response quality
- Add new features based on user feedback

## License and Legal

### Medical Disclaimer
This chatbot provides educational information only and should not replace professional medical advice. Users should always consult healthcare professionals for medical decisions.

### Terms of Use
- Information is for educational purposes only
- No medical advice is provided
- Users are responsible for their own health decisions
- MEDicos is not liable for any decisions made based on chatbot responses

## Contact

For support or questions about the medical chatbot:
- Technical issues: Check troubleshooting section
- Medical information: Consult healthcare professionals
- Feature requests: Contact development team

---

**⚠️ Important**: This chatbot is designed for educational purposes only. Always consult healthcare professionals for medical advice and treatment decisions. 