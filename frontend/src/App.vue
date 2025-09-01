<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import authService from './services/authService.js'

const router = useRouter()
const isMobileMenuOpen = ref(false)
const showUserMenu = ref(false)

// Authentication state
const isAuthenticated = ref(false)
const currentUser = ref(null)

// Load auth state on mount
onMounted(() => {
  updateAuthState()
})

// Update authentication state
const updateAuthState = () => {
  isAuthenticated.value = authService.checkAuth()
  currentUser.value = authService.getCurrentUser()
}

// Handle logout
const handleLogout = () => {
  authService.logout()
  updateAuthState()
  closeMobileMenu()
  router.push('/')
}

// Toggle mobile menu
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// Toggle user menu
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

// Computed properties
const userDisplayName = computed(() => {
  return authService.getDisplayName()
})

const userAvatar = computed(() => {
  return authService.getUserAvatar()
})
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <router-link to="/" class="brand-link" @click="closeMobileMenu">
          <span class="logo">🍽️</span>
          <span class="brand-name">BELP</span>
        </router-link>
      </div>
      
      <!-- Desktop Navigation -->
      <nav class="nav desktop-nav">
        <router-link to="/" class="nav-link" @click="closeMobileMenu">Home</router-link>
        <router-link to="/search" class="nav-link" @click="closeMobileMenu">Search</router-link>
        <router-link to="/rankings" class="nav-link" @click="closeMobileMenu">Rankings</router-link>
        <router-link to="/profile" class="nav-link" @click="closeMobileMenu">Profile</router-link>
        <router-link to="/share" class="nav-link" @click="closeMobileMenu">Share</router-link>
        
        <!-- Auth Navigation -->
        <div v-if="!isAuthenticated" class="auth-nav">
          <router-link to="/login" class="nav-link auth-link" @click="closeMobileMenu">
            Sign In
          </router-link>
        </div>
        <div v-else class="user-nav">
          <div class="user-menu">
            <button class="user-btn" @click="toggleUserMenu">
              <span class="user-avatar">{{ userAvatar }}</span>
              <span class="user-name">{{ userDisplayName }}</span>
              <span class="dropdown-arrow">▼</span>
            </button>
            <div class="user-dropdown" v-if="showUserMenu">
              <router-link to="/profile" class="dropdown-item" @click="closeUserMenu">
                <span class="dropdown-icon">👤</span>
                My Profile
              </router-link>
              <router-link to="/rankings" class="dropdown-item" @click="closeUserMenu">
                <span class="dropdown-icon">🏆</span>
                My Rankings
              </router-link>
              <router-link to="/share" class="dropdown-item" @click="closeUserMenu">
                <span class="dropdown-icon">📤</span>
                My Posts
              </router-link>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout-btn" @click="handleLogout">
                <span class="dropdown-icon">🚪</span>
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <!-- Mobile Menu Button -->
      <button class="mobile-menu-btn" @click="toggleMobileMenu" aria-label="Toggle mobile menu">
        <span class="hamburger-line" :class="{ 'open': isMobileMenuOpen }"></span>
        <span class="hamburger-line" :class="{ 'open': isMobileMenuOpen }"></span>
        <span class="hamburger-line" :class="{ 'open': isMobileMenuOpen }"></span>
      </button>
    </header>

    <!-- Mobile Navigation Overlay -->
    <div class="mobile-nav-overlay" :class="{ 'open': isMobileMenuOpen }" @click="closeMobileMenu">
      <nav class="mobile-nav" @click.stop>
        <router-link to="/" class="mobile-nav-link" @click="closeMobileMenu">
          <span class="nav-icon">🏠</span>
          Home
        </router-link>
        <router-link to="/search" class="mobile-nav-link" @click="closeMobileMenu">
          <span class="nav-icon">🔍</span>
          Search
        </router-link>
        <router-link to="/rankings" class="mobile-nav-link" @click="closeMobileMenu">
          <span class="nav-icon">🏆</span>
          Rankings
        </router-link>
        <router-link to="/profile" class="mobile-nav-link" @click="closeMobileMenu">
          <span class="nav-icon">👤</span>
          Profile
        </router-link>
        <router-link to="/share" class="mobile-nav-link" @click="closeMobileMenu">
          <span class="nav-icon">📤</span>
          Share
        </router-link>
        
        <!-- Mobile Auth Navigation -->
        <div v-if="!isAuthenticated" class="mobile-auth-nav">
          <router-link to="/login" class="mobile-nav-link auth-link" @click="closeMobileMenu">
            <span class="nav-icon">🔐</span>
            Sign In
          </router-link>
        </div>
        <div v-else class="mobile-user-nav">
          <div class="mobile-user-info">
            <span class="mobile-user-avatar">{{ userAvatar }}</span>
            <span class="mobile-user-name">{{ userDisplayName }}</span>
          </div>
          <button class="mobile-logout-btn" @click="handleLogout">
            <span class="nav-icon">🚪</span>
            Sign Out
          </button>
        </div>
      </nav>
    </div>

    <main class="content">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-section">
          <h3 class="footer-title">BELP</h3>
          <p class="footer-description">
            Discover amazing restaurants with AI-powered recommendations and community insights.
          </p>
        </div>
        <div class="footer-section">
          <h4 class="footer-subtitle">Quick Links</h4>
          <router-link to="/" class="footer-link">Home</router-link>
          <router-link to="/search" class="footer-link">Search</router-link>
          <router-link to="/rankings" class="footer-link">Rankings</router-link>
          <router-link to="/profile" class="footer-link">Profile</router-link>
          <router-link to="/share" class="footer-link">Share</router-link>
        </div>
        <div class="footer-section">
          <h4 class="footer-subtitle">Support</h4>
          <a href="#" class="footer-link">Help Center</a>
          <a href="#" class="footer-link">Contact Us</a>
          <a href="#" class="footer-link">Privacy Policy</a>
          <a href="#" class="footer-link">Terms of Service</a>
        </div>
        <div class="footer-section">
          <h4 class="footer-subtitle">Connect</h4>
          <div class="social-links">
            <a href="#" class="social-link" aria-label="Twitter">🐦</a>
            <a href="#" class="social-link" aria-label="Facebook">📘</a>
            <a href="#" class="social-link" aria-label="Instagram">📷</a>
            <a href="#" class="social-link" aria-label="LinkedIn">💼</a>
          </div>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2024 BELP. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style>
