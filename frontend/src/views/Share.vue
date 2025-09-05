<template>
  <div class="share-page">
    <div class="share-header fancy-hero">
      <div class="hero-text">
        <h1>Share & Discover</h1>
        <p>Share your dining experiences and discover amazing restaurants from others</p>
      </div>
    </div>

    <!-- Stories Strip -->
    <div class="stories-strip">
      <div class="story-card add-story" @click="triggerFilePicker">
        <div class="story-avatar add">+</div>
        <div class="story-name">Add Story</div>
      </div>
      <div
        v-for="s in stories"
        :key="s.id"
        class="story-card"
        :title="s.name"
      >
        <div class="story-avatar">
          <img :src="s.avatar" :alt="s.name" />
        </div>
        <div class="story-name">{{ s.name }}</div>
      </div>
    </div>

    <!-- Quick Share Section -->
    <div class="share-section sticky-composer">
      <h2>Quick Share</h2>
      <div class="quick-share-form">
        <div class="share-input-group relative">
          <input 
            v-model="quickShareText" 
            type="text" 
            placeholder="What's on your mind about food today?"
            class="share-input"
            maxlength="280"
          />
          <span class="char-count">{{ quickShareText.length }}/280</span>
        </div>
        <div class="attachments-row">
          <input ref="fileInput" type="file" accept="image/*" multiple @change="onFilesSelected" class="hidden-input" />
          <div class="attachment-actions">
            <button @click="triggerFilePicker" class="action-btn pill">Add Photos</button>
            <button @click="addLocation" class="action-btn pill outline">Add Location</button>
          </div>
          <div v-if="quickSharePreviews.length" class="preview-grid">
            <div v-for="(src, i) in quickSharePreviews" :key="i" class="preview-item">
              <img :src="src" alt="preview" />
              <button class="remove-preview" @click="removePreview(i)">✖</button>
            </div>
          </div>
        </div>
        <div class="share-actions">
          <button @click="postQuickShare" class="action-btn post-btn glow" :disabled="!quickShareText.trim() && quickSharePreviews.length === 0">
            Post
          </button>
        </div>
      </div>
    </div>

    <!-- Create Lists Section -->
    <div class="share-section">
      <h2>📝 Create Lists</h2>
      <div class="create-list-form">
        <div class="list-inputs">
          <input 
            v-model="newListName" 
            type="text" 
            placeholder="List name (e.g., 'Best Pizza Places')"
            class="list-name-input"
          />
          <textarea 
            v-model="newListDescription" 
            placeholder="Describe your list..."
            class="list-description-input"
            rows="3"
          ></textarea>
          <select v-model="newListPrivacy" class="list-privacy-select">
            <option value="public">🌍 Public</option>
            <option value="friends">👥 Friends Only</option>
            <option value="private">🔒 Private</option>
          </select>
        </div>
        <button @click="createList" class="create-list-btn" :disabled="!newListName.trim()">
          Create List
        </button>
      </div>
    </div>

    <!-- Your Lists Section -->
    <div class="share-section">
      <h2>📚 Your Lists</h2>
      <div class="lists-grid">
        <div v-for="list in userLists" :key="list.id" class="list-card">
          <div class="list-header">
            <h3 class="list-title">{{ list.name }}</h3>
            <div class="list-privacy-badge" :class="list.privacy">
              {{ getPrivacyIcon(list.privacy) }} {{ list.privacy }}
            </div>
          </div>
          <p class="list-description">{{ list.description }}</p>
          <div class="list-stats">
            <span class="stat">
              <span class="stat-icon">🍽️</span>
              {{ list.restaurants.length }} places
            </span>
            <span class="stat">
              <span class="stat-icon">👁️</span>
              {{ list.views }} views
            </span>
            <span class="stat">
              <span class="stat-icon">❤️</span>
              {{ list.likes }} likes
            </span>
          </div>
          <div class="list-actions">
            <button @click="editList(list)" class="list-action-btn edit-btn">
              ✏️ Edit
            </button>
            <button @click="shareList(list)" class="list-action-btn share-btn">
              📤 Share
            </button>
            <button @click="deleteList(list.id)" class="list-action-btn delete-btn">
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Social Feed Section -->
    <div class="share-section">
      <h2>📱 Social Feed</h2>
      
      <!-- Search Bar -->
      <div class="search-section">
        <div class="search-container">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search posts, users, or restaurants..."
            class="search-input"
            @input="onSearchInput"
          />
          <button @click="performSearch" class="search-btn">🔍</button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results" :class="{ active: searchResults.length > 0 }">
          <h4>Search Results ({{ searchResults.length }})</h4>
          <div class="search-results-list">
            <div v-for="result in searchResults" :key="result.id" class="search-result-item">
              <div class="result-avatar">
                <img :src="result.userAvatar || result.avatar" :alt="result.userName || result.name" />
              </div>
              <div class="result-content">
                <h5 class="result-title">{{ result.userName || result.name }}</h5>
                <p class="result-text">{{ result.text || result.description || 'User' }}</p>
                <span class="result-type">{{ getResultType(result) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="searchQuery && !searchResults.length" class="empty-results">No results found</div>
      </div>
      
      <div class="feed-filters">
        <button 
          v-for="filter in feedFilters" 
          :key="filter.id"
          @click="setFeedFilter(filter.id)"
          :class="['filter-btn', { active: currentFeedFilter === filter.id }]"
        >
          {{ filter.icon }} {{ filter.name }}
        </button>
      </div>
      
      <div class="social-feed">
        <div v-for="post in filteredFeed" :key="post.id" class="feed-post">
          <div class="post-header">
            <div class="post-user">
              <img :src="post.userAvatar" :alt="post.userName" class="user-avatar" />
              <div class="user-info">
                <h4 class="user-name">{{ post.userName }}</h4>
                <span class="post-time">{{ post.timeAgo }}</span>
              </div>
            </div>
            <div class="post-actions">
              <button @click="followUser(post.userId)" class="follow-btn" v-if="!post.isFollowing">Follow</button>
              <button @click="unfollowUser(post.userId)" class="following-btn" v-else>Following</button>
            </div>
          </div>
          
          <div class="post-content">
            <p class="post-text" v-if="!isEditing(post.id)">{{ post.text }}</p>
            <div v-else class="edit-post">
              <textarea v-model="editBuffer" rows="3" />
              <div class="edit-actions">
                <button @click="saveEdit(post.id)" class="edit-save">Save</button>
                <button @click="cancelEdit()" class="edit-cancel">Cancel</button>
              </div>
            </div>
            
            <div v-if="post.imageUrls && post.imageUrls.length" class="post-images">
              <img v-for="(img, idx) in post.imageUrls" :key="idx" :src="img" class="post-image" @error="onImageError(post, idx)" />
            </div>

            <div v-if="post.restaurant" class="post-restaurant">
              <img :src="post.restaurant.image" :alt="post.restaurant.name" class="restaurant-image" />
              <div class="restaurant-info">
                <h5 class="restaurant-name">{{ post.restaurant.name }}</h5>
                <div class="restaurant-rating">
                  <span class="stars">
                    <span v-for="i in 5" :key="i" class="star">{{ i <= post.restaurant.rating ? '★' : '☆' }}</span>
                  </span>
                  <span class="rating-text">{{ post.restaurant.rating }}/5</span>
                </div>
                <p class="restaurant-cuisine">{{ post.restaurant.cuisine }}</p>
                <div class="restaurant-actions">
                  <select v-model="selectedListId">
                    <option disabled value="">Add to list…</option>
                    <option v-for="l in userLists" :key="l.id" :value="l.id">{{ l.name }}</option>
                  </select>
                  <button @click="addRestaurantToList(post.restaurant.name)" :disabled="!selectedListId">Add</button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="post-actions-bar">
            <button @click="likePost(post.id)" class="action-btn" :class="{ liked: post.isLiked }">
              <span class="action-icon">{{ post.isLiked ? '❤️' : '🤍' }}</span>
              {{ post.likes }}
            </button>
            <button @click="toggleComments(post.id)" class="action-btn">
              <span class="action-icon">💬</span>
              {{ post.comments?.length || 0 }}
            </button>
            <button @click="sharePostNative(post.id)" class="action-btn">
              <span class="action-icon">🔗</span>
              Share
            </button>
            <button @click="toggleBookmark(post.id)" class="action-btn" :class="{ bookmarked: post.isBookmarked }">
              <span class="action-icon">{{ post.isBookmarked ? '🔖' : '🏷️' }}</span>
              {{ post.isBookmarked ? 'Saved' : 'Save' }}
            </button>
            <template v-if="post.userId === 0">
              <button @click="startEdit(post)" class="action-btn">
                <span class="action-icon">✏️</span>
                Edit
              </button>
              <button @click="deletePost(post.id)" class="action-btn delete">
                <span class="action-icon">🗑️</span>
                Delete
              </button>
            </template>
          </div>

          <!-- Comments Drawer -->
          <div v-if="isCommentsOpen(post.id)" class="comments-drawer">
            <div class="comments-list" v-if="post.comments && post.comments.length">
              <div v-for="c in post.comments" :key="c.id" class="comment-item">
                <span class="comment-user">{{ c.userName }}</span>
                <span class="comment-text">{{ c.text }}</span>
                <span class="comment-time">{{ c.timeAgo }}</span>
              </div>
            </div>
            <div v-else class="no-comments">No comments yet. Be the first!</div>
            <div class="add-comment">
              <input v-model="newCommentText" type="text" placeholder="Add a comment..." />
              <button @click="addComment(post.id)" :disabled="!newCommentText.trim()">Post</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Trending Now Section -->
    <div class="share-section">
      <h2>🔥 Trending Now</h2>
      <div class="trending-grid">
        <div v-for="trend in trendingTopics" :key="trend.id" class="trending-card">
          <div class="trend-icon">{{ trend.icon }}</div>
          <div class="trend-content">
            <h4 class="trend-title">{{ trend.title }}</h4>
            <p class="trend-description">{{ trend.description }}</p>
            <div class="trend-stats">
              <span class="trend-stat">{{ trend.posts }} posts</span>
              <span class="trend-stat">{{ trend.engagement }} engagement</span>
            </div>
          </div>
          <button @click="joinTrend(trend.id)" class="join-trend-btn" :class="{ joined: trend.isJoined }">
            {{ trend.isJoined ? 'Joined' : 'Join' }}
          </button>
        </div>
      </div>
    </div>

    <!-- User Recommendations Section -->
    <div class="share-section">
      <h2>👥 People You Might Like</h2>
      <div class="user-recommendations">
        <div v-for="user in userRecommendations" :key="user.id" class="user-recommendation-card">
          <div class="user-avatar">
            <img :src="user.avatar" :alt="user.name" />
          </div>
          <div class="user-info">
            <h4 class="user-name">{{ user.name }}</h4>
            <div class="user-stats">
              <span class="stat">{{ user.posts }} posts</span>
              <span class="stat">{{ user.followers }} followers</span>
            </div>
          </div>
          <button @click="followUser(user.id)" class="follow-recommendation-btn">
            Follow
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="showMessage" class="message-overlay" @click="hideMessage">
      <div class="message-content" :class="messageType">
        <span class="message-icon">{{ messageIcon }}</span>
        <p class="message-text">{{ messageText }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import socialService from '@/services/socialService.js'

export default {
  name: 'ShareView',
  data() {
    return {
      quickShareText: '',
      quickSharePreviews: [],
      quickShareFiles: [],
      newListName: '',
      newListDescription: '',
      newListPrivacy: 'public',
      currentFeedFilter: 'all',
      showMessage: false,
      messageText: '',
      messageType: 'success',
      messageIcon: '✅',
      
      // Get data from social service
      userLists: [],
      socialFeed: [],
      trendingTopics: [],
      userRecommendations: [], // Added for user recommendations
      
      stories: [
        { id: 1, name: 'Alex', avatar: 'https://i.pravatar.cc/100?img=12' },
        { id: 2, name: 'Maya', avatar: 'https://i.pravatar.cc/100?img=32' },
        { id: 3, name: 'Jordan', avatar: 'https://i.pravatar.cc/100?img=5' },
        { id: 4, name: 'Sam', avatar: 'https://i.pravatar.cc/100?img=21' },
        { id: 5, name: 'Taylor', avatar: 'https://i.pravatar.cc/100?img=17' }
      ],

      feedFilters: [
        { id: 'all', name: 'All Posts', icon: '📱' },
        { id: 'following', name: 'Following', icon: '👥' },
        { id: 'trending', name: 'Trending', icon: '🔥' },
        { id: 'reviews', name: 'Reviews', icon: '⭐' },
        { id: 'recent', name: 'Most Recent', icon: '🕒' }
      ],
      searchQuery: '',
      searchResults: [],
      searchTimer: null,
      openCommentsId: null,
      newCommentText: '',
      editBuffer: '', // New for editing
      isEditingPostId: null, // New for editing
      selectedListId: '', // New for adding restaurant to list
    }
  },
  computed: {
    filteredFeed() {
      return socialService.getPosts(this.currentFeedFilter)
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    loadData() {
      this.userLists = socialService.lists
      this.socialFeed = socialService.posts
      this.trendingTopics = socialService.trends
      this.userRecommendations = socialService.getUserRecommendations()
    },
    
    // Quick Share Methods
    triggerFilePicker() {
      this.$refs.fileInput.click()
    },
    onFilesSelected(e) {
      const files = Array.from(e.target.files || [])
      files.forEach(file => {
        const objectUrl = URL.createObjectURL(file)
        this.quickSharePreviews.push(objectUrl)
      })
      this.quickShareFiles.push(...files)
      e.target.value = ''
    },
    removePreview(index) {
      const url = this.quickSharePreviews[index]
      if (url && url.startsWith('blob:')) {
        try { URL.revokeObjectURL(url) } catch (_) {}
      }
      this.quickSharePreviews.splice(index, 1)
      this.quickShareFiles.splice(index, 1)
    },
    
    addPhoto() {
      this.triggerFilePicker()
    },
    
    addLocation() {
      this.showMessage = true
      this.messageText = 'Location picker feature coming soon!'
      this.messageType = 'info'
      this.messageIcon = '📍'
    },
    
    async postQuickShare() {
      if (!this.quickShareText.trim() && this.quickSharePreviews.length === 0) return
      // If files are present, convert to data URLs for persistence
      let imageUrls = []
      if (this.quickShareFiles.length) {
        const readers = this.quickShareFiles.map(file => new Promise(resolve => {
          const fr = new FileReader()
          fr.onload = e => resolve(e.target.result)
          fr.readAsDataURL(file)
        }))
        imageUrls = await Promise.all(readers)
      } else {
        // If no files, fall back to any URLs in previews (e.g., pasted URLs)
        imageUrls = this.quickSharePreviews.slice()
      }
      const newPost = socialService.createPost(this.quickShareText, null, imageUrls)
      this.socialFeed.unshift(newPost)
      this.quickShareText = ''
      // Revoke any blob URLs from previews to avoid leaks
      this.quickSharePreviews.forEach(url => { if (url && url.startsWith('blob:')) { try { URL.revokeObjectURL(url) } catch (_) {} } })
      this.quickSharePreviews = []
      this.quickShareFiles = []
      this.showMessage = true
      this.messageText = 'Your post has been shared!'
      this.messageType = 'success'
      this.messageIcon = '✅'
    },
    
    // List Methods
    createList() {
      if (this.newListName.trim()) {
        const newList = socialService.createList(
          this.newListName,
          this.newListDescription,
          this.newListPrivacy
        )
        
        this.userLists.unshift(newList)
        this.newListName = ''
        this.newListDescription = ''
        this.newListPrivacy = 'public'
        
        this.showMessage = true
        this.messageText = 'New list created successfully!'
        this.messageType = 'success'
        this.messageIcon = '✅'
      }
    },
    
    editList(list) {
      this.showMessage = true
      this.messageText = `Edit feature for "${list.name}" coming soon!`
      this.messageType = 'info'
      this.messageIcon = '✏️'
    },
    
    async shareList(list) {
      const url = `${window.location.origin}/share?list=${encodeURIComponent(list.id)}`
      try {
        await navigator.clipboard.writeText(url)
        this.showMessage = true
        this.messageText = 'List link copied to clipboard!'
        this.messageType = 'success'
        this.messageIcon = '📋'
      } catch (_) {
        this.showMessage = true
        this.messageText = 'Unable to copy link.'
        this.messageType = 'error'
        this.messageIcon = '⚠️'
      }
    },
    
    deleteList(listId) {
      if (confirm('Are you sure you want to delete this list?')) {
        socialService.deleteList(listId)
        this.userLists = this.userLists.filter(list => list.id !== listId)
        this.showMessage = true
        this.messageText = 'List deleted successfully!'
        this.messageType = 'success'
        this.messageIcon = '🗑️'
      }
    },
    
    // Feed Methods
    setFeedFilter(filterId) {
      this.currentFeedFilter = filterId
    },
    
    followUser(userId) {
      const updatedUser = socialService.toggleFollow(userId)
      if (updatedUser) {
        this.showMessage = true
        this.messageText = 'You are now following this user!'
        this.messageType = 'success'
        this.messageIcon = '👥'
        this.loadData() // Refresh data
      }
    },
    
    unfollowUser(userId) {
      const updatedUser = socialService.toggleFollow(userId)
      if (updatedUser) {
        this.showMessage = true
        this.messageText = 'You have unfollowed this user.'
        this.messageType = 'info'
        this.messageIcon = '👋'
        this.loadData() // Refresh data
      }
    },
    
    likePost(postId) {
      const updatedPost = socialService.toggleLike(postId)
      if (updatedPost) {
        this.loadData() // Refresh data
      }
    },
    
    // Comments
    toggleComments(postId) {
      this.openCommentsId = this.openCommentsId === postId ? null : postId
      this.newCommentText = ''
    },
    isCommentsOpen(postId) {
      return this.openCommentsId === postId
    },
    addComment(postId) {
      if (!this.newCommentText.trim()) return
      socialService.addComment(postId, 'You', this.newCommentText.trim())
      this.newCommentText = ''
      this.loadData()
    },

    // Share post
    async sharePost(postId) {
      const url = `${window.location.origin}/share?post=${encodeURIComponent(postId)}`
      try {
        await navigator.clipboard.writeText(url)
        this.showMessage = true
        this.messageText = 'Post link copied to clipboard!'
        this.messageType = 'success'
        this.messageIcon = '📋'
      } catch (_) {
        this.showMessage = true
        this.messageText = 'Unable to copy link.'
        this.messageType = 'error'
        this.messageIcon = '⚠️'
      }
    },

    // Native Share
    async sharePostNative(postId) {
      const post = this.socialFeed.find(p => p.id === postId);
      if (!post) return;

      const text = post.text;
      const url = `${window.location.origin}/share?post=${encodeURIComponent(postId)}`;
      const title = post.userName;
      const image = post.imageUrls && post.imageUrls.length > 0 ? post.imageUrls[0] : null;

      try {
        await navigator.share({
          title: title,
          text: text,
          url: url,
          ...(image ? { image: image } : {})
        });
        this.showMessage = true;
        this.messageText = 'Post shared successfully!';
        this.messageType = 'success';
        this.messageIcon = '🔗';
      } catch (error) {
        this.showMessage = true;
        this.messageText = 'Unable to share post.';
        this.messageType = 'error';
        this.messageIcon = '⚠️';
        console.error('Error sharing post:', error);
      }
    },

    // Bookmark
    toggleBookmark(postId) {
      const updatedPost = socialService.toggleBookmark(postId);
      if (updatedPost) {
        this.loadData(); // Refresh data
        this.showMessage = true;
        this.messageText = updatedPost.isBookmarked ? 'Post saved!' : 'Post removed from saved.';
        this.messageType = updatedPost.isBookmarked ? 'success' : 'info';
        this.messageIcon = updatedPost.isBookmarked ? '🔖' : '🏷️';
      }
    },

    // Edit/Delete
    startEdit(post) {
      this.isEditingPostId = post.id;
      this.editBuffer = post.text;
    },
    cancelEdit() {
      this.isEditingPostId = null;
      this.editBuffer = '';
    },
    async saveEdit(postId) {
      if (!this.editBuffer.trim()) {
        this.showMessage = true;
        this.messageText = 'Post text cannot be empty.';
        this.messageType = 'error';
        this.messageIcon = '⚠️';
        return;
      }
      const updatedPost = socialService.updatePost(postId, this.editBuffer);
      if (updatedPost) {
        this.isEditingPostId = null;
        this.editBuffer = '';
        this.loadData(); // Refresh data
        this.showMessage = true;
        this.messageText = 'Post updated successfully!';
        this.messageType = 'success';
        this.messageIcon = '✅';
      }
    },
    deletePost(postId) {
      if (confirm('Are you sure you want to delete this post?')) {
        socialService.deletePost(postId);
        this.socialFeed = this.socialFeed.filter(post => post.id !== postId);
        this.showMessage = true;
        this.messageText = 'Post deleted successfully!';
        this.messageType = 'success';
        this.messageIcon = '🗑️';
      }
    },

    // Add Restaurant to List
    addRestaurantToList(restaurantName) {
      if (!this.selectedListId) {
        this.showMessage = true;
        this.messageText = 'Please select a list to add this restaurant to.';
        this.messageType = 'error';
        this.messageIcon = '⚠️';
        return;
      }
      const list = this.userLists.find(l => l.id === this.selectedListId);
      if (list) {
        socialService.addRestaurantToList(this.selectedListId, restaurantName);
        this.showMessage = true;
        this.messageText = `${restaurantName} added to ${list.name}!`;
        this.messageType = 'success';
        this.messageIcon = '🍽️';
      } else {
        this.showMessage = true;
        this.messageText = 'List not found.';
        this.messageType = 'error';
        this.messageIcon = '⚠️';
      }
      this.selectedListId = ''; // Clear selected list
    },

    onImageError(post, idx) {
      // Replace broken image with a small placeholder
      if (post && post.imageUrls && post.imageUrls[idx]) {
        post.imageUrls.splice(idx, 1, 'https://via.placeholder.com/300x200/cccccc/000000?text=Image+unavailable')
      }
    },
    
    // Trending Methods
    joinTrend(trendId) {
      const updatedTrend = socialService.toggleTrend(trendId)
      if (updatedTrend) {
        this.showMessage = true
        this.messageText = updatedTrend.isJoined ? 'You have joined this trending topic!' : 'You have left this trending topic.'
        this.messageType = 'success'
        this.messageIcon = updatedTrend.isJoined ? '🔥' : '👋'
        this.loadData() // Refresh data
      }
    },
    
    // Search
    onSearchInput() {
      if (this.searchTimer) clearTimeout(this.searchTimer)
      this.searchTimer = setTimeout(() => {
        this.performSearch()
      }, 300)
    },
    performSearch() {
      if (this.searchQuery.trim()) {
        this.searchResults = socialService.search(this.searchQuery)
      } else {
        this.searchResults = []
      }
    },

    // Utility Methods
    getPrivacyIcon(privacy) {
      const icons = { public: '🌍', friends: '👥', private: '🔒' }
      return icons[privacy] || '🌍'
    },
    hideMessage() {
      this.showMessage = false
    },
    isEditing(postId) {
      return this.isEditingPostId === postId;
    }
  }
}
</script>

<style scoped>
.share-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Hero */
.fancy-hero {
  background: linear-gradient(135deg, rgba(7,69,12,0.12), rgba(7,69,12,0.04));
  border: 1px solid rgba(7,69,12,0.12);
  border-radius: 16px;
  padding: 1.5rem 2rem;
}
.hero-text h1 { font-size: 2.4rem; margin: 0 0 0.5rem 0; }
.hero-text p { margin: 0; opacity: 0.85; }

/* Stories */
.stories-strip { display: flex; gap: 0.8rem; overflow-x: auto; padding: 0.75rem 0.25rem 1rem; }
.story-card { flex: 0 0 auto; width: 76px; text-align: center; cursor: pointer; }
.story-avatar { width: 64px; height: 64px; border-radius: 50%; overflow: hidden; border: 3px solid #07450C22; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin: 0 auto 0.4rem; display: grid; place-items: center; background: #fff; }
.story-avatar img { width: 100%; height: 100%; object-fit: cover; }
.story-avatar.add { background: #07450C; color: #fff; font-weight: 800; font-size: 1.4rem; }
.story-name { font-size: 0.75rem; color: #35543a; font-weight: 700; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }
.add-story { opacity: 0.95; }

/* Sticky composer */
sticky-composer { position: sticky; top: 0; z-index: 5; }

.share-header {
  text-align: center;
  margin-bottom: 3rem;
}

.share-header h1 {
  color: #07450C;
  margin: 0 0 1rem 0;
  font-size: 2.5rem;
  font-weight: bold;
}

.share-header p {
  color: #07450C;
  margin: 0;
  opacity: 0.8;
  font-size: 1.1rem;
}

.share-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(7, 69, 12, 0.1);
  margin-bottom: 2rem;
}

.share-section h2 {
  color: #07450C;
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quick-share-form, .create-list-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.share-input-group, .list-inputs {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.share-input, .list-name-input, .list-description-input {
  padding: 0.75rem;
  border: 2px solid rgba(7, 69, 12, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  color: #07450C;
  background: white;
  transition: border-color 0.2s ease;
  flex: 1;
}

.share-input:focus, .list-name-input:focus, .list-description-input:focus {
  outline: none;
  border-color: #07450C;
}

.share-input {
  min-height: 50px;
  padding-right: 40px; /* Space for char count */
}

.char-count {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: #07450C;
  opacity: 0.7;
}

.share-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.action-btn.photo-btn {
  background: rgba(0, 0, 0, 0.05);
  color: #07450C;
}

.action-btn.photo-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.action-btn.location-btn {
  background: rgba(0, 0, 0, 0.05);
  color: #07450C;
}

.action-btn.location-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.action-btn.post-btn {
  background: #07450C;
  color: white;
}

.action-btn.post-btn:hover:not(:disabled) {
  background: #0a5a0f;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.create-list-btn {
  background: #07450C;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 1rem;
  align-self: flex-start;
}

.create-list-btn:hover:not(:disabled) {
  background: #0a5a0f;
}

.create-list-btn:disabled {
  background: #07450C;
  opacity: 0.6;
  cursor: not-allowed;
}

.list-inputs {
  margin-bottom: 1rem;
}

.list-name-input {
  min-height: 40px;
}

.list-description-input {
  min-height: 80px;
  resize: vertical;
}

.list-privacy-select {
  padding: 0.75rem;
  border: 2px solid rgba(7, 69, 12, 0.2);
  border-radius: 8px;
  font-size: 1rem;
  color: #07450C;
  background: white;
  transition: border-color 0.2s ease;
  min-height: 40px;
}

.list-privacy-select:focus {
  outline: none;
  border-color: #07450C;
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
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.list-title {
  color: #07450C;
  margin: 0;
  font-size: 1.2rem;
  font-weight: bold;
}

.list-privacy-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  text-transform: capitalize;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.list-privacy-badge.public {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
}

.list-privacy-badge.friends {
  background: rgba(255, 193, 7, 0.1);
  color: #856404;
}

.list-privacy-badge.private {
  background: rgba(108, 117, 125, 0.1);
  color: #6c757d;
}

.list-description {
  color: #07450C;
  margin: 0 0 1rem 0;
  opacity: 0.8;
  line-height: 1.5;
  flex-grow: 1;
}

.list-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #07450C;
  font-size: 0.9rem;
  opacity: 0.7;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-icon {
  font-size: 1rem;
}

.list-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.list-action-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.list-action-btn.edit-btn {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
}

.list-action-btn.edit-btn:hover {
  background: rgba(7, 69, 12, 0.2);
}

.list-action-btn.share-btn {
  background: rgba(0, 123, 255, 0.1);
  color: #007bff;
}

.list-action-btn.share-btn:hover {
  background: rgba(0, 123, 255, 0.2);
}

.list-action-btn.delete-btn {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.list-action-btn.delete-btn:hover {
  background: rgba(220, 53, 69, 0.2);
}

.feed-filters {
  display: flex;
  gap: 1rem;
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  gap: 1.5rem;
}

.feed-post {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(7, 69, 12, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.post-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  color: #07450C;
  margin: 0;
  font-size: 1rem;
  font-weight: bold;
}

.post-time {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

.post-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.follow-btn, .following-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #07450C;
  background: white;
  color: #07450C;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.follow-btn:hover {
  background: #07450C;
  color: white;
}

.following-btn {
  background: #07450C;
  color: white;
}

.following-btn:hover {
  background: #0a5a0f;
}

.post-content {
  margin-bottom: 1rem;
  flex-grow: 1;
}

.post-text {
  color: #07450C;
  margin: 0 0 1rem 0;
  line-height: 1.5;
  word-break: break-word;
}

.post-restaurant {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: rgba(7, 69, 12, 0.05);
  border-radius: 6px;
}

.restaurant-image {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.restaurant-info {
  display: flex;
  flex-direction: column;
}

.restaurant-name {
  color: #07450C;
  font-weight: bold;
  font-size: 1rem;
}

.restaurant-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #07450C;
  font-size: 0.9rem;
  margin-top: 0.25rem;
}

.stars {
  display: flex;
  gap: 0.25rem;
}

.star {
  font-size: 1.2rem;
  color: #FFD700; /* Gold stars */
}

.rating-text {
  color: #07450C;
  font-weight: bold;
}

.restaurant-cuisine {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
  margin-top: 0.25rem;
}

.restaurant-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.restaurant-actions select {
  padding: 0.5rem;
  border: 2px solid rgba(7, 69, 12, 0.2);
  border-radius: 8px;
  font-size: 0.9rem;
  color: #07450C;
  background: white;
  min-width: 150px;
}

.restaurant-actions select:focus {
  outline: none;
  border-color: #07450C;
}

.restaurant-actions button {
  padding: 0.5rem 1rem;
  border: 2px solid #07450C;
  background: white;
  color: #07450C;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.restaurant-actions button:hover {
  background: #07450C;
  color: white;
}

.post-actions-bar {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.post-actions-bar .action-btn {
  background: rgba(7, 69, 12, 0.1);
  color: #07450C;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.post-actions-bar .action-btn:hover {
  background: rgba(7, 69, 12, 0.2);
}

.post-actions-bar .action-btn.liked {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

.trending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.trending-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  border: 1px solid rgba(7, 69, 12, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.trend-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.trend-content {
  text-align: center;
}

.trend-title {
  color: #07450C;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: bold;
}

.trend-description {
  color: #07450C;
  margin: 0 0 1rem 0;
  line-height: 1.5;
  opacity: 0.8;
}

.trend-stats {
  display: flex;
  gap: 1rem;
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

.trend-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.join-trend-btn {
  padding: 0.5rem 1rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: 500;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.join-trend-btn:hover {
  background: #0a5a0f;
}

.join-trend-btn.joined {
  background: #28a745; /* Green for joined */
  color: white;
}

.join-trend-btn.joined:hover {
  background: #218838;
}

/* User Recommendations Section */
.user-recommendations {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.user-recommendation-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(7, 69, 12, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(7, 69, 12, 0.1);
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  flex: 1;
}

.user-name {
  color: #07450C;
  font-weight: bold;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.user-stats {
  display: flex;
  gap: 0.75rem;
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.stat-icon {
  font-size: 0.8rem;
}

.follow-recommendation-btn {
  padding: 0.5rem 1rem;
  background: #07450C;
  color: white;
  border: none;
  border-radius: 20px;
  font-weight: 500;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.follow-recommendation-btn:hover {
  background: #0a5a0f;
}

/* Success/Error Messages */
.message-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.message-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 1rem;
  max-width: 400px;
  width: 90%;
}

.message-content.success {
  border-left: 5px solid #28a745;
}

.message-content.info {
  border-left: 5px solid #17a2b8;
}

.message-content.error {
  border-left: 5px solid #dc3545;
}

.message-icon {
  font-size: 2.5rem;
}

.message-text {
  color: #07450C;
  font-size: 1.1rem;
  font-weight: 500;
}

/* Search Section Styles */
.search-section {
  margin-bottom: 1.5rem;
  position: relative;
}

.search-container {
  display: flex;
  align-items: center;
  background: #f0f0f0;
  border-radius: 25px;
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  max-width: 600px;
  margin: 0 auto 1rem auto;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  background: transparent;
  font-size: 1rem;
  color: #07450C;
  outline: none;
}

.search-btn {
  background: #07450C;
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 25px;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.search-btn:hover {
  background: #0a5a0f;
}

.search-results {
  position: absolute;
  top: 100%; /* Below the search bar */
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
  display: none; /* Hidden by default */
}

.search-results.active {
  display: block;
}

.search-results h4 {
  padding: 0.75rem 1rem;
  margin: 0;
  border-bottom: 1px solid #eee;
  color: #07450C;
  font-size: 1rem;
  font-weight: bold;
}

.search-results-list {
  padding: 0.5rem 0;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.search-result-item:hover {
  background-color: #f5f5f5;
}

.result-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 1rem;
}

.result-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-content {
  flex: 1;
}

.result-title {
  color: #07450C;
  font-size: 1rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.result-text {
  color: #07450C;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 0.25rem;
}

.result-type {
  color: #07450C;
  font-size: 0.8rem;
  opacity: 0.7;
}

/* Additional styles for new features */
.hidden-input { display: none; }
.attachments-row { display: flex; flex-direction: column; gap: 0.75rem; }
.attachment-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.preview-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 0.5rem; }
.preview-item { position: relative; }
.preview-item img { width: 100%; height: 100px; object-fit: cover; border-radius: 8px; background: #f0f0f0; }
.remove-preview { position: absolute; top: 6px; right: 6px; background: rgba(0,0,0,0.6); color: #fff; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; }

.post-images { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.5rem; margin-top: 0.5rem; }
.post-image { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; background: #f0f0f0; }

.comments-drawer { background: rgba(7,69,12,0.05); border: 1px solid rgba(7,69,12,0.1); border-radius: 8px; padding: 0.75rem; margin-top: 0.75rem; }
.comments-list { display: grid; gap: 0.5rem; margin-bottom: 0.5rem; }
.comment-item { display: flex; gap: 0.5rem; align-items: baseline; color: #07450C; }
.comment-user { font-weight: 700; }
.comment-text { opacity: 0.9; }
.comment-time { margin-left: auto; opacity: 0.6; font-size: 0.85rem; }
.add-comment { display: flex; gap: 0.5rem; }
.add-comment input { flex: 1; padding: 0.5rem 0.75rem; border: 2px solid rgba(7,69,12,0.2); border-radius: 8px; color: #07450C; }
.add-comment button { padding: 0.5rem 0.75rem; background: #07450C; color: #fff; border: none; border-radius: 8px; cursor: pointer; }

.empty-results { margin-top: 0.5rem; color: #07450C; opacity: 0.7; font-style: italic; }

/* Responsive Design */
@media (max-width: 768px) {
  .share-page {
    padding: 1rem;
  }
  
  .share-header {
    margin-bottom: 2rem;
  }
  
  .share-header h1 {
    font-size: 2rem;
  }
  
  .share-header p {
    font-size: 1rem;
  }
  
  .share-section {
    padding: 1.5rem;
  }
  
  .share-input-group, .list-inputs {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .share-input, .list-name-input, .list-description-input, .list-privacy-select {
    width: 100%;
  }

  .share-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .action-btn {
    width: 100%;
  }

  .create-list-btn {
    align-self: stretch;
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
  
  .follow-btn, .following-btn {
    align-self: flex-end;
  }
  
  .post-actions-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .search-container {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .search-input {
    padding: 0.75rem 1rem;
  }

  .search-btn {
    padding: 0.75rem 1rem;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .share-header {
    margin-bottom: 1.5rem;
  }
  
  .share-header h1 {
    font-size: 1.8rem;
  }
  
  .share-header p {
    font-size: 0.9rem;
  }
  
  .share-section {
    padding: 1rem;
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