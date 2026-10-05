<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="item in toasts"
        :key="item.id"
        class="toast"
        :class="`toast--${item.type}`"
        @click="remove(item.id)"
      >
        <span class="toast__icon">
          <svg v-if="item.type === 'success'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><path d="M21.8 10A10 10 0 1 1 17 3.34"/><path d="m9 11 3 3L22 4"/></svg>
          <svg v-else-if="item.type === 'error'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
          <svg v-else-if="item.type === 'warning'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </span>
        <span class="toast__message">{{ item.message }}</span>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let idCounter = 0

const add = (message, type = 'info', duration = 3500) => {
  const id = ++idCounter
  toasts.value.push({ id, message, type, duration })
  if (duration > 0) {
    setTimeout(() => remove(id), duration)
  }
}

const remove = (id) => {
  const idx = toasts.value.findIndex(t => t.id === id)
  if (idx > -1) toasts.value.splice(idx, 1)
}

const success = (msg) => add(msg, 'success')
const error = (msg) => add(msg, 'error', 5000)
const warning = (msg) => add(msg, 'warning', 4000)
const info = (msg) => add(msg, 'info')

defineExpose({ success, error, warning, info, add, remove })
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: var(--space-lg);
  right: var(--space-lg);
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  pointer-events: none;
  max-width: 360px;
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  pointer-events: auto;
  cursor: pointer;
  background: #fff;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  animation: toastIn 0.3s ease;
}

.toast--success { color: var(--color-success); }
.toast--success .toast__icon { color: var(--color-success); }
.toast--error   { color: var(--color-danger); }
.toast--error .toast__icon { color: var(--color-danger); }
.toast--warning { color: var(--color-warning); }
.toast--warning .toast__icon { color: var(--color-warning); }
.toast--info    { color: var(--color-primary-500); }
.toast--info .toast__icon { color: var(--color-primary-500); }

.toast__icon { flex-shrink: 0; display: flex; }
.toast__message { flex: 1; color: var(--color-text); }

.toast-leave-active { animation: toastOut 0.3s ease forwards; }
</style>
