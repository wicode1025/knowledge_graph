import { createRouter, createWebHashHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Home from '../views/Home.vue'
import Profile from '../views/Profile.vue'
import Devices from '../views/Devices.vue'
import Billing from '../views/Billing.vue'
import Repair from '../views/Repair.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { hideNav: true } },
  { path: '/register', name: 'Register', component: Register, meta: { hideNav: true } },
  { path: '/', name: 'Home', component: Home },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/devices', name: 'Devices', component: Devices },
  { path: '/billing', name: 'Billing', component: Billing },
  { path: '/repair', name: 'Repair', component: Repair },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/kg', name: 'AdminKG', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/data', name: 'AdminData', component: AdminDashboard, meta: { role: 'admin' } },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') || 'user'
  if (to.path !== '/login' && to.path !== '/register' && !token) next('/login')
  else if ((to.path === '/login' || to.path === '/register') && token) next('/')
  else if (to.meta.role === 'admin' && role !== 'admin') next('/')
  else next()
})

export default router
