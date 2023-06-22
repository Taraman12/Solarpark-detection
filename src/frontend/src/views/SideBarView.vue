<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from "vue";
import "ol/ol.css";
import Map from "ol/Map";
import View from "ol/View";
import GeoTIFF from "ol/source/GeoTIFF";
import TileLayer from "ol/layer/Tile";
import { fromLonLat } from "ol/proj";
import OSM from 'ol/source/OSM.js';
import WebGLTile from 'ol/layer/WebGLTile.js';
import Projection from 'ol/proj/Projection.js';
import { getCenter } from 'ol/extent.js';
import { setEPSGLookup } from 'ol/proj/proj4';
import { register } from 'ol/proj/proj4';
import { fromEPSGCode } from 'ol/proj/proj4';
import { transform } from 'ol/proj';
import { transformExtent } from 'ol/proj';
import proj4 from 'proj4';

// https://solar-detection-697553-eu-central-1.s3.eu-central-1.amazonaws.com/%09est%5Cimage_0_4.tif?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEID%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDGV1LWNlbnRyYWwtMSJIMEYCIQC3BBVwZUagb5y8X%2BR0WsQjNvAQH6Fzkt9xauwORpXxaQIhALXaw%2BibBvqomlTvzXL0gS0NKAWSkRB1zcRRE5UZ7p9ZKvECCNn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMMTAzOTc2MjI4NDM1IgyJ4xmQDvX5MvZmBc0qxQI4jPBcb0Npo43%2FloLIYyivYN9qV%2BqUYfY6evYYznh3N0fPWynVt16P3dGTTlInTv9tCshSt9fOTZEhM0BVS24fEqH2gZ4HVLsotn5%2FRpyR61QhaD4QYV6%2Bp6vw%2BEnc%2FGwXDXy%2Bb5nsbeoOEepK0b%2FiEs1ueQHCXsHwyK0oDumHLpe%2FNXV1suCML0zwYUDqqh1FxMyS%2F73EqA4RuP8%2BgI2Ft3Xe%2BShlf5c1k539CLy%2BajX8zMr1OI4v0zodnOgHIXmmwWADA6MRUaly8LcaGJY%2FeCdltW355zrhRnxkZxOYJd9YjHMaeb4yg3xfFPx%2BISW79O13peWwy0vdCAGAT6%2FQGY7BxCfNlGDrI2%2BQ44nSBbq8DT0d3dW%2F7%2B6EYW5wmGVNh6xTn50JcLNbCZ6H7QH3xm10%2F1JdgOHmgtvRuPHkYNwQ3gRkMPHe0aQGOrIC059%2B44EmkDnjAEGUG18irZ4LKpFDX7NvznVcGMnJ3gff9Eio99Na%2BRY7jKWqvvIao6xCgQ3Jsk8wau90uvSgL%2BcNrar%2F9MPYGG69GjIFnSc1fzfPRLwxyW%2BEy6QjqTgB6X%2FNJEgjYg5PhbriCFzOhMQ6usCav5X49IYEnOrVuAmp1AutiGX8HVRAAzh6B6k%2BIz8FhcQIIlXUf19RH7IH8OGQm44GLUXxkn0wByqPuhK7RyDY9jSD%2BRZjeIFOilLkbG%2BZIepFpP5FJoxukbqbv7MtoO9sAuz0MRUX9JBT7dgaiKvwISKbHTSt%2BSfei7diTpLe%2BPb%2FQiybOsQvFLD8dmftbEO8JRN5y3QpTjJidWi9n%2Br5vglkEtjozBq%2FVWAXyw4Cpub65LZ49mArRaJiTOVI&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230622T155823Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIARQNLXKZJUIMTPMWG%2F20230622%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=2c2710d12b2568c6adbc55379b7cd49c559bd48cfd6b999f0215a476842b7b61
// import L from "leaflet";
register(proj4);
const map = ref(null); // map object
// register(proj4);
// setEPSGLookup(proj4);
// fromEPSGCode('EPSG:25832')
// Definieren Sie die Projektionen
// proj4.defs('EPSG:32632', '+proj=utm +zone=32 +datum=WGS84 +units=m +no_defs +type=crs');
// proj4.defs('EPSG:3857', '+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs');
// 'EPSG:32632'
// const projection = new Projection({
//     code: 'EPSG:32631',
//     units: 'm',
// });

// const sourceExtent = [
//     689950, 5390200, 829760, 5600000];

const layer = new TileLayer({
    source: new OSM(),
});

