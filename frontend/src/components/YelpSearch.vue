<template>
  <div class="search-container">
    <!-- Logo and Title Section -->
    <div class="logo-section">
      <div class="logo">🍽️</div>
      <h1 class="app-title">BELP</h1>
      <h2 class="main-heading">Find the Best Restaurants</h2>
    </div>

    <!-- Location Search Section -->
    <div class="search-section">
      <label class="search-label">Enter Your Location</label>
      <div class="input-button-group">
        <input 
          v-model="location" 
          @keyup.enter="searchByLocation"
          type="text" 
          placeholder="Enter city, state, or zip code..." 
          class="location-input"
        >
        <button @click="searchByLocation" class="search-btn">Find Top Restaurants</button>
      </div>
    </div>

    <!-- Craving Search Section -->
    <div class="search-section">
      <label class="search-label">Or Search by Craving</label>
      <div class="input-button-group">
        <input 
          v-model="query" 
          @keyup.enter="searchByCraving"
          type="text" 
          placeholder="Type your craving or occasion..." 
          class="craving-input"
        >
        <button @click="searchByCraving" class="search-btn">Search</button>
      </div>
    </div>

    <!-- Results Section -->
    <div v-if="results.length > 0" class="results-section">
      <h3 class="results-title">{{ resultsTitle }}</h3>
      <div class="results-list">
        <div v-for="restaurant in results" :key="restaurant.name" class="restaurant-card">
          <h4 class="restaurant-name">{{ restaurant.name }}</h4>
          <p class="restaurant-address">{{ restaurant.address }}</p>
          <p class="restaurant-stars">⭐ {{ restaurant.stars }}/5</p>
          <p class="restaurant-categories">{{ restaurant.categories }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const location = ref('')
const query = ref('')
const results = ref([])
const loading = ref(false)
const error = ref('')
const resultsTitle = ref('')

const searchByLocation = async () => {
  if (!location.value.trim()) return
  loading.value = true
  error.value = ''
  results.value = []
  resultsTitle.value = `Top 10 Restaurants in ${location.value}`
  
  try {
    const res = await axios.post('http://localhost:8000/recommend-by-location', { 
      location: location.value 
    })
    results.value = res.data
    if (!results.value.length) error.value = 'No restaurants found in this location.'
  } catch (e) {
    error.value = 'Error fetching recommendations.'
  } finally {
    loading.value = false
  }
}

const searchByCraving = async () => {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  results.value = []
  resultsTitle.value = `Recommendations for: ${query.value}`
  
  try {
    const res = await axios.post('http://localhost:8000/recommend', { 
      query: query.value 
    })
    results.value = res.data
    if (!results.value.length) error.value = 'No recommendations found.'
  } catch (e) {
    error.value = 'Error fetching recommendations.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.yelp-search {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
}

.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  animation: logoFlip 1.5s ease-out forwards;
  transform-origin: center;
}

@keyframes logoFlip {
  0% {
    transform: rotateX(90deg) rotateY(90deg) scale(0.5);
    opacity: 0;
  }
  50% {
    transform: rotateX(0deg) rotateY(0deg) scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: rotateX(0deg) rotateY(0deg) scale(1);
    opacity: 1;
  }
}

.app-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-family: 'Georgia', 'Times New Roman', serif;
  text-transform: uppercase;
}

.main-heading {
  font-size: 1.2rem;
  color: #07450C;
  margin: 0;
  font-weight: normal;
}

.search-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.search-section {
  margin-bottom: 2rem;
  text-align: center;
}

.search-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #07450C;
  font-weight: bold;
  text-align: center;
}

.input-button-group {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.location-input, .craving-input {
  width: 60%;
  padding: 0.75rem;
  border: none;
  border-bottom: 2px solid #07450C;
  border-radius: 0;
  font-size: 1rem;
  background: white;
  color: #07450C;
}

.location-input::placeholder, .craving-input::placeholder {
  color: #07450C;
  opacity: 0.7;
}

.search-btn {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #07450C;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  white-space: nowrap;
}

.search-btn:hover {
  background: #07450C;
  color: white;
}

.loading {
  text-align: center;
  padding: 1rem;
  color: #07450C;
  background: white;
}

.error {
  color: #07450C;
  margin-top: 1rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
}

.results {
  margin-top: 2rem;
}

.results h3 {
  color: #07450C;
}

.restaurant-list {
  list-style: none;
  padding: 0;
}

.restaurant-item {
  margin-bottom: 1rem;
  padding: 1rem;
  background: white;
}

.restaurant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.restaurant-name {
  font-size: 1.1rem;
  color: #07450C;
}

.rating {
  background: white;
  color: #07450C;
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-weight: bold;
}

.restaurant-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.address {
  color: #07450C;
  font-size: 0.9rem;
}

.categories {
  color: #07450C;
  font-style: italic;
  font-size: 0.85rem;
  opacity: 0.8;
}

h2 {
  color: #07450C;
  text-align: center;
}

.results-section {
  margin-top: 2rem;
  text-align: center;
}

.results-title {
  color: #07450C;
  margin-bottom: 1rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.restaurant-card {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 500px;
  text-align: left;
}

.restaurant-name {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.restaurant-address {
  color: #07450C;
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

.restaurant-stars {
  color: #07450C;
  margin: 0.25rem 0;
  font-weight: bold;
}

.restaurant-categories {
  color: #07450C;
  margin: 0.25rem 0;
  font-size: 0.9rem;
  font-style: italic;
}

.error-message {
  color: #07450C;
  text-align: center;
  margin-top: 1rem;
}
</style>
