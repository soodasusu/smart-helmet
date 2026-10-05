<template>
  <div class="map-page">
    <div class="map-page__content">
      <div class="map-header">
        <div>
          <h1 class="map-header__title">
            <AppIcon name="map" :size="22" />
            预警地图
          </h1>
          <p class="map-header__sub">南京邮电大学仙林校区 · 实时安全态势</p>
        </div>
        <MapLegend />
      </div>

      <div class="map-body">
        <div class="map-body__main">
          <div id="map" class="map-container"></div>
          <!-- AMap 未加载兜底 -->
          <div v-if="mapLoadFailed" class="map-fallback">
            <AppIcon name="map" :size="40" />
            <p>地图资源加载中…</p>
            <small>若长时间空白，请刷新页面</small>
          </div>

          <MapMarkerForm
            :isAdding="isAddingMode"
            @add="enableAddMode"
            @refresh="refreshLocation"
            @get-location="getCurrentLocation"
            @cancel="cancelAddMode"
          />

          <div class="map-actions">
            <AppButton variant="primary" size="sm" @click="exportMarkers">
              <template #icon><AppIcon name="download" :size="15" /></template>
              导出标记
            </AppButton>
            <AppButton variant="danger" size="sm" @click="clearAllMarkers">
              <template #icon><AppIcon name="trash" :size="15" /></template>
              清除全部
            </AppButton>
            <AppButton variant="ghost" size="sm" @click="$router.push('/dashboard')">
              <template #icon><AppIcon name="arrow-left" :size="15" /></template>
              返回控制台
            </AppButton>
          </div>
        </div>

        <!-- ═══ 右侧安全统计面板 ═══ -->
        <aside class="map-side">
          <div class="side-panel">
            <div class="side-panel__title">今日安全统计</div>
            <div class="side-stat">
              <span class="side-stat__num">{{ stats.alerts }}</span>
              <span class="side-stat__label">预警次数</span>
            </div>
            <div class="side-stat">
              <span class="side-stat__num side-stat__num--warn">{{ stats.speed }}</span>
              <span class="side-stat__label">超速提醒</span>
            </div>
            <div class="side-stat">
              <span class="side-stat__num side-stat__num--ok">{{ stats.rideTime }}</span>
              <span class="side-stat__label">骑行时长(分)</span>
            </div>
          </div>

          <div class="side-panel">
            <div class="side-panel__title">风险分布</div>
            <div class="bar-row" v-for="b in riskBars" :key="b.label">
              <span class="bar-row__label">{{ b.label }}</span>
              <div class="bar-row__track">
                <div class="bar-row__fill" :style="{ width: b.pct + '%', background: b.color }"></div>
              </div>
              <span class="bar-row__num">{{ b.pct }}%</span>
            </div>
          </div>

          <div class="side-panel">
            <div class="side-panel__title">设备状态</div>
            <div class="kv-row"><span>头盔定位</span><b>在线 · 仙林校区</b></div>
            <div class="kv-row"><span>GPS 精度</span><b>±3.2 m</b></div>
            <div class="kv-row"><span>天气</span><b>晴 · 18°C</b></div>
          </div>
        </aside>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useAmap } from '@/composables/useAmap'
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'
import MapLegend from '@/components/map/MapLegend.vue'
import MapMarkerForm from '@/components/map/MapMarkerForm.vue'

const router = useRouter()
const toast = useToast()
const mapLoadFailed = ref(false)

const {
  isAddingMode,
  initMap,
  loadMarkers,
  renderMarkers,
  addMarker,
  clearMarkers,
  exportMarkers,
  getCurrentPosition,
  updateCurrentLocationMarker,
  startLocationTracking,
  stopLocationTracking,
  enableAddMode: enableAdd,
  cancelAddMode: cancelAdd,
  drawDemoRoute,
  drawDemoAlerts,
  destroy
} = useAmap('map')

// ═══ 演示统计数据（硬件未到货） ═══
const stats = ref({ alerts: 7, speed: 2, rideTime: 46 })
const riskBars = ref([
  { label: '事故高发', pct: 40, color: '#fb7185' },
  { label: '路面障碍', pct: 30, color: '#fbbf24' },
  { label: '缓行提醒', pct: 20, color: '#38bdf8' },
  { label: '安全路段', pct: 10, color: '#34d399' }
])

const newMarkerType = ref('medium')
const newMarkerDesc = ref('')

const enableAddMode = () => {
  enableAdd()
  toast.info('请在地图上点击要添加标记的位置')
}

const handleMapClick = async (e) => {
  if (!isAddingMode.value) return
  const result = await addMarker({
    lng: e.lnglat.getLng(),
    lat: e.lnglat.getLat(),
    type: newMarkerType.value,
    description: newMarkerDesc.value
  })
  if (result) toast.success('标记已添加')
  else toast.error('标记添加失败')
  cancelAdd()
}

