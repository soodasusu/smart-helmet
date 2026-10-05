<template>
  <AppCard class="helmet-panel" padding="xl">
    <!-- ═══ 设备连接核心（科技风） ═══ -->
    <div class="conn-core">
      <div
        class="conn-core__ring"
        :class="{
          'conn-core__ring--offline': !helmetOnline,
          'conn-core__ring--online': helmetOnline
        }"
      >
        <div class="conn-core__inner">
          <AppIcon :name="helmetOnline ? 'power' : 'bluetooth'" :size="30" />
        </div>
        <!-- 旋转流光环 -->
        <span class="conn-core__rotor conn-core__rotor--1"></span>
        <span class="conn-core__rotor conn-core__rotor--2"></span>
      </div>
      <div class="conn-core__meta">
        <div class="conn-core__title">树莓派头盔</div>
        <div class="conn-core__status" :class="{ 'is-online': helmetOnline }">
          <span class="conn-core__dot"></span>
          {{ helmetOnline ? '已连接 · 在线' : '未连接 · 等待设备' }}
        </div>
        <div class="conn-core__sub">
          <span v-if="recording" class="conn-core__rec">● 录制中</span>
          <span v-else class="conn-core__id">MAC · B8:27:EB:XX:XX</span>
        </div>
      </div>
    </div>

    <!-- ═══ 专家模式：代码日志终端（普通用户模式隐藏） ═══ -->
    <div class="conn-log expert-only">
      <div class="conn-log__head">
        <span class="conn-log__title">
          <span class="conn-log__rec-dot"></span>
          HARDWARE · 实时报文日志
        </span>
        <span class="conn-log__count">{{ logs.length }}</span>
      </div>
      <div class="conn-log__body">
        <div v-if="logs.length === 0" class="conn-log__empty">
          // 等待树莓派数据帧… 连接后此处实时显示收发报文
        </div>
        <div v-for="(log, i) in logs" :key="i" class="conn-log__line">
          <span class="conn-log__time">{{ log.time }}</span>
          <span class="conn-log__dir" :class="log.dir">{{ log.dir === 'tx' ? '→' : '←' }}</span>
          <span class="conn-log__msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>

    <!-- ═══ 系统控制 ═══ -->
    <div class="helmet-panel__section">
      <h4 class="helmet-panel__section-title">系统</h4>
      <div class="helmet-panel__btn-row">
        <AppButton variant="success" size="sm" @click="$emit('command', 'start')">
          <template #icon><AppIcon name="power" :size="15" /></template>
          启动头箍
        </AppButton>
        <AppButton variant="danger" size="sm" @click="$emit('command', 'stop')">
          <template #icon><AppIcon name="square" :size="15" /></template>
          停止头箍
        </AppButton>
        <AppButton variant="ghost" size="sm" @click="$emit('command', 'get_status')">
          <template #icon><AppIcon name="refresh" :size="15" /></template>
          获取状态
        </AppButton>
      </div>
    </div>

    <!-- ═══ 录制控制 ═══ -->
    <div class="helmet-panel__section">
      <h4 class="helmet-panel__section-title">录制</h4>
      <div class="helmet-panel__btn-row">
        <AppButton variant="success" size="sm" @click="$emit('command', 'start_recording')">
          <template #icon><AppIcon name="circle" :size="15" /></template>
          开始录制
        </AppButton>
        <AppButton variant="warning" size="sm" @click="$emit('command', 'stop_recording')">
          <template #icon><AppIcon name="square" :size="15" /></template>
          停止录制
        </AppButton>
        <AppButton variant="danger" size="sm" @click="$emit('command', 'stop_camera')">
          <template #icon><AppIcon name="camera" :size="15" /></template>
          关闭摄像头
        </AppButton>
      </div>
      <div class="helmet-panel__inline">
        <label class="helmet-panel__label">录制时长 (秒):</label>
        <input v-model.number="duration" type="number" min="5" max="300" class="helmet-panel__input" />
        <AppButton variant="primary" size="sm" @click="$emit('command', 'set_video_duration', { duration })">
          设置
        </AppButton>
      </div>
    </div>

    <!-- ═══ 检测控制 ═══ -->
    <div class="helmet-panel__section">
      <h4 class="helmet-panel__section-title">检测 &amp; 警报</h4>
      <div class="helmet-panel__btn-row">
        <AppButton variant="success" size="sm" @click="$emit('command', 'enable_detection')">
          <template #icon><AppIcon name="search" :size="15" /></template>
          开启检测
        </AppButton>
        <AppButton variant="warning" size="sm" @click="$emit('command', 'disable_detection')">
          <template #icon><AppIcon name="close" :size="15" /></template>
          关闭检测
        </AppButton>
        <AppButton variant="success" size="sm" @click="$emit('command', 'enable_alert')">
          <template #icon><AppIcon name="bell" :size="15" /></template>
          开启警报
        </AppButton>
        <AppButton variant="warning" size="sm" @click="$emit('command', 'disable_alert')">
          <template #icon><AppIcon name="bell" :size="15" /></template>
          警报静音
        </AppButton>
      </div>
    </div>

    <!-- ═══ 设置 ═══ -->
    <div class="helmet-panel__section">
      <h4 class="helmet-panel__section-title">设置</h4>
      <div class="helmet-panel__inline">
        <label class="helmet-panel__label">用户名:</label>
        <input v-model="username" type="text" class="helmet-panel__input" placeholder="设置 Pi 用户名" />
        <AppButton variant="primary" size="sm" @click="$emit('command', 'set_username', { username })">
          设置
        </AppButton>
      </div>
    </div>
  </AppCard>
