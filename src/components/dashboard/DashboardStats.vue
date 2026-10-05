<template>
  <div class="stats-row">
    <div class="stat-card" v-for="stat in stats" :key="stat.label">
      <div class="stat-card__icon">
        <AppIcon :name="stat.icon" :size="22" />
      </div>
      <div class="stat-card__info">
        <span class="stat-card__value tabular-nums">{{ stat.value }}</span>
        <span class="stat-card__label">{{ stat.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import AppIcon from '@/components/common/AppIcon.vue'

const props = defineProps({
  todayVideos: { type: Number, default: 0 },
  totalVideos: { type: Number, default: 0 },
  helmetOnline: { type: Boolean, default: false },
  recording: { type: Boolean, default: false },
  usageStats: { type: Object, default: () => ({}) }
})

const stats = computed(() => [
  { icon: 'video', value: props.todayVideos, label: '今日视频' },
  { icon: 'video', value: props.totalVideos, label: '总视频数' },
  { icon: 'activity', value: props.helmetOnline ? '在线' : '离线', label: '头箍状态' },
  { icon: props.recording ? 'circle' : 'square', value: props.recording ? '录制中' : '未录制', label: '录制状态' },
  { icon: 'key', value: props.usageStats?.total_logins || 0, label: '登录次数' },
  { icon: 'users', value: props.usageStats?.total_users || 0, label: '用户总数' }
])
</script>

<style scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-xl);
  margin-bottom: var(--space-2xl);
}

.stat-card {
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-lg) var(--space-xl);
  display: flex;
  align-items: center;
  gap: var(--space-md);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition-normal),
              box-shadow var(--transition-normal),
              transform var(--transition-normal);
  animation: cardIn 0.5s ease-out backwards;
}
.stat-card:nth-child(2) { animation-delay: 0.06s; }
.stat-card:nth-child(3) { animation-delay: 0.12s; }
.stat-card:nth-child(4) { animation-delay: 0.18s; }
.stat-card:nth-child(5) { animation-delay: 0.24s; }
.stat-card:nth-child(6) { animation-delay: 0.30s; }

.stat-card:hover {
  border-color: var(--border-color-hover);
  box-shadow: var(--shadow-glow), var(--shadow-card);
  transform: translateY(-3px);
}

.stat-card__icon {
  width: 50px;
  height: 50px;
  border-radius: var(--radius-md);
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.25);
  color: var(--color-primary-500);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: inset 0 0 12px rgba(34, 211, 238, 0.12), 0 0 14px rgba(34, 211, 238, 0.15);
}

.stat-card__info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-card__value {
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  line-height: 1.15;
  background: linear-gradient(135deg, #ffffff 20%, #67e8f9 80%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: var(--font-mono);
  letter-spacing: -0.5px;
}

.stat-card__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: 4px;
  letter-spacing: 0.3px;
}
</style>
