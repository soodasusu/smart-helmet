<template>
  <div class="app-layout">
    <AppSidebar :collapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />
    <div class="app-layout__main" :class="{ 'app-layout__main--expanded': sidebarCollapsed }">
      <AppHeader
        :helmetStatus="helmetStatus"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
      />
      <main class="app-layout__content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, provide } from 'vue'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'

const sidebarCollapsed = ref(false)
const helmetStatus = ref('offline')

provide('helmetStatus', helmetStatus)
provide('setHelmetStatus', (status) => { helmetStatus.value = status })
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
}

.app-layout__main {
  flex: 1;
  margin-left: var(--sidebar-width);
  transition: margin-left var(--transition-slow);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-layout__main--expanded {
  margin-left: var(--sidebar-collapsed-width);
}

.app-layout__content {
  flex: 1;
  position: relative;
}
</style>
