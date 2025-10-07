<template>
  <div class="audio-player-card">
    <div class="audio-player-container">
      <audio controls ref="audioRef" class="custom-audio-player">
        您的浏览器不支持音频播放。
      </audio>
      <div class="audio-controls">
        <button class="audio-btn" @click="download">
          <i class="fas fa-download"></i> 下载
        </button>
        <button class="audio-btn" @click="share">
          <i class="fas fa-share"></i> 分享
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';

const props = defineProps<{ src?: string; fileName?: string }>();
const audioRef = ref<HTMLAudioElement | null>(null);

watch(() => props.src, (url) => {
  if (audioRef.value && url) {
    audioRef.value.src = url;
    audioRef.value.load();
  }
});

onMounted(() => {
  if (audioRef.value && props.src) {
    audioRef.value.src = props.src;
    audioRef.value.load();
  }
});

function download() {
  if (!props.src) return;
  const a = document.createElement('a');
  a.href = props.src;
  a.download = props.fileName ?? 'generated_music.mp3';
  a.click();
}

function share() {
  if (navigator.share) {
    navigator.share({ title: 'AI生成的音乐', url: window.location.href });
  } else {
    navigator.clipboard.writeText(window.location.href);
  }
}
</script>

<style scoped>
</style>



