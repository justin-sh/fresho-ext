// import './assets/main.css'

import Vue, { createApp } from 'vue'
import { createPinia } from 'pinia'

import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'

// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

// @ts-ignore
import App from './App.vue'
import router from './router'

Vue.use(BootstrapVue);
Vue.use(IconsPlugin);

const app = createApp(App)

app.use(createPinia())
app.use(router)
// @ts-ignore
// app.use(BootstrapVue)
// @ts-ignore
// app.use(IconsPlugin)

app.mount('#app')
