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

fetch("http://localhost:8000/api/v1/solarpark/", settings)
.then((res) => res.json())
.then((json) => (data.value = json))
.then(data => console.log(data))
.catch((err) => (error.value = err))
</script>

<template>
    <div class="about">
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