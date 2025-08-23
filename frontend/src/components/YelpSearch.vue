<template>
  <div class="search-container">
    <!-- Logo and Title Section -->
    <div class="logo-section" v-if="false">
      <div class="logo">🍽️</div>
      <h1 class="app-title">BELP</h1>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <button class="toolbar-btn" @click="showFilters = !showFilters">
        {{ showFilters ? 'Hide Filters' : 'Show Filters' }}
      </button>
    </div>

    <!-- Advanced Search Options -->
    <div class="advanced-options" v-show="showFilters">
      <div class="options-row">
        <div class="option-group">
          <label class="option-label">Minimum Rating</label>
          <select v-model="minRating" class="select-input">
            <option value="0">Any Rating</option>
            <option value="1">1+ Stars</option>
            <option value="2">2+ Stars</option>
            <option value="3">3+ Stars</option>
            <option value="4">4+ Stars</option>
            <option value="5">5 Stars</option>
          </select>
        </div>

        <div class="option-group">
          <label class="option-label">Dietary Restrictions</label>
          <div class="checkbox-group">
            <label class="checkbox-item">
              <input type="checkbox" v-model="dietaryRestrictions" value="vegetarian">
              <span>Vegetarian</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="dietaryRestrictions" value="vegan">
              <span>Vegan</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="dietaryRestrictions" value="gluten-free">
              <span>Gluten-Free</span>
            </label>
            <label class="checkbox-item">
              <input type="checkbox" v-model="dietaryRestrictions" value="halal">
              <span>Halal</span>
            </label>
          </div>
        </div>

        <div class="option-group">
          <label class="option-label">Ambiance</label>
          <select v-model="selectedAmbiance" class="select-input">
            <option value="">Any Ambiance</option>
            <option value="romantic">Romantic</option>
            <option value="casual">Casual</option>
            <option value="family-friendly">Family-Friendly</option>
            <option value="upscale">Upscale</option>
            <option value="outdoor">Outdoor</option>
            <option value="lively">Lively</option>
          </select>
        </div>

        <div class="option-group">
          <label class="option-label">Price Range</label>
          <select v-model="selectedPriceRange" class="select-input">
            <option value="">Any Price</option>
            <option value="budget">Budget</option>
            <option value="moderate">Moderate</option>
            <option value="expensive">Expensive</option>
          </select>
        </div>
      </div>
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
        <button @click="searchByLocation" class="search-btn">Find Restaurants</button>
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

    <!-- Loading Animation -->
    <div v-if="loading" class="loading-section" aria-live="polite">
      <div class="kitchen-loader" role="status" aria-label="Cooking recommendations">
        <div class="pot">
          <div class="pot-body"></div>
          <div class="pot-lip"></div>
          <div class="spoon"></div>
          <div class="bubble b1"></div>
          <div class="bubble b2"></div>
          <div class="bubble b3"></div>
        </div>
        <div class="steam s1"></div>
        <div class="steam s2"></div>
        <div class="steam s3"></div>
      </div>
      <p class="loading-caption">Cooking up recommendations...</p>
    </div>

    <!-- Results Section -->
    <div v-if="!loading && results.length > 0" class="results-section">
      <div class="results-header">
        <h3 class="results-title">{{ resultsTitle }}</h3>
        <div class="results-controls">
          <label class="sort-label">Sort by:</label>
          <select v-model="sortBy" @change="sortResults" class="sort-select">
            <option value="stars">Rating (Highest First)</option>
            <option value="review_count">Popularity (Most Reviews)</option>
            <option value="score">Best Match</option>
          </select>
          <span class="sort-indicator">Currently: {{ getSortLabel() }}</span>
        </div>
      </div>

      <div class="results-list">
        <div v-for="restaurant in sortedResults" :key="restaurant.name" class="restaurant-card">
          <div class="restaurant-header">
            <div class="restaurant-title-section">
              <h4 class="restaurant-name">{{ restaurant.name }}</h4>
              <div class="restaurant-categories">{{ restaurant.categories }}</div>
            </div>
            <div class="restaurant-rating">
              <div class="stars-display">
                <span class="stars">⭐ {{ restaurant.stars }}/5</span>
                <div class="stars-visual">
                  <span v-for="i in 5" :key="i" class="star-icon">
                    {{ i <= restaurant.stars ? '★' : '☆' }}
                  </span>
                </div>
              </div>
              <span class="review-count">({{ restaurant.review_count }} reviews)</span>
            </div>
          </div>
          
          <div class="restaurant-details">
            <div class="detail-section">
              <div class="detail-item">
                <span class="detail-label">📍 Address:</span>
                <span class="detail-value">{{ restaurant.address }}</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">📊 Rating:</span>
                <span class="detail-value">{{ restaurant.stars }} stars</span>
              </div>
              
              <div class="detail-item">
                <span class="detail-label">👥 Reviews:</span>
                <span class="detail-value">{{ restaurant.review_count.toLocaleString() }} reviews</span>
              </div>
              
              <div v-if="restaurant.overall_score" class="detail-item">
                <span class="detail-label">🎯 Overall Score:</span>
                <span class="detail-value score-highlight">{{ restaurant.overall_score.toFixed(2) }}/5</span>
              </div>
              
              <div v-if="restaurant.cuisine_match_score" class="detail-item">
                <span class="detail-label">🍽️ Cuisine Match:</span>
                <span class="detail-value">{{ (restaurant.cuisine_match_score * 100).toFixed(0) }}%</span>
              </div>
            </div>
            
            <div class="restaurant-stats">
              <div class="stat-item">
                <div class="stat-number">{{ restaurant.stars }}</div>
                <div class="stat-label">Stars</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">{{ restaurant.review_count.toLocaleString() }}</div>
                <div class="stat-label">Reviews</div>
              </div>
              <div v-if="restaurant.score" class="stat-item">
                <div class="stat-number">{{ restaurant.score.toFixed(0) }}</div>
                <div class="stat-label">Score</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Load More Button -->
      <div v-if="hasMoreResults" class="load-more-section">
        <button 
          @click="loadMore" 
          :disabled="loadMoreLoading"
          class="load-more-btn"
        >
          <span v-if="!loadMoreLoading">
            Load More Restaurants ({{ filteredResults.length - displayedCount }} remaining)
          </span>
          <span v-else>
            <span class="loading-spinner">⏳</span> Loading...
          </span>
        </button>
        <p class="load-more-hint">Scroll down to auto-load more results</p>
      </div>
      
      <!-- Debug Info (temporary) -->
      <div class="debug-info">
        <p>Debug: Total results: {{ results.length }}, Filtered: {{ filteredResults.length }}, Displayed: {{ displayedCount }}, Has more: {{ hasMoreResults }}</p>
      </div>
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'YelpSearch',
  data() {
    return {
      query: '',
      location: '',
      results: [],
      error: '',
      resultsTitle: '',
      dietaryRestrictions: [],
      selectedAmbiance: '',
      selectedPriceRange: '',
      minRating: '0',
      sortBy: 'stars',
      loading: false,
      displayedCount: 25,  // Number of restaurants to show initially (increased from 10)
      loadMoreLoading: false,  // Loading state for load more button
      scrollThrottle: null,  // Throttle for scroll events
      showFilters: true // New data property for filter visibility
    }
  },
  computed: {
    filteredResults() {
      if (!this.results.length) return []
      
      let filtered = [...this.results]
      
      // Filter by minimum rating
      if (this.minRating !== '0') {
        const minRatingNum = parseInt(this.minRating)
        filtered = filtered.filter(restaurant => restaurant.stars >= minRatingNum)
      }
      
      return filtered
    },
    
    sortedResults() {
      if (!this.filteredResults.length) return []
      
      const sorted = [...this.filteredResults].sort((a, b) => {
        switch (this.sortBy) {
          case 'stars':
            // Sort by stars first, then by review count for tie-breaking
            if (b.stars !== a.stars) {
              return b.stars - a.stars
            }
            return b.review_count - a.review_count
          case 'review_count':
            // Sort by review count first, then by stars for tie-breaking
            if (b.review_count !== a.review_count) {
              return b.review_count - a.stars
            }
            return b.stars - a.stars
          case 'score':
          default:
            // Sort by score, with fallback to stars if no score
            const scoreA = a.score || a.stars * 10
            const scoreB = b.score || b.stars * 10
            if (scoreB !== scoreA) {
              return scoreB - scoreA
            }
            // Fallback to stars if scores are equal
            return b.stars - a.stars
        }
      })
      
      // Return only the number of restaurants to display
      return sorted.slice(0, this.displayedCount)
    },
    
    hasMoreResults() {
      return this.filteredResults.length > this.displayedCount
    }
  },
  methods: {
    async searchByCraving() {
      if (!this.query.trim()) return
      
      this.loading = true
      this.error = ''
      this.displayedCount = 25  // Reset to show first 25 results
      const startTime = Date.now()
      const MIN_LOADING_MS = 1200
      
      try {
        const requestData = {
          query: this.query,
          dietary_restrictions: this.dietaryRestrictions,
          ambiance: this.selectedAmbiance || null,
          price_range: this.selectedPriceRange || null
        }
        
        const res = await axios.post('http://localhost:8000/recommend', requestData)
        this.results = res.data
        this.resultsTitle = `Results for "${this.query}"`
        this.sortBy = 'stars' // Reset to stars (highest first)
      } catch (err) {
        console.error('Error fetching recommendations:', err)
        this.error = 'Error fetching recommendations. Please try again.'
      } finally {
        const elapsed = Date.now() - startTime
        if (elapsed < MIN_LOADING_MS) {
          await new Promise(resolve => setTimeout(resolve, MIN_LOADING_MS - elapsed))
        }
        this.loading = false
      }
    },

    async searchByLocation() {
      if (!this.location.trim()) return
      
      this.loading = true
      this.error = ''
      const startTime = Date.now()
      const MIN_LOADING_MS = 1200
      
      try {
        const requestData = {
          location: this.location,
          dietary_restrictions: this.dietaryRestrictions,
          ambiance: this.selectedAmbiance || null,
          price_range: this.selectedPriceRange || null
        }
        
        const res = await axios.post('http://localhost:8000/recommend-by-location', requestData)
        this.results = res.data
        this.resultsTitle = `Restaurants in ${this.location}`
        this.sortBy = 'stars' // Reset to stars (highest first)
      } catch (err) {
        console.error('Error fetching location recommendations:', err)
        this.error = 'Error fetching recommendations. Please try again.'
      } finally {
        const elapsed = Date.now() - startTime
        if (elapsed < MIN_LOADING_MS) {
          await new Promise(resolve => setTimeout(resolve, MIN_LOADING_MS - elapsed))
        }
        this.loading = false
      }
    },

    sortResults() {
      // Force reactivity by triggering a re-render
      this.$forceUpdate()
      console.log('Sorting by:', this.sortBy)
    },
    
    getSortLabel() {
      switch (this.sortBy) {
        case 'stars':
          return 'Rating'
        case 'review_count':
          return 'Popularity'
        case 'score':
          return 'Best Match'
        default:
          return 'Rating'
      }
    },

    async loadMore() {
      if (this.loadMoreLoading || !this.hasMoreResults) return

      this.loadMoreLoading = true
      this.error = ''

      try {
        // Increase the displayed count to show more results
        this.displayedCount += 10
        
        // No need to make another API call since we already have all results
        // Just show more of what we already have
        this.loadMoreLoading = false
      } catch (err) {
        console.error('Error loading more recommendations:', err)
        this.error = 'Error loading more recommendations. Please try again.'
        this.loadMoreLoading = false
      }
    },

    handleScroll() {
      // Throttle scroll events to prevent too many calls
      if (this.scrollThrottle) return
      
      this.scrollThrottle = setTimeout(() => {
        const { scrollHeight, scrollTop, clientHeight } = document.documentElement
        const isNearBottom = scrollTop + clientHeight >= scrollHeight - 200 // 200px from bottom
        
        if (isNearBottom && this.hasMoreResults && !this.loadMoreLoading) {
          this.loadMore()
        }
        
        this.scrollThrottle = null
      }, 100) // Throttle to 100ms
    }
  },
  mounted() {
    // Add scroll event listener for infinite scroll
    window.addEventListener('scroll', this.handleScroll)
  },
  
  beforeUnmount() {
    // Clean up scroll event listener
    window.removeEventListener('scroll', this.handleScroll)
  }
}
</script>