const refreshLocation = async () => {
  try {
    toast.info('正在获取位置...')
    const pos = await getCurrentPosition()
    updateCurrentLocationMarker(pos)
    toast.success('位置已更新')
  } catch (err) {
    toast.error(err.message)
  }
}

const getCurrentLocation = async () => {
  try {
    toast.info('正在获取当前位置...')
    const pos = await getCurrentPosition()
    updateCurrentLocationMarker(pos)
    toast.success(`当前位置: ${pos.lat.toFixed(4)}, ${pos.lng.toFixed(4)}`)
  } catch (err) {
    toast.error(err.message)
  }
}

const clearAllMarkers = async () => {
  await clearMarkers()
  toast.success('所有标记已清除')
}

let mapInstance = null

onMounted(async () => {
  const loggedIn = localStorage.getItem('isLoggedIn') || sessionStorage.getItem('isLoggedIn')
  if (loggedIn !== 'true') {
    router.push('/login')
    return
  }
  await loadMarkers()
  // AMap 可能尚未就绪，轮询等待
  let tries = 0
  const tryInit = setInterval(() => {
    tries++
    if (window.AMap) {
      clearInterval(tryInit)
      mapInstance = initMap()
      if (mapInstance) {
        renderMarkers()
        drawDemoRoute()
        drawDemoAlerts()
        // 演示模式：不强依赖浏览器定位失败
        try { startLocationTracking() } catch {}
        mapInstance.on('click', handleMapClick)
      }
    } else if (tries > 20) {
      clearInterval(tryInit)
      mapLoadFailed.value = true
    }
  }, 300)
})

onUnmounted(() => {
  destroy()
})
</script>

<style scoped>
.map-page {
  min-height: 100vh;
  animation: pageEnter 0.5s ease-out;
}

.map-page__content {
  padding: var(--space-xl) var(--space-2xl);
  max-width: 1440px;
  margin: 0 auto;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

.map-header__title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--color-text);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
}

.map-header__title :deep(svg) {
  color: var(--color-primary-500);
  filter: drop-shadow(0 0 8px rgba(34,211,238,0.5));
}

.map-header__sub {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  margin-top: 4px;
}

.map-body {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-lg);
  align-items: start;
}

.map-container {
  width: 100%;
  height: 600px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  border: 1px solid var(--border-color);
  box-shadow: 0 0 30px rgba(34,211,238,0.12), var(--shadow-card);
  position: relative;
}

.map-fallback {
  position: absolute;
  top: 600px;
  margin-top: -600px;
  width: 100%;
  height: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--color-text-secondary);
  background: rgba(7,11,22,0.6);
}
.map-fallback small { color: var(--color-text-tertiary); }

.map-container :deep(img) {
  filter: invert(0.9) hue-rotate(180deg) saturate(0.5) brightness(0.7) contrast(1.1);
}
.map-container :deep(.amap-layer) {
  filter: invert(0.9) hue-rotate(180deg) saturate(0.5) brightness(0.75) contrast(1.1);
}

.map-actions {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
  margin-top: var(--space-md);
}

/* 右侧统计面板 */
.map-side {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.side-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-lg);
  backdrop-filter: blur(14px);
}

.side-panel__title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

.side-stat {
  display: flex;
  align-items: baseline;
  gap: var(--space-sm);
  padding: 6px 0;
}
.side-stat__num {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: #eaf9ff;
  text-shadow: 0 0 16px rgba(34,211,238,0.35);
  min-width: 50px;
}
.side-stat__num--warn { color: var(--color-warning-light); }
.side-stat__num--ok { color: var(--color-success-light); }
.side-stat__label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 12px;
}
.bar-row:last-child { margin-bottom: 0; }
.bar-row__label { width: 60px; color: var(--color-text-secondary); }
.bar-row__track {
  flex: 1; height: 6px;
  background: rgba(120,170,230,0.12);
  border-radius: 3px; overflow: hidden;
}
.bar-row__fill {
  height: 100%; border-radius: 3px;
  box-shadow: 0 0 8px rgba(34,211,238,0.4);
}
.bar-row__num { width: 34px; text-align: right; color: var(--color-text); font-family: var(--font-mono); }

.kv-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: var(--font-size-sm);
  border-bottom: 1px dashed var(--border-color);
}
.kv-row:last-child { border-bottom: none; }
.kv-row span { color: var(--color-text-secondary); }
.kv-row b { color: var(--color-text); font-weight: var(--font-weight-medium); }

@media (max-width: 1100px) {
  .map-body { grid-template-columns: 1fr; }
  .map-container, .map-fallback { height: 420px; }
  .map-fallback { margin-top: -420px; }
}
</style>
