<template>
  <div class="profile-container">
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

    <div class="profile-content">
      <!-- Preferences Section -->
      <div class="profile-section">
        <h2 class="section-title">🍽️ Dietary Preferences</h2>
        <div class="preferences-grid">
          <div class="preference-item">
            <label class="preference-label">
              <input type="checkbox" v-model="preferences.vegetarian" class="preference-checkbox">
              <span class="preference-text">Vegetarian</span>
            </label>
          </div>
          <div class="preference-item">
            <label class="preference-label">
              <input type="checkbox" v-model="preferences.vegan" class="preference-checkbox">
              <span class="preference-text">Vegan</span>
            </label>
          </div>
          <div class="preference-item">
            <label class="preference-label">
              <input type="checkbox" v-model="preferences.glutenFree" class="preference-checkbox">
              <span class="preference-text">Gluten-Free</span>
            </label>
          </div>
          <div class="preference-item">
            <label class="preference-label">
              <input type="checkbox" v-model="preferences.halal" class="preference-checkbox">
              <span class="preference-text">Halal</span>
            </label>
          </div>
          <div class="preference-item">
            <label class="preference-label">
              <input type="checkbox" v-model="preferences.kosher" class="preference-checkbox">
              <span class="preference-text">Kosher</span>
            </label>
          </div>
          <div class="preference-item">
            <label class="preference-label">
              <input type="checkbox" v-model="preferences.dairyFree" class="preference-checkbox">
              <span class="preference-text">Dairy-Free</span>
            </label>
          </div>
        </div>
        <button @click="savePreferences" class="save-btn">Save Preferences</button>
      </div>

      <!-- Favorite Cuisines -->
      <div class="profile-section">
        <h2 class="section-title">🌮 Favorite Cuisines</h2>
        <div class="cuisine-tags">
          <span 
            v-for="cuisine in cuisines" 
            :key="cuisine.name"
            :class="['cuisine-tag', { active: cuisine.active }]"
            @click="toggleCuisine(cuisine.name)"
          >
            {{ cuisine.name }}
          </span>
        </div>
      </div>

      <!-- Recent Reviews -->
      <div class="profile-section">
        <h2 class="section-title">📝 Recent Reviews</h2>
        <div class="reviews-list">
          <div v-for="review in recentReviews" :key="review.id" class="review-card">
            <div class="review-header">
              <h3 class="restaurant-name">{{ review.restaurantName }}</h3>
              <div class="review-rating">
                <span class="stars">
                  <span v-for="i in 5" :key="i" class="star">
                    {{ i <= review.rating ? '★' : '☆' }}
                  </span>
                </span>
                <span class="review-date">{{ review.date }}</span>
              </div>
            </div>
            <p class="review-text">{{ review.text }}</p>
            <div class="review-meta">
              <span class="meta-item">
                <span class="meta-icon">🕐</span>
                {{ review.visitTime }} ({{ review.visitDay }})
              </span>
              <span class="meta-item">
                <span class="meta-icon">🍽️</span>
                {{ review.foodType }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">💰</span>
                {{ review.priceRange }}
              </span>
            </div>
            <div class="review-tags">
              <span v-for="tag in review.tags" :key="tag" class="review-tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Learning Insights -->
      <div class="profile-section">
        <h2 class="section-title">🧠 Your Dining Patterns</h2>
        <div class="insights-grid">
          <!-- Time Preferences -->
          <div class="insight-card">
            <h3 class="insight-title">⏰ Time Preferences</h3>
            <div class="insight-content">
              <div v-for="(count, time) in timePreferences" :key="time" class="preference-item">
                <span class="preference-label">{{ formatTime(time) }}</span>
                <div class="preference-bar">
                  <div class="preference-fill" :style="{ width: (count / maxTimeCount * 100) + '%' }"></div>
                </div>
                <span class="preference-count">{{ count }}</span>
              </div>
            </div>
          </div>

          <!-- Day Preferences -->
          <div class="insight-card">
            <h3 class="insight-title">📅 Day Preferences</h3>
            <div class="insight-content">
              <div v-for="(count, day) in dayPreferences" :key="day" class="preference-item">
                <span class="preference-label">{{ day }}</span>
                <div class="preference-bar">
                  <div class="preference-fill" :style="{ width: (count / maxDayCount * 100) + '%' }"></div>
                </div>
                <span class="preference-count">{{ count }}</span>
              </div>
            </div>
          </div>

          <!-- Cuisine Preferences -->
          <div class="insight-card">
            <h3 class="insight-title">🍕 Cuisine Preferences</h3>
            <div class="insight-content">
              <div v-for="(count, cuisine) in cuisinePreferences" :key="cuisine" class="preference-item">
                <span class="preference-label">{{ cuisine }}</span>
                <div class="preference-bar">
                  <div class="preference-fill" :style="{ width: (count / maxCuisineCount * 100) + '%' }"></div>
                </div>
                <span class="preference-count">{{ count }}</span>
              </div>
            </div>
          </div>

          <!-- Rating Patterns -->
          <div class="insight-card">
            <h3 class="insight-title">⭐ Rating Patterns</h3>
            <div class="insight-content">
              <div v-for="(count, rating) in ratingPatterns" :key="rating" class="preference-item">
                <span class="preference-label">{{ rating }} Stars</span>
                <div class="preference-bar">
                  <div class="preference-fill" :style="{ width: (count / maxRatingCount * 100) + '%' }"></div>
                </div>
                <span class="preference-count">{{ count }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Smart Recommendations -->
      <div class="profile-section">
        <h2 class="section-title">🎯 Smart Recommendations</h2>
        <div class="recommendations-grid">
          <div class="recommendation-card">
            <h3 class="rec-title">Based on Your Patterns</h3>
            <div class="rec-content">
              <p class="rec-text">You love <strong>{{ topCuisine }}</strong> on <strong>{{ topDay }}</strong> for <strong>{{ topTime }}</strong></p>
              <p class="rec-suggestion">Try exploring more {{ topCuisine }} restaurants during these times!</p>
            </div>
          </div>
          
          <div class="recommendation-card">
            <h3 class="rec-title">Hidden Gems</h3>
            <div class="rec-content">
              <p class="rec-text">You've rated <strong>{{ topCuisine }}</strong> restaurants highly</p>
              <p class="rec-suggestion">Discover new {{ topCuisine }} spots in your area</p>
            </div>
          </div>
          
          <div class="recommendation-card">
            <h3 class="rec-title">Try Something New</h3>
            <div class="rec-content">
              <p class="rec-text">You haven't explored <strong>{{ unexploredCuisine }}</strong> much</p>
              <p class="rec-suggestion">Expand your palate with {{ unexploredCuisine }} cuisine</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Favorite Restaurants -->
      <div class="profile-section">
        <h2 class="section-title">❤️ Favorite Restaurants</h2>
        <div class="favorites-grid">
          <div v-for="restaurant in favoriteRestaurants" :key="restaurant.id" class="favorite-card">
            <div class="favorite-image">
              <span class="restaurant-emoji">🍕</span>
            </div>
            <div class="favorite-info">
              <h3 class="favorite-name">{{ restaurant.name }}</h3>
              <p class="favorite-cuisine">{{ restaurant.cuisine }}</p>
              <div class="favorite-rating">
                <span class="stars">
                  <span v-for="i in 5" :key="i" class="star">
                    {{ i <= restaurant.rating ? '★' : '☆' }}
                  </span>
                </span>
                <span class="rating-text">{{ restaurant.rating }}/5</span>
              </div>
            </div>
            <button @click="removeFavorite(restaurant.id)" class="remove-btn">×</button>
          </div>
        </div>
      </div>

      <!-- Account Settings -->
      <div class="profile-section">
        <h2 class="section-title">⚙️ Account Settings</h2>
        <div class="settings-form">
          <div class="form-group">
            <label class="form-label">Display Name</label>
            <input v-model="settings.displayName" type="text" class="form-input" placeholder="Enter display name">
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="settings.email" type="email" class="form-input" placeholder="Enter email">
          </div>
          <div class="form-group">
            <label class="form-label">Location</label>
            <input v-model="settings.location" type="text" class="form-input" placeholder="Enter your city">
          </div>
          <button @click="saveSettings" class="save-btn">Save Settings</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileView',
  data() {
    return {
      preferences: {
        vegetarian: false,
        vegan: false,
        glutenFree: false,
        halal: false,
        kosher: false,
        dairyFree: false
      },
      cuisines: [
        { name: 'Italian', active: true },
        { name: 'Mexican', active: true },
        { name: 'Chinese', active: false },
        { name: 'Japanese', active: true },
        { name: 'Indian', active: false },
        { name: 'Thai', active: false },
        { name: 'Mediterranean', active: true },
        { name: 'American', active: false }
      ],
      recentReviews: [
        {
          id: 1,
          restaurantName: 'Pizza Palace',
          rating: 5,
          date: '2 days ago',
          text: 'Amazing pizza! The crust was perfectly crispy and the toppings were fresh.',
          tags: ['Great Service', 'Fresh Ingredients', 'Cozy Atmosphere'],
          visitTime: 'dinner',
          visitDay: 'Friday',
          foodType: 'Italian',
          cuisine: 'Pizza',
          priceRange: 'moderate',
          ambiance: 'casual',
          visitDate: '2024-01-12',
          visitHour: 19
        },
        {
          id: 2,
          restaurantName: 'Sushi Express',
          rating: 4,
          date: '1 week ago',
          text: 'Fresh sushi and quick service. Would definitely recommend!',
          tags: ['Fresh Fish', 'Quick Service'],
          visitTime: 'lunch',
          visitDay: 'Tuesday',
          foodType: 'Japanese',
          cuisine: 'Sushi',
          priceRange: 'moderate',
          ambiance: 'casual',
          visitDate: '2024-01-05',
          visitHour: 12
        },
        {
          id: 3,
          restaurantName: 'Sunrise Diner',
          rating: 5,
          date: '3 days ago',
          text: 'Best breakfast in town! The pancakes are fluffy and the coffee is perfect.',
          tags: ['Breakfast', 'Coffee', 'Friendly Staff'],
          visitTime: 'breakfast',
          visitDay: 'Saturday',
          foodType: 'American',
          cuisine: 'Breakfast',
          priceRange: 'budget',
          ambiance: 'casual',
          visitDate: '2024-01-10',
          visitHour: 8
        },
        {
          id: 4,
          restaurantName: 'Taco Fiesta',
          rating: 4,
          date: '2 weeks ago',
          text: 'Authentic Mexican flavors and great margaritas!',
          tags: ['Authentic', 'Margaritas', 'Spicy'],
          visitTime: 'dinner',
          visitDay: 'Wednesday',
          foodType: 'Mexican',
          cuisine: 'Tacos',
          priceRange: 'budget',
          ambiance: 'lively',
          visitDate: '2023-12-28',
          visitHour: 20
        },
        {
          id: 5,
          restaurantName: 'Golden Dragon',
          rating: 3,
          date: '1 month ago',
          text: 'Good Chinese food but service was slow.',
          tags: ['Chinese', 'Slow Service'],
          visitTime: 'lunch',
          visitDay: 'Monday',
          foodType: 'Chinese',
          cuisine: 'Asian',
          priceRange: 'budget',
          ambiance: 'casual',
          visitDate: '2023-12-15',
          visitHour: 13
        },
        {
          id: 6,
          restaurantName: 'Rooftop Lounge',
          rating: 5,
          date: '1 week ago',
          text: 'Incredible rooftop views and craft cocktails!',
          tags: ['Rooftop', 'Cocktails', 'Romantic'],
          visitTime: 'dinner',
          visitDay: 'Friday',
          foodType: 'American',
          cuisine: 'Bar Food',
          priceRange: 'expensive',
          ambiance: 'romantic',
          visitDate: '2024-01-05',
          visitHour: 21
        },
        {
          id: 7,
          restaurantName: 'Farm Fresh Market',
          rating: 4,
          date: '2 weeks ago',
          text: 'Healthy options and organic ingredients. Great for brunch!',
          tags: ['Healthy', 'Organic', 'Brunch'],
          visitTime: 'brunch',
          visitDay: 'Sunday',
          foodType: 'American',
          cuisine: 'Healthy',
          priceRange: 'moderate',
          ambiance: 'casual',
          visitDate: '2023-12-31',
          visitHour: 11
        },
        {
          id: 8,
          restaurantName: 'Midnight Bites',
          rating: 4,
          date: '3 weeks ago',
          text: 'Perfect late-night food! The burgers hit the spot.',
          tags: ['Late Night', 'Burgers', 'Quick'],
          visitTime: 'late-night',
          visitDay: 'Saturday',
          foodType: 'American',
          cuisine: 'Burgers',
          priceRange: 'budget',
          ambiance: 'casual',
          visitDate: '2023-12-23',
          visitHour: 2
        }
      ],
      favoriteRestaurants: [
        {
          id: 1,
          name: 'Pizza Palace',
          cuisine: 'Italian',
          rating: 5
        },
        {
          id: 2,
          name: 'Sushi Express',
          cuisine: 'Japanese',
          rating: 4
        },
        {
          id: 3,
          name: 'Taco Fiesta',
          cuisine: 'Mexican',
          rating: 4
        }
      ],
      settings: {
        displayName: 'Foodie',
        email: 'foodie@example.com',
        location: 'New York, NY'
      }
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
  methods: {
    formatTime(time) {
      const timeMap = {
        'breakfast': 'Breakfast (6AM-11AM)',
        'brunch': 'Brunch (10AM-2PM)',
        'lunch': 'Lunch (11AM-3PM)',
        'dinner': 'Dinner (5PM-9PM)',
        'late-night': 'Late Night (9PM-2AM)'
      }
      return timeMap[time] || time
    },
    
    toggleCuisine(cuisineName) {
      const cuisine = this.cuisines.find(c => c.name === cuisineName)
      if (cuisine) {
        cuisine.active = !cuisine.active
      }
    },
    savePreferences() {
      // TODO: Implement API call to save preferences
      console.log('Saving preferences:', this.preferences)
      // Show success message
    },
    removeFavorite(restaurantId) {
      this.favoriteRestaurants = this.favoriteRestaurants.filter(r => r.id !== restaurantId)
    },
    saveSettings() {
      // TODO: Implement API call to save settings
      console.log('Saving settings:', this.settings)
      // Show success message
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