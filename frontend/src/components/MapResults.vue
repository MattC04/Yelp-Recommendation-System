<template>
  <div class="map-results">
    <div class="map-header">
      <strong>Map</strong> — {{ results.length }} places
      <span v-if="locationQuery"> near {{ locationQuery }}</span>
    </div>

    <!-- Placeholder map area (replace with real map when ready) -->
    <div class="map-placeholder" role="img" aria-label="Map placeholder">
      🗺️ Map view placeholder
    </div>

    <ul class="map-list">
      <li v-for="r in results" :key="r.name + '|' + r.address">
        <span class="name">{{ r.name }}</span>
        <span class="meta"> — {{ r.address }}</span>
      </li>
    </ul>
  </div>
  
</template>

<script>
export default {
  name: 'MapResults',
  props: {
    results: { type: Array, default: () => [] },
    locationQuery: { type: String, default: '' },
  },
  methods: {
    // Called by parent via ref when view toggles
    resizeMap() {
      // No-op for placeholder. Keep method to avoid errors.
    },
  },
}
</script>

<style scoped>
.map-results { padding: 0.75rem; }
.map-header { font-weight: 700; color: #07450C; margin-bottom: 0.5rem; }
.map-placeholder {
  display: flex; align-items: center; justify-content: center;
  height: 260px; border: 1px dashed #aac4af; border-radius: 12px;
  background: rgba(7,69,12,0.04); color: #07450C; font-weight: 700;
  margin-bottom: 0.75rem;
}
.map-list { list-style: none; padding: 0; margin: 0; }
.map-list li { padding: 0.35rem 0; }
.name { color: #07450C; font-weight: 700; }
.meta { color: #34523a; }
</style>


