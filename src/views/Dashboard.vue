<template>
  <div class="dashboard">
    <div class="dashboard__content">
      <!-- KPI 统计 -->
      <DashboardStats
        :todayVideos="todayVideoCount"
        :totalVideos="totalVideoCount"
        :helmetOnline="helmetOnline"
        :recording="recording"
        :usageStats="usageStats"
      />

      <div class="dashboard__grid">
        <!-- 左：图表 + 动态 -->
        <div class="dashboard__left">
          <!-- 近7天活动趋势图 -->
          <div class="chart-card">
            <div class="chart-card__head">
              <h2 class="section-title">近 7 天活动趋势</h2>
              <span class="chart-card__legend"><i></i> 操作次数</span>
            </div>
            <svg class="trend-chart" viewBox="0 0 320 120" preserveAspectRatio="none">
              <defs>
                <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <line x1="0" y1="30" x2="320" y2="30" stroke="rgba(120,170,230,0.12)" stroke-dasharray="3 4"/>
              <line x1="0" y1="60" x2="320" y2="60" stroke="rgba(120,170,230,0.12)" stroke-dasharray="3 4"/>
              <line x1="0" y1="90" x2="320" y2="90" stroke="rgba(120,170,230,0.12)" stroke-dasharray="3 4"/>
              <path :d="areaPath" fill="url(#trendFill)"/>
              <path :d="linePath" fill="none" stroke="#22d3ee" stroke-width="2.5"
                    stroke-linecap="round" stroke-linejoin="round"/>
              <circle v-for="(p, i) in chartPoints" :key="i" :cx="p.x" :cy="p.y" r="3.5"
                      fill="#070b16" stroke="#22d3ee" stroke-width="2"/>
            </svg>
            <div class="chart-x">
              <span v-for="(d, i) in weekLabels" :key="i">{{ d }}</span>
            </div>
          </div>

          <!-- 快捷功能 -->
          <h2 class="section-title" style="margin-top: var(--space-2xl)">快捷功能</h2>
          <div class="feature-grid">
            <FeatureCard
              icon="map"
              title="预警地图"
              description="查看危险预警事件位置"
              @click="$router.push('/map')"
            />
            <FeatureCard
              icon="video"
              title="视频管理"
              description="查看和管理录制视频"
              @click="$router.push('/videos')"
            />
            <FeatureCard
              icon="bluetooth"
              title="头盔连接"
              description="蓝牙通信与硬件控制"
              @click="$router.push('/connect')"
            />
          </div>

          <!-- 使用统计 -->
          <h2 class="section-title" style="margin-top: var(--space-2xl)">使用统计</h2>
          <div class="usage-stats-row">
            <AppCard class="usage-stat" padding="md">
              <span class="usage-stat__value tabular-nums">{{ usageStats.total_logins || 0 }}</span>
              <span class="usage-stat__label">总登录次数</span>
            </AppCard>
            <AppCard class="usage-stat" padding="md">
              <span class="usage-stat__value tabular-nums">{{ usageStats.total_uploads || 0 }}</span>
              <span class="usage-stat__label">视频上传</span>
            </AppCard>
            <AppCard class="usage-stat" padding="md">
              <span class="usage-stat__value tabular-nums">{{ usageStats.total_commands || 0 }}</span>
              <span class="usage-stat__label">命令执行</span>
            </AppCard>
            <AppCard class="usage-stat" padding="md">
              <span class="usage-stat__value tabular-nums">{{ usageStats.today_activities || 0 }}</span>
              <span class="usage-stat__label">今日活动</span>
            </AppCard>
          </div>

          <!-- 最近动态 -->
          <h2 class="section-title" style="margin-top: var(--space-2xl)">最近动态</h2>
          <LoadingSpinner v-if="loadingActivities" text="加载动态..." size="sm" />
          <AppCard padding="lg" v-else-if="activityLog.length > 0">
            <div class="activity-list">
              <div v-for="(item, i) in activityLog" :key="i" class="activity-item">
                <span class="activity-item__icon"><AppIcon :name="item.icon" :size="16" /></span>
                <span class="activity-item__text">
                  <strong>{{ item.username || '系统' }}</strong>
                  {{ item.text }}
                </span>
                <span class="activity-item__time">{{ item.time }}</span>
              </div>
            </div>
          </AppCard>
          <EmptyState
            v-else
            icon="activity"
            title="暂无动态"
            description="当有新的视频上传、用户登录或头箍状态变化时，动态会显示在这里"
          />
        </div>

        <!-- 右：实时概览 -->
        <div class="dashboard__right">
          <AppCard padding="lg" class="overview-card">
            <h3 class="overview-title">实时状态</h3>
            <div class="overview-row">
              <span>头盔链路</span>
              <b :class="{ 'is-on': helmetOnline }">{{ helmetOnline ? '已连接' : '待机' }}</b>
            </div>
            <div class="overview-row">
              <span>录制状态</span>
              <b :class="{ 'is-on': recording }">{{ recording ? '录制中' : '未录制' }}</b>
            </div>
            <div class="overview-row">
              <span>GPS 定位</span>
              <b class="is-on">仙林校区</b>
            </div>
            <div class="overview-row">
              <span>今日预警</span>
              <b>7 次</b>
            </div>
          </AppCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useVideoStore } from '@/stores/video'
