<script setup>
import { ref, onMounted } from 'vue';

const models = ref(null);
const isLoading = ref(true);
const headers = {
    'Content-Type': 'application/json'
};

const options = {
    method: 'GET',
    headers: headers,
    mode: 'no-cors'
};

async function fetchModel() {

    try {
        const response = await fetch(`http://localhost:8081/models`, options);
        const data = await response;
        console.log("data" +data.statusText);
        return data;
    } catch (error) {
        console.error(error);
    } finally {
        isLoading.value = false;
    }
}
onMounted(async () => { //create map
    models.value = await fetchModel();
});

</script>


<template>
    <div>
        <div v-if="isLoading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <h2>Models:</h2>
            <ul>
                <li v-for="model in models" :key="model.modelName">
                    <a :href="model.modelUrl">{{ model.modelName }}</a>
                </li>
            </ul>
        </div>
    </div>
</template>