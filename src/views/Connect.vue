<template>
  <div class="connect-page">
    <div class="connect-page__inner">
      <div class="connect-head">
        <h1 class="connect-head__title">
          <AppIcon name="bluetooth" :size="24" />
          头盔连接
        </h1>
        <p class="connect-head__sub">树莓派 · 蓝牙通信 · 实时数据链路</p>
      </div>

      <div class="connect-layout">
        <!-- ═══ 左：设备列表 ═══ -->
        <div class="connect-col connect-col--left">
          <div class="panel">
            <div class="panel__head">
              <span class="panel__title">设备列表</span>
              <span class="panel__count">{{ devices.length }}</span>
            </div>
            <div
              v-for="d in devices"
              :key="d.mac"
              class="device-item"
              :class="{ 'device-item--active': d.connected }"
            >
              <div class="device-item__icon">
                <AppIcon name="bluetooth" :size="18" />
              </div>
              <div class="device-item__info">
                <div class="device-item__name">{{ d.name }}</div>
                <div class="device-item__mac">{{ d.mac }}</div>
              </div>
              <div class="device-item__bars" title="信号强度">
                <span v-for="i in 4" :key="i" class="bar" :class="{ 'bar--on': i <= d.signal }"></span>
              </div>
              <div class="device-item__status" :class="{ 'is-online': d.connected }">
                {{ d.connected ? '已连接' : '待机' }}
              </div>
            </div>
          </div>

          <!-- 设备硬件参数（专家模式可见） -->
          <div class="panel expert-only">
            <div class="panel__head">
              <span class="panel__title">硬件参数</span>
            </div>
            <div class="hw-row" v-for="h in hardwareParams" :key="h.label">
              <span class="hw-row__label">{{ h.label }}</span>
              <span class="hw-row__value">{{ h.value }}</span>
            </div>
          </div>
        </div>

        <!-- ═══ 中：连接核心 ═══ -->
        <div class="connect-col connect-col--center">
          <div class="core-panel">
            <div
              class="core-ring"
              :class="{ 'core-ring--online': helmetOnline }"
            >
              <div class="core-ring__rotor core-ring__rotor--1"></div>
              <div class="core-ring__rotor core-ring__rotor--2"></div>
              <div class="core-ring__inner">
                <AppIcon :name="helmetOnline ? 'power' : 'bluetooth'" :size="40" />
              </div>
            </div>
            <div class="core-status" :class="{ 'is-online': helmetOnline }">
              <span class="core-status__dot"></span>
              {{ helmetOnline ? '链路已建立' : '等待连接' }}
            </div>
            <div class="core-sub">
              <span v-if="recording" class="core-rec">● 录制中</span>
              <span v-else class="core-id">B8:27:EB:A3:9F:2C</span>
            </div>

            <!-- 数据链路动画（专家模式） -->
            <div class="link-lines expert-only">
              <div class="link-line">
                <span class="link-line__node">WEB</span>
                <span class="link-line__track"><span class="link-line__flow"></span></span>
                <span class="link-line__node">树莓派</span>
                <span class="link-line__track"><span class="link-line__flow link-line__flow--delay"></span></span>
                <span class="link-line__node">头盔</span>
              </div>
            </div>
          </div>

          <!-- 命令控制（分组，宽松排列） -->
          <div class="ctrl-panel">
            <div class="ctrl-group">
              <div class="ctrl-group__label">系统</div>
              <div class="ctrl-group__btns">
                <AppButton variant="success" size="sm" @click="send('start')">
                  <template #icon><AppIcon name="power" :size="15" /></template>启动
                </AppButton>
                <AppButton variant="danger" size="sm" @click="send('stop')">
                  <template #icon><AppIcon name="square" :size="15" /></template>停止
                </AppButton>
              </div>
            </div>
            <div class="ctrl-group">
              <div class="ctrl-group__label">录制</div>
              <div class="ctrl-group__btns">
                <AppButton variant="success" size="sm" @click="send('start_recording')">开始录制</AppButton>
                <AppButton variant="warning" size="sm" @click="send('stop_recording')">停止录制</AppButton>
              </div>
            </div>
            <div class="ctrl-group">
              <div class="ctrl-group__label">检测 &amp; 警报</div>
              <div class="ctrl-group__btns">
                <AppButton variant="success" size="sm" @click="send('enable_detection')">开启检测</AppButton>
                <AppButton variant="warning" size="sm" @click="send('disable_detection')">关闭检测</AppButton>
                <AppButton variant="success" size="sm" @click="send('enable_alert')">开启警报</AppButton>
              </div>
            </div>
          </div>
        </div>

        <!-- ═══ 右：日志终端 ═══ -->
        <div class="connect-col connect-col--right">
          <div class="log-term">
            <div class="log-term__head">
              <span class="log-term__title">
                <span class="log-term__rec"></span>
                串口报文日志
              </span>
              <span class="log-term__count">{{ logs.length }}</span>
            </div>
            <div class="log-term__body">
              <div v-if="logs.length === 0" class="log-term__empty">
                // 连接后此处实时显示蓝牙收发报文…
              </div>
              <div v-for="(l, i) in logs" :key="i" class="log-term__line">
                <span class="log-term__time">{{ l.time }}</span>
                <span class="log-term__dir" :class="l.dir">{{ l.dir === 'tx' ? '→' : '←' }}</span>
                <span class="log-term__msg">{{ l.msg }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import AppIcon from '@/components/common/AppIcon.vue'
import AppButton from '@/components/common/AppButton.vue'
import { useSocket } from '@/composables/useSocket'
import { useToast } from '@/composables/useToast'

const toast = useToast()
const { helmetOnline, recording, sendCommand, lastEvent } = useSocket()

// ═══ 假设备数据（硬件未到货，演示用） ═══
const devices = ref([
  { name: 'Raspberry Pi 4B', mac: 'B8:27:EB:A3:9F:2C', signal: 4, connected: true },
  { name: '智能头盔主控', mac: 'DC:A6:32:0E:7B:11', signal: 3, connected: false }
])

const hardwareParams = ref([
  { label: '主控芯片', value: 'BCM2711' },
  { label: '蓝牙版本', value: 'BLE 5.0' },
  { label: '传感器', value: 'MPU6050 + GPS' },
  { label: '电量', value: '87%' },
  { label: '固件版本', value: 'v1.3.2' }
])

// ═══ 日志终端 ═══
const logs = ref([])
const pushLog = (dir, msg) => {
  const now = new Date()
  const t = now.toLocaleTimeString('zh-CN', { hour12: false }) + '.' +
            String(now.getMilliseconds()).padStart(3, '0').slice(0, 2)
  logs.value.unshift({ time: t, dir, msg })
  if (logs.value.length > 30) logs.value.pop()
}

// 初始演示日志（假装已连接）
pushLog('rx', 'BLE handshake OK, MTU=512')
pushLog('rx', 'pi_status online=1 recording=0')
pushLog('tx', 'cmd=get_status ack=0x00')

watch(lastEvent, (ev) => {
  if (!ev) return
  if (ev.type === 'pi_status') pushLog('rx', `pi_status online=${ev.data?.online}`)
  else if (ev.type === 'web_response') pushLog('rx', `ack ${JSON.stringify(ev.data).slice(0, 50)}`)
}, { deep: true })

const send = (command) => {
  pushLog('tx', `cmd=${command}`)
  const r = sendCommand(command)
  if (r.success) toast.info(`命令已发送: ${command}`)
  else toast.warning('演示模式（未连接硬件），命令已本地记录')
}
</script>

<style scoped>
.connect-page {
  min-height: 100vh;
  animation: pageEnter 0.5s ease-out;
}
.connect-page__inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-2xl);
}
.connect-head { margin-bottom: var(--space-2xl); }
.connect-head__title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  font-size: var(--font-size-2xl);
  color: var(--color-text);
}
.connect-head__title :deep(svg) {
  color: var(--color-primary-500);
  filter: drop-shadow(0 0 8px rgba(34,211,238,0.5));
}
.connect-head__sub {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-top: 4px;
}

