/**
 * 主题管理 — 默认浅色，支持深色切换
 * 使用 data-theme 属性 + localStorage 持久化
 */

import { ref, onMounted } from 'vue'

const THEME_KEY = 'app-theme'
const theme = ref('light') // 默认浅色

export function useTheme() {
  onMounted(() => {
    const saved = localStorage.getItem(THEME_KEY)
    if (saved === 'light' || saved === 'dark') {
      theme.value = saved
    } else {
      theme.value = 'light'
    }
    applyTheme()
  })

  const applyTheme = () => {
    document.documentElement.setAttribute('data-theme', theme.value)
    localStorage.setItem(THEME_KEY, theme.value)
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    applyTheme()
  }

  const isDark = () => theme.value === 'dark'
  const isLight = () => theme.value === 'light'

  return { theme, toggleTheme, isDark, isLight }
}
