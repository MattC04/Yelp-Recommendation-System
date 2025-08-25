<template>
  <div class="smart-recommendations">
    <h3 class="rec-header">🎯 Smart Recommendations Based on Your Patterns</h3>
    
    <!-- Time-based Recommendations -->
    <div class="rec-section">
      <h4 class="rec-subtitle">⏰ Based on Current Time</h4>
      <div class="rec-cards">
        <div v-for="rec in timeBasedRecs" :key="rec.id" class="rec-card">
          <div class="rec-icon">{{ rec.icon }}</div>
          <div class="rec-content">
            <h5 class="rec-title">{{ rec.title }}</h5>
            <p class="rec-description">{{ rec.description }}</p>
            <div class="rec-meta">
              <span class="rec-time">{{ rec.time }}</span>
              <span class="rec-cuisine">{{ rec.cuisine }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pattern-based Recommendations -->
    <div class="rec-section">
      <h4 class="rec-subtitle">📊 Based on Your History</h4>
      <div class="rec-cards">
        <div v-for="rec in patternBasedRecs" :key="rec.id" class="rec-card">
          <div class="rec-icon">{{ rec.icon }}</div>
          <div class="rec-content">
            <h5 class="rec-title">{{ rec.title }}</h5>
            <p class="rec-description">{{ rec.description }}</p>
            <div class="rec-confidence">
              <span class="confidence-label">Confidence:</span>
              <div class="confidence-bar">
                <div class="confidence-fill" :style="{ width: rec.confidence + '%' }"></div>
              </div>
              <span class="confidence-value">{{ rec.confidence }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Discovery Recommendations -->
    <div class="rec-section">
      <h4 class="rec-subtitle">🌟 Try Something New</h4>
      <div class="rec-cards">
        <div v-for="rec in discoveryRecs" :key="rec.id" class="rec-card">
          <div class="rec-icon">{{ rec.icon }}</div>
          <div class="rec-content">
            <h5 class="rec-title">{{ rec.title }}</h5>
            <p class="rec-description">{{ rec.description }}</p>
            <button @click="exploreCuisine(rec.cuisine)" class="explore-btn">
              Explore {{ rec.cuisine }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SmartRecommendations',
  props: {
    userPatterns: {
      type: Object,
      default: () => ({
        timePreferences: {},
        dayPreferences: {},
        cuisinePreferences: {},
        ratingPatterns: {}
      })
    },
    currentTime: {
      type: String,
      default: 'dinner'
    },
    currentDay: {
      type: String,
      default: 'Friday'
    }
  },
  computed: {
    timeBasedRecs() {
      const currentHour = new Date().getHours()
      let mealTime = 'dinner'
      
      if (currentHour >= 6 && currentHour < 11) mealTime = 'breakfast'
      else if (currentHour >= 11 && currentHour < 15) mealTime = 'lunch'
      else if (currentHour >= 15 && currentHour < 18) mealTime = 'afternoon'
      else if (currentHour >= 18 && currentHour < 22) mealTime = 'dinner'
      else mealTime = 'late-night'
      
      const topCuisine = this.getTopCuisine()
      
      return [
        {
          id: 1,
          icon: '🍽️',
          title: `Perfect ${mealTime} choice`,
          description: `Based on your love for ${topCuisine} during ${mealTime}`,
          time: mealTime,
          cuisine: topCuisine
        },
        {
          id: 2,
          icon: '⭐',
          title: 'Highly rated by you',
          description: `You've given 5 stars to ${topCuisine} restaurants`,
          time: mealTime,
          cuisine: topCuisine
        }
      ]
    },
    
    patternBasedRecs() {
      const topCuisine = this.getTopCuisine()
      const topDay = this.getTopDay()
      const topTime = this.getTopTime()
      
      return [
        {
          id: 1,
          icon: '📅',
          title: `${topDay} is your favorite day`,
          description: `You visit restaurants most on ${topDay}`,
          confidence: this.calculateConfidence('day', topDay)
        },
        {
          id: 2,
          icon: '🕐',
          title: `${topTime} is your preferred time`,
          description: `You enjoy dining during ${topTime}`,
          confidence: this.calculateConfidence('time', topTime)
        },
        {
          id: 3,
          icon: '🍕',
          title: `${topCuisine} is your top choice`,
          description: `You've visited ${topCuisine} restaurants most often`,
          confidence: this.calculateConfidence('cuisine', topCuisine)
        }
      ]
    },
    
    discoveryRecs() {
      const unexploredCuisines = this.getUnexploredCuisines()
      
      return unexploredCuisines.slice(0, 3).map((cuisine, index) => ({
        id: index + 1,
        icon: this.getCuisineIcon(cuisine),
        title: `Try ${cuisine} cuisine`,
        description: `Expand your palate with ${cuisine} flavors`,
        cuisine: cuisine
      }))
    }
  },
  methods: {
    getTopCuisine() {
      const cuisines = Object.entries(this.userPatterns.cuisinePreferences || {})
      return cuisines.sort((a, b) => b[1] - a[1])[0]?.[0] || 'Various'
    },
    
    getTopDay() {
      const days = Object.entries(this.userPatterns.dayPreferences || {})
      return days.sort((a, b) => b[1] - a[1])[0]?.[0] || 'Various'
    },
    
    getTopTime() {
      const times = Object.entries(this.userPatterns.timePreferences || {})
      return times.sort((a, b) => b[1] - a[1])[0]?.[0] || 'Various'
    },
    
    calculateConfidence(type, value) {
      const patterns = this.userPatterns[`${type}Preferences`] || {}
      const total = Object.values(patterns).reduce((sum, count) => sum + count, 0)
      const count = patterns[value] || 0
      return total > 0 ? Math.round((count / total) * 100) : 0
    },
    
    getUnexploredCuisines() {
      const allCuisines = ['Italian', 'Mexican', 'Chinese', 'Japanese', 'Indian', 'Thai', 'Mediterranean', 'American', 'French', 'Greek', 'Korean', 'Vietnamese', 'Lebanese', 'Spanish', 'German']
      const exploredCuisines = Object.keys(this.userPatterns.cuisinePreferences || {})
      return allCuisines.filter(cuisine => !exploredCuisines.includes(cuisine))
    },
    
    getCuisineIcon(cuisine) {
      const iconMap = {
        'Italian': '🍝',
        'Mexican': '🌮',
        'Chinese': '🥡',
        'Japanese': '🍣',
        'Indian': '🍛',
        'Thai': '🍜',
        'Mediterranean': '🥙',
        'American': '🍔',
        'French': '🥐',
        'Greek': '🥙',
        'Korean': '🍚',
        'Vietnamese': '🍜',
        'Lebanese': '🥙',
        'Spanish': '🥘',
        'German': '🍖'
      }
      return iconMap[cuisine] || '🍽️'
    },
    
    exploreCuisine(cuisine) {
      this.$emit('explore-cuisine', cuisine)
    }
  }
}
</script>

<style scoped>
.smart-recommendations {
  margin: 2rem 0;
  padding: 2rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.rec-header {
  color: #07450C;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 0 2rem 0;
  text-align: center;
}

.rec-section {
  margin-bottom: 2rem;
}

.rec-subtitle {
  color: #07450C;
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rec-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.rec-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(7, 69, 12, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.rec-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.rec-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.rec-content {
  flex: 1;
}

.rec-title {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.rec-description {
  color: #07450C;
  margin: 0 0 1rem 0;
  line-height: 1.5;
  opacity: 0.8;
}

.rec-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.rec-time, .rec-cuisine {
  color: #07450C;
  opacity: 0.7;
  font-weight: 500;
}

.confidence-label {
  color: #07450C;
  font-size: 0.9rem;
  font-weight: 500;
}

.confidence-bar {
  width: 100px;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
  margin: 0 0.5rem;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.confidence-value {
  color: #07450C;
  font-size: 0.9rem;
  font-weight: bold;
  min-width: 40px;
}

.explore-btn {
  background: #07450C;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.explore-btn:hover {
  background: #0a5a0f;
}

/* Responsive Design */
@media (max-width: 768px) {
  .smart-recommendations {
    padding: 1rem;
  }
  
  .rec-cards {
    grid-template-columns: 1fr;
  }
  
  .rec-card {
    flex-direction: column;
    text-align: center;
  }
  
  .rec-meta {
    justify-content: center;
  }
  
  .confidence-bar {
    width: 80px;
  }
}
</style> 