// Ranking Service for BELP
// Handles restaurant ratings, comparisons, and ranking lists

class RankingService {
  constructor() {
    this.ratings = this.loadRatings();
    this.comparisons = this.loadComparisons();
    this.rankingLists = this.loadRankingLists();
    this.visited = this.loadVisited();
    this.rank10 = this.loadRank10();
    this.restaurantMeta = this.loadMeta();
  }

  // Load user ratings from localStorage
  loadRatings() {
    try {
      const stored = localStorage.getItem('belp_restaurant_ratings');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.warn('Failed to load ratings:', error);
      return {};
    }
  }

  // Load comparison data from localStorage
  loadComparisons() {
    try {
      const stored = localStorage.getItem('belp_restaurant_comparisons');
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.warn('Failed to load comparisons:', error);
      return [];
    }
    }

  // Load ranking lists from localStorage
  loadRankingLists() {
    try {
      const stored = localStorage.getItem('belp_ranking_lists');
      return stored ? JSON.parse(stored) : this.getDefaultLists();
    } catch (error) {
      console.warn('Failed to load ranking lists:', error);
      return this.getDefaultLists();
    }
  }

  // Load visited restaurants from localStorage
  loadVisited() {
    try {
      const stored = localStorage.getItem('belp_visited_restaurants');
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      console.warn('Failed to load visited:', e);
      return [];
    }
  }

  saveVisited() {
    try {
      localStorage.setItem('belp_visited_restaurants', JSON.stringify(this.visited));
    } catch (e) {
      console.error('Failed to save visited:', e);
    }
  }

  markVisited(restaurant) {
    const restaurantId = restaurant.restaurantId || `${restaurant.name}||${restaurant.address}`;
    // keep meta in sync
    this.setMeta(restaurantId, { name: restaurant.name, address: restaurant.address, categories: restaurant.categories, stars: restaurant.stars });
    if (!this.visited.find(v => v.restaurantId === restaurantId)) {
      this.visited.unshift({
        restaurantId,
        name: restaurant.name,
        address: restaurant.address,
        categories: restaurant.categories || '',
        stars: restaurant.stars || 0,
        timestamp: new Date().toISOString()
      });
      // keep last 200
      if (this.visited.length > 200) this.visited = this.visited.slice(0, 200);
      this.saveVisited();
    }
    return this.visited[0];
  }

  unmarkVisited(restaurantId) {
    this.visited = this.visited.filter(v => v.restaurantId !== restaurantId);
    this.saveVisited();
  }

  isVisited(restaurantId) {
    return !!this.visited.find(v => v.restaurantId === restaurantId);
  }

  getVisited() {
    return [...this.visited];
  }

  ensureList(listId, name, description, type = 'personal') {
    let list = this.rankingLists.find(l => l.id === listId);
    if (!list) {
      list = { id: listId, name, description, type, restaurants: [], createdAt: new Date().toISOString(), lastUpdated: new Date().toISOString() };
      this.rankingLists.push(list);
      this.saveRankingLists();
    }
    return list;
  }

  addToToRank(restaurantId) {
    const list = this.ensureList('to_rank', 'To Rank', 'Restaurants to rate', 'personal');
    if (!list.restaurants.includes(restaurantId)) {
      list.restaurants.unshift(restaurantId);
      list.lastUpdated = new Date().toISOString();
      this.saveRankingLists();
    }
    return list;
  }

  getToRankList() {
    return this.rankingLists.find(l => l.id === 'to_rank') || null;
  }

  // Get default ranking lists
  getDefaultLists() {
    return [
      {
        id: 'top_overall',
        name: 'Top Overall',
        description: 'Highest rated restaurants',
        type: 'community',
        restaurants: []
      },
      {
        id: 'best_new',
        name: 'Best New Places',
        description: 'Recently added top performers',
        type: 'community',
        restaurants: []
      },
      {
        id: 'personal_favorites',
        name: 'My Favorites',
        description: 'Your highest rated restaurants',
        type: 'personal',
        restaurants: []
      }
    ];
  }

  // Rate a restaurant
  rateRestaurant(restaurantId, rating, review = '', categories = []) {
    if (rating < 1 || rating > 5) {
      throw new Error('Rating must be between 1 and 5');
    }

    const ratingData = {
      restaurantId,
      rating,
      review: review.trim(),
      categories: categories.filter(c => c.trim()),
      timestamp: new Date().toISOString(),
      lastUpdated: new Date().toISOString()
    };

    this.ratings[restaurantId] = ratingData;
    this.saveRatings();
    this.updateRankingLists();
    
    return ratingData;
  }

  // Update an existing rating
  updateRating(restaurantId, rating, review = '', categories = []) {
    if (!this.ratings[restaurantId]) {
      throw new Error('No existing rating found for this restaurant');
    }

    const existing = this.ratings[restaurantId];
    existing.rating = rating;
    existing.review = review.trim();
    existing.categories = categories.filter(c => c.trim());
    existing.lastUpdated = new Date().toISOString();

    this.saveRatings();
    this.updateRankingLists();
    
    return existing;
  }