/* 三栏布局 */
.connect-layout {
  display: grid;
  grid-template-columns: 320px 1fr 340px;
  gap: var(--space-2xl);
  align-items: start;
}

.panel, .core-panel, .log-term {
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  padding: var(--space-lg);
  margin-bottom: var(--space-lg);
}
.panel:last-child { margin-bottom: 0; }

.panel__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}
.panel__title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  letter-spacing: 0.5px;
}
.panel__count {
  font-family: var(--font-mono);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* 设备项 */
.device-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}
.device-item--active {
  background: rgba(34,211,238,0.07);
  border-color: rgba(34,211,238,0.25);
}
.device-item__icon {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  background: rgba(34,211,238,0.1);
  color: var(--color-primary-500);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.device-item__info { flex: 1; min-width: 0; }
.device-item__name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text);
}
.device-item__mac {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--color-text-tertiary);
}
.device-item__bars { display: flex; align-items: flex-end; gap: 2px; }
.bar {
  width: 3px;
  background: rgba(90,111,142,0.4);
  border-radius: 1px;
}
.bar:nth-child(1) { height: 4px; }
.bar:nth-child(2) { height: 7px; }
.bar:nth-child(3) { height: 10px; }
.bar:nth-child(4) { height: 13px; }
.bar--on { background: var(--color-primary-500); }
.device-item__status {
  font-size: 11px;
  color: var(--color-text-tertiary);
  white-space: nowrap;
}
.device-item__status.is-online { color: var(--color-success); }

