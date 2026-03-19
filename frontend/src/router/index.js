import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Devices from '../views/Devices.vue'
import KnowledgeGraph from '../views/KnowledgeGraph.vue'
import Clustering from '../views/Clustering.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/devices', name: 'Devices', component: Devices },
  { path: '/graph', name: 'KnowledgeGraph', component: KnowledgeGraph },
  { path: '/clustering', name: 'Clustering', component: Clustering },
  { path: '/profile', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
