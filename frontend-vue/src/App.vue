<template>
  <div class="container" :class="{ 'fullpage': isFullPage }">
    <TopBar v-if="!isFullPage" />
    <header v-if="!isFullPage" class="header">
      <h1 class="logo">
        <i class="fas fa-music" />
        意韵成音
      </h1>
      <p class="tagline">让文字与图片蕴含的情感绽放出音乐的魅力</p>
    </header>

    <main class="main-content">
      <router-view />
    </main>
  </div>
  <Notification />
  <Loading />
</template>

<script setup lang="ts">
import { ref, provide, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import Notification from './components/Notification.vue';
import Loading from './components/Loading.vue';
import TopBar from './components/TopBar.vue';

const statusText = ref('准备就绪');
const statusType = ref<'ready' | 'analyzing' | 'generating' | 'error'>('ready');

function updateStatus(text: string, type: 'ready' | 'analyzing' | 'generating' | 'error') {
  statusText.value = text;
  statusType.value = type;
}

provide('updateStatus', updateStatus);

const route = useRoute();
const isFullPage = computed(() => Boolean(route.meta.fullPage));

// 默认启用“浅霓虹”主题：给 body 添加 theme-soft 类
onMounted(() => {
  document.body.classList.add('theme-soft');
});
</script>

<style scoped>
</style>


