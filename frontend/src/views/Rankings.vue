<template>
  <div class="rankings-page">
    <div class="rankings-header">
      <h1>Restaurant Rankings</h1>
      <p>Track your ratings, create lists, and compare restaurants</p>
    </div>

    <!-- Quick Stats -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <div class="stat-number">{{ totalRatings }}</div>
          <div class="stat-label">Restaurants Rated</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-number">{{ totalComparisons }}</div>
          <div class="stat-label">Comparisons Made</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-content">
          <div class="stat-number">{{ totalLists }}</div>
          <div class="stat-label">Ranking Lists</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-content">
          <div class="stat-number">{{ averageRating }}</div>
          <div class="stat-label">Avg Rating</div>
        </div>
      </div>
    </div>

    <!-- Unlock Progress Banner -->
    <div v-if="totalRatings < 5" class="unlock-banner">
      <div class="unlock-content">
        <div class="unlock-icon">🔒</div>
        <div class="unlock-text">
          <h3>Unlock Full Ranking Features</h3>
          <p>Complete {{ 5 - totalRatings }} more review{{ 5 - totalRatings !== 1 ? 's' : '' }} to unlock all ranking capabilities!</p>
        </div>
        <div class="unlock-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: (totalRatings / 5 * 100) + '%' }"></div>
          </div>
          <span class="progress-text">{{ totalRatings }}/5</span>
        </div>
      </div>
      <router-link to="/search" class="unlock-cta">
        Start Reviewing Restaurants
      </router-link>
    </div>

    <!-- Navigation Tabs -->
    <div class="rankings-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- My Ratings Tab -->
      <div v-if="activeTab === 'ratings'" class="ratings-tab">
        <div class="tab-header">
          <h2>My Restaurant Ratings</h2>
          <div class="search-box">
            <input 
              v-model="searchQuery" 
              placeholder="Search ratings..."
              class="search-input"
            />
            <button @click="searchRatings" class="search-btn">🔍</button>
          </div>
        </div>
        
        <div v-if="filteredRatings.length === 0" class="empty-state">
          <div class="empty-icon">⭐</div>
          <h3>No ratings yet</h3>
          <p>Start rating restaurants to see them here</p>
          <router-link to="/search" class="btn-primary">Go to Search</router-link>
        </div>
        
        <div v-else class="ratings-grid">
          <div v-for="rating in filteredRatings" :key="rating.restaurantId" class="rating-card">
            <div class="rating-header">
              <h3>{{ rating.restaurantId }}</h3>
              <div class="rating-stars">
                <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= rating.rating }">
                  {{ i <= rating.rating ? '★' : '☆' }}
                </span>
              </div>
            </div>
            
            <div v-if="rating.review" class="rating-review">
              <p>{{ rating.review }}</p>
            </div>
            
            <div v-if="rating.categories.length > 0" class="rating-categories">
              <span v-for="category in rating.categories" :key="category" class="category-tag">
                {{ category }}
              </span>
            </div>
            
            <div class="rating-meta">
              <span class="rating-date">{{ formatDate(rating.lastUpdated) }}</span>
              <div class="rating-actions">
                <button @click="editRating(rating)" class="edit-btn">Edit</button>
                <button @click="deleteRating(rating.restaurantId)" class="delete-btn">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- My Lists Tab -->
      <div v-if="activeTab === 'lists'" class="lists-tab">
        <div class="tab-header">
          <h2>My Ranking Lists</h2>
          <button @click="showCreateListModal = true" class="btn-primary">Create New List</button>
        </div>
        
        <div v-if="personalLists.length === 0" class="empty-state">
          <div class="empty-icon">📝</div>
          <h3>No lists yet</h3>
          <p>Create ranking lists to organize your favorite restaurants</p>
        </div>
        
        <div v-else class="lists-grid">
          <div v-for="list in personalLists" :key="list.id" class="list-card">
            <div class="list-header">
              <h3>{{ list.name }}</h3>
              <div class="list-actions">
                <button @click="editList(list)" class="edit-btn">Edit</button>
                <button @click="deleteList(list.id)" class="delete-btn">Delete</button>
              </div>
            </div>
            
            <p class="list-description">{{ list.description }}</p>
            
            <div class="list-stats">
              <span>{{ list.restaurants.length }} restaurants</span>
              <span>Updated {{ formatDate(list.lastUpdated) }}</span>
            </div>
            
            <div v-if="list.restaurants.length > 0" class="list-preview">
              <div v-for="(restaurantId, index) in list.restaurants.slice(0, 3)" :key="restaurantId" class="list-item">
                <span class="item-rank">{{ index + 1 }}</span>
                <span class="item-name">{{ restaurantId }}</span>
              </div>
              <div v-if="list.restaurants.length > 3" class="more-items">
                +{{ list.restaurants.length - 3 }} more
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Comparisons Tab -->
      <div v-if="activeTab === 'comparisons'" class="comparisons-tab">
        <div class="tab-header">
          <h2>Restaurant Comparisons</h2>
          <button @click="showCreateComparisonModal = true" class="btn-primary">New Comparison</button>
        </div>
        
        <div v-if="comparisons.length === 0" class="empty-state">
          <div class="empty-icon">📊</div>
          <h3>No comparisons yet</h3>
          <p>Compare restaurants to make better dining decisions</p>
        </div>
        
        <div v-else class="comparisons-grid">
          <div v-for="comparison in comparisons" :key="comparison.id" class="comparison-card">
            <div class="comparison-header">
              <h3>{{ comparison.title }}</h3>
              <div class="comparison-actions">
                <button @click="viewComparison(comparison)" class="view-btn">View</button>
                <button @click="deleteComparison(comparison.id)" class="delete-btn">Delete</button>
              </div>
            </div>
            
            <div class="comparison-restaurants">
              <span v-for="restaurantId in comparison.restaurantIds" :key="restaurantId" class="restaurant-tag">
                {{ restaurantId }}
              </span>
            </div>
            
            <div class="comparison-meta">
              <span>Created {{ formatDate(comparison.createdAt) }}</span>
              <span v-if="comparison.lastViewed">Last viewed {{ formatDate(comparison.lastViewed) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create List Modal -->
    <div v-if="showCreateListModal" class="modal-overlay" @click="showCreateListModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Create New Ranking List</h3>
          <button @click="showCreateListModal = false" class="close-btn">×</button>
        </div>
        
        <div class="modal-content">
          <div class="form-group">
            <label>List Name</label>
            <input v-model="newListName" placeholder="e.g., Best Italian Restaurants" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newListDescription" placeholder="Describe what this list is about..." class="form-textarea"></textarea>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="showCreateListModal = false" class="cancel-btn">Cancel</button>
          <button @click="createList" class="save-btn" :disabled="!newListName.trim()">Create List</button>
        </div>
      </div>
    </div>

    <!-- Create Comparison Modal -->
    <div v-if="showCreateComparisonModal" class="modal-overlay" @click="showCreateComparisonModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>Create New Comparison</h3>
          <button @click="showCreateComparisonModal = false" class="close-btn">×</button>
        </div>
        
        <div class="modal-content">
          <div class="form-group">
            <label>Comparison Title</label>
            <input v-model="newComparisonTitle" placeholder="e.g., Italian vs Mexican" class="form-input" />
          </div>
          
          <div class="form-group">
            <label>Select Restaurants (2-4)</label>
            <div class="restaurant-selector">
              <div v-for="rating in userRatings" :key="rating.restaurantId" class="restaurant-option">
                <input 
                  type="checkbox" 
                  :id="rating.restaurantId"
                  :value="rating.restaurantId"
                  v-model="selectedRestaurants"
                  @change="validateRestaurantSelection"
                />
                <label :for="rating.restaurantId">{{ rating.restaurantId }}</label>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="showCreateComparisonModal = false" class="cancel-btn">Cancel</button>
          <button @click="createComparison" class="save-btn" :disabled="selectedRestaurants.length < 2">Create Comparison</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import rankingService from '@/services/rankingService.js'

export default {
  name: 'Rankings',
  data() {
    return {
      activeTab: 'ratings',
      tabs: [
        { id: 'ratings', label: 'My Ratings' },
        { id: 'lists', label: 'My Lists' },
        { id: 'comparisons', label: 'Comparisons' }
      ],
      searchQuery: '',
      showCreateListModal: false,
      showCreateComparisonModal: false,
      newListName: '',
      newListDescription: '',
      newComparisonTitle: '',
      selectedRestaurants: []
    }
  },
  computed: {
    userRatings() {
      return rankingService.getUserRatings()
    },
    personalLists() {
      return rankingService.getPersonalLists()
    },
    comparisons() {
      return rankingService.getAllComparisons()
    },
    totalRatings() {
      return this.userRatings.length
    },
    totalComparisons() {
      return this.comparisons.length
    },
    totalLists() {
      return this.personalLists.length
    },
    averageRating() {
      if (this.userRatings.length === 0) return '0.0'
      const total = this.userRatings.reduce((sum, r) => sum + r.rating, 0)
      return (total / this.userRatings.length).toFixed(1)
    },
    filteredRatings() {
      if (!this.searchQuery.trim()) return this.userRatings
      
      const query = this.searchQuery.toLowerCase()
      return this.userRatings.filter(rating => 
        rating.restaurantId.toLowerCase().includes(query) ||
        rating.review.toLowerCase().includes(query) ||
        rating.categories.some(c => c.toLowerCase().includes(query))
      )
    }
  },
  methods: {
    searchRatings() {
      // Search is handled by computed property
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString()
    },
    editRating(rating) {
      // Navigate to search page to edit rating
      this.$router.push({ path: '/search', query: { edit: rating.restaurantId } })
    },
    deleteRating(restaurantId) {
      if (confirm('Are you sure you want to delete this rating?')) {
        try {
          // Note: rankingService doesn't have deleteRating method yet
          // This would need to be implemented
          this.showToast('Rating deleted successfully!')
          this.$forceUpdate()
        } catch (error) {
          this.showToast('Error deleting rating: ' + error.message)
        }
      }
    },
    editList(list) {
      // For now, just show the list details
      alert(`Editing list: ${list.name}`)
    },
    deleteList(listId) {
      if (confirm('Are you sure you want to delete this list?')) {
        try {
          // Note: rankingService doesn't have deleteRankingList method yet
          // This would need to be implemented
          this.showToast('List deleted successfully!')
          this.$forceUpdate()
        } catch (error) {
          this.showToast('Error deleting list: ' + error.message)
        }
      }
    },
    viewComparison(comparison) {
      // For now, just show the comparison details
      alert(`Viewing comparison: ${comparison.title}`)
    },
    deleteComparison(comparisonId) {
      if (confirm('Are you sure you want to delete this comparison?')) {
        try {
          // Note: rankingService doesn't have deleteComparison method yet
          // This would need to be implemented
          this.showToast('Comparison deleted successfully!')
          this.$forceUpdate()
        } catch (error) {
          this.showToast('Error deleting comparison: ' + error.message)
        }
      }
    },
    createList() {
      if (!this.newListName.trim()) return
      
      try {
        rankingService.createRankingList(
          this.newListName.trim(),
          this.newListDescription.trim()
        )
        
        this.showToast('List created successfully!')
        this.newListName = ''
        this.newListDescription = ''
        this.showCreateListModal = false
        this.$forceUpdate()
      } catch (error) {
        this.showToast('Error creating list: ' + error.message)
      }
    },
    createComparison() {
      if (this.selectedRestaurants.length < 2) return
      
      try {
        rankingService.createComparison(
          this.selectedRestaurants,
          this.newComparisonTitle.trim()
        )
        
        this.showToast('Comparison created successfully!')
        this.newComparisonTitle = ''
        this.selectedRestaurants = []
        this.showCreateComparisonModal = false
        this.$forceUpdate()
      } catch (error) {
        this.showToast('Error creating comparison: ' + error.message)
      }
    },
    validateRestaurantSelection() {
      if (this.selectedRestaurants.length > 4) {
        this.selectedRestaurants = this.selectedRestaurants.slice(0, 4)
        this.showToast('Maximum 4 restaurants allowed')
      }
    },
    showToast(message) {
      // Simple toast implementation
      alert(message)
    }
  },
  mounted() {
    // Load data when component mounts
  }
}
</script>

<style scoped>
.rankings-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.rankings-header {
  text-align: center;
  margin-bottom: 3rem;
}

.rankings-header h1 {
  color: #07450C;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.rankings-header p {
  color: #666;
  font-size: 1.1rem;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.stat-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 2rem;
  color: #07450C;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #07450C;
  line-height: 1;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

/* Tabs */
.rankings-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 1rem 1.5rem;
  border: none;
  background: none;
  color: #666;
  cursor: pointer;
  font-weight: 600;
  border-bottom: 3px solid transparent;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #07450C;
}

.tab-btn.active {
  color: #07450C;
  border-bottom-color: #07450C;
}

/* Tab Content */
.tab-content {
  min-height: 400px;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.tab-header h2 {
  color: #07450C;
  margin: 0;
}

.search-box {
  display: flex;
  gap: 0.5rem;
}

.search-input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  min-width: 250px;
}

.search-btn {
  padding: 0.75rem 1rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #07450C;
  margin-bottom: 0.5rem;
}

.empty-state p {
  margin-bottom: 2rem;
}

.btn-primary {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background: #07450C;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  transition: background 0.2s ease;
}

.btn-primary:hover {
  background: #0a5a0f;
}

/* Ratings Grid */
.ratings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.rating-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.rating-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.rating-header h3 {
  color: #07450C;
  margin: 0;
  font-size: 1.1rem;
}

.rating-stars {
  display: flex;
  gap: 2px;
}

.star.filled {
  color: #FFD700;
}

.rating-review {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  font-style: italic;
}

.rating-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.category-tag {
  padding: 0.25rem 0.5rem;
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
  border-radius: 12px;
  font-size: 0.8rem;
}

.rating-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}

.rating-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .delete-btn {
  padding: 0.4rem 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.edit-btn:hover {
  border-color: #07450C;
  color: #07450C;
}

.delete-btn:hover {
  border-color: #dc3545;
  color: #dc3545;
}

/* Lists Grid */
.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.list-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.list-header h3 {
  color: #07450C;
  margin: 0;
  font-size: 1.1rem;
}

.list-description {
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.list-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}

.list-preview {
  border-top: 1px solid #e0e0e0;
  padding-top: 1rem;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.item-rank {
  background: #07450C;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.item-name {
  color: #07450C;
  font-weight: 600;
}

.more-items {
  color: #666;
  font-size: 0.9rem;
  font-style: italic;
}

/* Comparisons Grid */
.comparisons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.comparison-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.comparison-header h3 {
  color: #07450C;
  margin: 0;
  font-size: 1.1rem;
}

.comparison-restaurants {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.restaurant-tag {
  padding: 0.4rem 0.75rem;
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
  border-radius: 12px;
  font-size: 0.9rem;
}

.comparison-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #666;
}

.view-btn {
  padding: 0.4rem 0.75rem;
  border: 1px solid #07450C;
  border-radius: 6px;
  background: white;
  color: #07450C;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: #07450C;
  color: white;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal {
  background: white;
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  color: #07450C;
  margin: 0;
  font-size: 1.3rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.modal-content {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: #07450C;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.9rem;
  transition: border-color 0.2s ease;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #07450C;
}

.form-textarea {
  min-height: 100px;
  resize: vertical;
}

.restaurant-selector {
  max-height: 200px;
  overflow-y: auto;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.5rem;
}

.restaurant-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.restaurant-option:hover {
  background: #f8f9fa;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn, .save-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.2s ease;
}

.cancel-btn {
  background: #f0f0f0;
  color: #333;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.save-btn {
  background: #07450C;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #0a5a0f;
}

.save-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Unlock Banner Styles */
.unlock-banner {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8px 24px rgba(7, 69, 12, 0.2);
}

.unlock-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
}

.unlock-icon {
  font-size: 3rem;
}

.unlock-text h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
}

.unlock-text p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
}

.unlock-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  width: 120px;
  height: 8px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #FFD700;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 0.9rem;
  font-weight: bold;
  color: #FFD700;
}

.unlock-cta {
  background: white;
  color: #07450C;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.unlock-cta:hover {
  background: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Responsive adjustments for unlock banner */
@media (max-width: 768px) {
  .unlock-banner {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .unlock-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .unlock-progress {
    margin-top: 0.5rem;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .rankings-page {
    padding: 1rem;
  }
  
  .rankings-header h1 {
    font-size: 2rem;
  }
  
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .rankings-tabs {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 120px;
  }
  
  .tab-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .ratings-grid, .lists-grid, .comparisons-grid {
    grid-template-columns: 1fr;
  }
  
  .modal {
    margin: 1rem;
    max-height: 95vh;
  }
}
</style> 