import { useSocket } from '@/composables/useSocket'
import { useToast } from '@/composables/useToast'
import { getVideos, getActivityLogs, getUsageStats } from '@/services/api'
import AppCard from '@/components/common/AppCard.vue'
import AppIcon from '@/components/common/AppIcon.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import DashboardStats from '@/components/dashboard/DashboardStats.vue'
import FeatureCard from '@/components/dashboard/FeatureCard.vue'

const router = useRouter()
const userStore = useUserStore()
const videoStore = useVideoStore()
const toast = useToast()
const { isConnected, helmetOnline, recording } = useSocket()

const totalVideos = ref([])
const todayVideoCount = ref(0)
const totalVideoCount = ref(0)
const activityLog = reactive([])
const loadingActivities = ref(false)
const usageStats = reactive({
  total_logins: 0,
  total_uploads: 0,
  total_commands: 0,
  today_activities: 0
})

const setHelmetStatus = inject('setHelmetStatus', null)

// ═══ 近7天活动趋势（演示数据） ═══
const weekLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '今天']
const trendData = ref([4, 7, 5, 9, 6, 11, 8])
const chartPoints = computed(() => {
  const max = Math.max(...trendData.value)
  return trendData.value.map((v, i) => ({
    x: 20 + i * (280 / (trendData.value.length - 1)),
    y: 100 - (v / (max + 2)) * 85
  }))
})
const linePath = computed(() =>
  chartPoints.value.map((p, i) => (i === 0 ? `M${p.x},${p.y}` : `L${p.x},${p.y}`)).join(' ')
)
const areaPath = computed(() =>
  linePath.value + ` L${chartPoints.value[chartPoints.value.length - 1].x},110 L${chartPoints.value[0].x},110 Z`
)

const actionIcons = {
  login: 'key',
  login_failed: 'x-circle',
  register: 'users',
  video_upload: 'video',
  video_delete: 'trash',
  logout: 'logout',
  command: 'activity'
}

const formatActionText = (action, details) => {
  const map = {
    login: '登录成功',
    login_failed: '登录失败',
    register: '注册了新账号',
    video_upload: details || '上传了新视频',
    video_delete: details || '删除了视频',
    logout: '退出登录'
  }
  return map[action] || details || action
}

const fetchActivityLogs = async () => {
  loadingActivities.value = true
  try {
    const { data } = await getActivityLogs(30)
    const logs = data.logs || []
    activityLog.length = 0
    logs.forEach(item => {
      activityLog.push({
        icon: actionIcons[item.action] || 'circle',
        username: item.username,
        text: formatActionText(item.action, item.details),
        time: formatTime(item.created_at)
      })
    })
  } catch { /* 静默 */ } finally {
    loadingActivities.value = false
  }
}