async function loadSource() {
    const source = new GeoTIFF({
        sources: [
            {
                url: 'https://solar-detection-697553-eu-central-1.s3.eu-central-1.amazonaws.com/predicted-solar-parks/test.tif?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEID%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDGV1LWNlbnRyYWwtMSJIMEYCIQC3BBVwZUagb5y8X%2BR0WsQjNvAQH6Fzkt9xauwORpXxaQIhALXaw%2BibBvqomlTvzXL0gS0NKAWSkRB1zcRRE5UZ7p9ZKvECCNn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQARoMMTAzOTc2MjI4NDM1IgyJ4xmQDvX5MvZmBc0qxQI4jPBcb0Npo43%2FloLIYyivYN9qV%2BqUYfY6evYYznh3N0fPWynVt16P3dGTTlInTv9tCshSt9fOTZEhM0BVS24fEqH2gZ4HVLsotn5%2FRpyR61QhaD4QYV6%2Bp6vw%2BEnc%2FGwXDXy%2Bb5nsbeoOEepK0b%2FiEs1ueQHCXsHwyK0oDumHLpe%2FNXV1suCML0zwYUDqqh1FxMyS%2F73EqA4RuP8%2BgI2Ft3Xe%2BShlf5c1k539CLy%2BajX8zMr1OI4v0zodnOgHIXmmwWADA6MRUaly8LcaGJY%2FeCdltW355zrhRnxkZxOYJd9YjHMaeb4yg3xfFPx%2BISW79O13peWwy0vdCAGAT6%2FQGY7BxCfNlGDrI2%2BQ44nSBbq8DT0d3dW%2F7%2B6EYW5wmGVNh6xTn50JcLNbCZ6H7QH3xm10%2F1JdgOHmgtvRuPHkYNwQ3gRkMPHe0aQGOrIC059%2B44EmkDnjAEGUG18irZ4LKpFDX7NvznVcGMnJ3gff9Eio99Na%2BRY7jKWqvvIao6xCgQ3Jsk8wau90uvSgL%2BcNrar%2F9MPYGG69GjIFnSc1fzfPRLwxyW%2BEy6QjqTgB6X%2FNJEgjYg5PhbriCFzOhMQ6usCav5X49IYEnOrVuAmp1AutiGX8HVRAAzh6B6k%2BIz8FhcQIIlXUf19RH7IH8OGQm44GLUXxkn0wByqPuhK7RyDY9jSD%2BRZjeIFOilLkbG%2BZIepFpP5FJoxukbqbv7MtoO9sAuz0MRUX9JBT7dgaiKvwISKbHTSt%2BSfei7diTpLe%2BPb%2FQiybOsQvFLD8dmftbEO8JRN5y3QpTjJidWi9n%2Br5vglkEtjozBq%2FVWAXyw4Cpub65LZ49mArRaJiTOVI&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230622T191204Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIARQNLXKZJUIMTPMWG%2F20230622%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=350bfa5e3a0d8af550451990d91761e92edc8e5f50503db3e7b7aa3b78089326',
                // url: 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/32/U/NA/2022/9/S2B_32UNA_20220923_0_L2A/TCI.tif',
            },
        ],
    });
    return source;
}

// function addTileLayer() {
//     const source = loadSource();
//     const view = source.getView()
//     // console.log(view);
//     // const fromProjection = proj4('EPSG:25832');
//     // const toProjection = proj4('EPSG:3857');
//     // const bbox = await source.getBoundingBox();
//     // const transformedExtent = proj4.extent.transform(extent, fromProjection, toProjection);
//     // source.setProjection(new Projection({
//     //     code: 'EPSG:3857',
//     //     extent: transformedExtent,
//     // }));

//     // const projection = source.getProjection();
//     // console.log(projection);
//     const imageLayer = new WebGLTile({
//         source: source,
//     });
//     map.value.addLayer(imageLayer);
//     return view;
// }

onMounted(async () => {
    const source = await loadSource();
    const sourceView = await source.getView()
    const newView = source.getView()
    const projection = sourceView.projection // await source.getProjection();
    // const bbox =  await projection.getBoundingBox();
    const epsgCode = projection.code_//await projection.getCode();
    await fromEPSGCode(epsgCode);
    // const extent = sourceView.extent;
    // const center = sourceView.center;
    // const transformedCenter = transform(center, 'EPSG:4326', epsgCode);
    // const transformedExtent = await transformExtent(extent, 'EPSG:3857', epsgCode);
    // const newView = new View({
    //     center: transformedCenter,
    //     zoom: 7,
    //     projection: epsgCode,
    // });

    // const test = fromEPSGCode(epsgCode);
    console.log(source);
    console.log(sourceView);
    // console.log(extent);
    // console.log(epsgCode);
    // console.log(projection);
    // dataProjection: 'EPSG:4326'
    const imageLayer = new WebGLTile({
        source: source,
    });
    // view = new View({
    //     center: fromLonLat([0, 0]),
    //     zoom: 2,
    //     // projection: 'EPSG:32632',
    // });
    // const view = addTileLayer();
    // console.log(view);
    map.value = new Map({
        target: "map",
        layers: [layer],
        view: new View({
            center: fromLonLat([10, 51]),
            zoom: 8,
        }),
    });
    map.value.addLayer(imageLayer);
    map.value.setView(newView);
});
// EPSG:3857
// onMounted(async () => {
//     const view = addTileLayer();
//     console.log(view);
//     map.value = new Map({
//         target: "map",
//         layers: [layer],
//         view: view,
//     });

// });
</script>

<template>
    <div>
        <div id="map" class="map"></div>
    </div>
</template>

<style>
#map {
    height: 600px;
    margin: 0px;
    padding: 0px;
}
</style>