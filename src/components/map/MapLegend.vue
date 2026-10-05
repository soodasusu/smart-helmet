<template>
  <div class="map-legend">
    <div v-for="item in items" :key="item.type" class="map-legend__item">
      <span class="map-legend__dot" :style="{ background: item.color }"></span>
      <span>{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup>
const items = [
  { type: 'high', color: '#dc2626', label: '高威胁' },
  { type: 'medium', color: '#f59e0b', label: '中威胁' },
  { type: 'low', color: '#eab308', label: '低威胁' }
]
</script>

<style scoped>
.map-legend {
  display: flex;
  gap: var(--space-lg);
  flex-wrap: wrap;
}

.map-legend__item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.map-legend__dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
</style>
