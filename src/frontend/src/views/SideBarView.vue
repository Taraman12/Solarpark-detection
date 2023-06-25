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
import { Style, Fill, Stroke } from 'ol/style';
import Projection from 'ol/proj/Projection';
import { transform } from 'ol/proj.js';
import { getCenter, getHeight, getWidth } from 'ol/extent.js';
import { transformExtent } from 'ol/proj.js';
// import transform from 'ol/proj/transform';
register(proj4);
const map = ref(null); // map object

const OSMlayer = new TileLayer({
    source: new OSM(),
});

async function loadSource() {
    const source = new GeoTIFF({
        sources: [
            {
                url: 'https://solar-detection-697553-eu-central-1.s3.eu-central-1.amazonaws.com/predicted-solar-parks/32UPC_34_2023-5-9.tif?response-content-disposition=inline&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEK3%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDGV1LWNlbnRyYWwtMSJGMEQCIAyi7dOk0avxmHcwcCC7QEqNpqQ0QbSwCnn8aQ7rz1neAiAhB0citNgpHsuj%2Bc7bRC21rdOHE3iQxllfweqj2eyhsSroAggWEAEaDDEwMzk3NjIyODQzNSIM%2BnmaK%2BrzTMxRS2cHKsUC2gUIe6XTPGC2rpZBFwzSUOexEP%2F8v17QjIrMgpHRhP%2BKaL7U%2B6rwzGL8eneACS3rq53AIbrxmWMK3TYGhXDkOLI52L%2F1Q7DZqAwpaxOmKz7CnxlExN9VJMq9b69nFnLSKmYBldW%2BbBIDOCvSPWIe%2FbxEDKV2LLXb0yai6vb2J0iTv0lZd2UHXs0Qbs7mgtKRL46UCCRTt4GuAM1Pzw0mLljo%2F%2BLUrUphsf18RIo%2BYD0SSeNv2rsV%2Fcdd9D9JPAzT7FCbSyR8Rv7yM%2FIba9mO2lYGu2g6N3a0dmyu2gAq%2Bt5Ca9wK9G3wKudWChzzCREmnVb7Kp134EKYSLY%2FL%2BUxziw9NyA%2FNS%2F36YUk8vKwIf9352EddVecALQq8GOIbgiTMciuTioZKQ7BDOJMridp0sEUCOsHfH%2B6GjuTIhYfUun7zZtWvTCv09ukBjq0Apc7khueZfj3AnlxrMlshNJs9ZH33sLgmlkmcrZOdkhyxu8j3z6x6WUeF7B5sG8h%2B%2F1j69SRer3O%2B78TpEzRl%2FvL1d8%2FT3xYmu0C75gTcBVJRCW4OOl2Y830XHy6U%2FmS22RqnOqzkM9YHp%2BSrQN2Zo9CBjCW%2BOk%2BmQyhPhDstRazEh8NdFQzwmhhDSQE6HEFy7Nx9NX64bHeKAJ2mmpqWdjMY9HqYfM8wKPHQyG9c652kthnNTnCOgFvPVKf5FJKNrZGD1aHc8imwejy8joOULY3b0kXERuOHGSbafdmpCr8HWiit7B7s3ngpAGaxKyDTp%2BUHRsIEHNunnIarXm%2F2QsqUymiBUFbLHhO3NEXT0SDPblWMt8dI563H73N1o7wcuIgVWrF5Rdp3frR4Z8GFI7m4bb8&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20230624T162116Z&X-Amz-SignedHeaders=host&X-Amz-Expires=43200&X-Amz-Credential=ASIARQNLXKZJ7PUWS66B%2F20230624%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Signature=c1fa8e791a30a223b0b4ec7664756b85239e0a83600ca41cd60dd72b2efe4962',
            },
        ],
    });
    return source;
}

const polygonCoords = [
    [11.684235259732432, 52.30315525794424],
    [11.6843817566629, 52.30315192634641],
    [11.684376321839016, 52.303062120155715],
    [11.684669315022768, 52.30305545643684],
    [11.684663879636004, 52.30296565026583],
    [11.685542856726995, 52.30294565481659],
    [11.685537419594448, 52.30285584870816],
    [11.685830411137989, 52.30284918212756],
    [11.685803222946829, 52.30240015166617],
    [11.685656728667956, 52.30240348499358],
    [11.685624105556233, 52.30186464831703],
    [11.685770598060834, 52.30186131505399],
    [11.685754286003759, 52.30159189672397],
    [11.685900777592657, 52.30158856331158],
    [11.685868152476136, 52.30104972666803],
    [11.685721662661427, 52.30105306001605],
    [11.685716225537753, 52.30096325389185],
    [11.685569735990152, 52.3009665870476],
    [11.685564299190755, 52.300876780910905],
    [11.685271320601188, 52.30088344665634],
    [11.685265884421753, 52.300793640496416],
    [11.684386949741333, 52.30081363331173],
    [11.684392384146621, 52.30090343953602],
    [11.684099405099852, 52.30091010237703],
    [11.684104838942325, 52.30099990862098],
    [11.683958349080395, 52.30100323977992],
    [11.683969216259655, 52.30118285228398],
    [11.683822725777766, 52.30118618328282],
    [11.683828159114547, 52.30127598954291],
    [11.683681668308395, 52.30127932037095],
    [11.683687101378041, 52.30136912663998],
    [11.683540610247624, 52.30137245729722],
    [11.683546043050132, 52.30146226357521],
    [11.683399551595452, 52.30146559406163],
    [11.683426714557894, 52.30191462547859],
    [11.683573207491106, 52.30191129493855],
    [11.683605805762872, 52.302450132516086],
    [11.683752300441814, 52.30244680173019],
    [11.683774034377171, 52.302806026703536],
    [11.683920530210436, 52.30280269569322],
    [11.68393139794097, 52.30298230814781],
    [11.68407789433712, 52.30297897693449],
    [11.684083328540972, 52.30306878314841],
    [11.68422982520428, 52.30306545174283],
    [11.684235259732432, 52.30315525794424],
];
// const polygonCoords = [
//     [52.30315525794424, 11.684235259732432],
//     [52.30105306001605, 11.685721662661427],
//     [52.30191129493855, 11.683573207491106],
//     [52.30315525794424, 11.684235259732432],
// ];
// const polygonCoords = [
//   [-80.19, 25.774],
//   [-66.118, 18.466],
//   [-64.757, 32.321],
//   [-80.19, 25.774],
// ];

