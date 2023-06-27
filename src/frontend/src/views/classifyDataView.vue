<script setup>
/* eslint-disable no-undef */
import { ref, watch, onMounted, } from 'vue'
import { useApiFetch } from '@/plugins/fetch'
import "ol/ol.css";
import Map from "ol/Map";
import View from "ol/View";
import GeoTIFF from "ol/source/GeoTIFF";
import TileLayer from "ol/layer/Tile";
import { fromLonLat } from "ol/proj";
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Feature from 'ol/Feature';
import Polygon from 'ol/geom/Polygon'
import { Style, Stroke } from 'ol/style';
import OSM from 'ol/source/OSM.js';
import WebGLTile from 'ol/layer/WebGLTile.js';
import { register } from 'ol/proj/proj4';
import { fromEPSGCode } from 'ol/proj/proj4';
import proj4 from 'proj4';
import { Loader } from '@googlemaps/js-api-loader'
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const AWS_ACCESS_KEY_ID = import.meta.env.VITE_AWS_ACCESS_KEY_ID;
const AWS_SECRET_ACCESS_KEY = import.meta.env.VITE_AWS_SECRET_ACCESS_KEY;
const DOCKERIZED = import.meta.env.VITE_DOCKERIZED;

register(proj4);

const { get, put } = useApiFetch()
const dataTable = ref(null)
const data = ref(null)
const error = ref(null)
const noneItem = ref(null)
const noneItemCount = ref(null)
const mapDiv = ref(null); // define divref to populate the map
let map = ref(null); // map object

const OSMmap = ref(null); // map object
const OSMmapDiv = ref(null); // define divref to populate the map

const layer = new TileLayer({
  source: new OSM(),
});
const loader = new Loader({
  apiKey: GOOGLE_MAPS_API_KEY,
  version: 'weekly',
  libraries: ['places']
})

let polygons = ref([]);

const polygonOptions = {
  strokeColor: "#FF0000",
  strokeOpacity: 0.8,
  strokeWeight: 2,
  fillColor: "#FF0000",
  fillOpacity: 0.00,
};

async function generateUrls(filename) {
  // https://stackoverflow.com/questions/65960693/aws-sdk-v3-s3client-in-web-worker-throws-referenceerror-window-is-not-defined
  const s3config = {
    region: 'eu-central-1',
    credentials: {
      accessKeyId: AWS_ACCESS_KEY_ID,
      secretAccessKey: AWS_SECRET_ACCESS_KEY
    }
  };

  let getParams = {
    Bucket: 'solar-detection-697553-eu-central-1',
    Key: `predicted-solar-parks/${filename}`
  };
  let url;

  const clientS3 = new S3Client(s3config);

  const getCmd = new GetObjectCommand(getParams);
  try {
    url = await getSignedUrl(clientS3, getCmd);
  } catch (err) {
    console.log('Error getting signed URL ', err);
  }
  console.log(url);
  return url;
}

async function addPolygons() {
  if (Array.isArray(data.value)) {
    // Loop through the data and add a polygon for each solar park
    data.value.forEach(park => {
      const coordinates = park.lat.map((lat, index) => {
        return { lat: lat, lng: park.lon[index] }
      })
      const polygon = new google.maps.Polygon({
        paths: coordinates,
        ...polygonOptions,
        map: map.value
      });
      polygons.value.push(polygon);
    });
  } else {
    // Add a polygon for the single solar park
    const park = data.value;
    const coordinates = park.lat.map((lat, index) => {
      return { lat: lat, lng: park.lon[index] }
    })
    const polygon = new google.maps.Polygon({
      paths: coordinates,
      ...polygonOptions,
      map: map.value
    });
    polygons.value.push(polygon);
  }
}

async function addOSMPolygon(data) {
  const lonCoords = data.value.lon;
  const latCoords = data.value.lat;
  const polygonCoords = latCoords.map((lat, index) => [lonCoords[index], lat]);

  const epsgCode = OSMmap.value.getView().getProjection().getCode();
  await fromEPSGCode(epsgCode);

  const openLayersCoords = polygonCoords.map(coord => fromLonLat(coord, epsgCode));

  const polygonGeometry = new Polygon([openLayersCoords]);

  const polygonFeature = new Feature({
    type: "Polygon",
    geometry: polygonGeometry,
  });

  const vectorSource = new VectorSource({
    features: [polygonFeature],
  });

  const vectorLayer = new VectorLayer({
    source: vectorSource,
    style: new Style({
      stroke: new Stroke({
        color: 'red',
        width: 2,
      }),
    }),
  });
  // console.log(vectorLayer);
  // testView = await vectorSource.getView()
  // console.log(testView);
  console.log(OSMmap.value.getView().getProjection().getCode());
  OSMmap.value.addLayer(vectorLayer);
  OSMmap.value.getView().fit(vectorSource.getExtent(), {
    padding: [50, 50, 50, 50],
    maxZoom: 15,
  });
}

async function loadSource(url) {
  // const url = url
  const source = new GeoTIFF({
    sources: [
      {
        url: url,
      },
    ],
  });
  return source;
}

async function addImage(name_in_aws) {

  const source = await loadSource(name_in_aws);
  const sourceView = await source.getView()
  const projection = sourceView.projection
  const epsgCode = projection.code_
  console.log(sourceView);

  await fromEPSGCode(epsgCode);

  // const newView = source.getView()

  const imageLayer = new WebGLTile({
    source: source,
  });
  OSMmap.value.addLayer(imageLayer)
  // OSMmap.value.setView(newView)
  OSMmap.value.getView()
}

async function fetchData(id) {
  try {
    const response = await get(`/solarpark/${id}`);
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
  OSMmap.value = new Map({
    target: "OSMmap",
    layers: [layer],
    view: new View({
      center: fromLonLat([9.93, 49.783]),
      zoom: 8,
    }),
  });
  await loader.load();
  map.value = new google.maps.Map(mapDiv.value, {
    // center: currPos.value,
    center: { lat: 49.783, lng: 9.93 },
    zoom: 8,
    // mapTypeId: 'satellite'
  });
});

watch(dataTable, (newVal) => {
  noneItem.value = newVal.find(item => item.is_valid === "None");
});
</script>

<template>
  <div class="flex mt-4 justify-center">
    <div class="w-2/5">
      <div id="OSMmap" class="h-96"></div>
      <div ref="mapDiv" class="h-96 mt-4"></div>
    </div>
    <div class="grid w-1/5 gap-4 ml-8 items-center">
      <div>
        <div class="border-2 border-neutral-500 rounded mb-2">
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
