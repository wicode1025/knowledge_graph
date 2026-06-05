import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initStore } from './api/mock/store.js'

const app = createApp(App)
app.use(router)
app.mount('#app')

// 预加载种子数据
initStore().catch(e => console.warn('[app] Store init failed:', e))

