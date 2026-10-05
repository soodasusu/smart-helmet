<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-box__logo">
        <AppIcon name="shield" :size="28" />
      </div>
      <h1>智鉴云卫头盔</h1>

      <form @submit.prevent="handleLogin">
        <AppInput
          v-model="username"
          label="用户名"
          placeholder="请输入用户名"
          required
          autocomplete="username"
        />

        <AppInput
          v-model="password"
          label="密码"
          type="password"
          placeholder="请输入密码"
          required
          autocomplete="current-password"
        />

        <div class="login-options">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe" />
            <span>记住我</span>
          </label>
          <a class="forgot-link" href="javascript:void(0)" @click="toast.info('请联系管理员重置密码')">忘记密码?</a>
        </div>

        <AppButton
          variant="primary"
          size="lg"
          block
          :loading="isLoading"
          @click="handleLogin"
        >
          {{ isLoading ? '登录中...' : '登 录' }}
        </AppButton>
      </form>

      <div class="login-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useVideoStore } from '@/stores/video'
import { useToast } from '@/composables/useToast'
import { login as apiLogin } from '@/services/api'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const videoStore = useVideoStore()
const toast = useToast()

const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const isLoading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    toast.warning('请输入用户名和密码')
    return
  }

  isLoading.value = true

  try {
    const { data } = await apiLogin(username.value, password.value)
    if (data.success) {
      userStore.login({ username: data.username, token: data.token, rememberMe: rememberMe.value })
      videoStore.setCurrentUser(data.username)
      videoStore.init()
      toast.success(`欢迎回来，${data.username}！`)
      const redirect = route.query.redirect || '/dashboard'
      router.push(redirect)
    } else {
      toast.error(data.error || '登录失败')
    }
  } catch {
    // 服务器不可用时降级为离线登录
    userStore.login({ username: username.value || 'test', rememberMe: rememberMe.value })
    videoStore.setCurrentUser(username.value || 'test')
    videoStore.init()
    toast.warning('服务器未连接，已离线登录')
    router.push('/dashboard')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(800px 500px at 20% 20%, rgba(34, 211, 238, 0.18), transparent 60%),
    radial-gradient(700px 500px at 80% 80%, rgba(99, 102, 241, 0.16), transparent 60%),
    #070b16;
}

.login-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(120, 180, 230, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(120, 180, 230, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(circle at center, #000 20%, transparent 75%);
  -webkit-mask-image: radial-gradient(circle at center, #000 20%, transparent 75%);
  pointer-events: none;
}

.login-box {
  position: relative;
  z-index: 1;
  background: rgba(14, 22, 40, 0.55);
  backdrop-filter: blur(22px);
  -webkit-backdrop-filter: blur(22px);
  padding: var(--space-3xl) var(--space-2xl);
  border-radius: var(--radius-2xl);
  border: 1px solid rgba(34, 211, 238, 0.2);
  box-shadow: 0 0 40px rgba(34, 211, 238, 0.12), var(--shadow-lg);
  width: 100%;
  max-width: 400px;
  animation: slideUp 0.4s ease-out;
}

.login-box__logo {
  width: 60px;
  height: 60px;
  margin: 0 auto var(--space-md);
  border-radius: var(--radius-lg);
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.35);
  color: var(--color-primary-500);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.3);
}

.login-box h1 {
  text-align: center;
  color: #eaf9ff;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: 2px;
  margin-bottom: var(--space-2xl);
  text-shadow: 0 0 20px rgba(34, 211, 238, 0.4);
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  accent-color: var(--color-primary-500);
}

.forgot-link {
  font-size: var(--font-size-sm);
  color: var(--color-primary-500);
}

.login-footer {
  text-align: center;
  margin-top: var(--space-xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.login-footer a {
  color: var(--color-primary-500);
  font-weight: var(--font-weight-medium);
}
</style>
