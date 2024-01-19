<script setup>
import { ref, onMounted } from 'vue'

defineProps({
  checkable: Boolean
})

// const items = computed(() => mainStore.clients)
// const items = tableData

const dataTable = ref(null)
const filteredData = ref(null);
</script>

<template>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Size in m&sup2;</th>
        <th>Peak Power (MW)</th>
        <th>Name of Model</th>
        <th>Classification</th>
      </tr>
    </thead>
    <tbody>
      <td>123</td>
      <td>4123</td>
      <td>123</td>
      <td>4123</td>
      <td>123</td>
    </tbody>
  </table>
  <!-- <table class="table">
    <thead class="sticky top-14 z-50">
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
  </table> -->
</template>