</template>

<script setup>
import { ref, watch } from 'vue'
import AppCard from '@/components/common/AppCard.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'
import { useSocket } from '@/composables/useSocket'

defineEmits(['command'])

const duration = ref(30)
const username = ref('')

const { helmetOnline, recording, lastEvent } = useSocket()

// ═══ 专家模式日志终端：记录收发报文 ═══
const logs = ref([])
const pushLog = (dir, msg) => {
  const now = new Date()
  const t = now.toLocaleTimeString('zh-CN', { hour12: false }) + '.' +
            String(now.getMilliseconds()).padStart(3, '0').slice(0, 2)
  logs.value.unshift({ time: t, dir, msg })
  if (logs.value.length > 18) logs.value.pop()
}

// 监听 socket 推送事件，写入日志终端
watch(lastEvent, (ev) => {
  if (!ev) return
  if (ev.type === 'pi_status') {
    pushLog('rx', `pi_status online=${ev.data?.online} recording=${ev.data?.recording}`)
  } else if (ev.type === 'web_response') {
    pushLog('rx', `ack ${JSON.stringify(ev.data).slice(0, 60)}`)
  }
}, { deep: true })
</script>

<style scoped>
.helmet-panel {
  margin-bottom: var(--space-2xl);
}

/* ── 连接核心 ── */
.conn-core {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: var(--space-md) var(--space-sm) var(--space-lg);
  margin-bottom: var(--space-xl);
  border-bottom: 1px solid var(--border-color);
}

.conn-core__ring {
  position: relative;
  width: 84px;
  height: 84px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.conn-core__inner {
  width: 62px;
  height: 62px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.conn-core__ring--offline .conn-core__inner {
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.4);
  color: var(--color-primary-500);
  animation: auraBreathe 2.6s ease-in-out infinite;
}

.conn-core__ring--online .conn-core__inner {
  background: rgba(52, 211, 153, 0.12);
  border: 1px solid rgba(52, 211, 153, 0.5);
  color: var(--color-success);
  animation: lockGlow 2.4s ease-in-out infinite;
}

.conn-core__rotor {
  position: absolute;
  inset: 0;
  border-radius: var(--radius-full);
  border: 2px solid transparent;
}
.conn-core__rotor--1 {
  border-top-color: var(--color-primary-500);
  border-right-color: rgba(34, 211, 238, 0.25);
  animation: ringSpin 3s linear infinite;
}
.conn-core__rotor--2 {
  inset: 8px;
  border-bottom-color: var(--color-primary-600);
  border-left-color: rgba(56, 189, 248, 0.2);
  animation: ringSpinReverse 4.5s linear infinite;
}
.conn-core__ring--online .conn-core__rotor--1 { border-top-color: var(--color-success); }
.conn-core__ring--online .conn-core__rotor--2 { border-bottom-color: #34d399; }

.conn-core__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.conn-core__status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-top: 2px;
}
.conn-core__status.is-online { color: var(--color-success); }

.conn-core__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-primary-500);
  animation: glowPulse 2s ease-in-out infinite;
}
.conn-core__status.is-online .conn-core__dot {
  background: var(--color-success);
  box-shadow: 0 0 8px var(--color-success);
}

.conn-core__sub {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: 2px;
  font-family: var(--font-mono);
}
.conn-core__rec { color: var(--color-danger-light); }

/* ── 日志终端（专家模式） ── */
.conn-log {
  background: rgba(3, 8, 18, 0.75);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-xl);
  overflow: hidden;
  font-family: var(--font-mono);
}

.conn-log__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 12px;
  background: rgba(34, 211, 238, 0.06);
  border-bottom: 1px solid var(--border-color);
  font-size: 11px;
}

.conn-log__title {
  color: var(--color-primary-500);
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: 0.5px;
}

.conn-log__rec-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-danger-light);
  box-shadow: 0 0 6px var(--color-danger-light);
  animation: glowPulse 1.5s infinite;
}

.conn-log__count {
  color: var(--color-text-tertiary);
}

.conn-log__body {
  padding: 10px 12px;
  max-height: 180px;
  overflow-y: auto;
  font-size: 11.5px;
  line-height: 1.7;
}

.conn-log__empty {
  color: var(--color-text-tertiary);
  font-style: italic;
}

.conn-log__line {
  display: flex;
  gap: 8px;
  animation: logScroll 0.25s ease-out;
  white-space: nowrap;
}

.conn-log__time { color: var(--color-text-tertiary); }
.conn-log__dir { color: var(--color-primary-500); width: 12px; }
.conn-log__dir.tx { color: var(--color-warning); }
.conn-log__msg {
  color: #9fd8e8;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── 分区（保留原有） ── */
.helmet-panel__section {
  margin-bottom: var(--space-lg);
}

.helmet-panel__section-title {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-sm);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.helmet-panel__btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.helmet-panel__inline {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
  flex-wrap: wrap;
}

.helmet-panel__label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  white-space: nowrap;
}

.helmet-panel__input {
  width: 120px;
  padding: 7px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--color-bg-input);
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
}

.helmet-panel__input:focus {
  outline: none;
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.15);
}
</style>
