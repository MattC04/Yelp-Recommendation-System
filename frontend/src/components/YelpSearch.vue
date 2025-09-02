<template>
  <div class="search-container">
    <div class="personalization-header">
      <div class="personalization-info">
        <h1 class="app-title" style="color: #07450C">🍽️ BELP</h1>
        <p class="app-subtitle">AI-Powered Restaurant Recommendations</p>
      </div>
      <div class="personalization-actions">
        <router-link to="/profile" class="profile-btn">📊 Your Profile</router-link>
        <button v-if="!hasProfile" @click="createProfile" class="create-profile-btn">✨ Create Profile</button>
      </div>
    </div>

    <div class="search-section sticky-search">
      <label class="search-label">Search</label>
      <div class="yelp-bar">
        <div class="yelp-field">
          <span class="yelp-field-label">Find</span>
          <input v-model="query" @keyup.enter="search" type="text" placeholder="burgers, sushi, date night..." class="yelp-input" />
        </div>
        <div class="yelp-field">
          <span class="yelp-field-label">Near</span>
          <input v-model="location" @keyup.enter="search" type="text" placeholder="San Francisco, CA or 94105" class="yelp-input" />
        </div>
        <button class="search-btn primary" @click="search" :disabled="loading">{{ loading ? 'Searching...' : 'Search' }}</button>
      </div>
      <div class="inline-debug" aria-live="polite">
        Results: {{ Array.isArray(results) ? results.length : 0 }}
        <span v-if="Array.isArray(results) && results.length > 0"> • First: {{ results[0]?.name }} ({{ results[0]?.stars }}⭐)</span>
      </div>
    </div>

    <div v-if="loading" class="loading-section" aria-live="polite">
      <p class="loading-caption">Cooking up recommendations...</p>
    </div>

    <div v-else-if="!error && results.length === 0" class="empty-state">
      <div class="empty-emoji">🔎</div>
      <h3 class="empty-title">Start exploring great places</h3>
      <p class="empty-text">Try a cuisine like "sushi" or an occasion like "date night", and set your location.</p>
    </div>

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
        <div v-for="r in sortedResults" :key="r.name + '|' + r.address" class="result-card" @mouseenter="recordView(r)" @click="recordClick(r)">
          <div class="card-main">
            <div class="card-title">{{ r.name }}</div>
            <div class="card-sub">{{ r.address }}</div>
            <div class="card-meta">{{ Number(r.stars || 0).toFixed(1) }} ⭐ • {{ r.review_count }} reviews • {{ r.categories }}</div>
          </div>
          <div class="card-score">{{ r.score || Math.round((r.stars || 0) * 20) }}</div>
        </div>
      </div>
    </div>

    <div v-if="toast.show" class="toast show">{{ toast.text }}</div>
  </div>
</template>

<script>
import axios from 'axios'
import aiRecommender from '@/services/aiRecommender.js'
import feedbackService from '@/services/feedbackService.js'
import securityService from '@/services/securityService.js'

