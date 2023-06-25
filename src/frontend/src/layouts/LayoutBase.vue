<script setup>
import { ref } from "vue";
import { useStyleStore } from "@/stores/style.js";

const styleStore = useStyleStore();

const layoutAsidePadding = "xl:pl-60";


</script>

<template>
    <div :class="{
        dark: styleStore.darkMode
    }">
        <div
            class="pt-14 min-h-screen h-full w-screen transition-position lg:w-auto bg-gray-50 dark:bg-neutral-800 dark:text-neutral-200">
            <div class="mx-auto px-4">
                <slot></slot>
            </div>
        </div>
    </div>
</template>