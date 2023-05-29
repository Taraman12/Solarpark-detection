import axios from 'axios'


const axiosClient = axios.create({
    baseURL: 'https://localhost:8000/api/v1',
    timeout: 1000,
    withCredentials: false,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json'
    }
});

// Normal CRUD methods for fetching data
// export async function getRequest(URL) {
//     return axiosClient.get(URL)
//         .then(response => response.data)
//         .catch(error => console.error(error))
// }

export default axiosClient

// https://blog.logrocket.com/how-use-axios-vue-js/
// import axios from 'axios'
// import type {App} from 'vue'
// const axios = require('axios').default;
// interface AxiosOptions {
//     baseUrl?: string
//     token?: string
// }

// export default {
//     install: (app: App, options: AxiosOptions) => {
//         app.config.globalProperties.$axios = axios.create({
//             baseURL: options.baseUrl,
//             headers: {
//                 Authorization: options.token ? `Bearer ${options.token}` : '',
//             }
//         })
//     }
// }

// import axios from 'axios'
// import { inject, provide } from 'vue'

// interface AxiosOptions {
//     baseUrl?: string
//     token?: string
// }

// const axiosInstance = axios.create({
//     baseURL: 'http://your-api-url.com',
//     timeout: 5000,
//     headers: {
//         'Content-Type': 'application/json'
//     }
// })

// export const provideAxios = (options: AxiosOptions) => {
//     if (options.baseUrl) {
//         axiosInstance.defaults.baseURL = options.baseUrl
//     }

//     if (options.token) {
//         axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${options.token}`
//     }

//     provide('axios', axiosInstance)
// }

// export const useAxios = () => {
//     const axiosInstance = inject<ReturnType<typeof axios.create>>('axios')

//     if (!axiosInstance) {
//         throw new Error('Axios instance not found')
//     }

//     return axiosInstance
// }
