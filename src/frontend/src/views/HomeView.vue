<script setup lang="ts">
import TheWelcome from '../components/TheWelcome.vue'
</script>

<template>
  <main class="mx-auto max-w-2xl mt-4">
    <h1 class="text-2xl">
      Continues Solar Park Detection
    </h1>
    <h2>Welcome</h2>
    <h3>
      On this website you will find information about my master’s thesis titled “Continues Solar Park
      Detection”.
    </h3>
    In this project, I used a neural network to continuously detect solar parks from Sentinel-2 data. On the
    website, you can view the results and interactively explore them on a map. You also have the option to validate the
    data.

    <h4 class="text-xl mt-4">Pipeline</h4>
    <img src="../assets/Final_Pipeline.svg" alt="pipeline" class="w-full" />
    <h4 class="text-xl mt-4">Docs for the API:</h4>
    <div>
      <a class="text-blue-500" href="http://3.66.239.204:8000/docs">API Docs</a>
    </div>

    <h4 class="text-xl mt-4">Github Repository:</h4>
    <div>
      <a class="text-blue-500" href="https://github.com/Taraman12/Solarpark-detection">solar-park-detection</a>
    </div>
  </main>
</template>
