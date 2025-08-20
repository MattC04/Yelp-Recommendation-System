<script setup>
import { ref } from 'vue'
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <router-link to="/" class="brand-link">
          <span class="logo">🍽️</span>
          <span class="brand-name">BELP</span>
        </router-link>
      </div>
      <nav class="nav">
        <router-link to="/" class="nav-link">Home</router-link>
        <router-link to="/profile" class="nav-link">Profile</router-link>
        <router-link to="/share" class="nav-link">Share</router-link>
      </nav>
    </header>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style>
body {
  background: white;
  margin: 0;
  padding: 0;
  font-family: 'Arial', 'Helvetica', sans-serif;
}

#app {
  min-height: 100vh;
}

.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid rgba(7,69,12,0.15);
  background: white;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
}

.logo {
  font-size: 1.4rem;
}

.brand-name {
  color: #07450C;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.nav {
  display: inline-flex;
  gap: 1rem;
}

.nav-link {
  color: #07450C;
  text-decoration: none;
  font-weight: 600;
}

.nav-link.router-link-active {
  text-decoration: underline;
}

.content {
  flex: 1;
  display: block;
}
</style>
