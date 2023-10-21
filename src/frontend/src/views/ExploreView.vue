<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from 'vue'
import { useApiFetch } from '@/plugins/fetch'

import { Loader } from '@googlemaps/js-api-loader'
import { MarkerClusterer } from "@googlemaps/markerclusterer";


const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const { data, error, get } = useApiFetch()



//* Google Map instances
let mapDiv = ref(null);
let map  // map object
let polygons = ref([]);
let locations = [];
let markers = [];

const polygonOptions = {
    strokeColor: "#FF0000",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#FF0000",
    fillOpacity: 0.00,
};

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

loader
    .load()
    .then((google) => {
        new google.maps.Map(document.getElementById("map"), mapOptions);
    })
    .catch(e => {
        console.log(e)
        // do something
    });

// async function addPolygons() {
//     if (Array.isArray(data.value)) {
//         // Loop through the data and add a polygon for each solar park
//         data.value.forEach(park => {
//             const coordinates = park.lat.map((lat, index) => {
//                 return { lat: lat, lng: park.lon[index] }
//             })
//             const polygon = new google.maps.Polygon({
//                 paths: coordinates,
//                 ...polygonOptions,
//                 map: map.value
//             });
//             polygons.value.push(polygon);
//         });
//     } else {
//         // Add a polygon for the single solar park
//         const park = data.value;
//         const coordinates = park.lat.map((lat, index) => {
//             return { lat: lat, lng: park.lon[index] }
//         })
//         const polygon = new google.maps.Polygon({
//             paths: coordinates,
//             ...polygonOptions,
//             map: map.value
//         });
//         polygons.value.push(polygon);
//     }
// }
// async function dataToCoords(data) {
//     let coordinates = data.value.forEach(park => {
//         let coordinates = park.lat.map((lat, index) => {
//             return { lat: lat, lng: park.lon[index] }
//         })
//         return coordinates
//         // locations.push(coordinates)
//     })
//     // coordinates = coordinates.slice(0, 1);
//     console.log('coordinates ' + coordinates )
//     return coordinates
// }
// async function addMarkerCluster(data) {
//     const locations = await dataToCoords(data)
//         // const infoWindow = new google.maps.InfoWindow({
//         //     content: "",
//         //     disableAutoPan: true,
//         // });

//         // const labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
//         const markers = locations.map((position, i) => {
//             // const label = labels[i % labels.length];
//             const marker = new google.maps.Marker({
//                 position,
//             });
//             // markers can only be keyboard focusable when they have click listeners
//             // open info window when marker is clicked
//             marker.addListener("click", () => {
//                 // infoWindow.setContent(label);
//                 infoWindow.open(map, marker);
//             });
//             return marker;
//         });
//         console.log('markers' + markers)
//         // new MarkerClusterer({ markers, map });;
//         // console.log(markerCluster)
//     }
async function addMarkerCluster() {
    // https://github.com/googlemaps/js-markerclusterer
    data.value.forEach(park => {
        const coordinates = park.lat.map((lat, index) => {
            return { lat: lat, lng: park.lon[index] }
        })
        const infoWindow = new google.maps.InfoWindow({
            content: "",
            disableAutoPan: true,
        });
        const locations = coordinates.slice(0, 1);

        // const labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
        const markers = locations.map((position, i) => {
            // const label = labels[i % labels.length];
            const marker = new google.maps.Marker({
                position,
            });
            // markers can only be keyboard focusable when they have click listeners
            // open info window when marker is clicked
            marker.addListener("click", () => {
                // infoWindow.setContent(label);
                infoWindow.open(map, marker);
            });
            // markers.push(marker)
            return marker;
        });
        console.log('markers' + markers)
        new MarkerClusterer({ markers, map });;
        // return markers
        // console.log(markerCluster)
    });
}

onMounted(async () => {
    const response = await get('/solarpark/')
    const json = await response.json()
    data.value = json
    console.log(data.value)
    await loader.load();
    map = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        center: { lat: 49.783, lng: 9.93 },
        zoom: 7,
        // mapTypeId: 'satellite'
    });
    // await addPolygons()
    await addMarkerCluster(data)
})
</script>

<template>
    <div class="h-96  mt-4">
        <div ref="mapDiv" class="h-full"></div>
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
