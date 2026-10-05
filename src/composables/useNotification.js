/**
 * 通知系统 — 整合 toast + 浏览器 Notification API
 * 用于 Socket.IO 事件自动弹通知
 */

import { useToast } from './useToast'

export function useNotification() {
  const toast = useToast()

  /**
   * 请求浏览器通知权限
   */
  const requestPermission = async () => {
    if (!('Notification' in window)) return 'denied'
    if (Notification.permission === 'granted') return 'granted'
    return await Notification.requestPermission()
  }

  /**
   * 发送浏览器桌面通知
   */
  const notifyDesktop = (title, options = {}) => {
    if (!('Notification' in window)) return
    if (Notification.permission !== 'granted') return

    new Notification(title, {
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      ...options
    })
  }

  /**
   * 通用通知 — toast + 桌面（如已授权）
   */
  const notify = (message, type = 'info', title = '智鉴云卫') => {
    // Toast 通知
    if (type === 'success') toast.success(message)
    else if (type === 'error') toast.error(message)
    else if (type === 'warning') toast.warning(message)
    else toast.info(message)

    // 桌面通知（仅对重要事件）
    if (type === 'success' || type === 'error') {
      notifyDesktop(title, { body: message })
    }
  }

  /**
   * 处理 Socket.IO 事件通知
   */
  const handleSocketEvent = (eventName, data) => {
    const eventMap = {
      pi_status_update: () => {
        const status = data?.online ? 'online' : 'offline'
        const msg = data?.online ? '树莓派已连接' : '树莓派已断开'
        toast.info(msg)
      },
      web_response: () => {
        if (data?.status === 'error') {
          toast.error(data?.message || '命令执行失败')
        } else if (data?.message) {
          toast.success(data?.message)
        }
      },
      video_uploaded: () => {
        toast.success(`新视频已上传: ${data?.filename || '未知文件'}`)
      }
    }

    const handler = eventMap[eventName]
    if (handler) handler()
  }

  return {
    toast,
    requestPermission,
    notifyDesktop,
    notify,
    handleSocketEvent
  }
}
