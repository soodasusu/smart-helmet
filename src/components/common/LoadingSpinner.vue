<template>
  <div class="loading-spinner" :class="`loading-spinner--${size}`">
    <div class="loading-spinner__ring"></div>
    <p v-if="text" class="loading-spinner__text">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '加载中...' },
  size: { type: String, default: 'md', validator: v => ['sm', 'md', 'lg'].includes(v) }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  padding: var(--space-3xl);
}

.loading-spinner__ring {
  border: 3px solid var(--color-primary-100);
  border-top-color: var(--color-primary-500);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.loading-spinner--sm .loading-spinner__ring { width: 22px; height: 22px; }
.loading-spinner--md .loading-spinner__ring { width: 36px; height: 36px; }
.loading-spinner--lg .loading-spinner__ring { width: 52px; height: 52px; }

.loading-spinner__text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}
</style>
