/**
 * API 服务层 — 中心化 HTTP 请求
 * 所有后端通信统一走此模块
 */

import axios from 'axios'

const http = axios.create({
  baseURL: '/',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// ═══ 从本地存储读取登录 token ═══
export function getToken() {
  return localStorage.getItem('token') || sessionStorage.getItem('token')
}

// ═══ 请求拦截器：自动附带 Authorization 头 ═══
http.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ═══ 认证 ═══

export function login(username, password) {
  return http.post('/api/login', { username, password })
}

export function register(username, password) {
  return http.post('/api/register', { username, password })
}

// ═══ 视频 ═══

export function getVideos() {
  return http.get('/get_videos')
}

export function uploadVideo(formData) {
  return http.post('/upload_video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function deleteVideo(filename) {
  return http.post('/api/delete_video', { filename })
}

export function renameVideo(old_filename, new_filename, username) {
  return http.post('/rename_video', { old_filename, new_filename, username })
}

export function getPlayUrl(filename) {
  return `/play/${filename}`
}

export function getDownloadUrl(filename) {
  return `/download/${filename}`
}

// ═══ 活动日志 & 统计数据 ═══

export function getActivityLogs(limit = 50, username = null) {
  const params = { limit }
  if (username) params.username = username
  return http.get('/api/activity_logs', { params })
}

export function getUsageStats(username = null) {
  const params = {}
  if (username) params.username = username
  return http.get('/api/usage_stats', { params })
}

export function getCommandHistory(limit = 20, username = null) {
  const params = { limit }
  if (username) params.username = username
  return http.get('/api/command_history', { params })
}

// ═══ 命令（旧版 HTTP 轮询） ═══

export function sendCommandHttp(command) {
  return http.post('/command_raspberry', { command })
}

export function getCommand() {
  return http.get('/get_command')
}

// ═══ 预警事件 / 地图标记 ═══

export function getAlerts(filters = {}) {
  return http.get('/api/alerts', { params: filters })
}

export function createAlert(data) {
  return http.post('/api/alerts', data)
}

export function updateAlert(id, data) {
  return http.patch(`/api/alerts/${id}`, data)
}

export function deleteAlerts(source = null) {
  const params = {}
  if (source) params.source = source
  return http.delete('/api/alerts', { params })
}

// ═══ 设备 ═══

export function registerDevice(data) {
  return http.post('/api/devices/register', data)
}

export function getDevices() {
  return http.get('/api/devices')
}

export default http
