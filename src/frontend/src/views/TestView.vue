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
    <div>
      <button @click="downloadGeoJSON">GeoJSON herunterladen</button>
    </div>
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