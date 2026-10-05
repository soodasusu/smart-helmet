import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const username = ref('')
  const token = ref('')
  const isLoggedIn = ref(false)
  const rememberMe = ref(false)
  const loginError = ref('')

  const getUsername = computed(() => username.value)
  const getIsLoggedIn = computed(() => isLoggedIn.value)
  const getToken = computed(() => token.value)

  function login(user) {
    username.value = user.username
    token.value = user.token || ''
    isLoggedIn.value = true
    rememberMe.value = user.rememberMe || false
    loginError.value = ''

    const storage = rememberMe.value ? localStorage : sessionStorage
    storage.setItem('isLoggedIn', 'true')
    storage.setItem('username', user.username)
    storage.setItem('token', token.value)
    if (rememberMe.value) storage.setItem('rememberMe', 'true')
  }

  function logout() {
    username.value = ''
    token.value = ''
    isLoggedIn.value = false
    rememberMe.value = false
    loginError.value = ''
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('username')
    localStorage.removeItem('token')
    localStorage.removeItem('rememberMe')
    sessionStorage.removeItem('isLoggedIn')
    sessionStorage.removeItem('username')
    sessionStorage.removeItem('token')
  }

  function initFromStorage() {
    // 先检查 localStorage (持久化)，再检查 sessionStorage (会话)
    const storedLogin = localStorage.getItem('isLoggedIn') || sessionStorage.getItem('isLoggedIn')
    const storedUsername = localStorage.getItem('username') || sessionStorage.getItem('username')
    const storedToken = localStorage.getItem('token') || sessionStorage.getItem('token')
    const storedRemember = localStorage.getItem('rememberMe')

    if (storedLogin === 'true' && storedUsername) {
      isLoggedIn.value = true
      username.value = storedUsername
      token.value = storedToken || ''
      rememberMe.value = storedRemember === 'true'
    }
  }

  return {
    username,
    token,
    isLoggedIn,
    rememberMe,
    loginError,
    getUsername,
    getIsLoggedIn,
    getToken,
    login,
    logout,
    initFromStorage
  }
})