/* Reset and Base Styles */
* {
  box-sizing: border-box;
}

body {
  background: white;
  margin: 0;
  padding: 0;
  font-family: 'Arial', 'Helvetica', sans-serif;
  line-height: 1.6;
}

#app {
  min-height: 100vh;
}

.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Topbar Styles */
.topbar {
  position: sticky;
  top: 0;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid rgba(7, 69, 12, 0.15);
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  transition: transform 0.2s ease;
}

.brand-link:hover {
  transform: scale(1.05);
}

.logo {
  font-size: 1.6rem;
  animation: logoBounce 2s ease-in-out infinite;
}

@keyframes logoBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.brand-name {
  color: #07450C;
  font-weight: 800;
  letter-spacing: 0.5px;
  font-size: 1.4rem;
}

/* Desktop Navigation */
.desktop-nav {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: #07450C;
  text-decoration: none;
  font-weight: 600;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.2s ease;
  position: relative;
  display: inline-flex;
  align-items: center;
}

.nav-link:hover {
  background: rgba(7, 69, 12, 0.1);
  color: #0a5a0f;
}

.nav-link:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(7, 69, 12, 0.2);
}

.nav-link.router-link-active {
  background: #07450C;
  color: white;
  box-shadow: inset 0 -3px 0 0 rgba(255,255,255,0.0); /* reset */
}

/* Replace pseudo underline with inset shadow to avoid square artifacts */
.nav-link.router-link-active {
  box-shadow: inset 0 -3px 0 0 #07450C;
}

/* Auth Navigation */
.auth-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.auth-link {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  border: 2px solid transparent;
}

.auth-link:hover {
  background: linear-gradient(135deg, #0a5a0f, #07450C);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(7, 69, 12, 0.3);
}

/* User Navigation */
.user-nav {
  display: flex;
  align-items: center;
}

.user-menu {
  position: relative;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #07450C;
  font-weight: 600;
}

.user-btn:hover {
  background: rgba(7, 69, 12, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: bold;
}

.user-name {
  font-size: 0.9rem;
}

.dropdown-arrow {
  font-size: 0.7rem;
  transition: transform 0.2s ease;
}

.user-menu:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* User Dropdown */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(7, 69, 12, 0.1);
  min-width: 200px;
  z-index: 1001;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s ease;
}

.user-menu:hover .user-dropdown {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #07450C;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
}

.dropdown-item:hover {
  background: rgba(7, 69, 12, 0.05);
}

.dropdown-item:first-child {
  border-radius: 12px 12px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 12px 12px;
}

.dropdown-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

.dropdown-divider {
  height: 1px;
  background: rgba(7, 69, 12, 0.1);
  margin: 0.5rem 0;
}

.logout-btn {
  color: #dc2626;
}

.logout-btn:hover {
  background: rgba(220, 38, 38, 0.05);
}

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  flex-direction: column;
  justify-content: space-around;
  width: 30px;
  height: 30px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 1001;
}

