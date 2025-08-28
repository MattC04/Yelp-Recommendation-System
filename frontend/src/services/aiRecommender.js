// Simple AI recommender that re-ranks restaurants using user social signals
// Inputs: list of restaurants (from search), optional context { now, location }
// Output: { restaurants: ranked[], explanations: Map<restaurantId, string[]> }

import socialService from '@/services/socialService.js'
import feedbackService from '@/services/feedbackService.js'

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
  if (restaurant.cuisine) return [String(restaurant.cuisine).toLowerCase()]
  if (Array.isArray(restaurant.categories)) {
    return restaurant.categories
      .toString()
      .split(',')
      .map(s => s.trim())
      .filter(Boolean)
      .map(s => String(s).toLowerCase())
  }
  if (Array.isArray(restaurant.tags)) {
    return restaurant.tags.map(t => String(t).toLowerCase())
  }
  return []
}

function scoreRestaurant(r, userPref, contextNow, feedbackWeights) {
  const explanations = []
  let score = 0

  // Cuisine match (social signals)
  const cuisines = extractRestaurantCuisine(r)
  let cuisineBoost = 0
  let negHit = false
  cuisines.forEach(c => {
    const pos = userPref.cuisine[c] || 0
    const neg = feedbackWeights.cuisineNeg[c] || 0
    const net = Math.max(0, pos - 0.7 * neg) // downweight if negative feedback exists
    cuisineBoost = Math.max(cuisineBoost, net)
    if (neg > 0.05) negHit = true
  })
  if (cuisineBoost > 0) {
    score += 0.6 * cuisineBoost
    const top = cuisines.find(c => userPref.cuisine[c])
    if (top) explanations.push(`Matches your taste for ${capitalize(top)}`)
  }
  if (negHit) explanations.push('De-emphasized cuisines you marked as not interested')

  // Time-of-day preference
  const mealNow = hourToMeal(contextNow.getHours())
  const timeBoost = userPref.time[mealNow] || 0
  if (timeBoost > 0) {
    score += 0.25 * timeBoost
    explanations.push(`Great for your typical ${mealNow}`)
  }

  // Recency/popularity proxy if provided
  if (typeof r.rating === 'number') score += 0.1 * (r.rating / 5)
  if (typeof r.review_count === 'number') score += 0.05 * Math.min(1, r.review_count / 500)

  // CTR/session context multipliers
  const ctrFactor = 1 + Math.min(0.15, (feedbackWeights.ctr || 0) * 0.3)
  const sessionFactor = feedbackWeights.sessionBoost || 1.0
  score *= ctrFactor * sessionFactor

  return { score, explanations }
}

function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1) }

export function scoreAndExplain(restaurants, context = {}) {
  const now = context.now || new Date()
  const signals = getUserSignals()
  const cuisineNorm = normalizeCounts(signals.cuisineCounts)
  const timeNorm = normalizeCounts(signals.timeCounts)
  const userPref = { cuisine: cuisineNorm, time: timeNorm }

  const feedbackWeights = feedbackService.getWeights(now.getTime())

  const scored = restaurants.map(r => {
    const { score, explanations } = scoreRestaurant(r, userPref, now, feedbackWeights)
    return { r, score, explanations }
  })

  scored.sort((a, b) => b.score - a.score)

  const ranked = scored.map(x => ({ ...x.r, _aiScore: x.score, _aiWhy: x.explanations }))
  const explanationsMap = new Map()
  ranked.forEach(item => explanationsMap.set(item.id || item.name, item._aiWhy))

  return { restaurants: ranked, explanations: explanationsMap, variant: feedbackWeights.variant }
}

export default { scoreAndExplain } 