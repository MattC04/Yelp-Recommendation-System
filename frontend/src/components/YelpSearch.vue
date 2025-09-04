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

    <!-- Toggle -->
    <div class="view-toggle">
      <button :class="['toggle-btn', { active: activeView==='list' }]" @click="activeView='list'">List</button>
      <button :class="['toggle-btn', { active: activeView==='map' }]" @click="activeView='map'">Map</button>
    </div>

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

    <div v-else-if="activeView==='map'">
      <MapResults :results="resultsWithCoords" />
    </div>

    <div v-else-if="!error && results.length === 0" class="empty-state">
      <div class="empty-emoji">🔎</div>
      <h3 class="empty-title">Start exploring great places</h3>
      <p class="empty-text">Try a cuisine like "sushi" or an occasion like "date night", and set your location.</p>
    </div>

    <div v-if="!loading && activeView==='list' && results.length > 0" class="results-section">
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
        <div v-for="r in sortedResults" :key="r.name + '|' + r.address" class="result-card" @mouseenter="recordView(r)">
          <div class="card-main" @click="recordClick(r)">
            <div class="card-title">{{ r.name }}</div>
            <div class="card-sub">{{ r.address }}</div>
            <div class="card-meta">{{ Number(r.stars || 0).toFixed(1) }} ⭐ • {{ r.review_count }} reviews • {{ r.categories }}</div>
          </div>
          <div class="card-actions">
            <button class="btn-outline" @click.stop="queueForRanking(r)">Rank</button>
            <button class="btn-visited" :class="{ active: isVisited(r) }" @click.stop="toggleVisited(r)">{{ isVisited(r) ? "I've been" : "I've been" }}</button>
            <div class="card-score">{{ r.score || Math.round((r.stars || 0) * 20) }}</div>
          </div>
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
import rankingService from '@/services/rankingService.js'
import MapResults from '@/components/MapResults.vue'

