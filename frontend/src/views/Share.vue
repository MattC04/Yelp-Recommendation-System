<template>
  <div class="share-container">
    <div class="share-header">
      <h1 class="share-title">Share & Discover</h1>
      <p class="share-subtitle">Share your favorite restaurants and discover new ones from friends</p>
    </div>

    <div class="share-content">
      <!-- Quick Share Section -->
      <div class="share-section">
        <h2 class="section-title">🚀 Quick Share</h2>
        <div class="quick-share-form">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Restaurant Name</label>
              <input v-model="quickShare.restaurantName" type="text" class="form-input" placeholder="Enter restaurant name">
            </div>
            <div class="form-group">
              <label class="form-label">Location</label>
              <input v-model="quickShare.location" type="text" class="form-input" placeholder="City, State">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Why You Love It</label>
            <textarea v-model="quickShare.reason" class="form-textarea" placeholder="Tell us why you love this restaurant..."></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Rating</label>
              <div class="rating-input">
                <span 
                  v-for="i in 5" 
                  :key="i" 
                  :class="['star-input', { active: i <= quickShare.rating }]"
                  @click="quickShare.rating = i"
                >
                  {{ i <= quickShare.rating ? '★' : '☆' }}
                </span>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Tags</label>
              <input v-model="quickShare.tags" type="text" class="form-input" placeholder="e.g., romantic, budget-friendly, outdoor">
            </div>
          </div>
          <button @click="submitQuickShare" class="share-btn">Share Restaurant</button>
        </div>
      </div>

      <!-- Create Lists Section -->
      <div class="share-section">
        <h2 class="section-title">📋 Create Lists</h2>
        <div class="list-creation">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">List Name</label>
              <input v-model="newList.name" type="text" class="form-input" placeholder="e.g., Date Night Spots">
            </div>
            <div class="form-group">
              <label class="form-label">Description</label>
              <input v-model="newList.description" type="text" class="form-input" placeholder="Brief description of your list">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Privacy</label>
            <div class="privacy-options">
              <label class="radio-option">
                <input type="radio" v-model="newList.privacy" value="public" class="radio-input">
                <span class="radio-text">Public - Anyone can see</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="newList.privacy" value="friends" class="radio-input">
                <span class="radio-text">Friends Only</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="newList.privacy" value="private" class="radio-input">
                <span class="radio-text">Private - Just you</span>
              </label>
            </div>
          </div>
          <button @click="createList" class="create-btn">Create List</button>
        </div>
      </div>

      <!-- Your Lists Section -->
      <div class="share-section">
        <h2 class="section-title">📚 Your Lists</h2>
        <div class="lists-grid">
          <div v-for="list in userLists" :key="list.id" class="list-card">
            <div class="list-header">
              <h3 class="list-name">{{ list.name }}</h3>
              <div class="list-privacy">
                <span :class="['privacy-badge', list.privacy]">{{ list.privacy }}</span>
              </div>
            </div>
            <p class="list-description">{{ list.description }}</p>
            <div class="list-stats">
              <span class="stat">{{ list.restaurantCount }} restaurants</span>
              <span class="stat">{{ list.followers }} followers</span>
            </div>
            <div class="list-actions">
              <button @click="editList(list.id)" class="action-btn edit">Edit</button>
              <button @click="shareList(list.id)" class="action-btn share">Share</button>
              <button @click="deleteList(list.id)" class="action-btn delete">Delete</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Social Feed Section -->
      <div class="share-section">
        <h2 class="section-title">👥 Social Feed</h2>
        <div class="feed-filters">
          <button 
            v-for="filter in feedFilters" 
            :key="filter.id"
            :class="['filter-btn', { active: activeFilter === filter.id }]"
            @click="activeFilter = filter.id"
          >
            {{ filter.name }}
          </button>
        </div>
        <div class="social-feed">
          <div v-for="post in filteredFeed" :key="post.id" class="feed-post">
            <div class="post-header">
              <div class="post-user">
                <span class="user-avatar">{{ post.userAvatar }}</span>
                <div class="user-info">
                  <span class="user-name">{{ post.userName }}</span>
                  <span class="post-time">{{ post.time }}</span>
                </div>
              </div>
              <button @click="followUser(post.userId)" class="follow-btn">
                {{ post.isFollowing ? 'Following' : 'Follow' }}
              </button>
            </div>
            <div class="post-content">
              <h4 class="post-title">{{ post.title }}</h4>
              <p class="post-text">{{ post.text }}</p>
              <div class="post-restaurant">
                <span class="restaurant-emoji">🍽️</span>
                <span class="restaurant-name">{{ post.restaurantName }}</span>
                <span class="restaurant-rating">⭐ {{ post.rating }}/5</span>
              </div>
            </div>
            <div class="post-actions">
              <button @click="likePost(post.id)" :class="['action-btn', { liked: post.isLiked }]">
                {{ post.isLiked ? '❤️' : '🤍' }} {{ post.likes }}
              </button>
              <button @click="commentPost(post.id)" class="action-btn">
                💬 {{ post.comments }}
              </button>
              <button @click="sharePost(post.id)" class="action-btn">
                📤 Share
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Trending Section -->
      <div class="share-section">
        <h2 class="section-title">🔥 Trending Now</h2>
        <div class="trending-grid">
          <div v-for="trend in trendingTopics" :key="trend.id" class="trending-card">
            <div class="trending-icon">{{ trend.icon }}</div>
            <div class="trending-content">
              <h3 class="trending-title">{{ trend.title }}</h3>
              <p class="trending-description">{{ trend.description }}</p>
              <div class="trending-stats">
                <span class="trend-stat">{{ trend.posts }} posts</span>
                <span class="trend-stat">{{ trend.engagement }} engagement</span>
              </div>
            </div>
            <button @click="joinTrend(trend.id)" class="join-btn">Join</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShareView',
  data() {
    return {
      quickShare: {
        restaurantName: '',
        location: '',
        reason: '',
        rating: 0,
        tags: ''
      },
      newList: {
        name: '',
        description: '',
        privacy: 'public'
      },
      userLists: [
        {
          id: 1,
          name: 'Date Night Spots',
          description: 'Perfect restaurants for romantic evenings',
          privacy: 'public',
          restaurantCount: 8,
          followers: 24
        },
        {
          id: 2,
          name: 'Budget Eats',
          description: 'Delicious food that won\'t break the bank',
          privacy: 'friends',
          restaurantCount: 12,
          followers: 15
        },
        {
          id: 3,
          name: 'Hidden Gems',
          description: 'Local favorites that tourists don\'t know about',
          privacy: 'private',
          restaurantCount: 5,
          followers: 0
        }
      ],
      feedFilters: [
        { id: 'all', name: 'All Posts' },
        { id: 'friends', name: 'Friends Only' },
        { id: 'following', name: 'Following' },
        { id: 'trending', name: 'Trending' }
      ],
      activeFilter: 'all',
      socialFeed: [
        {
          id: 1,
          userId: 1,
          userName: 'Sarah Foodie',
          userAvatar: '👩‍🍳',
          time: '2 hours ago',
          title: 'Just discovered this amazing Italian place!',
          text: 'The pasta was absolutely divine. Perfect for date night!',
          restaurantName: 'Bella Italia',
          rating: 5,
          likes: 12,
          comments: 3,
          isLiked: false,
          isFollowing: true
        },
        {
          id: 2,
          userId: 2,
          userName: 'Mike Eats',
          userAvatar: '👨‍🍳',
          time: '5 hours ago',
          title: 'Best sushi in town!',
          text: 'Fresh fish and amazing presentation. A must-visit!',
          restaurantName: 'Sakura Sushi',
          rating: 5,
          likes: 8,
          comments: 1,
          isLiked: true,
          isFollowing: false
        }
      ],
      trendingTopics: [
        {
          id: 1,
          icon: '🍕',
          title: 'Pizza Week',
          description: 'Celebrating the best pizza spots in the city',
          posts: 156,
          engagement: '2.4K'
        },
        {
          id: 2,
          icon: '🌮',
          title: 'Taco Tuesday',
          description: 'Share your favorite taco joints',
          posts: 89,
          engagement: '1.8K'
        },
        {
          id: 3,
          icon: '🍜',
          title: 'Ramen Hunt',
          description: 'Finding the perfect bowl of ramen',
          posts: 67,
          engagement: '1.2K'
        }
      ]
    }
  },
  computed: {
    filteredFeed() {
      if (this.activeFilter === 'all') {
        return this.socialFeed
      }
      // TODO: Implement proper filtering logic
      return this.socialFeed
    }
  },
  methods: {
    submitQuickShare() {
      // TODO: Implement API call to submit quick share
      console.log('Quick share:', this.quickShare)
      // Reset form
      this.quickShare = {
        restaurantName: '',
        location: '',
        reason: '',
        rating: 0,
        tags: ''
      }
      // Show success message
    },
    createList() {
      // TODO: Implement API call to create list
      console.log('Creating list:', this.newList)
      // Reset form
      this.newList = {
        name: '',
        description: '',
        privacy: 'public'
      }
      // Show success message
    },
    editList(listId) {
      // TODO: Implement edit list functionality
      console.log('Editing list:', listId)
    },
    shareList(listId) {
      // TODO: Implement share list functionality
      console.log('Sharing list:', listId)
    },
    deleteList(listId) {
      // TODO: Implement delete list functionality
      this.userLists = this.userLists.filter(list => list.id !== listId)
    },
    followUser(userId) {
      // TODO: Implement follow user functionality
      console.log('Following user:', userId)
    },
    likePost(postId) {
      const post = this.socialFeed.find(p => p.id === postId)
      if (post) {
        post.isLiked = !post.isLiked
        post.likes += post.isLiked ? 1 : -1
      }
    },
    commentPost(postId) {
      // TODO: Implement comment functionality
      console.log('Commenting on post:', postId)
    },
    sharePost(postId) {
      // TODO: Implement share post functionality
      console.log('Sharing post:', postId)
    },
    joinTrend(trendId) {
      // TODO: Implement join trend functionality
      console.log('Joining trend:', trendId)
    }
  }
}
</script>