export default {
  name: 'YelpSearch',
  data() {
    return {
      query: '',
      location: '',
      results: [],
      resultsTitle: '',
      sortBy: 'score',
      loading: false,
      displayedCount: 25,
      error: '',
      toast: { show: false, text: '' },
      hasProfile: false,
      discoveryProgress: 0
    }
  },
  computed: {
    filteredResults() {
      if (!Array.isArray(this.results) || this.results.length === 0) return []
      return [...this.results]
    },
    aiProcessedResults() {
      const base = this.filteredResults
      if (!base || base.length === 0) return []
      try {
        const { restaurants } = aiRecommender.scoreAndExplain(base, { now: new Date() })
        return restaurants.map(r => ({ ...r, score: Math.round((r._aiScore || 0) * 100) }))
      } catch (e) {
        return base.map(r => ({ ...r, score: Math.round(((r.stars || 0) * 20)) }))
      }
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
            if (b.review_count !== a.review_count) return b.review_count - a.review_count
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
    }
  },
  methods: {
    async search() {
      // Validate inputs
      if (this.query.trim()) {
        const v = securityService.validateSearchQuery(this.query)
        if (!v.isValid) { this.showToast(`Search error: ${v.error}`); return }
        this.query = v.sanitized
      }
      if (this.location.trim()) {
        const v = securityService.validateLocation(this.location)
        if (!v.isValid) { this.showToast(`Location error: ${v.error}`); return }
        this.location = v.sanitized
      }
      if (!this.query.trim() && !this.location.trim()) {
        this.showToast('Please enter a cuisine/occasion or location to search')
        return
      }

      this.loading = true
      this.error = ''
      this.displayedCount = 25
      const startTime = Date.now()
      const MIN_LOADING_MS = 900
      try {
        const payload = { query: this.query || null, location: this.location || null, limit: 25 }
        const res = await axios.post('http://localhost:8000/search', payload)
        this.results = Array.isArray(res.data) ? res.data : []
        if (this.query && this.location) this.resultsTitle = `"${this.query}" near ${this.location}`
        else if (this.query) this.resultsTitle = `Results for "${this.query}"`
        else this.resultsTitle = `Restaurants in ${this.location}`
        if (this.results.length === 0) this.showToast('No results found. Try a different query')
      } catch (err) {
        this.error = 'Error fetching recommendations. Please try again.'
        this.showToast('Search failed. Please try again.')
      } finally {
        const elapsed = Date.now() - startTime
        if (elapsed < MIN_LOADING_MS) await new Promise(r => setTimeout(r, MIN_LOADING_MS - elapsed))
        this.loading = false
      }
    },
    sortResults() { this.$forceUpdate() },
    getSortLabel() {
      switch (this.sortBy) {
        case 'stars': return 'Rating'
        case 'review_count': return 'Popularity'
        case 'score':
        default: return 'AI Score'
      }
    },
    recordView(restaurant) {
      const cuisine = String(restaurant.categories || restaurant.cuisine || '')
      feedbackService.recordView({ restaurantName: restaurant.name, cuisine })
    },
    recordClick(restaurant) {
      const cuisine = String(restaurant.categories || restaurant.cuisine || '')
      feedbackService.recordClick({ restaurantName: restaurant.name, cuisine })
    },
    createProfile() { this.$router.push('/profile') },
    showToast(text) { this.toast.text = text; this.toast.show = true; setTimeout(() => { this.toast.show = false }, 1800) }
  }
}
</script>

<style scoped>
.search-container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
.personalization-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; }
.app-title { font-size: 2rem; margin: 0; color: #07450C; }
.app-subtitle { color: #666; margin: 0.2rem 0 0 0; }
.profile-btn, .create-profile-btn { padding: 0.5rem 1rem; border: 2px solid #07450C; border-radius: 8px; background: white; color: #07450C; cursor: pointer; font-weight: bold; text-decoration: none; }
.profile-btn:hover, .create-profile-btn:hover { background: #07450C; color: white; }

.search-section { margin-top: 1rem; }
.yelp-bar { display: flex; gap: 0.75rem; align-items: end; }
.yelp-field { display: flex; flex-direction: column; flex: 1; }
.yelp-field-label { font-size: 0.85rem; color: #07450C; margin-bottom: 0.25rem; }
.yelp-input { padding: 0.6rem 0.8rem; border: 1px solid #ccc; border-radius: 8px; }
.search-btn { padding: 0.65rem 1rem; border-radius: 8px; border: none; background: #07450C; color: #fff; cursor: pointer; }
.search-btn:disabled { opacity: 0.6; cursor: default; }
.inline-debug { margin-top: 6px; font-size: 0.8rem; color: #666; }

.loading-section { padding: 2rem; text-align: center; }
.empty-state { padding: 2rem; text-align: center; color: #333; }
.empty-emoji { font-size: 2rem; }
.empty-title { margin: 0.5rem 0; }

.results-section { margin-top: 1rem; }
.results-header { display: flex; justify-content: space-between; align-items: center; }
.results-list { margin-top: 1rem; display: grid; gap: 0.75rem; }
.result-card { display: flex; justify-content: space-between; align-items: center; padding: 0.9rem; border: 1px solid #eee; border-radius: 10px; background: #fff; }
.card-title { font-weight: bold; color: #222; }
.card-sub { color: #555; font-size: 0.9rem; }
.card-meta { color: #666; font-size: 0.85rem; }
.card-score { font-weight: bold; color: #07450C; }

.toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #07450C; color: white; padding: 0.5rem 0.9rem; border-radius: 999px; box-shadow: 0 8px 18px rgba(0,0,0,0.15); opacity: 0; transition: opacity 0.2s ease; }
.toast.show { opacity: 1; }

@media (max-width: 768px) {
  .yelp-bar { flex-direction: column; align-items: stretch; }
}
</style>
