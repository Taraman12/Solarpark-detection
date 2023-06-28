<script setup>
import { ref, computed, onMounted } from 'vue'
import { mdiArrowUpBold } from '@mdi/js';
import { useApiFetch } from '@/plugins/fetch'
import Icon from '@/components/IconCanvas.vue'

const { get, post, filePost } = useApiFetch()
async function fetchData(id) {
  try {
    const response = await get(`/solarpark/${id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}

const dataTable = ref(null)
const totaldata = ref(null)
const noneItem = ref(null)
const noneItemCount = ref(null)
const validItemCount = ref(null)
const newestDate = ref(null)
const oldestDate = ref(null)

async function fetchKpis() {
  dataTable.value = await fetchData("");
  totaldata.value = dataTable.value.length;
  noneItem.value = dataTable.value.find(item => item.is_valid === "None");
  noneItemCount.value = dataTable.value.filter(item => item.is_valid === "None").length;
  validItemCount.value = dataTable.value.filter(item => item.is_valid === "valid").length;
  newestDate.value = dataTable.value.reduce((prev, current) => (prev.date > current.date) ? prev : current).date_of_data
  oldestDate.value = dataTable.value.reduce((prev, current) => (prev.date < current.date) ? prev : current).date_of_data
}

onMounted(async () => {

  await fetchKpis();
  // newestDate.value = dataTable.value.reduce((prev, current) => (prev.date > current.date) ? prev : current)
});


const file = ref(null);
async function downloadGeoJSON() {
  const response = await get('/solarpark/download/as-geojson')
  const filename = response.headers.get('Content-Disposition') ? response.headers.get('Content-Disposition').split('filename=')[1] : 'solar_parks.geojson';
  response.blob().then(blob => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  });
}

const uploadFile = (event) => {
  file.value = event.target.files[0];
};

const submitFile = async () => {
  let formData = new FormData();
  formData.append('file', file.value);
  formData.append('fileName', file.value.name);
  formData.forEach(el => console.log(el))
  try {
    const endpoint = '/solarpark/upload/as-geojson';
    const response = await filePost(endpoint, formData)
    console.log(response);
    fetchKpis();
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="grid gap-4 justify-center mt-4">
    <div class="border-2 border-neutral-500 rounded">
      <table>
        <tr>
          <td>Total solar parks in dataset:</td>
          <td>{{ totaldata }}</td>
        </tr>
        <tr>
          <td>Items Unclassified:</td>
          <td>{{ noneItemCount }}</td>
        </tr>
        <tr>
          <td>Valid solar parks:</td>
          <td>{{ validItemCount }}</td>
        </tr>
        <tr>
          <td>Newest data:</td>
          <td>{{ newestDate }}</td>
        </tr>
        <tr>
          <td>Oldest data:</td>
          <td>{{ newestDate }}</td>
        </tr>
      </table>
    </div>
    <div class="justify-end">
      <button @click="downloadGeoJSON"
        class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center">
        <svg class="fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
          <path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z" />
        </svg>
        <span>GeoJSON</span>
      </button>
    </div>

    <div>
      <input ref="file" type="file" @change="uploadFile" />
      <button @click="submitFile"
        class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center">
        <svg class="fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
          <path fill-rule="evenodd"
            d="M8 10a.5.5 0 0 0 .5-.5V3.707l2.146 2.147a.5.5 0 0 0 .708-.708l-3-3a.5.5 0 0 0-.708 0l-3 3a.5.5 0 1 0 .708.708L7.5 3.707V9.5a.5.5 0 0 0 .5.5zm-7 2.5a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 0 1h-13a.5.5 0 0 1-.5-.5z" />
        </svg>
        <span>Upload</span>
      </button>
    </div>

  </div>
</template>
