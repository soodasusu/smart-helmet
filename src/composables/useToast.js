/**
 * Toast 通知系统
 * 使用方式：const toast = useToast(); toast.success('操作成功');
 *
 * 需要在 App.vue 中放置 <AppToast ref="toastRef" /> 并通过 provide 共享
 */

import { inject } from 'vue'

export function useToast() {
  const toast = inject('$toast', null)
  if (!toast) {
    // 降级：没有 toast 实例时使用 console + alert
    return {
      success: (msg) => console.log('✅', msg),
      error: (msg) => { console.error('❌', msg); alert(msg) },
      warning: (msg) => console.warn('⚠️', msg),
      info: (msg) => console.log('ℹ️', msg)
    }
  }
  return toast
}

/**
 * 创建 toast 提供器 — 在 setup 中调用
 * 返回 { toastRef, provideToast }
 */
import { ref, provide, onMounted } from 'vue'

export function createToastProvider() {
  const toastRef = ref(null)

  onMounted(() => {
    if (toastRef.value) {
      provide('$toast', toastRef.value)
    }
  })

  // 双重确保 provide 在 setup 阶段就执行
  const toast_proxy = {
    success: (msg) => toastRef.value?.success(msg),
    error: (msg) => toastRef.value?.error(msg),
    warning: (msg) => toastRef.value?.warning(msg),
    info: (msg) => toastRef.value?.info(msg)
  }
  provide('$toast', toast_proxy)

  return { toastRef, toast: toast_proxy }
}
