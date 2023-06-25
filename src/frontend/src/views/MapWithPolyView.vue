<script setup>
/* eslint-disable no-undef */
import { Loader } from '@googlemaps/js-api-loader'
import { ref, watch, onMounted, } from 'vue'
import { useApiFetch } from '@/plugins/fetch'
import FKButton from '@/components/FKButton.vue'
const { dataSinglePoly, errorSinglePoly, get, put } = useApiFetch()
const dataTable = ref(null)
const data = ref(null)
const error = ref(null)
const noneItem = ref(null)
const noneItemCount = ref(null)

async function fetchData(id) {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/solarpark/${id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}

// async function handleCheckboxClick(item) {
//     try {
//         // copy item object and update is_valid property
//         const updatedItem = { ...item, is_valid: "valid" };

//         const response = await fetch(`http://localhost:8000/api/v1/solarpark/${item.id}`, {
//             method: 'PUT',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(updatedItem)
//         });
//         console.log(response);
//     } catch (error) {
//         console.error(error);
//     }
// }
async function updateItem(id, value) {
  try {
    const item = await get(`/solarpark/${id}`);
    const updatedItem = { ...item, is_valid: value };
    await put(`/solarpark/${id}`, updatedItem);
    console.log(`Item ${id} updated to ${value}`);
    dataTable.value = await fetchData("");
    noneItem.value = dataTable.value.find(item => item.is_valid === "None");
    noneItemCount.value = dataTable.value.filter(item => item.is_valid === "None").length;
  } catch (error) {
    console.error(error);
  }
}

onMounted(async () => {
  dataTable.value = await fetchData("");
  noneItem.value = dataTable.value.find(item => item.is_valid === "None");
  noneItemCount.value = dataTable.value.filter(item => item.is_valid === "None").length;
});

watch(dataTable, (newVal) => {
  noneItem.value = newVal.find(item => item.is_valid === "None");
});
</script>

<template>
  <div class="grid grid-cols-4 mt-4">
    <div class="grid col-span-1 gap-4">
      <div class="border-2 border-neutral-500 rounded">
        <table>
          <tr>
            <td>Items to classify:</td>
            <td>{{ noneItemCount }}</td>
          </tr>
        </table>
      </div>
      <div v-if="noneItem">
        <div class="border-2 border-neutral-500 rounded">
          <table>
            <tr>
              <td>ID</td>
              <td>{{ noneItem.id }}</td>
            </tr>
            <tr>
              <td>Size in m²</td>
              <td>{{ noneItem.size_in_sq_m }}</td>
            </tr>
            <tr>
              <td>Est. Peak Power (MW)</td>
              <td>{{ noneItem.peak_power.toFixed(2) }}</td>
            </tr>
            <tr>
              <td>first_detection</td>
              <td>{{ noneItem.first_detection }}</td>
            </tr>
            <tr>
              <td>last_detection</td>
              <td>{{ noneItem.last_detection }}</td>
            </tr>
            <tr>
              <td>avg_confidence</td>
              <td>{{ noneItem.avg_confidence.toFixed(2) }}</td>
            </tr>
          </table>
        </div>
        <div class="grid grid-cols-2 gap-3 mt-4">
          <button @click="updateItem(noneItem.id, 'valid')"
            class="bg-green-500 hover:bg-green-600 text-gray-800 dark:bg-green-700 dark:hover:bg-green-800 text-center font-bold py-2 px-4 rounded">
            Valid
          </button>
          <button @click="updateItem(noneItem.id, 'non-valid')"
            class="bg-red-500 hover:bg-red-600 text-gray-800 dark:bg-red-700 dark:hover:bg-red-800 text-center font-bold py-2 px-4 rounded">
            Non-valid
          </button>
          <div class="grid col-span-2">
            <button @click="updateItem(noneItem.id, 'unsure')"
              class="bg-yellow-500 hover:bg-yellow-600 text-gray-800 dark:bg-yellow-700 dark:hover:bg-yellow-800 text-center font-bold py-2 px-4 rounded">
              Unsure/Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!-- ! Dont delete! -->
  <!-- <div class="h-full overflow-y-auto col-span-2">
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Size in m&sup2;</th>
          <th>Peak Power (MW)</th>
          <th>first_detection</th>
          <th>last_detection</th>
          <th>avg_confidence</th>
          <th>Valid</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in dataTable" :key="item.id" @click="handleRowClick(item.id)">
          <td>{{ item.id }}</td>
          <td>{{ item.size_in_sq_m }}</td>
          <td>{{ item.peak_power.toFixed(2) }}</td>
          <td>{{ item.first_detection }}</td>
          <td>{{ item.last_detection }}</td>
          <td>{{ item.avg_confidence.toFixed(2) }}</td>
          <td v-if="item.is_valid === 'None'">
            <input type="checkbox" v-model="item.selected" @click="handleCheckboxClick(item)">
          </td>
          <td v-else-if="item.is_valid === 'valid'">
            <span class="text-green-500">Valid</span>
          </td>
          <td v-else-if="item.is_valid === 'non-valid'">
            <span class="text-red-500">Invalid</span>
          </td>
          <td v-else-if="item.is_valid === 'unsure'">
            <span class="text-yellow-500">Unsure</span>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="error">{{ error }}</div>
    <div v-else>Loading...</div>
  </div> -->
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}

#map {
  height: 600px;
  margin: auto;
  padding: 0px;
}

#map img {
  max-width: none;
}
</style>
