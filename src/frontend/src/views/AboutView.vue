<script setup>
import { ref, onMounted } from 'vue';

const models = ref(null);
const error = ref(null);
const isLoading = ref(true);
const options = {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
};
async function startInstance() {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/instance/start/ml-serve?instance_type=t3.medium`, options);
    const data = response.json();
    console.log("data " + data);
    return data;
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
}

</script>

<template>
  <div>
    <button @click="startInstance">Start Instance</button>
  </div>
  <div class="about">
    <h1>This is an about page</h1>
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
