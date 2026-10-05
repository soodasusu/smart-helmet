<template>
  <button
    class="app-btn"
    :class="[`app-btn--${variant}`, `app-btn--${size}`, { 'app-btn--block': block, 'app-btn--loading': loading }]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="app-btn__spinner"></span>
    <span v-else-if="$slots.icon" class="app-btn__icon"><slot name="icon" /></span>
    <span v-if="$slots.default" class="app-btn__text"><slot /></span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: v => ['primary', 'success', 'danger', 'warning', 'ghost'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: v => ['sm', 'md', 'lg'].includes(v)
  },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false }
})

defineEmits(['click'])
</script>

<style scoped>
.app-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: var(--font-weight-medium);
  letter-spacing: 0.2px;
  border-radius: var(--radius-md);
  white-space: nowrap;
  user-select: none;
  transition: background var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast), box-shadow var(--transition-fast);
}

.app-btn:focus-visible {
  outline: 2px solid var(--color-primary-400);
  outline-offset: 2px;
}

/* ── Sizes ── */
.app-btn--sm  { padding: 6px 14px; font-size: var(--font-size-sm); }
.app-btn--md  { padding: 9px 20px; font-size: var(--font-size-base); }
.app-btn--lg  { padding: 12px 28px; font-size: var(--font-size-lg); }

.app-btn--block { width: 100%; }

.app-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Variants · 极光质感 ── */
.app-btn--primary {
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
  color: #04121c;
  font-weight: var(--font-weight-semibold);
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.35);
}
.app-btn--primary:hover:not(:disabled) {
  box-shadow: 0 0 26px rgba(34, 211, 238, 0.6);
  transform: translateY(-1px);
}

.app-btn--success {
  background: linear-gradient(135deg, var(--color-success), #10b981);
  color: #04140c;
  box-shadow: 0 0 14px rgba(52, 211, 153, 0.3);
}
.app-btn--success:hover:not(:disabled) {
  box-shadow: 0 0 22px rgba(52, 211, 153, 0.55);
}

.app-btn--danger {
  background: linear-gradient(135deg, var(--color-danger), #f43f5e);
  color: #1a060c;
  box-shadow: 0 0 14px rgba(251, 113, 133, 0.3);
}
.app-btn--danger:hover:not(:disabled) {
  box-shadow: 0 0 22px rgba(251, 113, 133, 0.55);
}

.app-btn--warning {
  background: linear-gradient(135deg, var(--color-warning), #f59e0b);
  color: #1a1204;
  box-shadow: 0 0 14px rgba(251, 191, 36, 0.28);
}
.app-btn--warning:hover:not(:disabled) {
  box-shadow: 0 0 22px rgba(251, 191, 36, 0.5);
}

.app-btn--ghost {
  background: rgba(148, 184, 255, 0.06);
  border-color: var(--border-color);
  color: var(--color-text-secondary);
}
.app-btn--ghost:hover:not(:disabled) {
  background: rgba(34, 211, 238, 0.1);
  border-color: var(--border-color-hover);
  color: var(--color-text);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.2);
}

/* ── Spinner ── */
.app-btn__spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.app-btn--ghost .app-btn__spinner {
  border-color: rgba(17, 24, 39, 0.2);
  border-top-color: var(--color-text-secondary);
}

.app-btn__icon {
  display: inline-flex;
  align-items: center;
}

.app-btn--loading { pointer-events: none; }
</style>
