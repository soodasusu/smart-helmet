<template>
  <div
    class="app-card"
    :class="{ 'app-card--clickable': clickable }"
    :style="padding ? { padding: `var(--space-${padding})` } : {}"
  >
    <slot />
  </div>
</template>

<script setup>
defineProps({
  clickable: { type: Boolean, default: false },
  padding: { type: String, default: 'xl' }
})
</script>

<style scoped>
.app-card {
  position: relative;
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  overflow: hidden;
  transition: border-color var(--transition-normal),
              box-shadow var(--transition-normal),
              transform var(--transition-normal),
              background var(--transition-normal);
}

/* 顶部高光线（极光质感） */
.app-card::before {
  content: '';
  position: absolute;
  top: 0; left: 10%; right: 10%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34,211,238,0.5), transparent);
  opacity: 0.6;
  transition: opacity var(--transition-normal);
}

.app-card--clickable {
  cursor: pointer;
}

.app-card:hover::before {
  opacity: 1;
}

.app-card--clickable:hover {
  border-color: var(--border-color-hover);
  background: var(--color-bg-card-hover);
  box-shadow: var(--shadow-glow), var(--shadow-card);
  transform: translateY(-3px);
}
</style>
