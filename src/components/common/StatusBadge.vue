<template>
  <span class="status-badge" :class="`status-badge--${status}`">
    <span class="status-badge__dot"></span>
    <span v-if="!iconOnly" class="status-badge__text">{{ text }}</span>
  </span>
</template>

<script setup>
defineProps({
  status: { type: String, default: 'offline', validator: v => ['online', 'offline', 'warning'].includes(v) },
  text: { type: String, default: '' },
  iconOnly: { type: Boolean, default: false }
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border: 1px solid transparent;
}

.status-badge__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-badge--online {
  background: var(--color-success-bg);
  color: var(--color-success);
  border-color: rgba(52, 211, 153, 0.3);
}
.status-badge--online .status-badge__dot {
  background: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
  animation: glowPulse 2s ease-in-out infinite;
}

.status-badge--offline {
  background: rgba(90, 111, 142, 0.12);
  color: var(--color-text-secondary);
  border-color: var(--border-color);
}
.status-badge--offline .status-badge__dot {
  background: #5a6f8e;
}

.status-badge--warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
  border-color: rgba(251, 191, 36, 0.3);
}
.status-badge--warning .status-badge__dot {
  background: var(--color-warning);
  box-shadow: 0 0 8px var(--color-warning);
}
</style>
