<template>
  <div class="yelp-search">
    <h2>Find the Best Restaurants</h2>
    
    <!-- Location Search -->
    <div class="search-section">
      <h3>Enter Your Location</h3>
      <input 
        v-model="location" 
        @keyup.enter="searchByLocation" 
        placeholder="Enter city, state, or zip code..." 
        class="location-input"
      />
      <button @click="searchByLocation" class="search-btn">Find Top Restaurants</button>
    </div>

    <!-- Craving Search (existing) -->
    <div class="search-section">
      <h3>Or Search by Craving</h3>
      <input 
        v-model="query" 
        @keyup.enter="searchByCraving" 
        placeholder="Type your craving or occasion..." 
        class="craving-input"
      />
      <button @click="searchByCraving" class="search-btn">Search</button>
    </div>

    <!-- Loading and Error States -->
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>

    <!-- Results -->
    <div v-if="results.length" class="results">
      <h3>{{ resultsTitle }}</h3>
      <ul class="restaurant-list">
        <li v-for="(r, idx) in results" :key="idx" class="restaurant-item">
          <div class="restaurant-header">
            <strong class="restaurant-name">{{ r.name }}</strong>
            <span class="rating">{{ r.stars }}★</span>
          </div>
          <div class="restaurant-details">
            <span class="address">{{ r.address }}</span>
            <span class="categories">{{ r.categories }}</span>
          </div>
        </li>
      </ul>
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
  margin: 2rem auto;
  padding: 2rem;
  background: white;
}

.search-section {
  margin-bottom: 2rem;
  padding: 1rem;
  background: white;
}

.search-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #07450C;
}

.location-input, .craving-input {
  width: 70%;
  padding: 0.75rem;
  margin-right: 0.5rem;
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
</style>
