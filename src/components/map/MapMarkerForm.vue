<template>
  <div class="marker-form">
    <h3>添加标记</h3>
    <div class="marker-form__row">
      <div class="marker-form__group">
        <label>类型</label>
        <select v-model="localType" class="marker-form__select">
          <option value="high">高威胁</option>
          <option value="medium">中威胁</option>
          <option value="low">低威胁</option>
        </select>
      </div>
      <div class="marker-form__group marker-form__group--grow">
        <label>描述</label>
        <input v-model="localDesc" type="text" class="marker-form__input" placeholder="输入标记描述..." />
      </div>
    </div>
    <div class="marker-form__actions">
      <AppButton variant="primary" size="sm" @click="$emit('add', { type: localType, description: localDesc })">
        <template #icon><AppIcon name="map" :size="15" /></template>
        {{ isAdding ? '点击地图添加标记' : '添加标记' }}
      </AppButton>
      <AppButton variant="ghost" size="sm" @click="$emit('refresh')">
        <template #icon><AppIcon name="refresh" :size="15" /></template>
        更新位置
      </AppButton>
      <AppButton variant="ghost" size="sm" @click="$emit('get-location')">
        <template #icon><AppIcon name="map" :size="15" /></template>
        获取当前位置
      </AppButton>
      <AppButton v-if="isAdding" variant="danger" size="sm" @click="$emit('cancel')">
        <template #icon><AppIcon name="close" :size="15" /></template>
        取消
      </AppButton>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'

const props = defineProps({
  type: { type: String, default: 'medium' },
  description: { type: String, default: '' },
  isAdding: { type: Boolean, default: false }
})

defineEmits(['add', 'refresh', 'get-location', 'cancel', 'update:type', 'update:description'])

const localType = ref(props.type)
const localDesc = ref(props.description)

watch(() => props.type, (v) => { localType.value = v })
watch(() => props.description, (v) => { localDesc.value = v })
</script>

<style scoped>
.marker-form {
  padding: var(--space-lg) 0;
}

.marker-form h3 {
  color: var(--color-text);
  font-size: var(--font-size-md);
  margin-bottom: var(--space-md);
  font-weight: var(--font-weight-semibold);
}

.marker-form__row {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
  flex-wrap: wrap;
}

.marker-form__group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.marker-form__group--grow { flex: 1; }

.marker-form__group label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.marker-form__select,
.marker-form__input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--color-bg-input);
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
}

.marker-form__select:focus,
.marker-form__input:focus {
  outline: none;
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.marker-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}
</style>
