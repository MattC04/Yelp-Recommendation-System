# BELP - AI-Powered Restaurant Recommendation System

## Security-First Approach
BELP prioritizes user privacy and data security. All user data is encrypted and stored locally with comprehensive input validation and XSS protection.

**Security Features:**
- **Data Encryption**: All preferences encrypted before storage
- **XSS Prevention**: Input sanitization and Content Security Policy
- **Input Validation**: Comprehensive validation with length limits
- **Security Headers**: Modern security headers for attack prevention

**For detailed security information, see [SECURITY.md](./SECURITY.md)**

## Quick Start

### Prerequisites
- Node.js 16+ 
- Python 3.8+
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BELP-Recommendation-System
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start Backend Server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000

## Features

### Core Functionality
- **AI-Powered Recommendations**: Machine learning-based restaurant suggestions
- **Smart Onboarding**: Personalized preference collection for new users
- **Location-Based Search**: Find restaurants by city, state, or zipcode
- **Advanced Filtering**: Dietary restrictions, ambiance, price range
- **Personalization Dashboard**: User preference management and insights

### Technical Features
- **Vue.js 3 Frontend**: Modern, responsive web interface
- **FastAPI Backend**: High-performance Python API
- **AI Recommendation Engine**: Content-based filtering and semantic similarity
- **Real-time Feedback Loop**: User interaction tracking for improved suggestions
- **Secure Data Storage**: Encrypted localStorage with comprehensive validation

### Security Features
- **Data Encryption**: Client-side encryption for all user data
- **XSS Prevention**: Input sanitization and Content Security Policy
- **Input Validation**: Comprehensive validation with security limits
- **Security Headers**: Modern security headers for attack prevention

## Project Structure

```
BELP-Recommendation-System/
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main API endpoints
│   ├── requirements.txt    # Python dependencies
│   └── data/              # Restaurant dataset
├── frontend/               # Vue.js frontend application
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page views
│   │   ├── services/       # API and utility services
│   │   └── router/         # Vue router configuration
│   ├── package.json        # Node.js dependencies
│   └── index.html          # Main HTML file
├── SECURITY.md             # Security documentation
└── README.md               # This file
```

## API Endpoints

### Backend API
- `POST /recommend` - Get restaurant recommendations by query
- `POST /recommend-by-location` - Get restaurants by location
- `GET /health` - API health check
- `GET /debug/data` - Debug data inspection

### Frontend Routes
- `/` - Home page with app introduction
- `/search` - Main search interface
- `/profile` - User profile and preferences
- `/share` - Social sharing features

## Development

### Backend Development
- FastAPI with automatic API documentation
- Pandas for data manipulation
- Sentence transformers for semantic similarity
- SQLite for event storage

### Frontend Development
- Vue.js 3 with Composition API
- Vite for fast development builds
- Responsive design with CSS Grid and Flexbox
- Local storage for data persistence

### Security Development
- Custom encryption service for data protection
- Input validation and sanitization
- Content Security Policy implementation
- Security headers and XSS prevention

## Testing

### Manual Testing
1. Test onboarding flow for new users
2. Verify search functionality with various inputs
3. Test profile creation and editing
4. Verify security features (input validation, encryption)

### Security Testing
- Test XSS prevention with script tags
- Verify input length restrictions
- Test encryption/decryption functionality
- Verify CSP headers are working

## Deployment

### Production Checklist
- Enable HTTPS everywhere
- Configure proper CSP headers
- Enable security headers
- Regular dependency updates
- Security monitoring setup

### Environment Variables
```bash
NODE_ENV=production
HTTPS_ENABLED=true
CSP_STRICT=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Security

For security issues or vulnerabilities:
- Do NOT create public GitHub issues
- Contact: security@belp-app.com
- Include detailed description and steps to reproduce

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or support:
- Create a GitHub issue for feature requests
- Check the documentation in SECURITY.md
- Review the code comments for implementation details

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Security Level**: Production-Ready
