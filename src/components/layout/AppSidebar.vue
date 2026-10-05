<template>
  <aside class="sidebar" :class="{ 'sidebar--collapsed': collapsed }">
    <div class="sidebar__brand" @click="$emit('toggle')">
      <span class="sidebar__logo"><AppIcon name="shield" :size="24" /></span>
      <span v-show="!collapsed" class="sidebar__brand-text">智鉴云卫</span>
    </div>

    <nav class="sidebar__nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="sidebar__link"
        :class="{ 'sidebar__link--active': isActive(item.path) }"
        :title="collapsed ? item.label : ''"
      >
        <span class="sidebar__link-icon"><AppIcon :name="item.icon" :size="20" /></span>
        <span v-show="!collapsed" class="sidebar__link-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar__footer">
      <div class="sidebar__user" :title="collapsed ? username : ''">
        <span class="sidebar__avatar">{{ avatarLetter }}</span>
        <span v-show="!collapsed" class="sidebar__username">{{ username }}</span>
      </div>
      <button class="sidebar__logout" @click="handleLogout" :title="collapsed ? '退出登录' : ''">
        <span class="sidebar__logout-icon"><AppIcon name="logout" :size="18" /></span>
        <span v-show="!collapsed" class="sidebar__logout-text">退出登录</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import AppIcon from '@/components/common/AppIcon.vue'

defineProps({
  collapsed: { type: Boolean, default: false }
})

defineEmits(['toggle'])

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const username = computed(() => userStore.username || '用户')
const avatarLetter = computed(() => username.value.charAt(0).toUpperCase())

const navItems = [
  { path: '/dashboard', icon: 'dashboard', label: '控制台' },
  { path: '/connect', icon: 'bluetooth', label: '头盔连接' },
  { path: '/map', icon: 'map', label: '预警地图' },
  { path: '/videos', icon: 'video', label: '视频管理' }
]

const isActive = (path) => route.path.startsWith(path)

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: var(--color-bg-sidebar);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: var(--z-sidebar);
  transition: width var(--transition-slow);
  overflow: hidden;
}

.sidebar--collapsed {
  width: var(--sidebar-collapsed-width);
}

/* ── Brand ── */
.sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 0 var(--space-lg);
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  min-height: var(--header-height);
}

.sidebar__logo {
  color: var(--color-primary-500);
  display: flex;
  flex-shrink: 0;
  filter: drop-shadow(0 0 8px rgba(34, 211, 238, 0.6));
}

.sidebar__brand-text {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  letter-spacing: 1px;
  white-space: nowrap;
  background: linear-gradient(120deg, #eaf9ff, #22d3ee);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ── Nav ── */
.sidebar__nav {
  flex: 1;
  padding: var(--space-md) var(--space-sm);
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
  white-space: nowrap;
  position: relative;
}

.sidebar__link:hover {
  background: rgba(34, 211, 238, 0.07);
  color: var(--color-text);
}

.sidebar__link--active {
  background: rgba(34, 211, 238, 0.12);
  color: var(--color-primary-500);
  font-weight: var(--font-weight-semibold);
  box-shadow: inset 0 0 14px rgba(34, 211, 238, 0.08);
}

.sidebar__link--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 3px;
  border-radius: 3px;
  background: var(--color-primary-500);
  box-shadow: 0 0 10px var(--color-primary-500);
}

.sidebar__link-icon {
  display: flex;
  flex-shrink: 0;
}

.sidebar__link-label { overflow: hidden; }

/* ── Footer ── */
.sidebar__footer {
  padding: var(--space-md);
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sidebar__user {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
}

.sidebar__avatar {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-700));
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-md);
  color: #04121c;
  flex-shrink: 0;
  box-shadow: 0 0 12px rgba(34, 211, 238, 0.4);
}

.sidebar__username {
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.sidebar__logout {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 9px 12px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-danger);
  cursor: pointer;
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  transition: background var(--transition-fast);
}

.sidebar__logout:hover {
  background: var(--color-danger-bg);
}

.sidebar__logout-icon {
  display: flex;
  flex-shrink: 0;
}
</style>