export default {
  name: 'YelpSearch',
  components: { MapResults },
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
      discoveryProgress: 0,
      activeView: 'list'
    }
  },
  computed: {
    filteredResults() {
      if (!Array.isArray(this.results) || this.results.length === 0) return []
      return [...this.results]
    },
    resultsWithCoords() {
      // Filter to items that have valid lat/lng so map doesn’t try to plot nulls
      return this.results.filter(r => Number.isFinite(Number(r.latitude)) && Number.isFinite(Number(r.longitude)))
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
    queueForRanking(restaurant) {
      const id = restaurant.restaurantId || `${restaurant.name}||${restaurant.address}`
      rankingService.addToToRank(id)
      // persist meta for grouping
      const cats = String(restaurant.categories || '').toLowerCase()
      const name = String(restaurant.name || '').toLowerCase()
      const map = { italian:'Italian', pizza:'Italian', pasta:'Italian', mexican:'Mexican', taco:'Mexican', tacos:'Mexican', burrito:'Mexican', chinese:'Chinese', szechuan:'Chinese', dimsum:'Chinese', 'dim sum':'Chinese', japanese:'Japanese', sushi:'Japanese', ramen:'Japanese', korean:'Korean', bbq:'BBQ', thai:'Thai', vietnamese:'Vietnamese', pho:'Vietnamese', 'banh mi':'Vietnamese', indian:'Indian', mediterranean:'Mediterranean', greek:'Greek', french:'French', american:'American', seafood:'Seafood', burger:'Burgers', burgers:'Burgers' }
      const pick = () => {
        for (const k in map) { if (cats.includes(k) || name.includes(k)) return map[k] }
        const t = cats.split(',').map(x=>x.trim()).find(Boolean)
        return t ? t.charAt(0).toUpperCase() + t.slice(1) : ''
      }
      const primaryCuisine = pick()
      rankingService.setMeta(id, { name: restaurant.name, address: restaurant.address, categories: restaurant.categories, stars: restaurant.stars, primaryCuisine })
      this.showToast('Added to your To Rank list')
      this.$router.push({ path: '/rankings', query: { rank: id } })
    },
    toggleVisited(restaurant) {
      const id = restaurant.restaurantId || `${restaurant.name}||${restaurant.address}`
      if (rankingService.isVisited(id)) {
        rankingService.unmarkVisited(id)
        this.showToast('Removed from visited')
      } else {
        rankingService.markVisited({
          restaurantId: id,
          name: restaurant.name,
          address: restaurant.address,
          categories: restaurant.categories,
          stars: restaurant.stars
        })
        this.showToast('Marked as visited')
      }
      this.$forceUpdate()
    },
    isVisited(restaurant) {
      const id = restaurant.restaurantId || `${restaurant.name}||${restaurant.address}`
      return rankingService.isVisited(id)
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
/* Theme and typography */
.search-container { 
  --belp-green: #07450C; 
  --belp-green-100: #eaf3ec; 
  --belp-green-200: #d6e7d9; 
  --belp-ink: #1f2a1f; 
  --belp-ink-2: #4b5a4d; 
  --belp-border: #dde5df;
  --belp-soft: rgba(7,69,12,0.06);
  max-width: 1100px; 
  margin: 0 auto; 
  padding: 2rem; 
  font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
  color: var(--belp-ink);
}

.personalization-header { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 1rem 1.25rem; 
  background: linear-gradient(135deg, rgba(7,69,12,0.05), rgba(7,69,12,0.02)); 
  border: 1px solid var(--belp-border); border-radius: 14px; 
}
.app-title { font-size: 2rem; margin: 0; color: var(--belp-green); font-weight: 800; letter-spacing: .01em; }
.app-subtitle { color: var(--belp-ink-2); margin: 0.2rem 0 0 0; }
.profile-btn, .create-profile-btn { 
  padding: 0.6rem 1rem; border: 2px solid var(--belp-green); border-radius: 12px; 
  background: #fff; color: var(--belp-green); cursor: pointer; font-weight: 700; text-decoration: none; 
  transition: all .15s ease; 
}
.profile-btn:hover, .create-profile-btn:hover { 
  background: var(--belp-green); color: #fff; 
  box-shadow: 0 8px 22px rgba(7,69,12,0.18); transform: translateY(-1px); 
}

.search-section { margin-top: 1.25rem; }
.yelp-bar { 
  display: flex; gap: 0.9rem; align-items: end; 
  background: #fff; border: 1px solid var(--belp-border); border-radius: 14px; padding: 0.9rem; 
  box-shadow: 0 8px 22px rgba(7,69,12,0.06);
}
.yelp-field { display: flex; flex-direction: column; flex: 1; }
.yelp-field-label { font-size: 0.78rem; color: var(--belp-green); margin-bottom: 0.35rem; font-weight: 800; letter-spacing: .03em; text-transform: uppercase; }
.yelp-input { 
  padding: 0.7rem 0.9rem; border: 1px solid var(--belp-border); border-radius: 12px; 
  outline: none; background: #fbfdfc; color: var(--belp-ink);
  transition: border-color .15s ease, box-shadow .15s ease, background .15s ease; 
}
.yelp-input::placeholder { color: #98a59b; }
.yelp-input:focus { border-color: var(--belp-green); box-shadow: 0 0 0 3px rgba(7,69,12,0.12); background: #fff; }
.search-btn { 
  padding: 0.8rem 1.1rem; border-radius: 12px; border: none; 
  background: linear-gradient(180deg, #0b6f14, #07450C); color: #fff; cursor: pointer; 
  font-weight: 800; min-width: 132px; letter-spacing: .01em;
  box-shadow: 0 12px 24px rgba(7,69,12,0.25); transition: transform .06s ease, filter .15s ease; 
}
.search-btn:disabled { opacity: 0.7; cursor: default; filter: saturate(.7); box-shadow: none; }
.search-btn:not(:disabled):hover { filter: brightness(1.03); }
.search-btn:not(:disabled):active { transform: translateY(1px); }
.inline-debug { margin-top: 8px; font-size: 0.8rem; color: #667; }

.loading-section { padding: 1.5rem; text-align: center; }
.empty-state { 
  padding: 2rem; text-align: center; color: var(--belp-ink); 
  background: #fff; border: 2px dashed var(--belp-border); border-radius: 14px; 
}
.empty-emoji { font-size: 2rem; }
.empty-title { margin: 0.5rem 0; font-weight: 800; }

.results-section { margin-top: 1.25rem; }
.results-header { display: flex; justify-content: space-between; align-items: center; }
.sort-select, .sort-label { font-size: 0.92rem; }
.sort-select { border: 1px solid var(--belp-border); border-radius: 12px; padding: 0.45rem 0.6rem; background: #fff; }

.results-list { margin-top: 1rem; display: grid; gap: 1rem; }
.result-card { 
  display: flex; justify-content: space-between; align-items: center; padding: 1rem; 
  border: 1px solid var(--belp-border); border-radius: 14px; background: #fff; 
  transition: box-shadow .2s ease, transform .06s ease; cursor: pointer; 
}
.result-card:hover { box-shadow: 0 16px 32px rgba(7,69,12,0.12); transform: translateY(-1px); }
.card-title { font-weight: 900; color: var(--belp-ink); letter-spacing: .01em; }
.card-sub { color: var(--belp-ink-2); font-size: 0.94rem; margin-top: 2px; }
.card-meta { color: #5f6d62; font-size: 0.86rem; margin-top: 8px; }
.card-actions { display: grid; grid-auto-flow: column; align-items: center; gap: 0.5rem; }
.btn-outline { padding: 0.45rem 0.8rem; border: 1px solid var(--belp-green); color: var(--belp-green); background: #fff; border-radius: 10px; font-weight: 700; cursor: pointer; }
.btn-outline:hover { background: rgba(7,69,12,0.05); }
.btn-visited { padding: 0.45rem 0.8rem; border: 1px solid #e0e0e0; color: #2b2b2b; background: #fff; border-radius: 10px; font-weight: 700; cursor: pointer; }
.btn-visited.active { border-color: var(--belp-green); color: var(--belp-green); background: rgba(7,69,12,0.06); }
.card-score { 
  font-weight: 900; color: var(--belp-green); font-size: 1.05rem; 
  padding: 0.45rem 0.7rem; background: var(--belp-soft); border-radius: 12px; min-width: 48px; text-align: center; 
}

/* Animated loader */
.kitchen-loader { position: relative; width: 180px; height: 140px; margin: 12px auto; }
.pot { position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 160px; height: 70px; }
.pot-body { width: 100%; height: 100%; background: #eee; border: 3px solid #ccc; border-radius: 0 0 16px 16px; }
.pot-lip { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 140px; height: 14px; background: #ddd; border: 3px solid #c9c9c9; border-bottom: none; border-radius: 12px 12px 0 0; }
.spoon { position: absolute; right: 20px; top: -32px; width: 8px; height: 48px; background: #c2a07a; border-radius: 4px; transform: rotate(10deg); animation: stir 1.8s ease-in-out infinite; transform-origin: bottom center; }
@keyframes stir { 0%,100% { transform: rotate(8deg); } 50% { transform: rotate(-6deg); } }
.bubble { position: absolute; bottom: 10px; left: 35%; width: 10px; height: 10px; background: #fff; border-radius: 50%; opacity: 0.8; animation: bubble 2s ease-in-out infinite; }
.b2 { left: 55%; animation-delay: 0.3s; }
.b3 { left: 45%; animation-delay: 0.6s; }
@keyframes bubble { 0% { transform: translateY(0) scale(1); opacity: 0.2; } 50% { transform: translateY(-20px) scale(1.2); opacity: 1; } 100% { transform: translateY(-40px) scale(0.9); opacity: 0; } }
.steam { position: absolute; bottom: 70px; left: 50%; width: 6px; height: 6px; background: rgba(255,255,255,0.7); border-radius: 50%; filter: blur(1px); animation: steam 2.6s ease-in-out infinite; }
.s1 { animation-delay: 0s; }
.s2 { animation-delay: 0.5s; }
.s3 { animation-delay: 1s; }
@keyframes steam { 0% { transform: translate(-10px, 0) scale(0.9); opacity: 0.2; } 50% { transform: translate(-4px, -25px) scale(1); opacity: 0.8; } 100% { transform: translate(8px, -50px) scale(0.8); opacity: 0; } }

/* Add minimal styles for view toggle */
.view-toggle { display: inline-flex; gap: 6px; margin: 0.5rem 0 0.75rem; }
.toggle-btn { padding: 0.4rem 0.8rem; border: 1px solid #e0e0e0; background: #fff; border-radius: 999px; cursor: pointer; font-weight: 700; color: #2b2b2b; }
.toggle-btn.active { border-color: #07450C; color: #07450C; background: rgba(7,69,12,0.06); }

@media (max-width: 768px) {
  .yelp-bar { flex-direction: column; align-items: stretch; }
}

/* Toast */
.toast { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--belp-green); color: #fff; padding: 0.6rem 1rem; border-radius: 999px; box-shadow: 0 8px 18px rgba(0,0,0,0.15); opacity: 0; transition: opacity 0.2s ease; font-weight: 700; }
.toast.show { opacity: 1; }
</style>
