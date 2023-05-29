import { createApp } from 'vue'
import { createPinia } from 'pinia'
// import { provideAxios } from './plugins/axios'
// import axios from './plugins/axios'

import App from './App.vue'
import router from './router'

import './assets/main.css'

const app = createApp(App)
// app.config.globalProperties.axios=axios
// provideAxios({
//     baseUrl: 'https://192.168.178.21:8000/api/v1',
//   })

app.use(createPinia())
app.use(router)
// app.use(axios)
// app.use(axios, {
//     baseUrl: 'https://192.168.178.21:8000/api/v1',
// })
app.mount('#app')
