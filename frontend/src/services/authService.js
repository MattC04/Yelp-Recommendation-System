class AuthService {
  constructor() {
    this.currentUser = null;
    this.isAuthenticated = false;
    this.loadUserFromStorage();
  }

  // Load user from localStorage on service initialization
  loadUserFromStorage() {
    try {
      const userData = localStorage.getItem('belp_user');
      if (userData) {
        this.currentUser = JSON.parse(userData);
        this.isAuthenticated = true;
      }
    } catch (error) {
      console.error('Error loading user from storage:', error);
      this.logout();
    }
  }

  // Register new user
  async register(userData) {
    try {
      // Simulate API call - replace with actual backend endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const newUser = {
        id: Date.now().toString(),
        email: userData.email,
        username: userData.username,
        name: userData.name,
        createdAt: new Date().toISOString(),
        preferences: {
          cuisines: [],
          dietary: [],
          budget: 'medium',
          occasion: 'casual'
        },
        stats: {
          reviews: 0,
          lists: 0,
          comparisons: 0
        }
      };

      // Save to localStorage
      this.currentUser = newUser;
      this.isAuthenticated = true;
      localStorage.setItem('belp_user', JSON.stringify(newUser));
      
      return { success: true, user: newUser };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration failed' };
    }
  }

  // Login user
  async login(credentials) {
    try {
      // Simulate API call - replace with actual backend endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo purposes, accept any email/password combination
      // In production, this would validate against backend
      if (!credentials.email || !credentials.password) {
        throw new Error('Email and password are required');
      }

      // Check if user exists in localStorage (simulating user database)
      const existingUser = localStorage.getItem('belp_user');
      let user;

      if (existingUser) {
        user = JSON.parse(existingUser);
        // Update last login
        user.lastLogin = new Date().toISOString();
      } else {
        // Create demo user if none exists
        user = {
          id: Date.now().toString(),
          email: credentials.email,
          username: credentials.email.split('@')[0],
          name: 'Demo User',
          createdAt: new Date().toISOString(),
          lastLogin: new Date().toISOString(),
          preferences: {
            cuisines: ['Italian', 'Mexican', 'Asian'],
            dietary: ['Vegetarian'],
            budget: 'medium',
            occasion: 'casual'
          },
          stats: {
            reviews: 3,
            lists: 2,
            comparisons: 1
          }
        };
      }

      // Save to localStorage
      this.currentUser = user;
      this.isAuthenticated = true;
      localStorage.setItem('belp_user', JSON.stringify(user));
      
      return { success: true, user };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message };
    }
  }

  // Logout user
  logout() {
    this.currentUser = null;
    this.isAuthenticated = false;
    localStorage.removeItem('belp_user');
    
    // Clear other app data
    localStorage.removeItem('belp_preferences');
    localStorage.removeItem('belp_search_history');
    localStorage.removeItem('belp_favorites');
  }

  // Get current user
  getCurrentUser() {
    return this.currentUser;
  }

  // Check if user is authenticated
  checkAuth() {
    return this.isAuthenticated;
  }

  // Update user preferences
  updatePreferences(preferences) {
    if (this.currentUser) {
      this.currentUser.preferences = { ...this.currentUser.preferences, ...preferences };
      localStorage.setItem('belp_user', JSON.stringify(this.currentUser));
      return true;
    }
    return false;
  }

  // Update user stats
  updateStats(stats) {
    if (this.currentUser) {
      this.currentUser.stats = { ...this.currentUser.stats, ...stats };
      localStorage.setItem('belp_user', JSON.stringify(this.currentUser));
      return true;
    }
    return false;
  }

  // Check if user has completed onboarding
  hasCompletedOnboarding() {
    if (!this.currentUser) return false;
    return this.currentUser.preferences && 
           this.currentUser.preferences.cuisines && 
           this.currentUser.preferences.cuisines.length > 0;
  }

  // Get user's display name
  getDisplayName() {
    if (!this.currentUser) return 'Guest';
    return this.currentUser.name || this.currentUser.username || 'User';
  }

  // Get user's avatar/initials
  getUserAvatar() {
    if (!this.currentUser) return '👤';
    const name = this.currentUser.name || this.currentUser.username || '';
    if (name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    return '👤';
  }
}

// Create singleton instance
const authService = new AuthService();

export default authService; 