.hamburger-line {
  width: 100%;
  height: 3px;
  background: #07450C;
  border-radius: 2px;
  transition: all 0.3s ease;
  transform-origin: center;
}

.hamburger-line.open:nth-child(1) {
  transform: rotate(45deg) translate(6px, 6px);
}

.hamburger-line.open:nth-child(2) {
  opacity: 0;
}

.hamburger-line.open:nth-child(3) {
  transform: rotate(-45deg) translate(6px, -6px);
}

/* Mobile Navigation */
.mobile-nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-nav-overlay.open {
  opacity: 1;
  visibility: visible;
}

.mobile-nav {
  position: fixed;
  top: 0;
  right: -300px;
  width: 300px;
  height: 100%;
  background: white;
  padding: 5rem 2rem 2rem;
  box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
  transition: right 0.3s ease;
  z-index: 1000;
}

.mobile-nav-overlay.open .mobile-nav {
  right: 0;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  color: #07450C;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  border-bottom: 1px solid rgba(7, 69, 12, 0.1);
  transition: all 0.2s ease;
}

.mobile-nav-link:hover {
  background: rgba(7, 69, 12, 0.05);
  padding-left: 1rem;
}

.mobile-nav-link.router-link-active {
  background: rgba(7, 69, 12, 0.1);
  color: #0a5a0f;
  border-left: 4px solid #07450C;
  padding-left: 1rem;
}

.nav-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

/* Mobile Auth Navigation */
.mobile-auth-nav {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid rgba(7, 69, 12, 0.1);
}

.mobile-user-nav {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid rgba(7, 69, 12, 0.1);
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  margin-bottom: 1rem;
}

.mobile-user-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: bold;
}

.mobile-user-name {
  font-weight: 600;
  color: #07450C;
}

.mobile-logout-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  padding: 1rem 0;
  background: none;
  border: none;
  color: #dc2626;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.mobile-logout-btn:hover {
  background: rgba(220, 38, 38, 0.05);
}

/* Content */
.content {
  flex: 1;
  display: block;
}

/* Footer */
.footer {
  background: linear-gradient(135deg, #07450C, #0a5a0f);
  color: white;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.footer-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 0 1rem 0;
}

.footer-subtitle {
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0 0 1rem 0;
}

.footer-description {
  margin: 0;
  opacity: 0.9;
  line-height: 1.6;
}

.footer-link {
  display: block;
  color: white;
  text-decoration: none;
  padding: 0.5rem 0;
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.footer-link:hover {
  opacity: 1;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  display: inline-block;
  font-size: 1.5rem;
  transition: transform 0.2s ease;
}

.social-link:hover {
  transform: scale(1.2);
}

.footer-bottom {
  text-align: center;
  padding: 1.5rem 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0.8;
}

/* Responsive Design */
@media (max-width: 768px) {
  .topbar {
    padding: 0.75rem 1rem;
  }
  
  .desktop-nav {
    display: none;
  }
  
  .mobile-menu-btn {
    display: flex;
  }
  
  .brand-name {
    font-size: 1.2rem;
  }
  
  .logo {
    font-size: 1.4rem;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 2rem 1rem 1rem;
  }
  
  .social-links {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .topbar {
    padding: 0.5rem 1rem;
  }
  
  .brand-name {
    font-size: 1.1rem;
  }
  
  .logo {
    font-size: 1.2rem;
  }
  
  .mobile-nav {
    width: 100%;
    right: -100%;
  }
  
  .footer-content {
    padding: 1.5rem 1rem 1rem;
  }
  
  .footer-bottom {
    padding: 1rem;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  body {
    background: #1a1a1a;
    color: #ffffff;
  }
  
  .topbar {
    background: #2d2d2d;
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .mobile-nav {
    background: #2d2d2d;
  }
  
  .hamburger-line {
    background: #ffffff;
  }
  
  .user-dropdown {
    background: #2d2d2d;
    border-color: rgba(255, 255, 255, 0.1);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .nav-link {
    border: 2px solid transparent;
  }
  
  .nav-link:hover {
    border-color: #07450C;
  }
  
  .nav-link.router-link-active {
    border-color: #ffffff;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .logo {
    animation: none;
  }
  
  .nav-link,
  .mobile-nav-link,
  .social-link {
    transition: none;
  }
  
  .hamburger-line {
    transition: none;
  }
  
  .mobile-nav-overlay,
  .mobile-nav {
    transition: none;
  }
  
  .user-dropdown {
    transition: none;
  }
  
  .dropdown-arrow {
    transition: none;
  }
}
</style>
