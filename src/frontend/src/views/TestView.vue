<script setup>
import { ref } from 'vue'

const data = ref(null)
const error = ref(null)

const options = {
  method: "GET",
  mode: "cors",
  headers: {
    Accept: "application/json",
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
  },
}

fetch("http://localhost:5000/", options)
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