<style scoped>
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.search-section {
  margin-bottom: 2rem;
  text-align: left;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.search-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #07450C;
  font-weight: bold;
  text-align: left;
}

.input-button-group {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.location-input, .craving-input {
  width: 70%;
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

.toolbar {
  margin-bottom: 2rem;
  text-align: left;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.toolbar-btn {
  padding: 0.75rem 1.5rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.toolbar-btn:hover {
  background: #0a5a0f;
}

.advanced-options {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(7, 69, 12, 0.05);
  border-radius: 8px;
  text-align: center;
}

.options-row {
  display: flex;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.option-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 150px;
}

.option-label {
  color: #07450C;
  font-weight: bold;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  align-items: flex-start;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #07450C;
  font-size: 0.85rem;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  accent-color: #07450C;
}

.select-input {
  padding: 0.5rem;
  border: 1px solid #07450C;
  border-radius: 4px;
  background: white;
  color: #07450C;
  font-size: 0.9rem;
  min-width: 120px;
}

/* Loading animation */
.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 220px;
}

.kitchen-loader {
  position: relative;
  width: 140px;
  height: 130px;
  margin-bottom: 0.75rem;
}

.pot-body {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 50px;
  background: rgba(7, 69, 12, 0.08);
  border: 2px solid #07450C;
  border-radius: 0 0 12px 12px;
}

.pot-lip {
  position: absolute;
  bottom: 48px;
  left: 50%;
  transform: translateX(-50%);
  width: 130px;
  height: 10px;
  background: #07450C;
  border-radius: 6px;
}

.spoon {
  position: absolute;
  bottom: 30px;
  left: 65px;
  width: 8px;
  height: 50px;
  background: #07450C;
  border-radius: 4px;
  transform-origin: bottom center;
  animation: stir 1.4s ease-in-out infinite;
}

.bubble {
  position: absolute;
  bottom: 12px;
  left: 50%;
  width: 10px;
  height: 10px;
  background: #74b67a;
  border-radius: 50%;
  opacity: 0;
  animation: bubbleUp 1.4s ease-in-out infinite;
}
.bubble.b1 { left: 55%; animation-delay: 0s; }
.bubble.b2 { left: 45%; animation-delay: 0.25s; }
.bubble.b3 { left: 50%; animation-delay: 0.5s; }

.steam {
  position: absolute;
  bottom: 58px;
  left: 50%;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(7, 69, 12, 0.5);
  border-radius: 50% 50% 50% 50%;
  opacity: 0;
  transform: translateX(-50%);
  animation: steamRise 1.8s ease-in-out infinite;
}
.steam.s1 { left: 40%; animation-delay: 0s; }
.steam.s2 { left: 50%; animation-delay: 0.3s; }
.steam.s3 { left: 60%; animation-delay: 0.6s; }

.loading-caption {
  color: #07450C;
  font-weight: bold;
}

@keyframes bubbleUp {
  0% { transform: translate(-50%, 0) scale(0.6); opacity: 0; }
  30% { opacity: 1; }
  100% { transform: translate(-50%, -40px) scale(1.1); opacity: 0; }
}

@keyframes steamRise {
  0% { transform: translate(-50%, 0) scale(0.8); opacity: 0; }
  20% { opacity: 0.6; }
  100% { transform: translate(-50%, -45px) scale(1.2); opacity: 0; }
}

@keyframes stir {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(12deg); }
}

.results-section {
  margin-top: 2rem;
  text-align: center;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-title {
  color: #07450C;
  margin-bottom: 1rem;
}

.results-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-label {
  color: #07450C;
  font-weight: bold;
  font-size: 0.9rem;
}

.sort-select {
  padding: 0.5rem;
  border: 1px solid #07450C;
  border-radius: 4px;
  background: white;
  color: #07450C;
  font-size: 0.9rem;
}

.sort-indicator {
  color: #07450C;
  font-size: 0.8rem;
  font-style: italic;
  margin-left: 0.5rem;
  opacity: 0.8;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
  width: 100%;
}

.restaurant-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 800px;
  text-align: left;
  border: 1px solid rgba(7, 69, 12, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.restaurant-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.restaurant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
  border-bottom: 2px solid rgba(7, 69, 12, 0.1);
  padding-bottom: 1rem;
}

.restaurant-title-section {
  flex: 1;
  min-width: 300px;
}

.restaurant-name {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.4rem;
  font-weight: bold;
}

.restaurant-categories {
  color: #07450C;
  font-size: 0.95rem;
  font-style: italic;
  opacity: 0.8;
}

.restaurant-rating {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  min-width: 150px;
}

.stars-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.stars {
  color: #07450C;
  font-weight: bold;
  font-size: 1rem;
}

.stars-visual {
  display: flex;
  gap: 2px;
}

.star-icon {
  color: #FFD700;
  font-size: 1.2rem;
}

.review-count {
  color: #07450C;
  font-size: 0.85rem;
  opacity: 0.8;
}

.restaurant-details {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.detail-section {
  flex: 1;
  min-width: 300px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 6px;
  border-left: 3px solid #07450C;
}

.detail-label {
  color: #07450C;
  font-weight: bold;
  font-size: 0.9rem;
  min-width: 120px;
}

.detail-value {
  color: #07450C;
  font-size: 0.9rem;
  text-align: right;
  flex: 1;
}

.score-highlight {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
}

.restaurant-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 120px;
}

.stat-item {
  text-align: center;
  padding: 0.75rem;
  background: linear-gradient(135deg, rgba(7, 69, 12, 0.1), rgba(7, 69, 12, 0.05));
  border-radius: 8px;
  border: 1px solid rgba(7, 69, 12, 0.2);
}

.stat-number {
  color: #07450C;
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #07450C;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.error-message {
  color: #07450C;
  text-align: center;
  margin-top: 1rem;
}

.load-more-section {
  margin-top: 2rem;
  text-align: center;
}

.load-more-btn {
  padding: 0.75rem 1.5rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.load-more-btn:hover:not(:disabled) {
  background: #0a5a0f;
}

.load-more-btn:disabled {
  background: #ccc;
  color: #666;
  cursor: not-allowed;
}

.loading-spinner {
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 0.5rem;
}

.debug-info {
  margin-top: 2rem;
  padding: 1rem;
  background: #f0f0f0;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 0.9rem;
  color: #333;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.load-more-hint {
  color: #07450C;
  font-size: 0.8rem;
  margin-top: 0.5rem;
  opacity: 0.7;
}

/* Responsive Design */
@media (max-width: 768px) {
  .search-container {
    padding: 1rem;
  }
  
  .logo-section {
    margin-bottom: 1.5rem;
  }
  
  .app-title {
    font-size: 2rem;
  }
  
  .main-heading {
    font-size: 1rem;
  }
  
  .search-section {
    margin-bottom: 1.5rem;
  }
  
  .input-button-group {
    flex-direction: column;
    gap: 1rem;
  }
  
  .location-input, .craving-input {
    width: 100%;
  }
  
  .search-btn {
    width: 100%;
    padding: 1rem;
  }
  
  .toolbar {
    margin-bottom: 1.5rem;
  }
  
  .toolbar-btn {
    width: 100%;
    padding: 1rem;
  }
  
  .advanced-options {
    padding: 1rem;
  }
  
  .options-row {
    flex-direction: column;
    gap: 1rem;
  }
  
  .option-group {
    min-width: auto;
  }
  
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .results-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .restaurant-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .restaurant-title-section {
    min-width: auto;
  }
  
  .restaurant-rating {
    align-items: flex-start;
    min-width: auto;
  }
  
  .restaurant-details {
    flex-direction: column;
    gap: 1rem;
  }
  
  .detail-section {
    min-width: auto;
  }
  
  .restaurant-stats {
    flex-direction: row;
    justify-content: space-around;
    min-width: auto;
  }
  
  .debug-info {
    font-size: 0.8rem;
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .search-container {
    padding: 0.75rem;
  }
  
  .hero-section {
    padding: 1rem 0;
  }
  
  .app-title {
    font-size: 1.75rem;
  }
  
  .search-section {
    margin-bottom: 1rem;
  }
  
  .advanced-options {
    padding: 0.75rem;
  }
  
  .restaurant-card {
    padding: 1rem;
  }
  
  .restaurant-name {
    font-size: 1.2rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .detail-label {
    min-width: auto;
  }
  
  .detail-value {
    text-align: left;
  }
  
  .restaurant-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stat-item {
    padding: 0.5rem;
  }
  
  .stat-number {
    font-size: 1.25rem;
  }
  
  .load-more-btn {
    width: 100%;
    padding: 1rem;
  }
}
</style>
