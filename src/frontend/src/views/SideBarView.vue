<script setup>
import { useStyleStore } from "@/stores/style.js";
import LayoutBase from "@/layouts/LayoutBase.vue";
const styleStore = useStyleStore();



</script>

<template>
    <LayoutBase>

        <div class="container mx-auto bg-gray-200 dark:bg-gray-700 rounded-xl shadow border p-8 m-10">
            <p class="text-3xl  font-bold mb-5">
                Welcome!
            </p>
            <p class="text-lg">
                Vue and Tailwind CSS in action!
            </p>
        </div>
        <button @click="styleStore.setDarkMode()">Dark Mode</button>
        <div class="container bg-white dark:bg-gray-600">
            Hiere ist der Inhalt
        </div>
    </LayoutBase>
</template>

<style>
.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 200px;
    background-color: #f0f0f0;
    overflow-y: auto;
}

ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

li {
    padding: 10px;
}

li a {
    color: #333;
    text-decoration: none;
}

li a:hover {
    color: #000;
}
</style>