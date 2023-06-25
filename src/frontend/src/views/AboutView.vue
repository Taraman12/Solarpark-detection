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
    <p>
      See the following source for the 1,6 MW peak per 1 acres:
      <a
        href="https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Energie/Unternehmen_Institutionen/ErneuerbareEnergien/PV-Freiflaechenanlagen/Bericht_Flaecheninanspruchnahme_2016.pdf?__blob=publicationFile&v=2#:~:text=Die%20bereits%20im%20Rahmen%20der,Ackerland%20in%20benachteiligten%20Gebieten%20errichtet.">Bundesnetzagentur
        Report Dec. 2016</a>
    </p>
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
