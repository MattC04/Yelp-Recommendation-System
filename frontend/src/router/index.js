import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import YelpSearch from '../components/YelpSearch.vue'
import Profile from '../views/Profile.vue'
import Share from '../views/Share.vue'
import Rankings from '../views/Rankings.vue'
import Login from '../components/Login.vue'
import authService from '../services/authService.js'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/search', name: 'Search', component: YelpSearch },
  { path: '/rankings', name: 'Rankings', component: Rankings, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/share', name: 'Share', component: Share, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: Login }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Route guard for authentication
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authService.checkAuth()) {
    // Redirect to login if trying to access protected route
    next('/login')
  } else if (to.path === '/login' && authService.checkAuth()) {
    // Redirect to home if already logged in
    next('/')
  } else {
    next()
  }
})

export default router 