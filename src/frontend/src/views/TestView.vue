<script setup>
import { ref, computed } from 'vue'
import { useApiFetch } from '@/plugins/fetch'

const { get, post, filePost } = useApiFetch()

const data = ref(null)
const error = ref(null)

const settings = {
  method: "GET",
  mode: "cors",
  headers: {
    "Access-Control-Allow-Origin": "*",
  },
}

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

// function downloadGeoJSON() {
//   fetch('http://localhost:8000/api/v1/solarpark/download/as-geojson', settings)
//     .then(response => {
//       // Dateinamen aus dem Content-Disposition-Header extrahieren oder Standardnamen verwenden
//       const filename = response.headers.get('Content-Disposition') ? response.headers.get('Content-Disposition').split('filename=')[1] : 'solar_parks.geojson';
//       // Datei herunterladen
//       response.blob().then(blob => {
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement('a');
//         a.href = url;
//         a.download = filename;
//         document.body.appendChild(a);
//         a.click();
//         a.remove();
//       });
//     });
// }

// /** @param {Event} event */
// function handleSubmit(event) {
//   /** @type {HTMLFormElement} */
//   const form = event.currentTarget;
//   const url = new URL(form.action);
//   const formData = new FormData(form);
//   const searchParams = new URLSearchParams(formData);

//   /** @type {Parameters<fetch>[1]} */
//   const fetchOptions = {
//     method: form.method,
//   };

//   if (form.method.toLowerCase() === 'post') {
//     if (form.enctype === 'multipart/form-data') {
//       fetchOptions.body = formData;
//     } else {
//       fetchOptions.body = searchParams;
//     }
//   } else {
//     url.search = searchParams;
//   }

//   fetch(url, fetchOptions);

//   event.preventDefault();
// }
// let file = ref(null)
// const form = ref < HTMLFormElement > ();
function onFileChanged() {
  console.log('upload');
  const file = document.getElementById('MyGreatFileUploadHidedButton').files[0];
  const formData = new FormData();
  formData.append('file', file);
  fetch('/api', {
    method: 'POST',
    body: formData
  });
}
let fileInput = ref(null);

async function handleSubmit() {
  console.log('upload');
  console.log(fileInput.value);
  const file = fileInput.value;
  const formData = new FormData();
  formData.append('file', file);
  console.log(formData);

  try {
    const response = await post('/solarpark/upload/as-geojson', formData, {
      // Accept: "application/json",
      'Access-Control-Allow-Origin': '*',
      "Content-Type": "multipart/form-data",
    },);
    console.log('Upload successful:', response);
  } catch (error) {
    console.error('Upload failed:', error);
  }
}
const file = ref(null);

const fileName = computed(() => file.value?.name);
const fileExtension = computed(() => fileName.value?.substr(fileName.value?.lastIndexOf(".") + 1));
// const fileMimeType = computed(() => file.value?.type);

const uploadFile = (event) => {
  file.value = event.target.files[0];
};
// const submitFile = async () => {
//   console.log(file.value)
//   const reader = new FileReader();
//   reader.readAsDataURL(file.value);
//   reader.onload = async () => {
//     const encodedFile = reader.result.split(",")[1];
//     const data = {
//       file: encodedFile,
//       fileName: fileName.value,
//       // fileExtension: fileExtension.value,
//     };
//     let formData = new FormData();
//     formData.append('file', file.value.file);
//     console.log(formData);
//     try {
//       const endpoint = 'http://localhost:8000/api/v1/solarpark/upload/as-geojson';
//       const response = await fetch(endpoint, {
//         method: "POST",
//         headers: {
//           // Accept: "application/json",
//           "Content-Type": "multipart/form-data",
//           'Access-Control-Allow-Origin': '*',
//         },
//         body: formData,
//       });
//       console.log(response.data);
//     } catch (error) {
//       console.error(error);
//     }
//   };
// };
// const submitFile = async () => {
//   // ! works
//   // console.log(file.value)
//   let formData = new FormData();
//   formData.append('file', file.value);
//   formData.append('fileName', file.value.name);
//   console.log(formData);
//   formData.forEach(el => console.log(el))
//   try {
//     const endpoint = 'http://localhost:8000/api/v1/solarpark/upload/as-geojson';
//     const response = await fetch(endpoint, {
//       method: "POST",
//       headers: {
//         // Accept: "application/json",
//         'Access-Control-Allow-Origin': '*',
//       },
//       body: formData,
//     });
//     console.log(response);
//   } catch (error) {
//     console.error(error);
//   }
// };
const submitFile = async () => {
  // ! works
  // console.log(file.value)
  let formData = new FormData();
  formData.append('file', file.value);
  formData.append('fileName', file.value.name);
  console.log(formData);
  formData.forEach(el => console.log(el))
  try {
    const endpoint = '/solarpark/upload/as-geojson';
    const response = await filePost(endpoint, formData)
    console.log(response);
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="about">
    <button @click="downloadGeoJSON"
      class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center">
      <svg class="fill-current w-4 h-4 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
        <path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z" />
      </svg>
      <span>GeoJSON</span>
    </button>

    <!-- <form action="/api" method="post" enctype="multipart/form-data">
      <label for="file">File</label>
      <input id="file" name="file" type="file" />
      <button>Upload</button>
    </form>
    <div>
      <input type="file" @change="onFileChanged($event)" accept="geojson/*" capture />
    </div>
    <form @submit.prevent="handleSubmit">
      <input type="file" ref="fileInput">
      <button type="submit">Upload</button>
    </form> -->
    <div>
      <input ref="file" type="file" @change="uploadFile" />
      <button @click="submitFile">Submit</button>
    </div>
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