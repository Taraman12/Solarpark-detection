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

// lost and found
const data = ref(null)

// all
const { get, put } = useApiFetch()
const dataTable = ref(null)
const noneItem = ref(null)
const noneItemCount = ref(null)
const toggleValue = ref(false)
const FilterModelName = ref("solar-park-detection");
const filteredData = ref([]);

async function fetchData(id) {
  try {
    const response = await get(`/prediction/${id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}

// google maps
let map = ref(null); // map object
const mapDiv = ref(null); // populate the map
let polygons = ref([]);

const polygonOptions = {
  strokeColor: "#FF0000",
  strokeOpacity: 0.8,
  strokeWeight: 2,
  fillColor: "#FF0000",
  fillOpacity: 0.00,
};

const loader = new Loader({
  apiKey: GOOGLE_MAPS_API_KEY,
  version: 'weekly',
  libraries: ['places']
})

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

// OpenLayers
register(proj4);
const OSMmap = ref(null); // map object

const layer = new TileLayer({
  source: new OSM(),
});

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
  console.log(OSMmap.value.getView().getProjection().getCode());
  OSMmap.value.addLayer(vectorLayer);
  OSMmap.value.getView().fit(vectorSource.getExtent(), {
    padding: [50, 50, 50, 50],
    maxZoom: 15,
  });
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




async function updateItem(id, value) {
  try {
    const item = await get(`/prediction/${id}`);
    console.log(item);
    const object = await item.json();
    const updatedItem = { ...object, is_valid: value };
    console.log(updatedItem);
    await put(`/prediction/${id}`, updatedItem);
    console.log(`Item ${id} updated to ${value}`);
    filteredData.value = await fetchData("");
    noneItem.value = filteredData.value.find(item => item.is_valid === "None");
    noneItemCount.value = filteredData.value.filter(item => item.is_valid === "None").length;
  } catch (error) {
    console.error(error);
  }
}

async function handleItemUpdate(item) {
  data.value = await fetchData(item.id);
  map.value = new google.maps.Map(mapDiv.value, {
    // center: currPos.value,
    // ToDo: center map on solar park
    center: { lat: data.value.lat[0], lng: data.value.lon[0] },
    zoom: 16,
    mapTypeId: 'satellite'
  })
  polygons.value.pop(-1);
  const url = await generateUrls(item.name_in_aws)
  await addPolygons()
  await addImage(url)
  await addOSMPolygon(data);
}

async function loadGoogleMaps(item) {
  await loader.load();
  map.value = new google.maps.Map(mapDiv.value, {
    // center: currPos.value,
    // ToDo: center map on solar park
    center: { lat: item.lat[0], lng: item.lon[0] },
    zoom: 16,
    mapTypeId: 'satellite'
  })
}

async function loadOSMMap(item) {
  OSMmap.value = new Map({
    target: "OSMmap",
    layers: [layer],
    view: new View({
      center: fromLonLat([9.93, 49.783]),
      zoom: 8,
    }),
  });
  const url = await generateUrls(item.name_in_aws)
  await addImage(url)
  await addOSMPolygon(data);
}

onMounted(async () => {
  dataTable.value = await fetchData("");
  noneItem.value = dataTable.value.find(item => item.is_valid === "None");
  noneItemCount.value = dataTable.value.filter(item => item.is_valid === "None").length;
  loadGoogleMaps(noneItem.value)
  loadOSMMap(noneItem.value)
});


watch(filteredData, (newVal) => {
  noneItem.value = newVal.find(item => item.is_valid === "None");
  noneItemCount.value = filteredData.value.filter(item => item.is_valid === "None").length;
  handleItemUpdate(noneItem.value)
});


watch(toggleValue, (newVal) => {
  console.log(newVal);
  if (newVal) {
    noneItem.value = filteredData.value.find(item => {
      return item.is_valid === "None" || item.is_valid === "unsure";
    });
    noneItemCount.value = filteredData.value.filter(item => {
      return item.is_valid === "None" || item.is_valid === "unsure";
    }).length;
  } else {
    noneItem.value = filteredData.value.find(item => item.is_valid === "None");
    noneItemCount.value = filteredData.value.filter(item => item.is_valid === "None").length;
  }
});


watch(FilterModelName, (newVal) => {
  console.log(newVal);
  console.log("dataTable", dataTable.value);
  if (FilterModelName.value === "") {
    filteredData.value = dataTable.value;
  } else {
    filteredData.value = dataTable.value.filter((item) => {
      return item.name_of_model === FilterModelName.value;
    });
  }
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
        <div class="mb-3">
          <select id="filter" v-model="FilterModelName" class="text-black border dark:bg-neutral-300 p-1 rounded">
            <option value="solar-park-detection">solar-park-detection</option>
            <option value="training">training</option>
            <option value="validation">validation</option>
            <option value="test">test</option>
          </select>
        </div>
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
                <td>Date of Data</td>
                <td>{{ noneItem.date_of_data }}</td>
              </tr>
              <!-- <tr>
                <td>First Detection</td>
                <td>{{ noneItem.first_detection }}</td>
              </tr>
              <tr>
                <td>Last Detection</td>
                <td>{{ noneItem.last_detection }}</td>
              </tr> -->
              <!-- <tr>
                <td>avg_confidence</td>
                <td>{{ noneItem.avg_confidence.toFixed(2) }}</td>
              </tr> -->
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
            <!-- <label>
              Include Unsure
              <input type="checkbox" v-model="toggleValue" />
            </label> -->

          </div>
        </div>
        <div>
          <label class="relative inline-flex items-center cursor-pointer mt-3">
            <input type="checkbox" class="sr-only peer" v-model="toggleValue" />
            <div
              class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600">
            </div>
            <span class="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">Include Unsure</span>
          </label>
        </div>
      </div>

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

#map {
  height: 600px;
  margin: auto;
  padding: 0px;
}

#map img {
  max-width: none;
}
</style>
