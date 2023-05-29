<script setup>
/* eslint-disable no-undef */
import { Loader } from '@googlemaps/js-api-loader'
import { ref, watch, onMounted, } from 'vue'
import { useApiFetch } from '@/plugins/fetch'

// https://stackoverflow.com/questions/76076055/how-to-delete-google-maps-markers-in-vue-3-composition-api-js-gmaps-api
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

// to delete polygons later
// import {toRaw} from 'vue';
// this.markers.map((marker) => toRaw(marker).setMap(null))
const { dataSinglePoly, errorSinglePoly, get, put } = useApiFetch()

//* Google Map instances
const loader = new Loader({
    apiKey: GOOGLE_MAPS_API_KEY,
    version: 'weekly',
    libraries: ['places']
})
const mapDiv = ref(null); // define divref to populate the map
let map = ref(null); // map object

const dataTable = ref(null)
const data = ref(null)
const error = ref(null)

let polygons = ref([]);
let polygon = ref(null);

const polygonOptions = {
    strokeColor: "#FF0000",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#FF0000",
    fillOpacity: 0.00,
};


// async function fetchData() {
//     try {
//         const response = await fetch("http://localhost:8000/api/v1/solarpark/");
//         const data = await response.json();
//         console.log(data);
//         return data;
//     } catch (error) {
//         console.error(error);
//     }
// }

async function fetchData(id) {
    try {
        const response = await fetch(`http://localhost:8000/api/v1/solarpark/${id}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}

async function addPolygons() {
    if (Array.isArray(data.value)) {
        // Loop through the data and add a polygon for each solar park
        data.value.forEach(park => {
            const coordinates = park.lat.map((lat, index) => {
                return { lat: lat, lng: park.lon[index] }
            })
            const polygon = new google.maps.Polygon({
                paths: coordinates,
                ...polygonOptions,
                map: map.value
            });
            polygons.value.push(polygon);
        });
    } else {
        // Add a polygon for the single solar park
        const park = data.value;
        const coordinates = park.lat.map((lat, index) => {
            return { lat: lat, lng: park.lon[index] }
        })
        const polygon = new google.maps.Polygon({
            paths: coordinates,
            ...polygonOptions,
            map: map.value
        });
        polygons.value.push(polygon);
    }
}
// async function addPolygon(park) {

//     const coordinates = park.lat.map((lat, index) => {
//         return { lat: lat, lng: park.lon[index] }
//     });
//     polygon.value = new google.maps.Polygon({
//         paths: coordinates,
//         strokeColor: "#FF0000",
//         strokeOpacity: 0.8,
//         strokeWeight: 2,
//         fillColor: "#FF0000",
//         fillOpacity: 0.00,
//         map: map.value
//     });
// }

async function handleRowClick(id) {
    // Do something with the selected row ID
    data.value = await fetchData(id);

    console.log("here: " + data.value.lat[0]);
    map.value = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        center: { lat: data.value.lat[0], lng: data.value.lon[0] },
        zoom: 7,
    })
    // removes the last added polygon
    polygons.value.pop(-1);
    await addPolygons()
    // get(`/solarpark/${id}`).then(park => {
    //     console.log("park " + park);
    //     if (polygon.value) {
    //         polygon.value.setMap(null);
    //     }
    //     addPolygon(park);
    // });
}

async function handleCheckboxClick(item) {
    try {
        // copy item object and update is_valid property
        const updatedItem = { ...item, is_valid: "True" };

        const response = await fetch(`http://localhost:8000/api/v1/solarpark/${item.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedItem)
        });
        console.log(response);
    } catch (error) {
        console.error(error);
    }
}

onMounted(async () => { //create map
    dataTable.value = await fetchData("");
    // ! Hardcoded for now
    data.value = await fetchData(4)
    await loader.load();
    map.value = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        center: { lat: 40, lng: -80 },
        zoom: 7,
    });
    await addPolygons();

});
</script>

<template>
    <div class="flex h-screen justify-between">
        <div class="w-2/5 h-full">
            <div style="overflow-y: hidden">
                <div ref="mapDiv" style="width: 100%; height: 50vh"></div>
            </div>
        </div>
        <div class="w-3/5 h-full overflow-y-auto">
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>size_in_sq_m</th>
                        <th>peak_power</th>
                        <th>first_detection</th>
                        <th>last_detection</th>
                        <th>Valid</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in dataTable" :key="item.id" @click="handleRowClick(item.id)">
                        <td>{{ item.id }}</td>
                        <td>{{ item.size_in_sq_m }}</td>
                        <td>{{ item.peak_power }}</td>
                        <td>{{ item.first_detection }}</td>
                        <td>{{ item.last_detection }}</td>
                        <td v-if="item.is_valid === 'None'">
                            <input type="checkbox" v-model="item.selected" @click="handleCheckboxClick(item)">
                        </td>
                        <td v-else-if="item.is_valid === 'True'">
                            <span class="text-green-500">Valid</span>
                        </td>
                        <td v-else-if="item.is_valid === 'False'">
                            <span class="text-red-500">Invalid</span>
                        </td>
                        <td v-else-if="item.is_valid === 'Unsure'">
                            <span class="text-yellow-500">Unsure</span>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div v-if="error">{{ error }}</div>
            <div v-else>Loading...</div>
        </div>
    </div>
</template>

<style>
/* #map {
    height: 600px;
    margin: auto;
    padding: 0px;
}

#map img {
    max-width: none;
} */
</style>
