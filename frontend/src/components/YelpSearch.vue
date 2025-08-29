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

    <!-- Combined Yelp-style Search Bar -->
    <div class="search-section sticky-search">
      <label class="search-label">Search</label>
      <div class="yelp-bar">
        <div class="yelp-field">
          <span class="yelp-field-label">Find</span>
          <input 
            v-model="query"
            @keyup.enter="search"
            type="text"
            placeholder="burgers, sushi, date night..."
            class="yelp-input"
          >
        </div>
        <div class="yelp-field">
          <span class="yelp-field-label">Near</span>
          <input 
            v-model="location"
            @keyup.enter="search"
            type="text"
            placeholder="San Francisco, CA or 94105"
            class="yelp-input"
          >
        </div>
        <button @click="search" class="search-btn primary">Search</button>
      </div>

      <!-- Quick Filter Pills -->
      <div class="quick-filters">
        <button 
          v-for="pill in quickFilterPills" 
          :key="pill.id" 
          @click="applyQuickFilter(pill.id)"
          :class="['filter-pill', { active: activeQuickFilter === pill.id }]"
        >
          {{ pill.icon }} {{ pill.label }}
        </button>
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
      <!-- Skeleton rows -->
      <div class="skeleton-list">
        <div class="skeleton-card" v-for="i in 3" :key="i">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-lines">
            <div class="line l1"></div>
            <div class="line l2"></div>
            <div class="line l3"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && !error && results.length === 0" class="empty-state">
      <div class="empty-emoji">🔎</div>
      <h3 class="empty-title">Start exploring great places</h3>
      <p class="empty-text">Try a cuisine like “sushi” or an occasion like “date night”, and set your location.</p>
    </div>

    <!-- Results Section -->
    <div v-if="!loading && results.length > 0" class="results-section">
      <div class="results-header">
        <h3 class="results-title">{{ resultsTitle }}</h3>
        <div class="results-controls">
          <label class="sort-label">Sort by:</label>
          <select v-model="sortBy" @change="sortResults" class="sort-select">
            <option value="score">AI Score (Best Match)</option>
            <option value="stars">Rating (Highest First)</option>
            <option value="review_count">Popularity (Most Reviews)</option>
          </select>
          <span class="sort-indicator">Currently: {{ getSortLabel() }}</span>
        </div>
      </div>

      <div class="results-list">
        <div v-for="restaurant in sortedResults" :key="restaurant.name" class="restaurant-card" @mouseenter="recordView(restaurant)" @click.capture="recordClick(restaurant)">
          <div class="restaurant-header">
            <div class="restaurant-title-section">
              <div class="avatar">{{ getInitials(restaurant.name) }}</div>
              <div>
                <h4 class="restaurant-name">{{ restaurant.name }}</h4>
                <div class="restaurant-categories">{{ restaurant.categories }}</div>
                <div v-if="restaurant._aiWhy && restaurant._aiWhy.length" class="ai-badges">
                  <span v-for="(why, idx) in restaurant._aiWhy.slice(0, 2)" :key="idx" class="ai-badge">🤖 {{ why }}</span>
                  <button class="why-btn" @click.stop="toggleWhy(restaurant)">Why?</button>
                </div>
              </div>
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
          
          <!-- Why Popover -->
          <div v-if="showWhyForId === restaurant.name && restaurant._aiWhy && restaurant._aiWhy.length" class="why-popover">
            <div class="why-header">Why we recommended this</div>
            <ul class="why-list">
              <li v-for="(why, idx) in restaurant._aiWhy" :key="idx">{{ why }}</li>
            </ul>
            <button class="why-close" @click.stop="showWhyForId = null">Close</button>
          </div>
          
          <div class="restaurant-details">
            <div class="detail-section">
              <div class="detail-item">
                <span class="detail-label">📍 Address:</span>
                <span class="detail-value">{{ restaurant.address }}</span>
                <button class="copy-btn" @click="copyAddress(restaurant)">Copy</button>
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
                <div class="score-display">
                  <div class="score-bar-container">
                    <div class="score-bar" :style="{ width: (restaurant.overall_score / 5 * 100) + '%' }"></div>
                  </div>
                  <span class="score-value">{{ restaurant.overall_score.toFixed(2) }}/5</span>
                  <span class="score-percentage">({{ Math.round(restaurant.overall_score / 5 * 100) }}%)</span>
                </div>
              </div>
              
              <div v-if="restaurant.cuisine_match_score" class="detail-item">
                <span class="detail-label">🍽️ Cuisine Match:</span>
                <div class="score-display">
                  <div class="score-bar-container">
                    <div class="score-bar cuisine-bar" :style="{ width: (restaurant.cuisine_match_score * 100) + '%' }"></div>
                  </div>
                  <span class="score-value">{{ (restaurant.cuisine_match_score * 100).toFixed(0) }}%</span>
                  <span class="score-percentage">({{ restaurant.cuisine_match_score.toFixed(2) }})</span>
                </div>
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
              <div class="stat-item feedback-actions">
                <button class="feedback-btn pos" @click.stop="markPositive(restaurant)">More like this</button>
                <button class="feedback-btn neg" @click.stop="markNegative(restaurant)">Not interested</button>
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

    <!-- Toast element -->
    <div v-if="toast.show" class="toast show">{{ toast.text }}</div>
  </div>
