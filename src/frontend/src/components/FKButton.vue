<script setup>
const props = defineProps({
    color: {
        type: String,
        default: 'grey'
    },
})
</script>

<template>
    <button :class="[
        'bg-' + color + '-500',
        'hover:bg-' + color + '-700',
        'text-white',
        'font-bold',
        'py-2',
        'px-4',
        'rounded',
        'inline-flex',
        'items-center',
        'focus:outline-none',
        'focus:shadow-outline',
    ]" @click="$emit('click')">
        <slot />
    </button>
</template>