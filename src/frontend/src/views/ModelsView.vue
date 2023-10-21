<script setup>
import { ref, onMounted } from 'vue';
import { useApiFetch } from '@/plugins/fetch';


const models = ref(null);
const error = ref(null);
const isLoading = ref(true);
const modelsDetail = ref(null);

const { get, post } = useApiFetch()
async function fetchData(model) {
    try {
        const response = await get(`/models/${model}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}


async function registerModel(model) {
    try {
        console.log(model);
        const response = await post(`/models/${model}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}

async function registerTestModel() {
    try {
        const response = await post(`/models/`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}
const modelInput = ref("");

onMounted(async () => { //create map
    models.value = await fetchData("");
    modelsDetail.value = await fetchData("solar-park-detection");
    console.log("models " + models.value);
});

</script>


<template>
    <div class="grid gap-4 justify-center mt-4">
        <button @click="registerTestModel()"
            class="bg-green-500 hover:bg-green-600 text-gray-800 dark:bg-green-700 dark:hover:bg-green-800 text-center font-bold py-2 px-4 rounded">
            register test model
        </button>
        <input v-model="modelInput" placeholder="Name or URL" class="dark:bg-neutral-300 text-black border" />
        <button @click="registerModel(modelInput)"
            class="bg-green-500 hover:bg-green-600 text-gray-800 dark:bg-green-700 dark:hover:bg-green-800 text-center font-bold py-2 px-4 rounded">
            register model model by Name
        </button>
        <button @click="registerModel(`as-url/${modelInput}`)"
            class="bg-green-500 hover:bg-green-600 text-gray-800 dark:bg-green-700 dark:hover:bg-green-800 text-center font-bold py-2 px-4 rounded">
            register model model by url
        </button>
        <table>
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
        </table>
        <div>
            <div v-for="models in modelsDetail" :key="models.modelName">
                <table>
                    <tr>
                        <td>Model Name</td>
                        <td>{{ models.modelName }}</td>
                    </tr>
                    <tr>
                        <td>Model Version</td>
                        <td>{{ models.modelVersion }}</td>
                    </tr>
                    <tr>
                        <td>Model URL</td>
                        <td>{{ models.modelUrl }}</td>
                    </tr>
                    <tr>
                        <td>Runtime</td>
                        <td>{{ models.runtime }}</td>
                    </tr>
                    <tr>
                        <td>Min Workers</td>
                        <td>{{ models.minWorkers }}</td>
                    </tr>
                    <tr>
                        <td>Max Workers</td>
                        <td>{{ models.maxWorkers }}</td>
                    </tr>
                    <tr>
                        <td>Batch Size</td>
                        <td>{{ models.batchSize }}</td>
                    </tr>
                    <tr>
                        <td>Max Batch Delay</td>
                        <td>{{ models.maxBatchDelay }}</td>
                    </tr>
                    <tr>
                        <td>Loaded At Startup</td>
                        <td>{{ models.loadedAtStartup }}</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
</template>
