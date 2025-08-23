import { createRouter, createWebHistory } from 'vue-router'

import Home from '../components/Home.vue'
import YelpSearch from '../components/YelpSearch.vue'

const Profile = () => import('../views/Profile.vue')
const Share = () => import('../views/Share.vue')

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/search', name: 'Search', component: YelpSearch },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/share', name: 'Share', component: Share }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 