</template>

<script>
import axios from 'axios'
import aiRecommender from '@/services/aiRecommender.js'
import feedbackService from '@/services/feedbackService.js'

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
      sortBy: 'score',
      loading: false,
      displayedCount: 25,
      loadMoreLoading: false,
      scrollThrottle: null,
      showFilters: true,
      activeQuickFilter: '',
      quickFilterPills: [
        { id: 'top_rated', label: 'Top Rated', icon: '⭐' },
        { id: 'popular', label: 'Popular', icon: '🔥' },
        { id: 'budget', label: 'Budget', icon: '💸' },
        { id: 'family', label: 'Family Friendly', icon: '👨‍👩‍👧‍👦' }
      ],
      showWhyForId: null,
      toast: { show: false, text: '' }
    }
  },
  computed: {
    filteredResults() {
      if (!this.results.length) return []
      let filtered = [...this.results]
      if (this.minRating !== '0') {
        const minRatingNum = parseInt(this.minRating)
        filtered = filtered.filter(restaurant => restaurant.stars >= minRatingNum)
      }
      return filtered
    },
    aiProcessedResults() {
      const { restaurants } = aiRecommender.scoreAndExplain(this.filteredResults, { now: new Date() })
      return restaurants.map(r => ({ ...r, score: Math.round((r._aiScore || 0) * 100) }))
    },
    sortedResults() {
      const base = this.aiProcessedResults
      if (!base.length) return []
      const sorted = [...base].sort((a, b) => {
        switch (this.sortBy) {
          case 'stars':
            if (b.stars !== a.stars) return b.stars - a.stars
            return b.review_count - a.review_count
          case 'review_count':
            if (b.review_count !== a.review_count) return b.review_count - a.stars
            return b.stars - a.stars
          case 'score':
          default:
            const scoreA = a.score || a.stars * 10
            const scoreB = b.score || b.stars * 10
            if (scoreB !== scoreA) return scoreB - scoreA
            return b.stars - a.stars
        }
      })
      return sorted.slice(0, this.displayedCount)
    },
    hasMoreResults() {
      return this.filteredResults.length > this.displayedCount
    }
  },
  methods: {
    async search() {
      // Prefer location-based search when location is provided; otherwise use craving
      if (this.location && this.location.trim().length > 0) {
        await this.searchByLocation()
      } else {
        await this.searchByCraving()
      }
    },
    async searchByCraving() {
      if (!this.query.trim()) return
      this.loading = true
      this.error = ''
      this.displayedCount = 25
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
        this.sortBy = 'score'
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
        this.resultsTitle = this.query.trim() ? `"${this.query}" near ${this.location}` : `Restaurants in ${this.location}`
        this.sortBy = 'score'
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
      this.$forceUpdate()
    },
    getSortLabel() {
      switch (this.sortBy) {
        case 'stars':
          return 'Rating'
        case 'review_count':
          return 'Popularity'
        case 'score':
          return 'AI Score'
        default:
          return 'AI Score'
      }
    },
    async loadMore() {
      if (this.loadMoreLoading || !this.hasMoreResults) return
      this.loadMoreLoading = true
      this.error = ''
      try {
        this.displayedCount += 10
        this.loadMoreLoading = false
      } catch (err) {
        console.error('Error loading more recommendations:', err)
        this.error = 'Error loading more recommendations. Please try again.'
        this.loadMoreLoading = false
      }
    },
    handleScroll() {
      if (this.scrollThrottle) return
      this.scrollThrottle = setTimeout(() => {
        const { scrollHeight, scrollTop, clientHeight } = document.documentElement
        const isNearBottom = scrollTop + clientHeight >= scrollHeight - 200
        if (isNearBottom && this.hasMoreResults && !this.loadMoreLoading) {
          this.loadMore()
        }
        this.scrollThrottle = null
      }, 100)
    },
    recordView(restaurant) {
      const cuisine = String(restaurant.categories || restaurant.cuisine || '').toString()
      feedbackService.recordView({ restaurantName: restaurant.name, cuisine })
    },
    recordClick(restaurant) {
      const cuisine = String(restaurant.categories || restaurant.cuisine || '').toString()
      feedbackService.recordClick({ restaurantName: restaurant.name, cuisine })
    },
    markPositive(restaurant) {
      const cuisine = String(restaurant.categories || restaurant.cuisine || '').toString()
      feedbackService.recordPositive({ restaurantName: restaurant.name, cuisine })
      this.$forceUpdate()
    },
    markNegative(restaurant) {
      const cuisine = String(restaurant.categories || restaurant.cuisine || '').toString()
      feedbackService.recordNegative({ restaurantName: restaurant.name, cuisine })
      this.$forceUpdate()
    },
    applyQuickFilter(id) {
      this.activeQuickFilter = id === this.activeQuickFilter ? '' : id
      switch (this.activeQuickFilter) {
        case 'top_rated':
          this.sortBy = 'stars'
          break
        case 'popular':
          this.sortBy = 'review_count'
          break
        case 'budget':
          this.selectedPriceRange = 'budget'
          this.sortBy = 'score'
          break
        case 'family':
          // Soft filter by family keywords via client-side filter pass
          // We re-run search to let backend filter if possible in future
          this.sortBy = 'score'
          break
        default:
          this.selectedPriceRange = ''
          this.sortBy = 'score'
      }
      this.$forceUpdate()
    },
    toggleWhy(restaurant) {
      this.showWhyForId = this.showWhyForId === restaurant.name ? null : restaurant.name
    },
    copyAddress(restaurant) {
      navigator.clipboard.writeText(`${restaurant.name} — ${restaurant.address}`).then(() => {
        this.showToast('Address copied to clipboard')
      }).catch(() => {
        this.showToast('Unable to copy')
      })
    },
    showToast(text) {
      this.toast.text = text
      this.toast.show = true
      setTimeout(() => { this.toast.show = false }, 1800)
    },
    getInitials(name) {
      const parts = String(name || '').split(' ').filter(Boolean)
      return (parts[0]?.[0] || 'R').toUpperCase() + (parts[1]?.[0] || '')
    }
  },
  mounted() {
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeUnmount() {
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
  background: linear-gradient(180deg, rgba(7, 69, 12, 0.06), rgba(7, 69, 12, 0.03));
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(7, 69, 12, 0.15);
  box-shadow: 0 6px 18px rgba(7, 69, 12, 0.08);
}

.options-row {
  display: flex;
  justify-content: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.option-group {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  min-width: 220px;
  background: white;
  border: 1px solid rgba(7, 69, 12, 0.12);
  border-radius: 10px;
  padding: 0.75rem 1rem;
}

.option-label {
  color: #07450C;
  font-weight: 800;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
  letter-spacing: 0.2px;
}

/* Custom select styling */
.select-input {
  padding: 0.6rem 0.75rem;
  border: 2px solid rgba(7, 69, 12, 0.25);
  border-radius: 10px;
  background: white;
  color: #07450C;
  font-size: 0.95rem;
  min-width: 140px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  appearance: none;
  background-image: linear-gradient(45deg, transparent 50%, #07450C 50%), linear-gradient(135deg, #07450C 50%, transparent 50%);
  background-position: calc(100% - 18px) calc(1em + 2px), calc(100% - 13px) calc(1em + 2px);
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
}

.select-input:focus {
  border-color: #07450C;
  box-shadow: 0 0 0 3px rgba(7, 69, 12, 0.15);
}

/* Custom checkboxes */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  align-items: flex-start;
}

.checkbox-item {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #07450C;
  font-size: 0.9rem;
  cursor: pointer;
  user-select: none;
}

.checkbox-item input[type="checkbox"] {
  appearance: none;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(7, 69, 12, 0.4);
  border-radius: 6px;
  display: inline-grid;
  place-content: center;
  background: white;
  transition: all 0.15s ease;
}

.checkbox-item input[type="checkbox"]:checked {
  background: #07450C;
  border-color: #07450C;
}

.checkbox-item input[type="checkbox"]::before {
  content: "";
  width: 10px;
  height: 10px;
  transform: scale(0);
  transition: 120ms transform ease-in-out;
  box-shadow: inset 1em 1em white;
  border-radius: 2px;
}

.checkbox-item input[type="checkbox"]:checked::before {
  transform: scale(1);
}

/* Yelp search bar enhancements */
.yelp-field {
  border: 2px solid rgba(7, 69, 12, 0.25);
  border-radius: 10px;
  background: white;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.yelp-field:focus-within {
  border-color: #07450C;
  box-shadow: 0 0 0 4px rgba(7, 69, 12, 0.12);
}

.yelp-field-label {
  background: rgba(7, 69, 12, 0.08);
  color: #07450C;
  font-weight: 800;
}

.yelp-input::placeholder {
  color: #07450C;
  opacity: 0.6;
}

/* Buttons */
.search-btn.primary {
  border-radius: 10px;
  box-shadow: 0 8px 16px rgba(7, 69, 12, 0.2);
}

.toolbar-btn {
  border-radius: 10px;
}

/* Cards and stats enhancements */
.restaurant-card {
  border-radius: 14px;
  border: 1px solid rgba(7, 69, 12, 0.12);
}

.detail-item {
  background: linear-gradient(180deg, rgba(7,69,12,0.05), rgba(7,69,12,0.03));
  border-left: 4px solid #07450C;
}

.stat-item {
  background: linear-gradient(135deg, rgba(7, 69, 12, 0.1), rgba(7, 69, 12, 0.06));
  border: 1px solid rgba(7, 69, 12, 0.18);
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

.score-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.score-bar-container {
  flex: 1;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar {
  height: 100%;
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  border-radius: 4px;
  transition: width 0.3s ease-in-out;
}

.score-bar.cuisine-bar {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.score-value {
  color: #07450C;
  font-weight: bold;
  font-size: 0.9rem;
  min-width: 40px;
  text-align: right;
}

.score-percentage {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.8;
  min-width: 60px;
  text-align: left;
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

/* Responsive adjustments for score display */
@media (max-width: 768px) {
  .score-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .score-bar-container {
    width: 100%;
  }
  
  .score-value, .score-percentage {
    min-width: auto;
    text-align: left;
  }
}

/* AI badges and toggle styles */
.ai-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin-left: 0.75rem;
  padding-left: 0.75rem;
  border-left: 1px solid rgba(7, 69, 12, 0.2);
  color: #07450C;
  font-weight: 600;
}

.ai-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.35rem;
}

.ai-badge {
  background: rgba(7, 69, 12, 0.08);
  color: #07450C;
  border: 1px solid rgba(7, 69, 12, 0.15);
  padding: 0.15rem 0.4rem;
  border-radius: 999px;
  font-size: 0.8rem;
}

.feedback-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.feedback-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: bold;
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.feedback-btn.pos {
  background: #4CAF50; /* Green */
  color: white;
}

.feedback-btn.pos:hover {
  background: #388E3C; /* Darker Green */
}

.feedback-btn.neg {
  background: #F44336; /* Red */
  color: white;
}

.feedback-btn.neg:hover {
  background: #D32F2F; /* Darker Red */
}

/* Combined Yelp-style bar */
.yelp-bar {
  display: grid;
  grid-template-columns: 1.2fr 1fr auto;
  gap: 0.5rem;
  align-items: stretch;
  max-width: 800px;
  margin: 0 auto 1rem auto;
}

.yelp-field {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #07450C;
  border-radius: 6px;
  overflow: hidden;
}

.yelp-field-label {
  background: rgba(7, 69, 12, 0.08);
  color: #07450C;
  font-weight: 700;
  padding: 0.5rem 0.75rem;
  border-right: 1px solid rgba(7, 69, 12, 0.2);
}

.yelp-input {
  flex: 1;
  padding: 0.75rem 0.75rem;
  border: none;
  outline: none;
  color: #07450C;
}

.search-btn.primary {
  padding: 0.75rem 1.25rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.search-btn.primary:hover {
  background: #0a5a0f;
}

@media (max-width: 768px) {
  .yelp-bar {
    grid-template-columns: 1fr;
  }
}

/* Responsive tweaks for filter cards */
@media (max-width: 768px) {
  .option-group {
    min-width: 100%;
  }
}

/* Sticky search bar */
.sticky-search {
  position: sticky;
  top: 70px;
  z-index: 50;
  background: white;
  padding-top: 0.5rem;
}

/* Quick filter pills */
.quick-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.filter-pill {
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  border: 2px solid rgba(7, 69, 12, 0.25);
  background: white;
  color: #07450C;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
}

.filter-pill.active,
.filter-pill:hover {
  background: #07450C;
  color: white;
  border-color: #07450C;
}

/* Why popover */
.why-btn {
  margin-left: 0.5rem;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  border: 1px solid rgba(7,69,12,0.25);
  background: white;
  color: #07450C;
  cursor: pointer;
  font-size: 0.8rem;
}

.why-btn:hover { background: rgba(7,69,12,0.08); }

.why-popover {
  position: relative;
  margin: 0.5rem 0 0.25rem 0;
  padding: 0.75rem;
  background: white;
  border: 1px solid rgba(7,69,12,0.2);
  border-radius: 8px;
  box-shadow: 0 8px 18px rgba(0,0,0,0.08);
}

.why-header { color: #07450C; font-weight: 800; margin-bottom: 0.5rem; }
.why-list { margin: 0; padding-left: 1rem; color: #07450C; }
.why-list li { margin: 0.2rem 0; }
.why-close { margin-top: 0.5rem; padding: 0.35rem 0.75rem; border: none; border-radius: 6px; background: #07450C; color: white; cursor: pointer; }

@media (max-width: 768px) {
  .sticky-search { top: 60px; }
}

/* Skeletons */
.skeleton-list { max-width: 800px; margin: 0.5rem auto 0; display: grid; gap: 0.75rem; }
.skeleton-card { display: flex; gap: 0.75rem; padding: 0.75rem; border: 1px solid #eee; border-radius: 10px; }
.skeleton-avatar { width: 40px; height: 40px; border-radius: 50%; background: #eaeaea; }
.skeleton-lines { flex: 1; display: grid; gap: 0.35rem; }
.line { height: 10px; background: #eaeaea; border-radius: 6px; }
.line.l1 { width: 60%; }
.line.l2 { width: 80%; }
.line.l3 { width: 40%; }

/* Empty state */
.empty-state { text-align: center; color: #07450C; padding: 2rem 0; }
.empty-emoji { font-size: 2rem; margin-bottom: 0.25rem; }
.empty-title { margin: 0.25rem 0; }
.empty-text { opacity: 0.7; }

/* Avatars */
avatar, .avatar { width: 40px; height: 40px; border-radius: 50%; background: rgba(7,69,12,0.1); color: #07450C; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; margin-right: 0.75rem; }

/* Copy button */
.copy-btn { margin-left: 0.5rem; padding: 0.25rem 0.5rem; border-radius: 6px; border: 1px solid rgba(7,69,12,0.25); background: white; color: #07450C; cursor: pointer; font-size: 0.8rem; }
.copy-btn:hover { background: rgba(7,69,12,0.08); }

/* Toast */
.toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #07450C; color: white; padding: 0.5rem 0.9rem; border-radius: 999px; box-shadow: 0 8px 18px rgba(0,0,0,0.15); opacity: 0; transition: opacity 0.2s ease; }
.toast.show { opacity: 1; }
</style>