async function addPolygon() {
    // proj4.defs("EPSG:4326", "+proj=longlat +datum=WGS84 +units=degrees +no_defs");
    // const polygonGeometry = new Polygon([polygonCoords])
    const epsgCode = map.value.getView().getProjection().getCode();
    const openLayersCoords = polygonCoords.map(coord => fromLonLat(coord, epsgCode));
    const polygonGeometry = new Polygon([openLayersCoords]);
    // ! best solution so far
    // const polygonGeometry = new Polygon([polygonCoords]).transform('EPSG:4326', 'EPSG:4326');

    // const transformedGeometry = new Polygon([polygonCoords])
    // const transformedGeometry = polygonGeometry.clone().transform('EPSG:3857', 'EPSG:4326')
    // console.log(transformedGeometry);
    const polygonFeature = new Feature({
        type: "Polygon",
        geometry: polygonGeometry,
    });
    // console.log(polygonFeature);

    // console.log(polygonFeature.getGeometry().getCoordinates());
    const vectorSource = new VectorSource({
        features: [polygonFeature],
    });

    const vectorLayer = new VectorLayer({
        source: vectorSource,
        style: new Style({
            stroke: new Stroke({
                color: 'red',
                width: 3,
            }),
        }),
    });
    // testView = await vectorSource.getView()
    // console.log(testView);
    console.log(map.value.getView().getProjection().getCode());
    map.value.addLayer(vectorLayer);
    map.value.getView().fit(vectorSource.getExtent(), {
        padding: [50, 50, 50, 50],
        maxZoom: 15,
    });
}

async function addImage() {
    const source = await loadSource();
    const sourceView = await source.getView()
    const projection = sourceView.projection
    const epsgCode = projection.code_
    console.log(sourceView);
    // console.log(projection);
    // console.log(epsgCode);
    await fromEPSGCode(epsgCode);
    // const extent = sourceView.extent
    // const extent = transformExtent(
    //     sourceView.extent,
    //     sourceView.projection,
    //     projection
    // );
    // const size = map.value.getSize()
    const newView = source.getView()
    // const newView = new View({
    //     projection: projection,
    //     center: getCenter(extent),
    //     resolution: Math.max(
    //         getWidth(extent) / size[0],
    //         getHeight(extent) / size[1]
    //     ),
    // })
    // const newView2 = newView.clone()
    // const newView3 = newView2.fit(source.getExtent(), {
    //     padding: [50, 50, 50, 50],
    //     maxZoom: 15,
    // })
    // const projection = sourceView.projection
    // const epsgCode = projection.code_
    // console.log(epsgCode);
    // await fromEPSGCode(epsgCode);
    // console.log(source);
    // console.log(sourceView);
    // dataProjection: 'EPSG:4326'
    const imageLayer = new WebGLTile({
        source: source,
    });
    map.value.addLayer(imageLayer)
    map.value.setView(newView);
}
// async function addImage() {
//     const source = await loadImage();
//     const sourceView = source.getView()
//     const newView2 = await source.getView()
//     // const projection = sourceView.projection
//     const extent =  newView2.extent
//     console.log(extent);
//     console.log(sourceView);
//     const newView = source.getView()
//     map.value.setView(newView)
//     console.log("added image");
// }
onMounted(async () => {
    // const source = await loadSource();
    // const sourceView = await source.getView()
    // const extent = sourceView.extent
    // const imageLayer = new WebGLTile({
    //     source: source,
    // });
    // // const projection = 'EPSG:3857';
    // const projection = sourceView.projection
    // const epsgCode = projection.code_
    // await fromEPSGCode(epsgCode);
    // const extent = transformExtent(
    //     sourceView.extent,
    //     sourceView.projection,
    //     projection
    // );
    // map.value = new Map({
    //     target: "map",
    //     layers: [OSMlayer, imageLayer],
    //     view: new View({
    //         projection: projection,
    //         center: getCenter(extent),
    //         zoom: 15,
    //     }),
    // });
    // const size = map.value.getSize()
    // const newView = source.getView()

    map.value = new Map({
        target: "map",
        layers: [OSMlayer],
        view: new View({
            center: fromLonLat([10, 51]),
            zoom: 8,
        }),
    });
    // console.log(map.value.getView().getProjection().getCode());
    // map.value.addLayer(imageLayer);
    // map.value.setView(newView);

});
</script>

<template>
    <div>
        <div id="map" class="map"></div>
    </div>
    <div>
        <button @click="addPolygon">Show-Polygon</button>
    </div>
    <div>
        <button @click="addImage">Showimage</button>
    </div>
</template>

<style>
#map {
    height: 600px;
    margin: 0px;
    padding: 0px;
}
</style>