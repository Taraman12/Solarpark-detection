<script setup>
/* eslint-disable no-undef */
import { mdiViewListOutline } from '@mdi/js'
import SectionMain from '@/components/SectionMain.vue'
import { useFetch } from '@/plugins/fetch'
import CardBox from '@/components/CardBox.vue'
import LayoutAuthenticated from '@/layouts/LayoutAuthenticated.vue'
import SectionTitleLineWithButton from '@/components/SectionTitleLineWithButton.vue'
import { ref, onMounted, watch } from 'vue'
// import SolarParkTable from '@/components/Tables/SolarPark.vue'
import { Loader } from '@googlemaps/js-api-loader'

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

// defineProps({
//   checkable: Boolean
// })

const { get, put } = useFetch()
// S2B_MSIL2A_20200602T100559_N0500_R022_T32UQE_20230618T155201

// https://stackoverflow.com/questions/76076055/how-to-delete-google-maps-markers-in-vue-3-composition-api-js-gmaps-api
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

// needed to get the epsg code definitions
register(proj4);

const OSMmap = ref(null); // map object
const OSMmapDiv = ref(null);

const layer = new TileLayer({
  source: new OSM(),
});

// const items = computed(() => mainStore.clients)

// lost and found
const data = ref(null)

// all
const dataTable = ref(null)
const noneItem = ref(null)
const noneItemCount = ref(null)
const toggleValue = ref(false)
const FilterModelName = ref("solar-park-detection");
const filteredData = ref([]);

// ---- Google Maps ----
const loader = new Loader({
  apiKey: GOOGLE_MAPS_API_KEY,
  version: 'weekly',
  libraries: ['places']
})

let map = ref(null);
let mapDiv = ref(null);



let polygons = ref([]);

const polygonOptions = {
  strokeColor: "#FF0000",
  strokeOpacity: 0.8,
  strokeWeight: 2,
  fillColor: "#FF0000",
  fillOpacity: 0.00,
};

async function fetchData(id) {
  try {
    // change to solarpark
    const response = await get(`solarpark/${id}`);
    // const data = await response.json();
    return response;
  } catch (error) {
    console.error(error);
  }
}

async function addPolygons() {
  // Adds the polygons to the google maps object
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
      console.log(polygons.value);
      polygons.value.push(polygon);
    });
  } else {
    // Add a polygon for the single solar park
    console.log("data.value", data.value);
    const park = data.value;
    const coordinates = park.lat.map((lat, index) => {
      return { lat: lat, lng: park.lon[index] }
    })
    console.log(coordinates);
    const polygon = new google.maps.Polygon({
      paths: coordinates,
      ...polygonOptions,
      map: map.value
    });
    console.log(polygon);
    polygons.value.push(polygon);
  }
}

// ---- OpenLayers ----


function createSentinelUrl(identifier) {
  const IDENTIFIER_REGEX = new RegExp(
    "(S2[A-B])_MSI" +
    "(L[1-2][A-C])_" +
    "(\\d{8}T\\d{6})_" +
    "(N\\d{4})_" +
    "(R\\d{3})_T" +
    "(\\d{2})" +
    "(\\w{1})" +
    "(\\w{2})_" +
    "(\\d{4})" +
    "(\\d{2})" +
    "(\\d{2})T" +
    "(\\d{6})"
  );

  const match = IDENTIFIER_REGEX.exec(identifier);

  if (match) {
    const satellite = match[1];
    const date = match[3].substring(0, 8);
    const year = date.substring(0, 4);
    let month = date.substring(4, 6);
    const UTM = match[6];
    const latitudeBand = match[7];
    const gridSquare = match[8];

    // Remove leading zero from month
    month = parseInt(month, 10).toString();

    // Construct the product ID
    const productId = `${satellite}_${UTM}${latitudeBand}${gridSquare}_${date}_0_L2A`;

    // Construct the URL
    const url = `https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/${UTM}/${latitudeBand}/${gridSquare}/${year}/${month}/${productId}/TCI.tif`;

    return url;
  } else {
    throw new Error('Invalid identifier');
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
  const identifier = 'S2B_MSIL2A_20200602T100559_N0500_R022_T32UQE_20230618T155201';
  const url = createSentinelUrl(identifier)
  await addPolygons()
  await addImage(url)
  await addOSMPolygon(data);
}

async function handleRowClick(item) {
  // Do something with the selected row ID
  data.value = await fetchData(item.id);
  // const source = await loadSource();
  console.log("here: " + data.value.lat[0] + " " + data.value.lon[0]);
  map.value = new google.maps.Map(mapDiv.value, {
    // center: currPos.value,
    // ! reprojection of coordinates is needed
    center: { lat: data.value.lat[0], lng: data.value.lon[0] },
    zoom: 15,
    mapTypeId: 'satellite'
  });
  // removes the last added polygon
  polygons.value.pop(-1);
  const identifier = 'S2B_MSIL2A_20200602T100559_N0500_R022_T32UQE_20230618T155201';
  const url = createSentinelUrl(identifier)
  console.log(url);
  await addPolygons()
  await addImage(url)
  await addOSMPolygon(data);
}

async function loadGoogleMaps(item) {
  await loader.load();
  console.log("here: " + item.lat[0] + " " + item.lon[0]);
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
      center: fromLonLat([item.lon[0], item.lat[0]]),
      zoom: 8,
    }),
  });

  const identifier = 'S2B_MSIL2A_20200602T100559_N0500_R022_T32UQE_20230618T155201';
  const url = await createSentinelUrl(identifier)
  await addImage(url)
  await addOSMPolygon(data);
}

onMounted(async () => {
  dataTable.value = await get('prediction')
  noneItem.value = dataTable.value.find(item => item.is_valid === "None");
  noneItemCount.value = dataTable.value.filter(item => item.is_valid === "None").length;
  loadGoogleMaps(noneItem.value)
  loadOSMMap(noneItem.value)
})

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
  <button @click="handleRowClick()">Here</button>
  <LayoutAuthenticated>
    <SectionMain>
      <!-- <SectionTitleLineWithButton :icon="mdiViewListOutline" title="Overview" main>
    </SectionTitleLineWithButton> -->
      <div class="flex">
        <div class="w-2/5 place-self-start justify-center sticky top-20 m-4">
          <div class="h-96">
            <div id="OSMmap" class="h-full" />
          </div>
          <div class="h-96 mt-4">
            <div ref="mapDiv" class="h-full" />
          </div>
        </div>


        <CardBox class="mb-6" has-table>
          <table class="table">
            <thead class="sticky top-14 z-20">
              <tr>
                <th>ID</th>
                <th>Size in m&sup2;</th>
                <th>Peak Power (MW)</th>
                <th>Name of Model</th>
                <th>Classification</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredData" :key="item.id" @click="handleRowClick(item)">
                <td>{{ item.id }}</td>
                <td>{{ item.size_in_sq_m }}</td>
                <td>{{ item.peak_power.toFixed(2) }}</td>
                <td>{{ item.name_of_model }}</td>
                <td v-if="item.is_valid === 'None'">
                  <span>Unclassified</span>
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
        </CardBox>
      </div>
    </SectionMain>
  </LayoutAuthenticated>
</template>
