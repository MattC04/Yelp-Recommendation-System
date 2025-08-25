// Social Service for managing social features
class SocialService {
  constructor() {
    // Initialize with sample data
    this.posts = this.getInitialPosts()
    this.lists = this.getInitialLists()
    this.users = this.getInitialUsers()
    this.trends = this.getInitialTrends()
  }

  // Get initial sample posts
  getInitialPosts() {
    return [
      {
        id: 1,
        userId: 1,
        userName: 'Foodie Sarah',
        userAvatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=S',
        timeAgo: '2 hours ago',
        text: 'Just discovered the most amazing Italian restaurant! The pasta was absolutely divine. 🍝✨',
        restaurant: {
          name: 'Bella Italia',
          image: 'https://via.placeholder.com/80x60/07450C/ffffff?text=BI',
          rating: 5,
          cuisine: 'Italian'
        },
        likes: 24,
        comments: 8,
        isLiked: false,
        isFollowing: true,
        timestamp: Date.now() - (2 * 60 * 60 * 1000)
      },
      {
        id: 2,
        userId: 2,
        userName: 'Chef Mike',
        userAvatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=M',
        timeAgo: '4 hours ago',
        text: 'Made my own sushi tonight! 🍣 Not as good as the pros, but pretty proud of the result.',
        restaurant: null,
        likes: 18,
        comments: 12,
        isLiked: true,
        isFollowing: false,
        timestamp: Date.now() - (4 * 60 * 60 * 1000)
      },
      {
        id: 3,
        userId: 3,
        userName: 'Taco Lover',
        userAvatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=T',
        timeAgo: '6 hours ago',
        text: 'Taco Tuesday is the best day of the week! 🌮 These street tacos from Taco Fiesta are incredible.',
        restaurant: {
          name: 'Taco Fiesta',
          image: 'https://via.placeholder.com/80x60/07450C/ffffff?text=TF',
          rating: 4,
          cuisine: 'Mexican'
        },
        likes: 31,
        comments: 15,
        isLiked: false,
        isFollowing: false,
        timestamp: Date.now() - (6 * 60 * 60 * 1000)
      },
      {
        id: 4,
        userId: 4,
        userName: 'Pizza Master',
        userAvatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=P',
        timeAgo: '1 day ago',
        text: 'Pizza night with friends! 🍕 Nothing beats a good wood-fired pizza with fresh ingredients.',
        restaurant: {
          name: 'Pizza Palace',
          image: 'https://via.placeholder.com/80x60/07450C/ffffff?text=PP',
          rating: 5,
          cuisine: 'Italian'
        },
        likes: 42,
        comments: 18,
        isLiked: false,
        isFollowing: true,
        timestamp: Date.now() - (24 * 60 * 60 * 1000)
      },
      {
        id: 5,
        userId: 5,
        userName: 'Sushi Explorer',
        userAvatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=S',
        timeAgo: '2 days ago',
        text: 'Omakase experience at Sakura! 🍣 The chef\'s selection was mind-blowing. Worth every penny!',
        restaurant: {
          name: 'Sakura Sushi',
          image: 'https://via.placeholder.com/80x60/07450C/ffffff?text=SS',
          rating: 5,
          cuisine: 'Japanese'
        },
        likes: 67,
        comments: 23,
        isLiked: true,
        isFollowing: false,
        timestamp: Date.now() - (2 * 24 * 60 * 60 * 1000)
      }
    ]
  }

  // Get initial sample lists
  getInitialLists() {
    return [
      {
        id: 1,
        name: 'Best Pizza Places',
        description: 'My favorite pizza spots around the city',
        privacy: 'public',
        restaurants: ['Pizza Palace', 'Slice Heaven', 'Wood Fired'],
        views: 45,
        likes: 12,
        userId: 0,
        createdAt: Date.now() - (7 * 24 * 60 * 60 * 1000)
      },
      {
        id: 2,
        name: 'Date Night Spots',
        description: 'Perfect restaurants for romantic evenings',
        privacy: 'friends',
        restaurants: ['Rooftop Lounge', 'Candlelight Cafe'],
        views: 23,
        likes: 8,
        userId: 0,
        createdAt: Date.now() - (14 * 24 * 60 * 60 * 1000)
      },
      {
        id: 3,
        name: 'Budget Eats',
        description: 'Delicious food that won\'t break the bank',
        privacy: 'public',
        restaurants: ['Taco Fiesta', 'Sunrise Diner', 'Midnight Bites'],
        views: 67,
        likes: 19,
        userId: 0,
        createdAt: Date.now() - (21 * 24 * 60 * 60 * 1000)
      }
    ]
  }

