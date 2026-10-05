<template>
  <div class="video-page">
    <div class="video-page__content">
      <div class="video-page__head">
        <h1 class="video-page__title">
          <AppIcon name="video" :size="22" />
          视频管理
        </h1>
      </div>

      <!-- 统计卡片 -->
      <div class="video-stats">
        <AppCard class="video-stat" padding="lg">
          <span class="video-stat__icon"><AppIcon name="video" :size="22" /></span>
          <span class="video-stat__value tabular-nums">{{ todayVideos.length }}</span>
          <span class="video-stat__label">今日视频</span>
        </AppCard>
        <AppCard class="video-stat" padding="lg">
          <span class="video-stat__icon"><AppIcon name="video" :size="22" /></span>
          <span class="video-stat__value tabular-nums">{{ videos.length }}</span>
          <span class="video-stat__label">总视频数</span>
        </AppCard>
      </div>

      <!-- 操作栏 -->
      <div class="video-toolbar">
        <AppButton variant="primary" size="sm" @click="fetchVideos">
          <template #icon><AppIcon name="refresh" :size="15" /></template>
          刷新列表
        </AppButton>
        <div class="video-toolbar__right">
          <select v-model="sortBy" class="video-sort">
            <option value="time">按时间排序</option>
            <option value="name">按名称排序</option>
            <option value="size">按大小排序</option>
          </select>
          <AppButton variant="ghost" size="sm" @click="$router.push('/dashboard')">
            <template #icon><AppIcon name="arrow-left" :size="15" /></template>
            返回控制台
          </AppButton>
        </div>
      </div>

      <!-- 加载状态 -->
      <LoadingSpinner v-if="loading" text="加载视频列表..." />

      <!-- 今日视频 -->
      <template v-else>
        <h2 class="video-section-title">今日视频</h2>
        <EmptyState
          v-if="todayVideos.length === 0"
          icon="video"
          title="今天还没有视频"
          description="头箍连接后会自动录制并上传视频"
        />
        <VideoCard
          v-for="video in sortedTodayVideos"
          :key="video.filename"
          :video="video"
          @play="playVideo"
          @download="downloadVideo"
          @delete="confirmDelete"
        />

        <!-- 全部视频 -->
        <h2 class="video-section-title" style="margin-top: var(--space-2xl)">全部视频</h2>
        <EmptyState
          v-if="videos.length === 0"
          icon="video"
          title="暂无视频记录"
          description="树莓派连接后会自动录制并上传视频"
        />
        <VideoCard
          v-for="video in sortedAllVideos"
          :key="video.filename"
          :video="video"
          @play="playVideo"
          @download="downloadVideo"
          @delete="confirmDelete"
        />
      </template>

      <!-- 视频播放 Modal -->
      <AppModal :visible="showPlayer" :title="playingVideo?.filename" size="lg" @close="showPlayer = false">
        <video
          v-if="showPlayer"
          :src="'/play/' + playingVideo?.filename"
          controls
          autoplay
          style="width:100%;max-height:65vh;border-radius:var(--radius-md);background:#000"
        ></video>
      </AppModal>

      <!-- 删除确认 -->
      <ConfirmDialog
        :visible="showConfirm"
        title="删除视频"
        :message="'确定要删除 ' + (deleteTarget || '') + ' 吗？'"
        @confirm="doDelete"
        @cancel="showConfirm = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { getVideos, deleteVideo } from '@/services/api'
import AppCard from '@/components/common/AppCard.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'
import AppModal from '@/components/common/AppModal.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
import VideoCard from '@/components/video/VideoCard.vue'

const router = useRouter()
const toast = useToast()

const videos = ref([])
const loading = ref(false)
const sortBy = ref('time')
const showPlayer = ref(false)
const playingVideo = ref(null)
const showConfirm = ref(false)
const deleteTarget = ref('')
let refreshInterval = null

// Computed
const todayVideos = computed(() => {
  const today = new Date().toDateString()
  return videos.value.filter(v =>
    v.upload_time && new Date(v.upload_time).toDateString() === today
  )
})

const sortVideos = (list) => {
  return [...list].sort((a, b) => {
    if (sortBy.value === 'name') return (a.filename || '').localeCompare(b.filename || '')
    if (sortBy.value === 'size') return (b.size || 0) - (a.size || 0)
    return new Date(b.upload_time || 0) - new Date(a.upload_time || 0)
  })
}

const sortedTodayVideos = computed(() => sortVideos(todayVideos.value))
const sortedAllVideos = computed(() => sortVideos(videos.value))

// ═══ 演示假数据（硬件未到货时，待机展示用） ═══
const demoVideos = [
  { filename: 'ride_demo_001.mp4', username: 'jhn', upload_time: Date.now() - 3600000, size: 2411724 },
  { filename: 'ride_demo_002.mp4', username: 'jhn', upload_time: Date.now() - 7200000, size: 3812314 },
  { filename: 'crash_alert_001.mp4', username: 'jhn', upload_time: Date.now() - 86400000, size: 5123456 },
  { filename: 'commute_morning.mp4', username: 'jhn', upload_time: Date.now() - 172800000, size: 8234567 }
]

// Actions
const fetchVideos = async () => {
  loading.value = true
  try {
    const { data } = await getVideos()
    videos.value = data.videos || []
    // 后端无数据时，注入演示条目，保证待机状态下界面不空
    if (videos.value.length === 0) {
      videos.value = demoVideos
    }
  } catch {
    // 离线降级为演示数据
    videos.value = [...demoVideos]
  } finally {
    loading.value = false
  }
}

const playVideo = (filename) => {
  playingVideo.value = { filename }
  showPlayer.value = true
}

const downloadVideo = (filename) => {
  window.open(`/download/${filename}`, '_blank')
}

const confirmDelete = (filename) => {
  deleteTarget.value = filename
  showConfirm.value = true
}

const doDelete = async () => {
  try {
    await deleteVideo(deleteTarget.value)
    videos.value = videos.value.filter(v => v.filename !== deleteTarget.value)
    toast.success('视频已删除')
  } catch {
    videos.value = videos.value.filter(v => v.filename !== deleteTarget.value)
    toast.warning('视频已从列表移除（服务器删除功能未实现）')
  } finally {
    showConfirm.value = false
    deleteTarget.value = ''
  }
}

onMounted(() => {
  const loggedIn = localStorage.getItem('isLoggedIn') || sessionStorage.getItem('isLoggedIn')
  if (loggedIn !== 'true') {
    router.push('/login')
    return
  }
  fetchVideos()
  refreshInterval = setInterval(fetchVideos, 10000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
.video-page {
  min-height: 100vh;
}

.video-page__content {
  padding: var(--space-xl) var(--space-2xl);
  max-width: 1200px;
  margin: 0 auto;
}

.video-page__title {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--color-text);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-xl);
  letter-spacing: 0.5px;
}

.video-page__title :deep(svg) {
  color: var(--color-primary-500);
  filter: drop-shadow(0 0 8px rgba(34, 211, 238, 0.5));
}

.video-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.video-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  text-align: center;
}

.video-stat__icon {
  color: var(--color-primary-500);
  display: flex;
}

.video-stat__value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
}

.video-stat__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.video-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.video-toolbar__right {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

.video-sort {
  padding: 7px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--color-bg-input);
  color: var(--color-text);
  font-size: var(--font-size-sm);
  font-family: var(--font-family);
}

.video-section-title {
  color: var(--color-text);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .video-page__content { padding: var(--space-md); }
}
</style>
