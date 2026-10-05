<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-box__logo">
        <AppIcon name="shield" :size="28" />
      </div>
      <h1>注册账号</h1>
      <p class="register-subtitle">创建您的智鉴云卫账户</p>

      <form @submit.prevent="handleRegister">
        <AppInput
          v-model="registerForm.username"
          label="用户名"
          placeholder="至少3个字符"
          required
        />

        <AppInput
          v-model="registerForm.password"
          label="密码"
          type="password"
          placeholder="至少6个字符"
          required
        />

        <AppInput
          v-model="registerForm.confirmPassword"
          label="确认密码"
          type="password"
          placeholder="请再次输入密码"
          required
        />

        <AppButton
          variant="primary"
          size="lg"
          block
          :loading="isLoading"
          @click="handleRegister"
        >
          {{ isLoading ? '注册中...' : '注 册' }}
        </AppButton>
      </form>

      <div class="register-footer">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useVideoStore } from '@/stores/video'
import { useToast } from '@/composables/useToast'
import { register as apiRegister } from '@/services/api'
import AppInput from '@/components/common/AppInput.vue'
import AppButton from '@/components/common/AppButton.vue'
import AppIcon from '@/components/common/AppIcon.vue'

const router = useRouter()
const userStore = useUserStore()
const videoStore = useVideoStore()
const toast = useToast()
const isLoading = ref(false)

const registerForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    toast.error('两次输入的密码不一致')
    return
  }

  if (registerForm.value.username.length < 3) {
    toast.warning('用户名长度至少为3个字符')
    return
  }

  if (registerForm.value.password.length < 6) {
    toast.warning('密码长度至少为6个字符')
    return
  }

  isLoading.value = true

  try {
    const { data } = await apiRegister(registerForm.value.username, registerForm.value.password)
    if (data.success) {
      userStore.login({ username: registerForm.value.username, token: data.token })
      videoStore.setCurrentUser(registerForm.value.username)
      videoStore.init()
      toast.success('注册成功！')
      router.push('/dashboard')
    } else {
      toast.error(data.error || '注册失败')
    }
  } catch {
    toast.error('网络错误，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-lg);
  background: var(--color-bg-page);
}

.register-box {
  background: #fff;
  padding: var(--space-3xl) var(--space-2xl);
  border-radius: var(--radius-2xl);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 400px;
  animation: slideUp 0.4s ease-out;
}

.register-box__logo {
  width: 56px;
  height: 56px;
  margin: 0 auto var(--space-md);
  border-radius: var(--radius-lg);
  background: var(--color-primary-50);
  color: var(--color-primary-500);
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-box h1 {
  text-align: center;
  color: var(--color-text);
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  letter-spacing: 1px;
}

.register-subtitle {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin: var(--space-xs) 0 var(--space-2xl);
}

.register-footer {
  text-align: center;
  margin-top: var(--space-xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.register-footer a {
  color: var(--color-primary-500);
  font-weight: var(--font-weight-medium);
}
</style>
