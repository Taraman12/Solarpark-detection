<script setup>
/* eslint-disable no-undef */
import { Loader } from '@googlemaps/js-api-loader'
import { ref, watch, onMounted, } from 'vue'

// https://stackoverflow.com/questions/76076055/how-to-delete-google-maps-markers-in-vue-3-composition-api-js-gmaps-api
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

// to delete polygons later
// import {toRaw} from 'vue';
// this.markers.map((marker) => toRaw(marker).setMap(null))

//* Google Map instances
const loader = new Loader({
    apiKey: GOOGLE_MAPS_API_KEY,
    version: 'weekly',
    libraries: ['places']
})
const mapDiv = ref(null); // define divref to populate the map
let map = ref(null); // map object

const data = ref(null)
const error = ref(null)

let polygons = ref([]);
const polygonOptions = {
    strokeColor: "#FF0000",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#FF0000",
    fillOpacity: 0.00,
};


async function fetchData() {
    try {
        const response = await fetch("http://localhost:8000/api/v1/solarpark/");
        const data = await response.json();
        console.log(data);
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

onMounted(async () => { //create map
    data.value = await fetchData();

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
    <div style="overflow-y: hidden">
        <div ref="mapDiv" style="width: 100%; height: 80vh"></div>
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
    height: 600px;
    margin: auto;
    padding: 0px;
}

#map img {
    max-width: none;
}
</style>
