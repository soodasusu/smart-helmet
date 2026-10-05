<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="app-modal__overlay" @click.self="closeOnOverlay && $emit('close')">
        <div class="app-modal" :class="`app-modal--${size}`" :style="maxWidth ? { maxWidth } : {}">
          <div class="app-modal__header">
            <h3 v-if="title" class="app-modal__title">{{ title }}</h3>
            <button v-if="closable" class="app-modal__close" @click="$emit('close')" aria-label="关闭">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" width="18" height="18"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>
          <div class="app-modal__body">
            <slot />
          </div>
          <div v-if="$slots.footer" class="app-modal__footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md', validator: v => ['sm', 'md', 'lg', 'xl'].includes(v) },
  closable: { type: Boolean, default: true },
  closeOnOverlay: { type: Boolean, default: true },
  maxWidth: { type: String, default: '' }
})

defineEmits(['close'])

const onEsc = (e) => {
  if (e.key === 'Escape' && props.visible && props.closable) {
    // 关闭逻辑由父组件监听 close 事件处理
  }
}

onMounted(() => document.addEventListener('keydown', onEsc))
onUnmounted(() => document.removeEventListener('keydown', onEsc))
</script>

<style scoped>
.app-modal__overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  background: var(--color-bg-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
}

.app-modal {
  background: #fff;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.app-modal--sm { max-width: 400px; }
.app-modal--md { max-width: 540px; }
.app-modal--lg { max-width: 720px; }
.app-modal--xl { max-width: 960px; }

.app-modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-xl) var(--space-xl) 0;
}

.app-modal__title {
  color: var(--color-text);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.app-modal__close {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast), color var(--transition-fast);
}
.app-modal__close:hover {
  color: var(--color-text);
  background: var(--color-bg-subtle);
}

.app-modal__body {
  padding: var(--space-xl);
  flex: 1;
}

.app-modal__footer {
  padding: 0 var(--space-xl) var(--space-xl);
  display: flex;
  gap: var(--space-sm);
  justify-content: flex-end;
}

/* ── Transitions ── */
.modal-enter-active { animation: fadeIn 0.2s ease; }
.modal-leave-active { animation: fadeIn 0.15s ease reverse; }
.modal-enter-active .app-modal { animation: slideUp 0.25s ease-out; }
.modal-leave-active .app-modal { animation: slideDown 0.15s ease-in reverse; }
</style>
