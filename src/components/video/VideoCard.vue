<template>
  <div class="video-card">
    <div class="video-card__icon">
      <AppIcon name="video" :size="20" />
    </div>
    <div class="video-card__info">
      <span class="video-card__name" :title="video.filename">{{ video.filename }}</span>
      <div class="video-card__meta">
        <span class="video-card__meta-item"><AppIcon name="users" :size="13" /> {{ video.username || 'unknown' }}</span>
        <span class="video-card__meta-item"><AppIcon name="clock" :size="13" /> {{ formatTime(video.upload_time) }}</span>
        <span class="video-card__meta-item"><AppIcon name="download" :size="13" /> {{ formatSize(video.size) }}</span>
      </div>
    </div>
    <div class="video-card__actions">
      <AppButton variant="warning" size="sm" @click="$emit('play', video.filename)">
        <template #icon><AppIcon name="play" :size="14" /></template>
        播放
      </AppButton>
      <AppButton variant="ghost" size="sm" @click="$emit('download', video.filename)">
        <template #icon><AppIcon name="download" :size="14" /></template>
        下载
      </AppButton>
      <AppButton variant="danger" size="sm" @click="$emit('delete', video.filename)">
        <template #icon><AppIcon name="trash" :size="14" /></template>
        删除
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'

defineProps({
  video: { type: Object, required: true }
})

defineEmits(['play', 'download', 'delete'])

const formatTime = (ts) => {
  if (!ts) return '未知'
  return new Date(ts).toLocaleString('zh-CN')
}

const formatSize = (bytes) => {
  if (!bytes) return '未知'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}
</script>

<style scoped>
.video-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.video-card:hover {
  border-color: var(--border-color-hover);
  box-shadow: var(--shadow-sm);
}

.video-card__icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--color-primary-50);
  color: var(--color-primary-500);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.video-card__info {
  flex: 1;
  min-width: 0;
}

.video-card__name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text);
  display: block;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.video-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.video-card__meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.video-card__actions {
  display: flex;
  gap: var(--space-xs);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .video-card {
    flex-direction: column;
    align-items: stretch;
  }
  .video-card__actions {
    justify-content: flex-start;
  }
}
</style>