/* 硬件参数 */
.hw-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px dashed var(--border-color);
  font-size: var(--font-size-sm);
}
.hw-row:last-child { border-bottom: none; }
.hw-row__label { color: var(--color-text-secondary); }
.hw-row__value { color: var(--color-text); font-family: var(--font-mono); }

/* 中间核心 */
.core-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-2xl) var(--space-lg);
}
.core-ring {
  position: relative;
  width: 160px; height: 160px;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: var(--space-lg);
}
.core-ring__inner {
  width: 110px; height: 110px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: rgba(34,211,238,0.1);
  border: 1px solid rgba(34,211,238,0.4);
  color: var(--color-primary-500);
  z-index: 2;
  animation: auraBreathe 2.8s ease-in-out infinite;
}
.core-ring--online .core-ring__inner {
  background: rgba(52,211,153,0.12);
  border-color: rgba(52,211,153,0.5);
  color: var(--color-success);
  animation: lockGlow 2.6s ease-in-out infinite;
}
.core-ring__rotor {
  position: absolute; inset: 0;
  border-radius: 50%;
  border: 2px solid transparent;
}
.core-ring__rotor--1 {
  border-top-color: var(--color-primary-500);
  border-right-color: rgba(34,211,238,0.2);
  animation: ringSpin 3.5s linear infinite;
}
.core-ring__rotor--2 {
  inset: 14px;
  border-bottom-color: var(--color-primary-600);
  border-left-color: rgba(56,189,248,0.15);
  animation: ringSpinReverse 5s linear infinite;
}
.core-ring--online .core-ring__rotor--1 { border-top-color: var(--color-success); }
.core-ring--online .core-ring__rotor--2 { border-bottom-color: #34d399; }

.core-status {
  display: flex; align-items: center; gap: 8px;
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
}
.core-status.is-online { color: var(--color-success); }
.core-status__dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: var(--color-primary-500);
  animation: glowPulse 2s infinite;
}
.core-status.is-online .core-status__dot {
  background: var(--color-success);
  box-shadow: 0 0 10px var(--color-success);
}
.core-sub {
  margin-top: 6px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  font-family: var(--font-mono);
}
.core-rec { color: var(--color-danger-light); }

/* 数据链路动画 */
.link-lines { margin-top: var(--space-lg); width: 100%; }
.link-line {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-mono); font-size: 11px;
  color: var(--color-text-tertiary);
}
.link-line__node {
  padding: 2px 8px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  white-space: nowrap;
}
.link-line__track {
  flex: 1; height: 2px;
  background: rgba(34,211,238,0.15);
  position: relative; overflow: hidden;
}
.link-line__flow {
  position: absolute; top: 0; left: 0;
  width: 40%; height: 100%;
  background: linear-gradient(90deg, transparent, var(--color-primary-500), transparent);
  animation: flowMove 1.6s linear infinite;
}
.link-line__flow--delay { animation-delay: 0.8s; }
@keyframes flowMove {
  from { left: -40%; } to { left: 100%; }
}

/* 命令控制 */
.ctrl-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  backdrop-filter: blur(14px);
}
.ctrl-group { margin-bottom: var(--space-lg); }
.ctrl-group:last-child { margin-bottom: 0; }
.ctrl-group__label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: var(--space-sm);
}
.ctrl-group__btns {
  display: flex; flex-wrap: wrap; gap: var(--space-sm);
}

/* 日志终端 */
.log-term {
  background: rgba(3,8,18,0.8);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  overflow: hidden;
  font-family: var(--font-mono);
  display: flex; flex-direction: column;
}
.log-term__head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 14px;
  background: rgba(34,211,238,0.06);
  border-bottom: 1px solid var(--border-color);
  font-size: 11px;
}
.log-term__title {
  color: var(--color-primary-500);
  display: flex; align-items: center; gap: 7px;
}
.log-term__rec {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--color-danger-light);
  box-shadow: 0 0 6px var(--color-danger-light);
  animation: glowPulse 1.5s infinite;
}
.log-term__count { color: var(--color-text-tertiary); }
.log-term__body {
  padding: 12px 14px;
  max-height: 480px;
  overflow-y: auto;
  font-size: 11.5px;
  line-height: 1.8;
}
.log-term__empty { color: var(--color-text-tertiary); font-style: italic; }
.log-term__line {
  display: flex; gap: 8px;
  animation: logScroll 0.25s ease-out;
  white-space: nowrap;
}
.log-term__time { color: var(--color-text-tertiary); }
.log-term__dir { color: var(--color-primary-500); width: 12px; }
.log-term__dir.tx { color: var(--color-warning); }
.log-term__msg {
  color: #9fd8e8;
  overflow: hidden; text-overflow: ellipsis;
}

@media (max-width: 1100px) {
  .connect-layout { grid-template-columns: 1fr; }
}
</style>
