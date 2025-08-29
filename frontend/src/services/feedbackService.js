// Feedback service: tracks positives/negatives, CTR, and provides decayed weights
// Persists to localStorage and exposes A/B variant assignment

const STORAGE_KEY = 'belp_feedback'
const QUEUE_KEY = 'belp_feedback_queue'
const API_BASE = 'http://localhost:8000'

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
    // delivery state
    const q = this.loadQueue()
    this.queue = Array.isArray(q) ? q : []
    this.isSending = false
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
  saveQueue() {
    try { localStorage.setItem(QUEUE_KEY, JSON.stringify(this.queue)) } catch (_) {}
  }

  load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : null
    } catch (_) {
      return null
    }
  }
  loadQueue() {
    try { const raw = localStorage.getItem(QUEUE_KEY); return raw ? JSON.parse(raw) : [] } catch (_) { return [] }
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
    // enqueue for backend delivery
    this.queue.push(payload)
    this.saveQueue()
    this.flushSoon()
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

  // Delivery batching with backoff
  async flushSoon() {
    if (this.isSending) return
    this.isSending = true
    try {
      let delay = 0
      while (this.queue.length > 0) {
        const batch = this.queue.splice(0, Math.min(50, this.queue.length))
        const body = { events: batch.map(e => ({
          type: e.type,
          restaurantName: e.restaurantName || '',
          cuisine: e.cuisine || '',
          sessionId: e.sessionId || this.sessionId,
          userId: e.userId || '',
          ts: e.ts
        })) }
        const res = await fetch(`${API_BASE}/events`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        })
        if (!res.ok) throw new Error('Failed to POST events')
        delay = 0
        this.saveQueue()
      }
    } catch (e) {
      // exponential backoff capped at 30s
      const jitter = Math.random() * 300
      const current = this._backoff || 500
      const next = Math.min(30000, current * 2)
      this._backoff = next
      this.saveQueue()
      setTimeout(() => this.flushSoon(), next + jitter)
    } finally {
      this.isSending = false
    }
  }
}

export default new FeedbackService() 