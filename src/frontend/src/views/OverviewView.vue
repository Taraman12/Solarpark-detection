<script setup>
/* eslint-disable no-undef */
import { ref, onMounted, computed, watch } from "vue";
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
import { useApiFetch } from '@/plugins/fetch'

// import { fromNodeProviderChain } from "@aws-sdk/credential-providers";
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

// https://stackoverflow.com/questions/76076055/how-to-delete-google-maps-markers-in-vue-3-composition-api-js-gmaps-api
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const AWS_ACCESS_KEY_ID = import.meta.env.VITE_AWS_ACCESS_KEY_ID;
const AWS_SECRET_ACCESS_KEY = import.meta.env.VITE_AWS_SECRET_ACCESS_KEY;
// const DOCKERIZED = import.meta.env.VITE_DOCKERIZED;

// console.log(DOCKERIZED);
// needed to get the epsg code definitions
register(proj4);

const OSMmap = ref(null); // map object
// const OSMmapDiv = ref(null);

const layer = new TileLayer({
    source: new OSM(),
});



// const { dataSinglePoly, errorSinglePoly, get, put } = useApiFetch()
const { get } = useApiFetch()
//* Google Map instances
const loader = new Loader({
    apiKey: GOOGLE_MAPS_API_KEY,
    version: 'weekly',
    libraries: ['places']
})

const mapDiv = ref(null);
let map = ref(null); // map object

const dataTable = ref(null)
const data = ref(null)
const error = ref(null)
const FilterIsValid = ref("");
const FilterModelName = ref("solar-park-detection");
const filteredData = ref(null);

let polygons = ref([]);
// let polygon = ref(null);

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
        const response = await get(`/solarpark_observation/${id}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
}

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

async function handleRowClick(item) {
    // Do something with the selected row ID
    data.value = await fetchData(item.id);
    // const source = await loadSource();
    console.log("here: " + data.value.lat[0]);
    map.value = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        // ToDo: center map on solar park
        center: { lat: data.value.lat[0], lng: data.value.lon[0] },
        zoom: 16,
        mapTypeId: 'satellite'
    })
    // removes the last added polygon
    polygons.value.pop(-1);
    const url = await generateUrls(item.name_in_aws)
    await addPolygons()
    await addImage(url)
    await addOSMPolygon(data);
}


onMounted(async () => {
    dataTable.value = await fetchData("");
    filteredData.value = dataTable.value
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

watch(FilterIsValid, () => {
    if (FilterIsValid.value === "") {
        filteredData.value = dataTable.value;
    } else {
        filteredData.value = dataTable.value.filter((item) => {
            return item.is_valid === FilterIsValid.value;
        });
    }
});

watch(FilterModelName, () => {
    if (FilterModelName.value === "solar-park-detection") {
        filteredData.value = dataTable.value;
    } else {
        filteredData.value = dataTable.value.filter((item) => {
            return item.name_of_model === FilterModelName.value;
        });
    }
});

</script>
<template>
    <div class="flex">
        <div class="w-2/5 place-self-start justify-center sticky top-20 m-4">
            <div class="h-96">
                <div id="OSMmap" class="h-full" />
            </div>
            <div class="h-96 mt-4">
                <div ref="mapDiv" class="h-full" />
            </div>
        </div>
        <div class="w-3/5 ">
            <div class="flex justify-center">
                <div class="m-4">
                    <!-- <label for="filter" class="mr-4 p-1">Filter:</label> -->
                    <select id="filter" v-model="FilterIsValid" class="text-black border dark:bg-neutral-300 p-1 rounded">
                        <option value="">All</option>
                        <option value="None">Unclassified</option>
                        <option value="valid">Valid</option>
                        <option value="non-valid">Invalid</option>
                        <option value="unsure">Unsure</option>
                    </select>
                </div>
                <div class="m-4">
                    <select id="filter" v-model="FilterModelName" class="text-black border dark:bg-neutral-300 p-1 rounded">
                        <option value="solar-park-detection">solar-park-detection</option>
                        <option value="training">training</option>
                        <option value="validation">validation</option>
                        <option value="test">test</option>
                    </select>
                </div>
            </div>
            <div class="h-full col-span-2">
                <div v-if="error">{{ error }}</div>
                <div v-else>
                    <table class="table">
                        <thead class="sticky top-14 z-50">
                            <tr>
                                <th>ID</th>
                                <th>Size in m&sup2;</th>
                                <th>Peak Power (MW)</th>
                                <!-- <th>First detection</th>
                                <th>Last detection</th> -->
                                <th>Name of Model</th>
                                <th>Classification</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in filteredData" :key="item.id" @click="handleRowClick(item)">
                                <td>{{ item.id }}</td>
                                <td>{{ item.size_in_sq_m }}</td>
                                <td>{{ item.peak_power.toFixed(2) }}</td>
                                <!-- <td>{{ item.first_detection }}</td>
                                <td>{{ item.last_detection }}</td> -->
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
                </div>
            </div>
        </div>
    </div>
</template>
