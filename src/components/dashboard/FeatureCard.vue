<template>
  <div class="feature-card" @click="$emit('click')">
    <div class="feature-card__icon">
      <AppIcon :name="icon" :size="28" />
    </div>
    <h3 class="feature-card__title">{{ title }}</h3>
    <p class="feature-card__desc">{{ description }}</p>
    <span class="feature-card__arrow">
      <AppIcon name="arrow-left" :size="16" />
    </span>
  </div>
</template>

<script setup>
import AppIcon from '@/components/common/AppIcon.vue'

defineProps({
  icon: { type: String, default: 'circle' },
  title: { type: String, default: '' },
  description: { type: String, default: '' }
})

defineEmits(['click'])
</script>

<style scoped>
.feature-card {
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  cursor: pointer;
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal), transform var(--transition-normal);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(14px);
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0; left: 15%; right: 15%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(34,211,238,0.5), transparent);
  opacity: 0.5;
  transition: opacity var(--transition-normal);
}

.feature-card:hover {
  border-color: var(--border-color-hover);
  box-shadow: var(--shadow-glow), var(--shadow-card);
  transform: translateY(-4px);
}

.feature-card:hover::before { opacity: 1; }

.feature-card__icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.25);
  color: var(--color-primary-500);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-md);
  box-shadow: inset 0 0 14px rgba(34, 211, 238, 0.12), 0 0 16px rgba(34, 211, 238, 0.15);
}

.feature-card__title {
  color: var(--color-text);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-xs);
}

.feature-card__desc {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  line-height: 1.5;
}

.feature-card__arrow {
  position: absolute;
  top: var(--space-xl);
  right: var(--space-xl);
  color: var(--color-text-tertiary);
  display: flex;
  transform: rotate(180deg);
  transition: color var(--transition-fast), transform var(--transition-fast);
}

.feature-card:hover .feature-card__arrow {
  color: var(--color-primary-500);
  transform: rotate(180deg) translateX(3px);
}
</style>
