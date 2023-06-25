<script setup>
import { ref } from 'vue'

const data = ref(null)
const error = ref(null)

const settings = {
  method: "GET",
  mode: "cors",
  headers: {
    "Access-Control-Allow-Origin": "*",
  },
}

fetch("http://localhost:8000/api/v1/solarpark/")
  .then((res) => res.json())
  .then((json) => (data.value = json))
  .then(data => console.log(data))
  .catch((err) => (error.value = err))

function downloadGeoJSON() {
  fetch('http://localhost:8000/api/v1/solarpark/download/as-geojson')
    .then(response => {
      // Dateinamen aus dem Content-Disposition-Header extrahieren oder Standardnamen verwenden
      const filename = response.headers.get('Content-Disposition') ? response.headers.get('Content-Disposition').split('filename=')[1] : 'solar_parks.geojson';
      // Datei herunterladen
      response.blob().then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
    });
}

</script>

<template>
  <div class="about">
    <button @click="downloadGeoJSON"
      class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center">
      <svg class="fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
        <path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z" />
      </svg>
      <span>GeoJSON</span>
    </button>

    <h1>This is my first test page</h1>
    <div v-if="error">Oops! Error encountered: {{ error.message }}</div>
    <div v-else-if="data">
      Data loaded:
      <pre>{{ data.message }}</pre>
    </div>
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