  // Get initial sample users
  getInitialUsers() {
    return [
      {
        id: 1,
        name: 'Foodie Sarah',
        avatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=S',
        followers: 156,
        following: 89,
        posts: 23,
        isFollowing: true
      },
      {
        id: 2,
        name: 'Chef Mike',
        avatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=M',
        followers: 89,
        following: 45,
        posts: 17,
        isFollowing: false
      },
      {
        id: 3,
        name: 'Taco Lover',
        avatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=T',
        followers: 234,
        following: 123,
        posts: 31,
        isFollowing: false
      },
      {
        id: 4,
        name: 'Pizza Master',
        avatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=P',
        followers: 78,
        following: 34,
        posts: 12,
        isFollowing: true
      },
      {
        id: 5,
        name: 'Sushi Explorer',
        avatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=S',
        followers: 189,
        following: 67,
        posts: 28,
        isFollowing: false
      }
    ]
  }

  // Get initial trending topics
  getInitialTrends() {
    return [
      {
        id: 1,
        icon: '🍕',
        title: 'Pizza Wars',
        description: 'The great debate: Chicago vs New York style',
        posts: 156,
        engagement: '2.3K',
        isJoined: false
      },
      {
        id: 2,
        icon: '🌮',
        title: 'Taco Tuesday',
        description: 'Share your best taco finds',
        posts: 89,
        engagement: '1.7K',
        isJoined: true
      },
      {
        id: 3,
        icon: '🍜',
        title: 'Ramen Revolution',
        description: 'Discovering the best ramen spots',
        posts: 67,
        engagement: '1.2K',
        isJoined: false
      },
      {
        id: 4,
        icon: '🍣',
        title: 'Sushi Sunday',
        description: 'Weekend sushi adventures',
        posts: 45,
        engagement: '890',
        isJoined: false
      },
      {
        id: 5,
        icon: '☕',
        title: 'Coffee Culture',
        description: 'Best coffee shops and brews',
        posts: 123,
        engagement: '1.8K',
        isJoined: false
      },
      {
        id: 6,
        icon: '🍰',
        title: 'Dessert Dreams',
        description: 'Sweet treats and pastry perfection',
        posts: 78,
        engagement: '1.1K',
        isJoined: true
      }
    ]
  }

  // Update timestamps for posts
  updateTimestamps() {
    this.posts.forEach(post => {
      const now = Date.now()
      const diff = now - post.timestamp
      
      if (diff < 60 * 1000) {
        post.timeAgo = 'Just now'
      } else if (diff < 60 * 60 * 1000) {
        const minutes = Math.floor(diff / (60 * 1000))
        post.timeAgo = `${minutes} minute${minutes > 1 ? 's' : ''} ago`
      } else if (diff < 24 * 60 * 60 * 1000) {
        const hours = Math.floor(diff / (60 * 60 * 1000))
        post.timeAgo = `${hours} hour${hours > 1 ? 's' : ''} ago`
      } else {
        const days = Math.floor(diff / (24 * 60 * 60 * 1000))
        post.timeAgo = `${days} day${days > 1 ? 's' : ''} ago`
      }
    })
  }

  // Get posts with optional filtering
  getPosts(filter = 'all') {
    this.updateTimestamps()
    
    switch (filter) {
      case 'following':
        return this.posts.filter(post => post.isFollowing)
      case 'trending':
        return this.posts.filter(post => post.likes > 20)
      case 'reviews':
        return this.posts.filter(post => post.restaurant)
      case 'recent':
        return this.posts.sort((a, b) => b.timestamp - a.timestamp)
      default:
        return this.posts
    }
  }

