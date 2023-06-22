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
import OSM from 'ol/source/OSM.js';
import WebGLTile from 'ol/layer/WebGLTile.js';
import { register } from 'ol/proj/proj4';
import { fromEPSGCode } from 'ol/proj/proj4';
import proj4 from 'proj4';
import { Loader } from '@googlemaps/js-api-loader'
import { useApiFetch } from '@/plugins/fetch'

register(proj4);
const OSMmap = ref(null); // map object

const layer = new TileLayer({
    source: new OSM(),
});

async function loadSource() {
    const source = new GeoTIFF({
        sources: [
            {
                url: 'https://solar-detection-697553-eu-central-1.s3.eu-central-1.amazonaws.com/predicted-solar-parks/test.tif?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEID%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDGV1LWNlbnRyYWwtMSJIMEYCIQC3BBVwZUagb5y8X%2BR0WsQjNvAQH6Fzkt9xauwORpXxaQIhALXaw%2BibBvqomlTvzXL0gS0NKAWSkRB1zcRRE5UZ7p9ZKvECCNn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMMTAzOTc2MjI4NDM1IgyJ4xmQDvX5MvZmBc0qxQI4jPBcb0Npo43%2FloLIYyivYN9qV%2BqUYfY6evYYznh3N0fPWynVt16P3dGTTlInTv9tCshSt9fOTZEhM0BVS24fEqH2gZ4HVLsotn5%2FRpyR61QhaD4QYV6%2Bp6vw%2BEnc%2FGwXDXy%2Bb5nsbeoOEepK0b%2FiEs1ueQHCXsHwyK0oDumHLpe%2FNXV1suCML0zwYUDqqh1FxMyS%2F73EqA4RuP8%2BgI2Ft3Xe%2BShlf5c1k539CLy%2BajX8zMr1OI4v0zodnOgHIXmmwWADA6MRUaly8LcaGJY%2FeCdltW355zrhRnxkZxOYJd9YjHMaeb4yg3xfFPx%2BISW79O13peWwy0vdCAGAT6%2FQGY7BxCfNlGDrI2%2BQ44nSBbq8DT0d3dW%2F7%2B6EYW5wmGVNh6xTn50JcLNbCZ6H7QH3xm10%2F1JdgOHmgtvRuPHkYNwQ3gRkMPHe0aQGOrIC059%2B44EmkDnjAEGUG18irZ4LKpFDX7NvznVcGMnJ3gff9Eio99Na%2BRY7jKWqvvIao6xCgQ3Jsk8wau90uvSgL%2BcNrar%2F9MPYGG69GjIFnSc1fzfPRLwxyW%2BEy6QjqTgB6X%2FNJEgjYg5PhbriCFzOhMQ6usCav5X49IYEnOrVuAmp1AutiGX8HVRAAzh6B6k%2BIz8FhcQIIlXUf19RH7IH8OGQm44GLUXxkn0wByqPuhK7RyDY9jSD%2BRZjeIFOilLkbG%2BZIepFpP5FJoxukbqbv7MtoO9sAuz0MRUX9JBT7dgaiKvwISKbHTSt%2BSfei7diTpLe%2BPb%2FQiybOsQvFLD8dmftbEO8JRN5y3QpTjJidWi9n%2Br5vglkEtjozBq%2FVWAXyw4Cpub65LZ49mArRaJiTOVI&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230622T201307Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=ASIARQNLXKZJUIMTPMWG%2F20230622%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=bcb0cf1cd456b968061047b66435e98e40c287c6dc2c83833de494dc6329e6b8',
                // url: 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/U/NA/2022/9/S2B_32UNA_20220923_0_L2A/TCI.tif',
            },
        ],
    });
    return source;
}

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

async function handleRowClick(id) {
    // Do something with the selected row ID
    data.value = await fetchData(id);

    console.log("here: " + data.value.lat[0]);
    map.value = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        center: { lat: data.value.lat[0], lng: data.value.lon[0] },
        zoom: 16,
        mapTypeId: 'satellite'
    })
    // removes the last added polygon
    polygons.value.pop(-1);
    await addPolygons()
    // get(`/solarpark/${id}`).then(park => {
    //     console.log("park " + park);
    //     if (polygon.value) {
    //         polygon.value.setMap(null);
    //     }
    //     addPolygon(park);
    // });
    // Create a new polygon geometry from the coordinates
    const polygonCoords = latCoords.map((lat, index) => [lonCoords[index], lat]);
    const polygonGeometry = new Polygon(polygonCoords);
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
    const source = await loadSource();
    const sourceView = await source.getView()
    const newView = source.getView()
    const projection = sourceView.projection
    const epsgCode = projection.code_
    await fromEPSGCode(epsgCode);
    const imageLayer = new WebGLTile({
        source: source,
    });

    OSMmap.value = new Map({
        target: "OSMmap",
        layers: [layer],
        view: new View({
            center: fromLonLat([10, 51]),
            zoom: 8,
        }),
    });
    OSMmap.value.addLayer(imageLayer);
    OSMmap.value.setView(newView);

    // ! Hardcoded for now
    data.value = await fetchData(4)
    await loader.load();
    map.value = new google.maps.Map(mapDiv.value, {
        // center: currPos.value,
        center: { lat: 40, lng: -80 },
        zoom: 7,
        // mapTypeId: 'satellite'
    });
    await addPolygons();
});
</script>
<template>
    <div class="grid grid-cols-3 gap-4">
        <div class="grid gap-2  overflow-hidden">
            <div id="OSMmap" class="h-full"></div>
            <div ref="mapDiv" class="h-full"></div>
        </div>
        <div class="h-full overflow-y-auto col-span-2">
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
