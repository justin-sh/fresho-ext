// import './assets/main.css'

import {
    createApp,
} from 'vue'
import {createPinia} from 'pinia'
import {createBootstrap} from 'bootstrap-vue-next'

// Add the necessary CSS
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

// @ts-ignore
import App from './App.vue'
import router from './router'


const app = createApp(App)

app.use(createBootstrap())
app.use(createPinia())
app.use(router)

app.mount('#app')
