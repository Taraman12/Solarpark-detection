import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { useStyleStore } from "@/stores/style.js";
import { darkModeKey, styleKey } from "@/config.js";
// import { provideAxios } from './plugins/axios'
// import axios from './plugins/axios'

import App from './App.vue'
import router from './router'

import './assets/main.css'

/* Init Pinia */
const pinia = createPinia();



const styleStore = useStyleStore(pinia);


/* App style */
styleStore.setStyle(localStorage[styleKey] ?? "basic");

// const app = createApp(App)
// app.config.globalProperties.axios=axios
// provideAxios({
//     baseUrl: 'https://192.168.178.21:8000/api/v1',
//   })

// app.use(createPinia())
// app.use(router)
// app.use(axios)
// app.use(axios, {
//     baseUrl: 'https://192.168.178.21:8000/api/v1',
// })
// app.mount('#app')

/* Dark mode */
if (
    (!localStorage[darkModeKey] &&
        window.matchMedia("(prefers-color-scheme: dark)").matches) ||
    localStorage[darkModeKey] === "1"
) {
    styleStore.setDarkMode(true);
}

/* Create Vue app */
createApp(App).use(router).use(pinia).mount("#app");
