/**
 * Loading 状态管理 — 计数器模式支持并发操作
 * const { isLoading, start, stop } = useLoading()
 */

import { ref, computed } from 'vue'

export function useLoading() {
  const counter = ref(0)

  const isLoading = computed(() => counter.value > 0)

  const start = () => { counter.value++ }
  const stop = () => { if (counter.value > 0) counter.value-- }

  /**
   * 包装异步函数，自动管理 loading 状态
   */
  const wrap = async (fn) => {
    start()
    try {
      return await fn()
    } finally {
      stop()
    }
  }

  return { isLoading, start, stop, wrap }
}
