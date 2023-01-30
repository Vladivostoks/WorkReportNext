import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import Vue3Lottie from 'vue3-lottie'

import 'element-plus/dist/index.css'
import 'vue3-lottie/dist/style.css'
import './assets/css/main.css'

const app = createApp(App)

app.use(Vue3Lottie)
app.use(ElementPlus)
app.use(createPinia())
app.use(router)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

app.mount('#app')
