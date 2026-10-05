/**
 * Socket.IO 连接管理 — 单例模式
 * 全局共享一个 socket 实例，自动处理连接/重连
 */

import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { useNotification } from './useNotification'
import { useUserStore } from '@/stores/user'

let socketInstance = null
let socketRefCount = 0

export function useSocket() {
  const isConnected = ref(false)
  const helmetOnline = ref(false)
  const recording = ref(false)
  const detectionEnabled = ref(false)
  const lastEvent = ref(null)
  const { handleSocketEvent } = useNotification()

  // 初始化单例 socket
  if (!socketInstance) {
    socketInstance = io({
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 10000
    })

    // 连接事件
    socketInstance.on('connect', () => {
      socketInstance.emit('web_identify', {})
      isConnected.value = true
    })

    socketInstance.on('disconnect', () => {
      isConnected.value = false
      helmetOnline.value = false
    })

    // 服务端推送
    socketInstance.on('pi_status_update', (data) => {
      helmetOnline.value = data?.online || false
      recording.value = data?.recording || false
      lastEvent.value = { type: 'pi_status', data, time: Date.now() }
      handleSocketEvent('pi_status_update', data)
    })

    socketInstance.on('web_response', (data) => {
      lastEvent.value = { type: 'web_response', data, time: Date.now() }
      handleSocketEvent('web_response', data)
    })
  }

  // 引用计数
  socketRefCount++

  // 同步初始状态
  isConnected.value = socketInstance.connected

  // 组件卸载时自动减少引用
  onUnmounted(() => {
    socketRefCount--
    // 注意：不在这里断开 socket，因为是全局单例
  })

  /**
   * 发送控制命令到树莓派
   */
  const sendCommand = (command, params = {}) => {
    if (!socketInstance?.connected) {
      return { success: false, error: '未连接到服务器' }
    }
    let username = 'web_user'
    try {
      const userStore = useUserStore()
      username = userStore.username || 'web_user'
    } catch {}
    socketInstance.emit('web_command', { command, params, username })
    return { success: true }
  }

  /**
   * 发送 WebSocket 消息（通用）
   */
  const emit = (event, data) => {
    if (!socketInstance?.connected) return false
    socketInstance.emit(event, data)
    return true
  }

  return {
    socket: socketInstance,
    isConnected,
    helmetOnline,
    recording,
    detectionEnabled,
    lastEvent,
    sendCommand,
    emit
  }
}

/**
 * 断开全局 socket（应用退出时调用）
 */
export function disconnectSocket() {
  if (socketInstance) {
    socketInstance.disconnect()
    socketInstance = null
    socketRefCount = 0
  }
}
