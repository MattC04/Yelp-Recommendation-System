<template>
  <div class="profile-container">
    <!-- Smart Onboarding Flow -->
    <div v-if="!hasCompletedOnboarding" class="onboarding-overlay">
      <div class="onboarding-container">
        <div class="onboarding-header">
          <h1 class="onboarding-title">🍽️ Welcome to BELP</h1>
          <p class="onboarding-subtitle">Let's personalize your dining experience with AI-powered recommendations</p>
        </div>
        
        <div class="onboarding-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: (onboardingStep / 4) * 100 + '%' }"></div>
          </div>
          <span class="progress-text">Step {{ onboardingStep }} of 4</span>
        </div>

        <!-- Step 1: Cuisine Preferences -->
        <div v-if="onboardingStep === 1" class="onboarding-step">
          <h2>What cuisines do you love?</h2>
          <p>Select all that apply to help us understand your taste</p>
          <div class="preference-grid">
            <button
              v-for="cuisine in cuisineOptions"
              :key="cuisine.id"
              @click="togglePreference('cuisines', cuisine.id)"
              :class="['preference-btn', { active: userPreferences.cuisines.includes(cuisine.id) }]"
            >
              {{ cuisine.icon }} {{ cuisine.name }}
            </button>
          </div>
          <div class="step-actions">
            <button @click="nextOnboardingStep" class="btn-primary" :disabled="userPreferences.cuisines.length === 0">
              Next: Budget Preferences →
            </button>
          </div>
        </div>

        <!-- Step 2: Budget Preferences -->
        <div v-if="onboardingStep === 2" class="onboarding-step">
          <h2>What's your typical dining budget?</h2>
          <p>This helps us suggest restaurants that fit your lifestyle</p>
          <div class="budget-options">
            <button
              v-for="budget in budgetOptions"
              :key="budget.id"
              @click="selectBudget(budget.id)"
              :class="['budget-btn', { active: userPreferences.budget === budget.id }]"
            >
              <div class="budget-icon">{{ budget.icon }}</div>
              <div class="budget-info">
                <div class="budget-name">{{ budget.name }}</div>
                <div class="budget-range">{{ budget.range }}</div>
              </div>
            </button>
          </div>
          <div class="step-actions">
            <button @click="onboardingStep--" class="btn-secondary">← Back</button>
            <button @click="nextOnboardingStep" class="btn-primary" :disabled="!userPreferences.budget">
              Next: Occasion Preferences →
            </button>
          </div>
        </div>

        <!-- Step 3: Occasion Preferences -->
        <div v-if="onboardingStep === 3" class="onboarding-step">
          <h2>What occasions do you dine out for?</h2>
          <p>Select the dining experiences that matter most to you</p>
          <div class="preference-grid">
            <button
              v-for="occasion in occasionOptions"
              :key="occasion.id"
              @click="togglePreference('occasions', occasion.id)"
              :class="['preference-btn', { active: userPreferences.occasions.includes(occasion.id) }]"
            >
              {{ occasion.icon }} {{ occasion.name }}
            </button>
          </div>
          <div class="step-actions">
            <button @click="onboardingStep--" class="btn-secondary">← Back</button>
            <button @click="nextOnboardingStep" class="btn-primary" :disabled="userPreferences.occasions.length === 0">
              Next: Dietary Needs →
            </button>
          </div>
        </div>

        <!-- Step 4: Dietary Preferences -->
        <div v-if="onboardingStep === 4" class="onboarding-step">
          <h2>Any dietary restrictions or preferences?</h2>
          <p>We'll make sure all recommendations work for you</p>
          <div class="preference-grid">
            <button
              v-for="diet in dietaryOptions"
              :key="diet.id"
              @click="togglePreference('dietary', diet.id)"
              :class="['preference-btn', { active: userPreferences.dietary.includes(diet.id) }]"
            >
              {{ diet.icon }} {{ diet.name }}
            </button>
          </div>
          <div class="step-actions">
            <button @click="onboardingStep--" class="btn-secondary">← Back</button>
            <button @click="completeOnboarding" class="btn-primary">
              🎉 Start Discovering!
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Profile Content (shown after onboarding) -->
    <div v-else class="profile-content-wrapper">
      <!-- Profile Header -->
      <div class="profile-header">
        <div class="profile-avatar">
          <span class="avatar-icon">👤</span>
        </div>
        <div class="profile-info">
          <h1 class="profile-name">Welcome, Foodie!</h1>
          <p class="profile-email">foodie@example.com</p>
          <div class="profile-stats">
            <div class="stat-item">
              <span class="stat-number">12</span>
              <span class="stat-label">Reviews</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">8</span>
              <span class="stat-label">Favorites</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">5</span>
              <span class="stat-label">Lists</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Personalization Dashboard -->
      <div class="dashboard-section">
        <h2 class="section-title">🎯 Your Taste Profile</h2>
        <div class="taste-profile">
          <div class="profile-item">
            <span class="profile-label">Favorite Cuisines:</span>
            <div class="profile-tags">
              <span v-for="cuisine in userPreferences.cuisines" :key="cuisine" class="profile-tag">
                {{ getCuisineName(cuisine) }}
              </span>
            </div>
          </div>
          <div class="profile-item">
            <span class="profile-label">Budget Range:</span>
            <span class="profile-value">{{ getBudgetName(userPreferences.budget) }}</span>
          </div>
          <div class="profile-item">
            <span class="profile-label">Occasions:</span>
            <div class="profile-tags">
              <span v-for="occasion in userPreferences.occasions" :key="occasion" class="profile-tag">
                {{ getOccasionName(occasion) }}
              </span>
            </div>
          </div>
          <div class="profile-item">
            <span class="profile-label">Dietary Needs:</span>
            <div class="profile-tags">
              <span v-for="diet in userPreferences.dietary" :key="diet" class="profile-tag">
                {{ getDietaryName(diet) }}
              </span>
            </div>
          </div>
        </div>
        <button @click="editPreferences" class="edit-btn">✏️ Edit Preferences</button>
      </div>

      <!-- AI Learning Progress -->
      <div class="dashboard-section">
        <h2 class="section-title">🤖 AI Learning Progress</h2>
        <div class="learning-metrics">
          <div class="metric">
            <div class="metric-value">{{ totalInteractions }}</div>
            <div class="metric-label">Total Interactions</div>
          </div>
          <div class="metric">
            <div class="metric-value">{{ learningScore }}%</div>
            <div class="metric-label">Learning Score</div>
          </div>
          <div class="metric">
            <div class="metric-value">{{ recommendationAccuracy }}%</div>
            <div class="metric-label">Accuracy</div>
          </div>
        </div>
      </div>

      <!-- Recommendation History -->
      <div class="dashboard-section">
        <h2 class="section-title">📈 Your Recommendation Journey</h2>
        <div class="recommendation-timeline">
          <div v-for="(item, index) in recommendationHistory" :key="index" class="timeline-item">
            <div class="timeline-date">{{ formatDate(item.date) }}</div>
            <div class="timeline-content">
              <div class="timeline-icon">{{ item.icon }}</div>
              <div class="timeline-text">
                <strong>{{ item.action }}</strong>
                <span class="timeline-detail">{{ item.detail }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Back to Search Button -->
      <div class="back-to-search">
        <router-link to="/search" class="search-btn">
          🔍 Back to Search
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileView',
  data() {
    return {
      onboardingStep: 1,
      userPreferences: {
        cuisines: [],
        budget: null,
        occasions: [],
        dietary: []
      },
      cuisineOptions: [
        { id: 'italian', name: 'Italian', icon: '🍕' },
        { id: 'mexican', name: 'Mexican', icon: '🌮' },
        { id: 'chinese', name: 'Chinese', icon: '🥟' },
        { id: 'japanese', name: 'Japanese', icon: '🍣' },
        { id: 'indian', name: 'Indian', icon: '🍛' },
        { id: 'thai', name: 'Thai', icon: '🍜' },
        { id: 'mediterranean', name: 'Mediterranean', icon: '🍽️' },
        { id: 'american', name: 'American', icon: '🍔' },
        { id: 'french', name: 'French', icon: '🥖' },
        { id: 'greek', name: 'Greek', icon: '🧀' }
      ],
      budgetOptions: [
        { id: 'budget', name: 'Budget-Friendly', icon: '💰', range: '$10-$30' },
        { id: 'moderate', name: 'Moderate', icon: '💸', range: '$30-$70' },
        { id: 'expensive', name: 'Expensive', icon: '💎', range: '$70+' }
      ],
      occasionOptions: [
        { id: 'casual', name: 'Casual Dining', icon: '🍴' },
        { id: 'romantic', name: 'Romantic Dinner', icon: '💖' },
        { id: 'family', name: 'Family Gathering', icon: '👨‍👩‍👧‍👦' },
        { id: 'business', name: 'Business Lunch', icon: '👔' },
        { id: 'date', name: 'Date Night', icon: '👫' },
        { id: 'special', name: 'Special Occasion', icon: '🎉' }
      ],
      dietaryOptions: [
        { id: 'vegetarian', name: 'Vegetarian', icon: '🥦' },
        { id: 'vegan', name: 'Vegan', icon: '🌱' },
        { id: 'glutenFree', name: 'Gluten-Free', icon: '🌾' },
        { id: 'halal', name: 'Halal', icon: '🕌' },
        { id: 'kosher', name: 'Kosher', icon: '⚖️' },
        { id: 'dairyFree', name: 'Dairy-Free', icon: '🥛' }
      ],
      hasCompletedOnboarding: false,
      totalInteractions: 0,
      learningScore: 0,
      recommendationAccuracy: 0,
      recommendationHistory: [
        { date: '2024-01-15', action: 'New User Onboarding', detail: 'Completed initial preferences quiz' },
        { date: '2024-01-16', action: 'First Search', detail: 'Searched for "Italian restaurants in New York"' },
        { date: '2024-01-17', action: 'First Recommendation', detail: 'Received AI-powered Italian restaurant suggestion' },
        { date: '2024-01-18', action: 'Second Search', detail: 'Searched for "Mexican food in Los Angeles"' },
        { date: '2024-01-19', action: 'Second Recommendation', detail: 'Received AI-powered Mexican restaurant suggestion' }
      ]
    }
  },
  computed: {
    // Analyze time preferences
    timePreferences() {
      const timeCounts = {}
      this.recentReviews.forEach(review => {
        const time = review.visitTime
        timeCounts[time] = (timeCounts[time] || 0) + 1
      })
      return timeCounts
    },
    
    // Analyze day preferences
    dayPreferences() {
      const dayCounts = {}
      this.recentReviews.forEach(review => {
        const day = review.visitDay
        dayCounts[day] = (dayCounts[day] || 0) + 1
      })
      return dayCounts
    },
    
    // Analyze cuisine preferences
    cuisinePreferences() {
      const cuisineCounts = {}
      this.recentReviews.forEach(review => {
        const cuisine = review.foodType
        cuisineCounts[cuisine] = (cuisineCounts[cuisine] || 0) + 1
      })
      return cuisineCounts
    },
    
    // Analyze rating patterns
    ratingPatterns() {
      const ratingCounts = {}
      this.recentReviews.forEach(review => {
        const rating = review.rating
        ratingCounts[rating] = (ratingCounts[rating] || 0) + 1
      })
      return ratingCounts
    },
    
    // Get max counts for normalization
    maxTimeCount() {
      return Math.max(...Object.values(this.timePreferences))
    },
    
    maxDayCount() {
      return Math.max(...Object.values(this.dayPreferences))
    },
    
    maxCuisineCount() {
      return Math.max(...Object.values(this.cuisinePreferences))
    },
    
    maxRatingCount() {
      return Math.max(...Object.values(this.ratingPatterns))
    },
    
    // Get top preferences
    topCuisine() {
      const cuisines = Object.entries(this.cuisinePreferences)
      return cuisines.sort((a, b) => b[1] - a[1])[0]?.[0] || 'Various'
    },
    
    topDay() {
      const days = Object.entries(this.dayPreferences)
      return days.sort((a, b) => b[1] - a[1])[0]?.[0] || 'Various'
    },
    
    topTime() {
      const times = Object.entries(this.timePreferences)
      return times.sort((a, b) => b[1] - a[1])[0]?.[0] || 'Various'
    },
    
    // Find unexplored cuisines
    unexploredCuisine() {
      const allCuisines = ['Italian', 'Mexican', 'Chinese', 'Japanese', 'Indian', 'Thai', 'Mediterranean', 'American', 'French', 'Greek']
      const exploredCuisines = Object.keys(this.cuisinePreferences)
      const unexplored = allCuisines.filter(cuisine => !exploredCuisines.includes(cuisine))
      return unexplored[0] || 'International'
    }
  },
  mounted() {
    this.checkExistingPreferences();
  },
  methods: {
    checkExistingPreferences() {
      const savedPreferences = localStorage.getItem('belp_user_preferences');
      if (savedPreferences) {
        try {
          this.userPreferences = JSON.parse(savedPreferences);
          this.hasCompletedOnboarding = true;
          this.updateMetrics();
        } catch (e) {
          console.warn('Failed to load user preferences:', e);
        }
      }
    },
    updateMetrics() {
      // Calculate learning score based on preferences
      const preferenceCount = Object.values(this.userPreferences).reduce((total, pref) => {
        return total + (Array.isArray(pref) ? pref.length : (pref ? 1 : 0));
      }, 0);
      
      this.learningScore = Math.min(100, Math.round((preferenceCount / 15) * 100));
      this.totalInteractions = Math.floor(Math.random() * 50) + 10; // Simulated data
      this.recommendationAccuracy = Math.min(100, Math.round((this.learningScore + 70) / 2));
    },
    savePreferences() {
      localStorage.setItem('belp_user_preferences', JSON.stringify(this.userPreferences));
      this.updateMetrics();
      console.log('Preferences saved:', this.userPreferences);
    },
    removeFavorite(restaurantId) {
      this.favoriteRestaurants = this.favoriteRestaurants.filter(r => r.id !== restaurantId)
    },
    saveSettings() {
      console.log('Saving settings:', this.settings)
      // Show success message
    },
    togglePreference(category, id) {
      const index = this.userPreferences[category].indexOf(id);
      if (index > -1) {
        this.userPreferences[category].splice(index, 1);
      } else {
        this.userPreferences[category].push(id);
      }
    },
    selectBudget(id) {
      this.userPreferences.budget = id;
    },
    nextOnboardingStep() {
      if (this.onboardingStep < 4) {
        this.onboardingStep++;
      }
    },
    completeOnboarding() {
      this.hasCompletedOnboarding = true;
      this.onboardingStep = 1; // Reset for main profile view
      this.userPreferences = {
        cuisines: [],
        budget: null,
        occasions: [],
        dietary: []
      };
      // TODO: Implement actual onboarding completion logic (e.g., save preferences)
      console.log('Onboarding completed. User preferences:', this.userPreferences);
    },
    editPreferences() {
      this.hasCompletedOnboarding = false;
      this.onboardingStep = 1;
    },
    getCuisineName(id) {
      const cuisine = this.cuisineOptions.find(c => c.id === id);
      return cuisine ? cuisine.name : id;
    },
    getBudgetName(id) {
      const budget = this.budgetOptions.find(b => b.id === id);
      return budget ? budget.name : id;
    },
    getOccasionName(id) {
      const occasion = this.occasionOptions.find(o => o.id === id);
      return occasion ? occasion.name : id;
    },
    getDietaryName(id) {
      const dietary = this.dietaryOptions.find(d => d.id === id);
      return dietary ? dietary.name : id;
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    }
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(7, 69, 12, 0.05), rgba(7, 69, 12, 0.1));
  border-radius: 16px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.profile-avatar {
  flex-shrink: 0;
}

.avatar-icon {
  font-size: 4rem;
  display: block;
}

.profile-info {
  flex: 1;
}

.profile-name {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  font-weight: bold;
}

.profile-email {
  color: #07450C;
  margin: 0 0 1.5rem 0;
  opacity: 0.8;
}

.profile-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  color: #07450C;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  color: #07450C;
  font-size: 0.9rem;
  opacity: 0.8;
}

