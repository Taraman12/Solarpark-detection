<script setup>
import { ref, onMounted } from 'vue';


const models = ref(null);
const error = ref(null);
const isLoading = ref(true);

// const headers = {
//     'Content-Type': 'application/json'
// };

const options = {
    headers: {
        'Content-Type': 'application/json'
    }
};
// fetch('http://localhost:8081/models', options)
//     .then(response => {
//         if (response.headers.get('Content-Type').includes('application/json')) {
//             return response.json();
//         } else {
//             throw new TypeError('Response was not JSON');
//         }
//     })
//     .then(data => console.log(data.models[0].modelName))
//     .catch(error => console.error(error));

// fetch('http://localhost:8000/api/v1/ml-server', options)
//     .then(response => {
//         console.log(response.headers);
//         return response.json()})
//     .then(data => console.log(data.models[0].modelName))
//     .catch(error => console.error(error));

async function fetchModel() {
    try {
        const response = await fetch(`http://localhost:8000/api/v1/ml-server`, options);
        const data = response.json();
        console.log("data " + data);
        return data;
    } catch (error) {
        console.error(error);
    } finally {
        isLoading.value = false;
    }
}
onMounted(async () => { //create map
    models.value = await fetchModel();
    console.log("models " + models.value);
});

</script>


<template>
    <div>{{ models }}</div>
    <!-- <table class="table">
      <thead>
        <tr>
          <th>Model Name</th>
          <th>Model URL</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="model in models" :key="model.modelName">
          <td>{{ model.modelName }}</td>
          <td>{{ model.modelUrl }}</td>
        </tr>
      </tbody>
    </table> -->
    <!-- <div>
        <li v-for="model in models" :key="model.modelName">
            <a>{{ model.modelName }}</a>
        </li>
    </div> -->
    <!-- <div>
        <div v-if="isLoading">Loading...</div>
        <div v-else-if="error">Error: {{ error }}</div>
        <div v-else>
            <h2>Models:</h2>
            <table class="table">
                <ul>
                    <li v-for="model in models" :key="model.modelName">
                        <a :href="model.modelUrl">{{ model.modelName }}</a>
                    </li>
                </ul>
            </table>
        </div>
    </div> -->
</template>