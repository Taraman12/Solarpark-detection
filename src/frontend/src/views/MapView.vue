<script setup>
/* eslint-disable no-undef */
import { useApiFetch } from '@/plugins/fetch'

import { Loader } from '@googlemaps/js-api-loader'


const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const { data, error, get } = useApiFetch()

get('/solarpark/')

//* Google Map instances
let map
let polygons = []
const loader = new Loader({
    apiKey: GOOGLE_MAPS_API_KEY,
    version: 'weekly',
    libraries: ['places']
})
const mapOptions = {
    center: {
        lat: 0,
        lng: 0
    },
    zoom: 4,
    // mapTypeId: "satellite",
};

// Promise
loader
    .load()
    .then((google) => {
        new google.maps.Map(document.getElementById("map"), mapOptions);
    })
    .catch(e => {
        console.log(e)
        // do something
    });

// fetch("http://localhost:8000/api/v1/solarpark/")
//   .then((res) => res.json())
//   .then((json) => (data.value = json))
//   .then(data => console.log(data))
//   .catch((err) => (error.value = err))


</script>

<template>
    <div id="map" class="map"></div>
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
                    <td>{{ item.peak_power }}</td>
                    <td>{{ item.first_detection }}</td>
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

#map {
    height: 400px;
    margin: 0px;
    padding: 0px;
}

#map img {
    max-width: none;
}
</style>