  // Create a new post
  createPost(text, restaurant = null) {
    const newPost = {
      id: Date.now(),
      userId: 0, // Current user
      userName: 'You',
      userAvatar: 'https://via.placeholder.com/40x40/07450C/ffffff?text=Y',
      timeAgo: 'Just now',
      text: text,
      restaurant: restaurant,
      likes: 0,
      comments: 0,
      isLiked: false,
      isFollowing: false,
      timestamp: Date.now()
    }
    
    this.posts.unshift(newPost)
    return newPost
  }

  // Like/unlike a post
  toggleLike(postId) {
    const post = this.posts.find(p => p.id === postId)
    if (post) {
      post.isLiked = !post.isLiked
      post.likes += post.isLiked ? 1 : -1
      return post
    }
    return null
  }

  // Follow/unfollow a user
  toggleFollow(userId) {
    const user = this.users.find(u => u.id === userId)
    if (user) {
      user.isFollowing = !user.isFollowing
      user.followers += user.isFollowing ? 1 : -1
      
      // Update all posts from this user
      this.posts.forEach(post => {
        if (post.userId === userId) {
          post.isFollowing = user.isFollowing
        }
      })
      
      return user
    }
    return null
  }

  // Create a new list
  createList(name, description, privacy) {
    const newList = {
      id: Date.now(),
      name: name,
      description: description,
      privacy: privacy,
      restaurants: [],
      views: 0,
      likes: 0,
      userId: 0,
      createdAt: Date.now()
    }
    
    this.lists.unshift(newList)
    return newList
  }

  // Delete a list
  deleteList(listId) {
    this.lists = this.lists.filter(list => list.id !== listId)
    return true
  }

  // Join/leave a trend
  toggleTrend(trendId) {
    const trend = this.trends.find(t => t.id === trendId)
    if (trend) {
      trend.isJoined = !trend.isJoined
      trend.posts += trend.isJoined ? 1 : -1
      return trend
    }
    return null
  }

  // Get user recommendations based on following
  getUserRecommendations() {
    return this.users
      .filter(user => !user.isFollowing)
      .sort((a, b) => b.followers - a.followers)
      .slice(0, 5)
  }

  // Get trending posts
  getTrendingPosts() {
    return this.posts
      .filter(post => post.likes > 15)
      .sort((a, b) => b.likes - a.likes)
      .slice(0, 10)
  }

  // Search posts by text
  searchPosts(query) {
    const lowercaseQuery = query.toLowerCase()
    return this.posts.filter(post => 
      post.text.toLowerCase().includes(lowercaseQuery) ||
      (post.restaurant && post.restaurant.name.toLowerCase().includes(lowercaseQuery))
    )
  }

  // Comprehensive search across all data types
  search(query) {
    const lowercaseQuery = query.toLowerCase()
    const results = []
    
    // Search posts
    this.posts.forEach(post => {
      if (post.text.toLowerCase().includes(lowercaseQuery) ||
          (post.restaurant && post.restaurant.name.toLowerCase().includes(lowercaseQuery))) {
        results.push({
          ...post,
          type: 'post'
        })
      }
    })
    
    // Search users
    this.users.forEach(user => {
      if (user.name.toLowerCase().includes(lowercaseQuery)) {
        results.push({
          ...user,
          type: 'user'
        })
      }
    })
    
    // Search lists
    this.lists.forEach(list => {
      if (list.name.toLowerCase().includes(lowercaseQuery) ||
          list.description.toLowerCase().includes(lowercaseQuery)) {
        results.push({
          ...list,
          type: 'list'
        })
      }
    })
    
    // Sort results by relevance (posts first, then users, then lists)
    return results.sort((a, b) => {
      const typeOrder = { post: 0, user: 1, list: 2 }
      return typeOrder[a.type] - typeOrder[b.type]
    }).slice(0, 10) // Limit to 10 results
  }

  // Get user profile
  getUserProfile(userId) {
    const user = this.users.find(u => u.id === userId)
    if (user) {
      const userPosts = this.posts.filter(p => p.userId === userId)
      return {
        ...user,
        posts: userPosts
      }
    }
    return null
  }
}

// Export singleton instance
export default new SocialService() 