<style scoped>
.share-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.share-header {
  text-align: center;
  margin-bottom: 3rem;
}

.share-title {
  color: #07450C;
  margin: 0 0 1rem 0;
  font-size: 2.5rem;
  font-weight: bold;
}

.share-subtitle {
  color: #07450C;
  margin: 0;
  opacity: 0.8;
  font-size: 1.1rem;
}

.share-content {
  display: grid;
  gap: 2rem;
}

.share-section {
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-label {
  color: #07450C;
  font-weight: bold;
  font-size: 0.9rem;
}

.form-input, .form-textarea {
  padding: 0.75rem;
  border: 2px solid rgba(7, 69, 12, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  color: #07450C;
  background: white;
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

.rating-input {
  display: flex;
  gap: 0.5rem;
}

.star-input {
  font-size: 1.5rem;
  color: #ccc;
  cursor: pointer;
  transition: color 0.2s ease;
}

.star-input:hover {
  color: #FFD700;
}

.star-input.active {
  color: #FFD700;
}

.privacy-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  color: #07450C;
}

.radio-input {
  accent-color: #07450C;
}

.share-btn, .create-btn {
  background: #07450C;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 1rem;
}

.share-btn:hover, .create-btn:hover {
  background: #0a5a0f;
}

.lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.list-card {
  padding: 1.5rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.list-name {
  color: #07450C;
  margin: 0;
  font-size: 1.2rem;
  font-weight: bold;
}

.privacy-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: capitalize;
}

.privacy-badge.public {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
}

.privacy-badge.friends {
  background: rgba(255, 193, 7, 0.1);
  color: #856404;
}

.privacy-badge.private {
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.list-description {
  color: #07450C;
  margin: 0 0 1rem 0;
  opacity: 0.8;
  line-height: 1.5;
}

.list-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat {
  color: #07450C;
  font-size: 0.9rem;
  opacity: 0.7;
}

.list-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn.edit {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
}

.action-btn.edit:hover {
  background: rgba(7, 69, 12, 0.2);
}

.action-btn.share {
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.action-btn.share:hover {
  background: rgba(0, 123, 255, 0.2);
}

.action-btn.delete {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.action-btn.delete:hover {
  background: rgba(220, 53, 69, 0.2);
}

.feed-filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 2px solid rgba(7, 69, 12, 0.2);
  background: white;
  color: #07450C;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  border-color: #07450C;
}

.filter-btn.active {
  background: #07450C;
  color: white;
  border-color: #07450C;
}

.social-feed {
  display: grid;
  gap: 1rem;
}

.feed-post {
  padding: 1.5rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.post-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  font-size: 2rem;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  color: #07450C;
  font-weight: bold;
  font-size: 1rem;
}

.post-time {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

.follow-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #07450C;
  background: white;
  color: #07450C;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.follow-btn:hover {
  background: #07450C;
  color: white;
}

.post-content {
  margin-bottom: 1rem;
}

.post-title {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.post-text {
  color: #07450C;
  margin: 0 0 1rem 0;
  line-height: 1.5;
}

.post-restaurant {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(7, 69, 12, 0.05);
  border-radius: 6px;
}

.restaurant-emoji {
  font-size: 1.2rem;
}

.restaurant-name {
  color: #07450C;
  font-weight: bold;
}

.restaurant-rating {
  color: #07450C;
  margin-left: auto;
}

.post-actions {
  display: flex;
  gap: 1rem;
}

.post-actions .action-btn {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.post-actions .action-btn:hover {
  background: rgba(7, 69, 12, 0.2);
}

.post-actions .action-btn.liked {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.trending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.trending-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: rgba(7, 69, 12, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.trending-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.trending-content {
  flex: 1;
}

.trending-title {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.trending-description {
  color: #07450C;
  margin: 0 0 1rem 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.trending-stats {
  display: flex;
  gap: 1rem;
}

.trend-stat {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

.join-btn {
  padding: 0.5rem 1rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s ease;
  flex-shrink: 0;
}

.join-btn:hover {
  background: #0a5a0f;
}

/* Responsive Design */
@media (max-width: 768px) {
  .share-container {
    padding: 1rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .lists-grid {
    grid-template-columns: 1fr;
  }
  
  .trending-grid {
    grid-template-columns: 1fr;
  }
  
  .post-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .follow-btn {
    align-self: flex-end;
  }
  
  .post-actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .share-header {
    margin-bottom: 2rem;
  }
  
  .share-title {
    font-size: 2rem;
  }
  
  .share-section {
    padding: 1.5rem;
  }
  
  .feed-filters {
    justify-content: center;
  }
  
  .trending-card {
    flex-direction: column;
    text-align: center;
  }
}
</style> 