  // Get rating for a restaurant
  getRating(restaurantId) {
    return this.ratings[restaurantId] || null;
  }

  // Get all user ratings
  getUserRatings() {
    return Object.values(this.ratings).sort((a, b) => 
      new Date(b.lastUpdated) - new Date(a.lastUpdated)
    );
  }



  // Create a comparison between restaurants
  createComparison(restaurantIds, title = '') {
    if (restaurantIds.length < 2 || restaurantIds.length > 4) {
      throw new Error('Comparison must include 2-4 restaurants');
    }

    const comparison = {
      id: `comp_${Date.now()}`,
      title: title.trim() || `Comparison ${new Date().toLocaleDateString()}`,
      restaurantIds,
      createdAt: new Date().toISOString(),
      lastViewed: new Date().toISOString()
    };

    this.comparisons.unshift(comparison);
    
    // Keep only last 20 comparisons
    if (this.comparisons.length > 20) {
      this.comparisons = this.comparisons.slice(0, 20);
    }

    this.saveComparisons();
    return comparison;
  }

  // Get comparison data
  getComparison(comparisonId) {
    return this.comparisons.find(c => c.id === comparisonId);
  }

  // Get all comparisons
  getAllComparisons() {
    return this.comparisons;
  }

  // Update comparison view time
  updateComparisonView(comparisonId) {
    const comparison = this.comparisons.find(c => c.id === comparisonId);
    if (comparison) {
      comparison.lastViewed = new Date().toISOString();
      this.saveComparisons();
    }
  }

  // Create a ranking list
  createRankingList(name, description, restaurants = [], type = 'personal') {
    const list = {
      id: `list_${Date.now()}`,
      name: name.trim(),
      description: description.trim(),
      restaurants: restaurants,
      type: type,
      createdAt: new Date().toISOString(),
      lastUpdated: new Date().toISOString()
    };

    this.rankingLists.push(list);
    this.saveRankingLists();
    return list;
  }

  // Add restaurant to ranking list
  addToRankingList(listId, restaurantId, position = null) {
    const list = this.rankingLists.find(l => l.id === listId);
    if (!list) {
      throw new Error('Ranking list not found');
    }

    if (position !== null && position >= 0 && position <= list.restaurants.length) {
      list.restaurants.splice(position, 0, restaurantId);
    } else {
      list.restaurants.push(restaurantId);
    }

    list.lastUpdated = new Date().toISOString();
    this.saveRankingLists();
    return list;
  }

  // Remove restaurant from ranking list
  removeFromRankingList(listId, restaurantId) {
    const list = this.rankingLists.find(l => l.id === listId);
    if (!list) {
      throw new Error('Ranking list not found');
    }

    const index = list.restaurants.indexOf(restaurantId);
    if (index > -1) {
      list.restaurants.splice(index, 1);
      list.lastUpdated = new Date().toISOString();
      this.saveRankingLists();
    }

    return list;
  }

  // Reorder restaurants in a list
  reorderRankingList(listId, newOrder) {
    const list = this.rankingLists.find(l => l.id === listId);
    if (!list) {
      throw new Error('Ranking list not found');
    }

    list.restaurants = newOrder;
    list.lastUpdated = new Date().toISOString();
    this.saveRankingLists();
    return list;
  }

  // Get ranking list
  getRankingList(listId) {
    return this.rankingLists.find(l => l.id === listId);
  }

  // Get all ranking lists
  getAllRankingLists() {
    return this.rankingLists;
  }

  // Get personal ranking lists
  getPersonalLists() {
    return this.rankingLists.filter(l => l.type === 'personal');
  }

  // Get community ranking lists
  getCommunityLists() {
    return this.rankingLists.filter(l => l.type === 'community');
  }

  // Update ranking lists based on current ratings
  updateRankingLists() {
    // Update personal favorites list
    const personalFavorites = this.rankingLists.find(l => l.id === 'personal_favorites');
    if (personalFavorites) {
      const userRatings = this.getUserRatings();
      const topRated = userRatings
        .filter(r => r.rating >= 4)
        .sort((a, b) => b.rating - a.rating)
        .slice(0, 10)
        .map(r => r.restaurantId);
      
      personalFavorites.restaurants = topRated;
      personalFavorites.lastUpdated = new Date().toISOString();
    }

    this.saveRankingLists();
  }

  // Get restaurant ranking stats
  getRestaurantStats(restaurantId) {
    const rating = this.ratings[restaurantId];
    if (!rating) return null;

    const allRatings = this.getUserRatings();
    const totalRated = allRatings.length;
    const rank = allRatings
      .sort((a, b) => b.rating - a.rating)
      .findIndex(r => r.restaurantId === restaurantId) + 1;

    return {
      userRating: rating.rating,
      userReview: rating.review,
      userCategories: rating.categories,
      totalRated,
      rank: rank > 0 ? rank : 'Unranked',
      lastRated: rating.lastUpdated
    };
  }

