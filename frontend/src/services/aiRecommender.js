// Simple AI recommender that re-ranks restaurants using user social signals
// Inputs: list of restaurants (from search), optional context { now, location }
// Output: { restaurants: ranked[], explanations: Map<restaurantId, string[]> }

import socialService from '@/services/socialService.js'

function getUserSignals() {
  const liked = socialService.posts.filter(p => p.isLiked)
  const bookmarked = socialService.posts.filter(p => p.isBookmarked)
  const signals = { cuisineCounts: {}, timeCounts: {}, dayCounts: {}, sample: [] }

  const addCuisine = (name) => {
    if (!name) return
    const key = name.toLowerCase()
    signals.cuisineCounts[key] = (signals.cuisineCounts[key] || 0) + 1
  }
  const addTime = (hour) => {
    const bucket = hourToMeal(hour)
    signals.timeCounts[bucket] = (signals.timeCounts[bucket] || 0) + 1
  }
  const addDay = (day) => {
    if (!day) return
    signals.dayCounts[day] = (signals.dayCounts[day] || 0) + 1
  }

  const now = new Date()
  const all = [...liked, ...bookmarked]
  all.forEach(p => {
    if (p.restaurant && p.restaurant.cuisine) addCuisine(p.restaurant.cuisine)
    const ts = p.timestamp || now.getTime()
    const d = new Date(ts)
    addTime(d.getHours())
    addDay(d.toLocaleDateString(undefined, { weekday: 'long' }))
    signals.sample.push(p)
  })

  return signals
}

function hourToMeal(hour) {
  if (hour >= 6 && hour < 11) return 'breakfast'
  if (hour >= 11 && hour < 15) return 'lunch'
  if (hour >= 15 && hour < 18) return 'afternoon'
  if (hour >= 18 && hour < 22) return 'dinner'
  return 'late-night'
}

function normalizeCounts(counts) {
  const entries = Object.entries(counts)
  if (entries.length === 0) return counts
  const max = Math.max(...entries.map(([, c]) => c)) || 1
  const norm = {}
  entries.forEach(([k, v]) => { norm[k] = v / max })
  return norm
}

function extractRestaurantCuisine(restaurant) {
  // Tries multiple fields commonly seen
  // categories: array of { title } or strings; cuisine field; tags
  if (restaurant.cuisine) return [String(restaurant.cuisine).toLowerCase()]
  if (Array.isArray(restaurant.categories)) {
    return restaurant.categories
      .map(c => (typeof c === 'string' ? c : (c?.title || c?.alias || '')))
      .filter(Boolean)
      .map(s => String(s).toLowerCase())
  }
  if (Array.isArray(restaurant.tags)) {
    return restaurant.tags.map(t => String(t).toLowerCase())
  }
  return []
}

function scoreRestaurant(r, userPref, contextNow) {
  const explanations = []
  let score = 0

  // Cuisine match
  const cuisines = extractRestaurantCuisine(r)
  let cuisineBoost = 0
  cuisines.forEach(c => {
    const w = userPref.cuisine[c] || 0
    cuisineBoost = Math.max(cuisineBoost, w)
  })
  if (cuisineBoost > 0) {
    score += 0.6 * cuisineBoost
    const top = cuisines.find(c => userPref.cuisine[c])
    if (top) explanations.push(`Matches your taste for ${capitalize(top)}`)
  }

  // Time-of-day preference
  const mealNow = hourToMeal(contextNow.getHours())
  const timeBoost = userPref.time[mealNow] || 0
  if (timeBoost > 0) {
    score += 0.25 * timeBoost
    explanations.push(`Great for your typical ${mealNow}`)
  }

  // Recency/popularity proxy if provided
  if (typeof r.rating === 'number') {
    score += 0.1 * (r.rating / 5)
  }
  if (typeof r.review_count === 'number') {
    const pop = Math.min(1, r.review_count / 500)
    score += 0.05 * pop
  }

  return { score, explanations }
}

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1) }

export function scoreAndExplain(restaurants, context = {}) {
  const now = context.now || new Date()
  const signals = getUserSignals()
  const cuisineNorm = normalizeCounts(signals.cuisineCounts)
  const timeNorm = normalizeCounts(signals.timeCounts)

  const userPref = { cuisine: cuisineNorm, time: timeNorm }

  const scored = restaurants.map(r => {
    const { score, explanations } = scoreRestaurant(r, userPref, now)
    return { r, score, explanations }
  })

  scored.sort((a, b) => b.score - a.score)

  const ranked = scored.map(x => ({ ...x.r, _aiScore: x.score, _aiWhy: x.explanations }))
  const explanationsMap = new Map()
  ranked.forEach(item => explanationsMap.set(item.id || item.name, item._aiWhy))

  return { restaurants: ranked, explanations: explanationsMap }
}

export default { scoreAndExplain } 