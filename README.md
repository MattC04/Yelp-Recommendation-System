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
