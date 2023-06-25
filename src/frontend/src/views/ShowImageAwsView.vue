<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from "vue";
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
import { Style, Fill, Stroke } from 'ol/style';
import OSM from 'ol/source/OSM.js';
import WebGLTile from 'ol/layer/WebGLTile.js';
import { register } from 'ol/proj/proj4';
import { fromEPSGCode } from 'ol/proj/proj4';
import proj4 from 'proj4';
import { Loader } from '@googlemaps/js-api-loader'
import { useApiFetch } from '@/plugins/fetch'

register(proj4);
const OSMmap = ref(null); // map object
const OSMmapDiv = ref(null); // define divref to populate the map

const layer = new TileLayer({
    source: new OSM(),
});

// https://stackoverflow.com/questions/76076055/how-to-delete-google-maps-markers-in-vue-3-composition-api-js-gmaps-api
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;
const { dataSinglePoly, errorSinglePoly, get, put } = useApiFetch()
//* Google Map instances
const loader = new Loader({
    apiKey: GOOGLE_MAPS_API_KEY,
    version: 'weekly',
    libraries: ['places']
})
const mapDiv = ref(null); // define divref to populate the map
let map = ref(null); // map object

const dataTable = ref(null)
const data = ref(null)
const error = ref(null)

let polygons = ref([]);
let polygon = ref(null);

const polygonOptions = {
    strokeColor: "#FF0000",
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: "#FF0000",
    fillOpacity: 0.00,
};

async function fetchData(id) {
    try {
        const response = await fetch(`http://localhost:8000/api/v1/solarpark/${id}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error(error);
    }
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
async function loadSource(name_in_aws) {
    const url = `https://solar-detection-697553-eu-central-1.s3.eu-central-1.amazonaws.com/predicted-solar-parks/${name_in_aws}`
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
    await addPolygons()
    await addImage(item.name_in_aws)
    await addOSMPolygon(data);
}

async function handleCheckboxClick(item) {
    try {
        // copy item object and update is_valid property
        const updatedItem = { ...item, is_valid: "True" };

        const response = await fetch(`http://localhost:8000/api/v1/solarpark/${item.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedItem)
        });
        console.log(response);
    } catch (error) {
        console.error(error);
    }
}

onMounted(async () => {
    dataTable.value = await fetchData("");
    // const source = await loadSource();
    // const sourceView = await source.getView()
    // const newView = source.getView()
    // const projection = sourceView.projection
    // const epsgCode = projection.code_
    // await fromEPSGCode(epsgCode);
    // const imageLayer = new WebGLTile({
    //     source: source,
    // });

    OSMmap.value = new Map({
        target: "OSMmap",
        layers: [layer],
        view: new View({
            center: fromLonLat([9.93, 49.783]),
            zoom: 8,
        }),
    });
    // OSMmap.value.addLayer(imageLayer);
    // OSMmap.value.setView(newView);

    // ! Hardcoded for now
    // data.value = await fetchData(4)
    await loader.load();
    map.value = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        center: { lat: 49.783, lng: 9.93 },
        zoom: 8,
        // mapTypeId: 'satellite'
    });
    // await addPolygons();
});
</script>
<template>
    <div class="grid grid-cols-3 grid-rows-2 gap-4">
        <div class="grid gap-2 row-span-full mt-4">
            <div id="OSMmap" class="h-full"></div>
            <div ref="mapDiv" class="h-full"></div>
        </div>
        <div class="h-full overflow-y-auto col-span-2 mt-4">
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
                    <tr v-for="item in dataTable" :key="item.id" @click="handleRowClick(item)">
                        <td>{{ item.id }}</td>
                        <td>{{ item.size_in_sq_m }}</td>
                        <td>{{ item.peak_power.toFixed(2) }}</td>
                        <td>{{ item.first_detection }}</td>
                        <td>{{ item.last_detection }}</td>
                        <td>{{ item.avg_confidence.toFixed(2) }}</td>
                        <td v-if="item.is_valid === 'None'">
                            <input type="checkbox" v-model="item.selected" @click="handleCheckboxClick(item)">
                        </td>
                        <td v-else-if="item.is_valid === 'True'">
                            <span class="text-green-500">Valid</span>
                        </td>
                        <td v-else-if="item.is_valid === 'False'">
                            <span class="text-red-500">Invalid</span>
                        </td>
                        <td v-else-if="item.is_valid === 'Unsure'">
                            <span class="text-yellow-500">Unsure</span>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div v-if="error">{{ error }}</div>
            <div v-else>Loading...</div>
        </div>
    </div>
</template>