.profile-content {
  display: grid;
  gap: 2rem;
}

.profile-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.section-title {
  color: #07450C;
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preferences-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.preference-item {
  display: flex;
  align-items: center;
}

.preference-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  color: #07450C;
  font-weight: 500;
}

.preference-checkbox {
  width: 18px;
  height: 18px;
  accent-color: #07450C;
}

.preference-text {
  font-size: 1rem;
}

.cuisine-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.cuisine-tag {
  padding: 0.5rem 1rem;
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
  border: 2px solid transparent;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.cuisine-tag:hover {
  background: rgba(7, 69, 12, 0.2);
}

.cuisine-tag.active {
  background: #07450C;
  color: white;
  border-color: #07450C;
}

.save-btn {
  background: #07450C;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-btn:hover {
  background: #0a5a0f;
}

.reviews-list {
  display: grid;
  gap: 1rem;
}

.review-card {
  padding: 1.5rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 8px;
  border-left: 4px solid #07450C;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.restaurant-name {
  color: #07450C;
  margin: 0;
  font-size: 1.2rem;
  font-weight: bold;
}

.review-rating {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.stars {
  color: #FFD700;
  font-size: 1.1rem;
}

.star {
  margin-right: 2px;
}

.review-date {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

.review-text {
  color: #07450C;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.review-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1rem;
  color: #07450C;
  font-size: 0.9rem;
  opacity: 0.8;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.meta-icon {
  font-size: 1rem;
}

.review-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.review-tag {
  padding: 0.25rem 0.75rem;
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.insight-card {
  background: rgba(7, 69, 12, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.insight-title {
  color: #07450C;
  margin: 0 0 1.5rem 0;
  font-size: 1.2rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.insight-content {
  display: grid;
  gap: 1rem;
}

.preference-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.preference-label {
  font-size: 0.9rem;
  color: #07450C;
  opacity: 0.8;
  margin-bottom: 0.5rem;
}

.preference-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.preference-fill {
  height: 100%;
  background: #07450C;
  border-radius: 4px;
  transition: width 0.3s ease-in-out;
}

.preference-count {
  font-size: 0.8rem;
  color: #07450C;
  opacity: 0.7;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.recommendation-card {
  background: rgba(7, 69, 12, 0.05);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.rec-title {
  color: #07450C;
  margin: 0 0 1.5rem 0;
  font-size: 1.2rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rec-content {
  color: #07450C;
  font-size: 1rem;
  line-height: 1.6;
}

.rec-text {
  margin-bottom: 0.75rem;
}

.rec-suggestion {
  font-style: italic;
  color: #07450C;
  opacity: 0.8;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.favorite-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(7, 69, 12, 0.1);
  position: relative;
}

.favorite-image {
  flex-shrink: 0;
}

.restaurant-emoji {
  font-size: 2rem;
}

.favorite-info {
  flex: 1;
}

.favorite-name {
  color: #07450C;
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.favorite-cuisine {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.favorite-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rating-text {
  color: #07450C;
  font-size: 0.9rem;
  font-weight: 500;
}

.remove-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: #ff4444;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #cc0000;
}

.settings-form {
  display: grid;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  color: #07450C;
  font-weight: bold;
  font-size: 0.9rem;
}

.form-input {
  padding: 0.75rem;
  border: 2px solid rgba(7, 69, 12, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  color: #07450C;
  background: white;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #07450C;
}

.form-input::placeholder {
  color: #07450C;
  opacity: 0.5;
}

/* Onboarding Styles */
.onboarding-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #07450C 0%, #0a5a0f 100%);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.onboarding-container {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  text-align: center;
}

.onboarding-header {
  margin-bottom: 2rem;
}

.onboarding-title {
  font-size: 2.5rem;
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-weight: bold;
}

.onboarding-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

.onboarding-progress {
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #07450C, #0a5a0f);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: #666;
}

.onboarding-step h2 {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.onboarding-step p {
  color: #666;
  margin: 0 0 1.5rem 0;
}

.preference-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.preference-btn {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.preference-btn:hover {
  border-color: #07450C;
  background: rgba(7, 69, 12, 0.05);
}

.preference-btn.active {
  border-color: #07450C;
  background: #07450C;
  color: white;
}

.budget-options {
  display: grid;
  gap: 1rem;
  margin-bottom: 2rem;
}

.budget-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.budget-btn:hover {
  border-color: #07450C;
  background: rgba(7, 69, 12, 0.05);
}

.budget-btn.active {
  border-color: #07450C;
  background: #07450C;
  color: white;
}

.budget-icon {
  font-size: 1.5rem;
}

.budget-name {
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.budget-range {
  font-size: 0.9rem;
  opacity: 0.8;
}

.step-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #07450C;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0a5a0f;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

/* Dashboard Styles */
.dashboard-section {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 8px 24px rgba(7, 69, 12, 0.1);
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.section-title {
  color: #07450C;
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.taste-profile {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.profile-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.profile-label {
  font-weight: bold;
  color: #07450C;
  min-width: 120px;
}

.profile-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.profile-tag {
  background: #07450C;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
}

.profile-value {
  color: #333;
  font-weight: 500;
}

.edit-btn {
  padding: 0.75rem 1.5rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  background: #0a5a0f;
  transform: translateY(-2px);
}

.learning-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.metric {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  border: 1px solid #dee2e6;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  color: #07450C;
  margin-bottom: 0.5rem;
}

.metric-label {
  color: #666;
  font-size: 0.9rem;
}

.recommendation-timeline {
  max-height: 300px;
  overflow-y: auto;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-left: 3px solid #07450C;
  margin-left: 1rem;
  position: relative;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -0.5rem;
  top: 1.5rem;
  width: 0.5rem;
  height: 0.5rem;
  background: #07450C;
  border-radius: 50%;
}

.timeline-date {
  font-size: 0.8rem;
  color: #666;
  min-width: 80px;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.timeline-icon {
  font-size: 1.2rem;
}

.timeline-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.timeline-text strong {
  color: #07450C;
}

.timeline-detail {
  color: #666;
  font-size: 0.9rem;
}

.back-to-search {
  text-align: center;
  margin-top: 2rem;
}

.search-btn {
  display: inline-block;
  padding: 1rem 2rem;
  background: #07450C;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  transition: all 0.2s ease;
}

.search-btn:hover {
  background: #0a5a0f;
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .profile-container {
    padding: 1rem;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
    padding: 1.5rem;
  }
  
  .profile-stats {
    justify-content: center;
  }
  
  .preferences-grid {
    grid-template-columns: 1fr;
  }
  
  .favorites-grid {
    grid-template-columns: 1fr;
  }
  
  .review-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .review-rating {
    align-items: flex-start;
  }

  .onboarding-container {
    padding: 2rem 1.5rem;
    margin: 1rem;
  }
  
  .onboarding-title {
    font-size: 2rem;
  }
  
  .preference-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }
  
  .dashboard-section {
    padding: 1.5rem;
  }
  
  .learning-metrics {
    grid-template-columns: 1fr;
  }
  
  .profile-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .profile-label {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .profile-header {
    padding: 1rem;
  }
  
  .profile-section {
    padding: 1.5rem;
  }
  
  .cuisine-tags {
    justify-content: center;
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .review-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .insight-content {
    gap: 0.75rem;
  }
  
  .preference-item {
    align-items: center;
  }
  
  .preference-label {
    text-align: center;
  }
}
</style> 