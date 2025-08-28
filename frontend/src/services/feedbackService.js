// Feedback service: tracks positives/negatives, CTR, and provides decayed weights
// Persists to localStorage and exposes A/B variant assignment

const STORAGE_KEY = 'belp_feedback'

class FeedbackService {
  constructor() {
    const persisted = this.load()
    if (persisted) {
      this.events = persisted.events || []
      this.variant = persisted.variant || this.assignVariant()
      this.sessionId = persisted.sessionId || this.newSessionId()
      this.sessionStartedAt = persisted.sessionStartedAt || Date.now()
    } else {
      this.events = []
      this.variant = this.assignVariant()
      this.sessionId = this.newSessionId()
      this.sessionStartedAt = Date.now()
      this.save()
    }
  }

  assignVariant() {
    // Simple 50/50 A/B between 'A' and 'B'
    return Math.random() < 0.5 ? 'A' : 'B'
  }

  newSessionId() {
    return `sess_${Math.random().toString(36).slice(2)}_${Date.now()}`
  }

  save() {
    try {
      const payload = {
        events: this.events,
        variant: this.variant,
        sessionId: this.sessionId,
        sessionStartedAt: this.sessionStartedAt
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    } catch (_) {}
  }

  load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : null
    } catch (_) {
      return null
    }
  }

  // Record feedback events
  record(event) {
    // event: { type: 'click'|'view'|'positive'|'negative'|'save', restaurantName, cuisine, ts }
    const ts = event.ts || Date.now()
    const payload = { ...event, ts, sessionId: this.sessionId }
    this.events.unshift(payload)
    // cap size
    if (this.events.length > 1000) this.events.pop()
    this.save()
    return payload
  }

  // Convenience helpers
  recordPositive({ restaurantName, cuisine }) {
    return this.record({ type: 'positive', restaurantName, cuisine })
  }
  recordNegative({ restaurantName, cuisine }) {
    return this.record({ type: 'negative', restaurantName, cuisine })
  }
  recordClick({ restaurantName, cuisine }) {
    return this.record({ type: 'click', restaurantName, cuisine })
  }
  recordView({ restaurantName, cuisine }) {
    return this.record({ type: 'view', restaurantName, cuisine })
  }

  // Aggregate decayed weights
  getWeights(now = Date.now()) {
    const halfLifeHours = 72 // 3 days; older interactions decay
    const lambda = Math.log(2) / (halfLifeHours * 3600 * 1000)

    const cuisinePos = {}
    const cuisineNeg = {}
    let clicks = 0, views = 0

    for (const ev of this.events) {
      const age = now - ev.ts
      const w = Math.exp(-lambda * age)
      if (ev.type === 'positive' || ev.type === 'save') {
        const key = (ev.cuisine || '').toLowerCase()
        if (!key) continue
        cuisinePos[key] = (cuisinePos[key] || 0) + w
      } else if (ev.type === 'negative') {
        const key = (ev.cuisine || '').toLowerCase()
        if (!key) continue
        cuisineNeg[key] = (cuisineNeg[key] || 0) + w
      } else if (ev.type === 'click') {
        clicks += w
      } else if (ev.type === 'view') {
        views += w
      }
    }

    const ctr = views > 0 ? clicks / views : 0
    // Session boost (more weight early in a session)
    const sessionAgeMin = (now - this.sessionStartedAt) / 60000
    const sessionBoost = Math.max(0.85, 1.0 - Math.min(0.3, sessionAgeMin / 120 * 0.3))

    return { cuisinePos, cuisineNeg, ctr, sessionBoost, variant: this.variant }
  }
}

export default new FeedbackService() 