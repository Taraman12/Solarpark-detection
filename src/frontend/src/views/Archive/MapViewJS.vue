<script setup>
/* eslint-disable no-undef */
import { useApiFetch } from '@/plugins/fetch'
import { GOOGLE_MAPS_API_KEY } from '@/config.js'
import { Loader } from '@googlemaps/js-api-loader'

const { data, error, get } = useApiFetch()

get('/solarpark/')

// Initialize and add the map
function initMap() {
    // The location of Uluru
    const uluru = { lat: -25.344, lng: 131.031 };
    // The map, centered at Uluru
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 4,
        center: uluru,
    });
    // The marker, positioned at Uluru
    const marker = new google.maps.Marker({
        position: uluru,
        map: map,
    });
}

window.initMap = initMap;
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

    margin: 10;
    padding: 10;
}

#map img {
    max-width: none;
}
</style>