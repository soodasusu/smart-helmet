<template>
  <header class="app-header">
    <div class="app-header__left">
      <button class="app-header__toggle" @click="$emit('toggle-sidebar')" title="折叠侧边栏">
        <AppIcon name="menu" :size="20" />
      </button>
      <div class="app-header__breadcrumb">
        <span class="app-header__breadcrumb-item">{{ pageTitle }}</span>
      </div>
    </div>

    <div class="app-header__right">
      <!-- ═══ 双模式切换：普通用户 / 专家答辩 ═══ -->
      <button class="mode-switch" :class="{ 'mode-switch--expert': isExpert }" @click="toggleExpert" :title="isExpert ? '切换到普通用户模式' : '切换到专家答辩模式'">
        <span class="mode-switch__dot"></span>
        <span class="mode-switch__text">{{ isExpert ? '专家模式' : '普通模式' }}</span>
      </button>

      <StatusBadge
        v-if="helmetStatus !== 'unknown'"
        :status="helmetStatus"
        :text="helmetStatus === 'online' ? '头箍已连接' : '头箍未连接'"
      />
      <span v-else class="app-header__status-text">检测中...</span>
    </div>
  </header>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import StatusBadge from '@/components/common/StatusBadge.vue'
import AppIcon from '@/components/common/AppIcon.vue'

defineProps({
  helmetStatus: { type: String, default: 'unknown', validator: v => ['online', 'offline', 'unknown'].includes(v) }
})

defineEmits(['toggle-sidebar'])

const route = useRoute()
const pageTitle = computed(() => route.meta.title || '控制台')

// ═══ 普通 / 专家双模式（写在 body.expert-mode） ═══
const isExpert = ref(false)
const toggleExpert = () => {
  isExpert.value = !isExpert.value
  document.body.classList.toggle('expert-mode', isExpert.value)
}
onMounted(() => {
  isExpert.value = document.body.classList.contains('expert-mode')
})
onUnmounted(() => {})
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  background: rgba(7, 11, 22, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: var(--z-header);
}

.app-header__left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.app-header__toggle {
  background: none;
  border: 1px solid transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  transition: all var(--transition-fast);
}
.app-header__toggle:hover {
  background: rgba(34, 211, 238, 0.08);
  color: var(--color-primary-500);
}

.app-header__breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
}

.app-header__breadcrumb-item {
  color: var(--color-text);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.5px;
}

.app-header__right {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.app-header__status-text {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

/* ═══ 双模式切换按钮 ═══ */
.mode-switch {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 14px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: rgba(148, 184, 255, 0.05);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-family: var(--font-family);
  transition: all var(--transition-normal);
}

.mode-switch__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  transition: all var(--transition-normal);
}

.mode-switch:hover {
  border-color: var(--border-color-hover);
  color: var(--color-text);
}

.mode-switch--expert {
  background: rgba(34, 211, 238, 0.12);
  border-color: rgba(34, 211, 238, 0.45);
  color: var(--color-primary-500);
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.25);
}

.mode-switch--expert .mode-switch__dot {
  background: var(--color-primary-500);
  box-shadow: 0 0 8px var(--color-primary-500);
  animation: glowPulse 1.8s infinite;
}
</style>
