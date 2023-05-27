<script setup>
// import { getRequest } from "axios"
// import  type {AxiosInstance} from 'axios'
// import { useAxios } from '@/plugins/axios'
import { useApiFetch } from '@/plugins/fetch'
// import { ref } from 'vue'

// const axiosInstance = AxiosInstance()

// const data = ref(null)
// const error = ref(null)
const { data, error, get } = useApiFetch()
// const settings = {
//     method: "GET",
//     mode: "cors",
//     headers: {
//         "Access-Control-Allow-Origin": "*",
//     },
// }
// this.axios.get('/solarpark/')
//   .then(response => {
//     data.value = response.data
//   })
//   .catch(err => {
//     error.value = err.message
//   })
get('/solarpark/')
</script>

<template>
    <div class="container mx-auto bg-gray-200 rounded-xl shadow border p-8 m-10">
     <p class="text-3xl text-gray-700 font-bold mb-5">
       Welcome!
     </p>
     <p class="text-gray-500 text-lg">
       Vue and Tailwind CSS in action!
     </p>
  </div>
    <div>
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>size_in_sq_m</th>
                    <th>peak_power</th>
                    <th>first_detection</th>
                    <th>last_detection</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="item in data" :key="item.id">
                    <td>{{ item.id }}</td>
                    <td>{{ item.size_in_sq_m }}</td>
                    <td>{{ item.peak_power}}</td>
                    <td>{{ item.first_detection}}</td>
                    <td>{{ item.last_detection }}</td>
                </tr>
            </tbody>
        </table>
        <div v-if="error">{{ error }}</div>
        <div v-else>Loading...</div>
    </div>
</template>

<style>
@media (min-width: 1024px) {
    .about {
        min-height: 100vh;
        display: flex;
        align-items: center;
    }
}
</style>