const fetchUsageStats = async () => {
  try {
    const { data } = await getUsageStats()
    Object.assign(usageStats, data)
  } catch { /* 静默 */ }
}

const addLocalActivity = (icon, text) => {
  const now = new Date()
  activityLog.unshift({
    icon,
    username: userStore.username || '系统',
    text,
    time: now.toLocaleTimeString('zh-CN')
  })
  if (activityLog.length > 100) activityLog.pop()
}

const formatTime = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff/60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff/3600000)} 小时前`
  return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN')
}

const fetchVideos = async () => {
  try {
    const { data } = await getVideos()
    totalVideos.value = data.videos || []
    totalVideoCount.value = totalVideos.value.length
    const today = new Date().toDateString()
    todayVideoCount.value = totalVideos.value.filter(v =>
      v.upload_time && new Date(v.upload_time).toDateString() === today
    ).length
  } catch { /* 静默 */ }
}

watch(helmetOnline, (val) => {
  if (setHelmetStatus) setHelmetStatus(val ? 'online' : 'offline')
})

let refreshTimer = null

onMounted(async () => {
  userStore.initFromStorage()
  videoStore.init()
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  await Promise.all([fetchVideos(), fetchActivityLogs(), fetchUsageStats()])
  refreshTimer = setInterval(() => {
    fetchVideos()
    fetchActivityLogs()
    fetchUsageStats()
  }, 15000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
}

.dashboard__content {
  padding: var(--space-xl) var(--space-2xl);
  max-width: 1400px;
  margin: 0 auto;
}

.section-title {
  color: var(--color-text);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-lg);
}

.dashboard__grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-2xl);
  align-items: start;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

/* 趋势图卡片 */
.chart-card {
  background: var(--color-bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: var(--space-lg) var(--space-xl);
  backdrop-filter: blur(14px);
}
.chart-card__head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}
.chart-card__legend {
  display: flex; align-items: center; gap: 6px;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}
.chart-card__legend i {
  width: 10px; height: 3px; border-radius: 2px;
  background: #22d3ee;
  box-shadow: 0 0 6px #22d3ee;
}
.trend-chart {
  width: 100%;
  height: 140px;
}
.chart-x {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 11px;
  color: var(--color-text-tertiary);
}

/* 使用统计 */
.usage-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-sm);
}
.usage-stat {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.usage-stat__value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: #eaf9ff;
  text-shadow: 0 0 14px rgba(34,211,238,0.3);
}
.usage-stat__label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 动态流 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}
.activity-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--border-color);
  font-size: var(--font-size-sm);
}
.activity-item:last-child { border-bottom: none; }
.activity-item__icon {
  color: var(--color-primary-500);
  flex-shrink: 0;
  display: flex;
}
.activity-item__text { flex: 1; color: var(--color-text); }
.activity-item__text strong {
  color: var(--color-text);
  font-weight: var(--font-weight-semibold);
  margin-right: 4px;
}
.activity-item__time {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
  white-space: nowrap;
}

/* 右侧概览 */
.overview-card {
  position: sticky;
  top: calc(var(--header-height) + 20px);
}
.overview-title {
  font-size: var(--font-size-md);
  color: var(--color-text);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}
.overview-row {
  display: flex;
  justify-content: space-between;
  padding: 9px 0;
  font-size: var(--font-size-sm);
  border-bottom: 1px dashed var(--border-color);
}
.overview-row:last-child { border-bottom: none; }
.overview-row span { color: var(--color-text-secondary); }
.overview-row b {
  color: var(--color-text);
  font-weight: var(--font-weight-medium);
}
.overview-row b.is-on { color: var(--color-success); }

@media (max-width: 1024px) {
  .dashboard__grid { grid-template-columns: 1fr; }
  .usage-stats-row { grid-template-columns: repeat(2, 1fr); }
  .feature-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 768px) {
  .dashboard__content { padding: var(--space-md); }
  .feature-grid { grid-template-columns: 1fr; }
  .usage-stats-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
