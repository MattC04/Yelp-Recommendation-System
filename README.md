# BELP

A restaurant recommendation app that learns your preferences and suggests places you'll actually like.

## What it does

BELP uses AI to figure out what kind of restaurants you enjoy and recommends new places based on your taste. Instead of generic suggestions, it learns from your choices and gets better over time.

## Getting started

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The app will be running at http://localhost:5173

## How it works

When you first use BELP, it asks you about your food preferences - what cuisines you like, your budget, dining occasions, and any dietary restrictions. This creates your profile.

As you search for restaurants and interact with recommendations, the AI learns your patterns and gets better at suggesting places you'll enjoy. It tracks things like:
- What cuisines you search for most
- When you typically dine out
- What price ranges you prefer
- How you rate different types of restaurants

## Recommendation System Deep Dive

### Data Processing Pipeline

**1. Data Cleaning & Validation**
The system starts with raw restaurant data (name, address, cuisine, ratings, reviews) and cleans it through several steps:

- **Text normalization**: Standardizes cuisine names, removes duplicates, fixes typos
- **Data validation**: Ensures ratings are 1-5, prices are valid ranges, addresses are complete
- **Missing data handling**: Fills gaps with reasonable defaults or removes incomplete entries
- **Outlier detection**: Removes restaurants with suspicious ratings or review counts

**2. Feature Engineering**
For each restaurant, the system creates numerical features:
- **Cuisine encoding**: Converts text cuisine names to numerical vectors
- **Rating normalization**: Scales ratings to account for different rating distributions
- **Review sentiment**: Analyzes review text to extract positive/negative sentiment scores
- **Location features**: Encodes city/state information for geographic relevance

**3. AI Learning Process**
The recommendation engine uses multiple approaches:

**Content-based filtering**: 
- Analyzes your selected cuisines, budget, and dietary preferences
- Matches restaurants with similar characteristics to what you've liked before
- Uses semantic similarity to find restaurants even if exact cuisine matches aren't available

**Collaborative filtering**:
- Learns from your interactions (clicks, likes, search patterns)
- Builds a user preference profile based on your behavior
- Adjusts recommendations as you use the app more

**Hybrid approach**:
- Combines content and collaborative filtering for better accuracy
- Weights different signals based on how much data is available
- Falls back to content-based when there's limited user data

### How Recommendations Improve Over Time

**Initial recommendations** (0-5 interactions):
- Based purely on your onboarding preferences
- Uses content-based filtering with cuisine and budget matching
- May be somewhat generic but relevant to your stated preferences

**Learning phase** (5-20 interactions):
- Starts incorporating your actual behavior
- Learns which cuisines you actually search for vs. just said you liked
- Begins to understand your real budget preferences and dining patterns

**Mature recommendations** (20+ interactions):
- Highly personalized based on your actual behavior
- Can suggest restaurants you might not have considered
- Learns subtle preferences (e.g., you prefer casual Italian over fancy Italian)
- Adapts to seasonal changes and new preferences

### Data Validation & Security

**Input validation**:
- Search queries are sanitized to prevent XSS attacks
- Location inputs are restricted to safe characters
- Preference selections have reasonable limits (max 15 cuisines, 10 occasions)

**Data integrity**:
- All user preferences are encrypted before storage
- Validation ensures data meets expected formats before processing
- Fallback handling for corrupted or invalid data

**Privacy protection**:
- All learning happens locally on your device
- No personal data is sent to external servers
- Your preference patterns stay private

## Features

- **Smart onboarding** - Quick preference quiz to get started
- **Location search** - Find restaurants by city, state, or zipcode
- **AI recommendations** - Personalized suggestions that improve over time
- **Advanced filters** - Dietary restrictions, ambiance, price range
- **Personal dashboard** - See your preferences and how the AI is learning
- **Secure storage** - Your data is encrypted and stored locally

## Tech stack

**Backend**: FastAPI, Python, Pandas, machine learning for recommendations
**Frontend**: Vue.js 3, modern CSS, responsive design
**Security**: Client-side encryption, input validation, XSS protection

## Project structure

```
├── backend/          # Python API server
├── frontend/         # Vue.js web app
├── data/            # Restaurant dataset
└── docs/            # Documentation
```

## Security

Your data stays on your device and is encrypted. We don't collect or store personal information on our servers. The app includes security measures to prevent common web attacks.

## Contributing

Found a bug or want to add a feature? Open an issue or submit a pull request. This is a learning project, so contributions are welcome.

## License

MIT License - feel free to use this code for your own projects.

---

Built as a learning project to explore AI recommendation systems and modern web development.
