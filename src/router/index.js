import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import Connect from '../views/Connect.vue'
import Map from '../views/Map.vue'
import VideoManager from '../views/VideoManager.vue'
import AppLayout from '../components/layout/AppLayout.vue'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册', guest: true }
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '控制台' }
      },
      {
        path: 'connect',
        name: 'Connect',
        component: Connect,
        meta: { title: '头盔连接' }
      },
      {
        path: 'map',
        name: 'Map',
        component: Map,
        meta: { title: '预警地图' }
      },
      {
        path: 'videos',
        name: 'Videos',
        component: VideoManager,
        meta: { title: '视频管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ═══ 导航守卫 ═══
router.beforeEach((to, from, next) => {
  // Pinia stores 需要在 router 内部创建
  // 这里使用动态导入避免循环依赖
  let userStore
  try {
    userStore = useUserStore()
  } catch {
    // Pinia not yet installed, skip guard
    next()
    return
  }

  // 需要认证的路由
  if (to.matched.some(r => r.meta.requiresAuth)) {
    if (!userStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
  }

  // guest 路由（登录/注册），已登录则跳转
  if (to.meta.guest && userStore.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

// 动态设置页面标题
router.afterEach((to) => {
  const title = to.meta.title
    ? `${to.meta.title} - 智鉴云卫`
    : '智鉴云卫头盔 - 智能驾驶监控系统'
  document.title = title
})

export default router