  // Search ratings and lists
  searchRankings(query) {
    const results = {
      ratings: [],
      lists: [],
      comparisons: []
    };

    const searchTerm = query.toLowerCase();

    // Search ratings
    Object.values(this.ratings).forEach(rating => {
      if (rating.review.toLowerCase().includes(searchTerm) ||
          rating.categories.some(c => c.toLowerCase().includes(searchTerm))) {
        results.ratings.push(rating);
      }
    });

    // Search lists
    this.rankingLists.forEach(list => {
      if (list.name.toLowerCase().includes(searchTerm) ||
          list.description.toLowerCase().includes(searchTerm)) {
        results.lists.push(list);
      }
    });

    // Search comparisons
    this.comparisons.forEach(comp => {
      if (comp.title.toLowerCase().includes(searchTerm)) {
        results.comparisons.push(comp);
      }
    });

    return results;
  }

  // Save ratings to localStorage
  saveRatings() {
    try {
      localStorage.setItem('belp_restaurant_ratings', JSON.stringify(this.ratings));
    } catch (error) {
      console.error('Failed to save ratings:', error);
    }
  }

  // Save comparisons to localStorage
  saveComparisons() {
    try {
      localStorage.setItem('belp_restaurant_comparisons', JSON.stringify(this.comparisons));
    } catch (error) {
      console.error('Failed to save comparisons:', error);
    }
  }

  // Save ranking lists to localStorage
  saveRankingLists() {
    try {
      localStorage.setItem('belp_ranking_lists', JSON.stringify(this.rankingLists));
    } catch (error) {
      console.error('Failed to save ranking lists:', error);
    }
  }

  // Metadata store
  loadMeta() {
    try {
      const stored = localStorage.getItem('belp_restaurant_meta');
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      console.warn('Failed to load meta:', e);
      return {};
    }
  }
  saveMeta() {
    try {
      localStorage.setItem('belp_restaurant_meta', JSON.stringify(this.restaurantMeta));
    } catch (e) {
      console.error('Failed to save meta:', e);
    }
  }
  setMeta(restaurantId, meta) {
    if (!restaurantId) return;
    const safe = this.restaurantMeta[restaurantId] || {};
    this.restaurantMeta[restaurantId] = {
      ...safe,
      name: meta?.name || safe.name || '',
      address: meta?.address || safe.address || '',
      categories: meta?.categories || safe.categories || '',
      stars: typeof meta?.stars === 'number' ? meta.stars : (safe.stars || 0),
      primaryCuisine: meta?.primaryCuisine || safe.primaryCuisine || ''
    };
    this.saveMeta();
    return this.restaurantMeta[restaurantId];
  }
  getMeta(restaurantId) { return this.restaurantMeta[restaurantId] || null; }

  // 1-10 ranking store
  loadRank10() {
    try {
      const stored = localStorage.getItem('belp_rank10');
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      console.warn('Failed to load rank10:', e);
      return {};
    }
  }

  saveRank10() {
    try {
      localStorage.setItem('belp_rank10', JSON.stringify(this.rank10));
    } catch (e) {
      console.error('Failed to save rank10:', e);
    }
  }

  setRank10(restaurantId, score) {
    const bounded = Math.max(1, Math.min(10, Number(score) || 0));
    this.rank10[restaurantId] = { score: bounded, lastUpdated: new Date().toISOString() };
    this.saveRank10();
    this.updateRankedTopList();
    return this.rank10[restaurantId];
  }

  getRank10(restaurantId) {
    return this.rank10[restaurantId] || null;
  }

  getRank10Entries() {
    return Object.entries(this.rank10)
      .map(([restaurantId, v]) => ({ restaurantId, score: v.score, lastUpdated: v.lastUpdated, meta: this.getMeta(restaurantId) }))
      .sort((a, b) => b.score - a.score || new Date(b.lastUpdated) - new Date(a.lastUpdated));
  }

  updateRankedTopList() {
    const list = this.ensureList('ranked_top', 'Top Ranked (1-10)', 'Your top ranked restaurants', 'personal');
    list.restaurants = this.getRank10Entries().map(e => e.restaurantId).slice(0, 50);
    list.lastUpdated = new Date().toISOString();
    this.saveRankingLists();
  }

  // Clear all ranking data (for testing/reset)
  clearAllData() {
    this.ratings = {};
    this.comparisons = [];
    this.rankingLists = this.getDefaultLists();
    this.visited = []; // Clear visited restaurants
    this.rank10 = {}; // Clear 1-10 rankings
    this.restaurantMeta = {}; // Clear restaurant meta
    
    localStorage.removeItem('belp_restaurant_ratings');
    localStorage.removeItem('belp_restaurant_comparisons');
    localStorage.removeItem('belp_ranking_lists');
    localStorage.removeItem('belp_visited_restaurants'); // Clear visited restaurants
    localStorage.removeItem('belp_rank10'); // Clear 1-10 rankings
    localStorage.removeItem('belp_restaurant_meta'); // Clear restaurant meta
  }
}

// Create singleton instance
const rankingService = new RankingService();

export default rankingService; 