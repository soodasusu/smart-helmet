import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getToken } from '@/services/api'

function authHeaders() {
  const token = getToken()
  return token
    ? { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }
    : { 'Content-Type': 'application/json' }
}

export const useVideoStore = defineStore('video', () => {
  const videos = ref([])
  const currentUsername = ref('')
  const isLoading = ref(false)
  const lastFetched = ref(null)

  const getAllVideos = computed(() => videos.value)

  const getTodayVideos = computed(() => {
    const today = new Date().toDateString()
    return videos.value.filter(video => {
      if (!video.upload_time) return false
      return new Date(video.upload_time).toDateString() === today
    })
  })

  const getVideosByUsername = computed(() => {
    return (username) => videos.value.filter(v => v.username === username)
  })

  const getTodayVideosByUsername = computed(() => {
    return (username) => {
      const today = new Date().toDateString()
      return videos.value.filter(v => {
        if (!v.upload_time) return false
        return new Date(v.upload_time).toDateString() === today && v.username === username
      })
    }
  })

  // ═══ 从服务器获取视频列表 ═══
  async function fetchFromServer() {
    isLoading.value = true
    try {
      const response = await fetch('/get_videos')
      const data = await response.json()
      if (data.videos) {
        videos.value = data.videos
        lastFetched.value = Date.now()
        // 缓存到本地作为离线备份
        saveToStorage()
      }
    } catch (err) {
      // 降级：从本地缓存加载
      loadFromStorage()
    } finally {
      isLoading.value = false
    }
  }

  // ═══ 删除视频 ═══
  async function deleteVideo(filename) {
    try {
      await fetch('/api/delete_video', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ filename })
      })
    } catch {
      // API 可能不存在，静默处理
    }
    videos.value = videos.value.filter(v => v.filename !== filename)
    saveToStorage()
  }

  // ═══ 重命名视频 ═══
  async function renameVideo(oldFilename, newFilename) {
    try {
      await fetch('/rename_video', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          old_filename: oldFilename,
          new_filename: newFilename,
          username: currentUsername.value
        })
      })
      const video = videos.value.find(v => v.filename === oldFilename)
      if (video) {
        video.filename = newFilename
        video.custom_name = newFilename
      }
    } catch {
      // 静默处理
    }
  }

  // ═══ 本地操作 ═══
  function addVideo(videoName, username = null) {
    const newVideo = {
      id: Date.now(),
      name: videoName,
      filename: videoName,
      username: username || currentUsername.value,
      upload_time: new Date().toISOString(),
      size: 0
    }
    videos.value.push(newVideo)
    saveToStorage()
    return newVideo
  }

  function removeVideo(filename) {
    videos.value = videos.value.filter(v => v.filename !== filename)
    saveToStorage()
  }

  function setCurrentUser(username) {
    currentUsername.value = username
  }

  // ═══ 本地存储 ═══
  function saveToStorage() {
    try {
      localStorage.setItem('cachedVideos', JSON.stringify(videos.value.slice(0, 100)))
    } catch { /* quota exceeded */ }
  }

  function loadFromStorage() {
    try {
      const stored = localStorage.getItem('cachedVideos')
      if (stored) videos.value = JSON.parse(stored)
    } catch { videos.value = [] }
  }

  function init() {
    loadFromStorage()
  }

  return {
    videos,
    currentUsername,
    isLoading,
    lastFetched,
    getAllVideos,
    getTodayVideos,
    getVideosByUsername,
    getTodayVideosByUsername,
    fetchFromServer,
    deleteVideo,
    renameVideo,
    addVideo,
    removeVideo,
    setCurrentUser,
    init,
    loadFromStorage,
    saveToStorage
  }
})
