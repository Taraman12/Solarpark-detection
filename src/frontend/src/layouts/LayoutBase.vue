<script setup>
import { ref } from "vue";
import { useStyleStore } from "@/stores/style.js";

const styleStore = useStyleStore();

const layoutAsidePadding = "xl:pl-60";

const isAsideMobileExpanded = ref(false);

</script>

<template>
    <div :class="{
        dark: styleStore.darkMode,
        'overflow-hidden lg:overflow-visible': isAsideMobileExpanded,
    }">
        <div :class="[layoutAsidePadding, { 'ml-60 lg:ml-0': isAsideMobileExpanded }]"
            class="pt-14 min-h-screen w-screen transition-position lg:w-auto bg-gray-50 dark:bg-neutral-800 dark:text-neutral-200">
            <slot></slot>
        </div>
    </div>
</template>