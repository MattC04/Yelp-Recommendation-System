Setup Google Maps API for the Map View

1) Create a frontend/.env file with:

VITE_GOOGLE_MAPS_API_KEY=YOUR_KEY_HERE

2) Restart the frontend dev server:

npm run dev

3) In the app, run a search and switch to the Map view. The map centers on Los Angeles by default or on your Near input if provided.

Notes
- Markers only appear for results that include latitude/longitude from the backend.
- You can also pass an apiKey prop directly to MapResults if you prefer not to use .env.
