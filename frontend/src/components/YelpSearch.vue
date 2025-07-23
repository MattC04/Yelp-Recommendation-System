<template>
  <div class="yelp-search">
    <h2>Yelp Recommendation Search</h2>
    <input v-model="query" @keyup.enter="search" placeholder="Type your craving or occasion..." />
    <button @click="search">Search</button>
    <div v-if="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="results.length">
      <h3>Top Recommendations</h3>
      <ul>
        <li v-for="(r, idx) in results" :key="idx">
          <strong>{{ r.name }}</strong> ({{ r.stars }}★)<br />
          {{ r.address }}<br />
          <em>{{ r.categories }}</em>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const query = ref('')
const results = ref([])
const loading = ref(false)
const error = ref('')

const search = async () => {
  if (!query.value.trim()) return
  loading.value = true
  error.value = ''
  results.value = []
  try {
    const res = await axios.post('http://localhost:8000/recommend', { query: query.value })
    results.value = res.data
    if (!results.value.length) error.value = 'No recommendations found.'
  } catch (e) {
    error.value = 'Error fetching recommendations.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.yelp-search {
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fafbfc;
}
input {
  width: 70%;
  padding: 0.5rem;
  margin-right: 0.5rem;
}
button {
  padding: 0.5rem 1rem;
}
.error {
  color: #c00;
  margin-top: 1rem;
}
ul {
  margin-top: 1rem;
  padding-left: 1.2rem;
}
li {
  margin-bottom: 1rem;
}
</style>
