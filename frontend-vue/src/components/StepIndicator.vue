<template>
  <div class="step-indicator">
    <div v-for="n in 3" :key="n" class="step" :class="stepClass(n)">
      <div class="step-number">{{ n }}</div>
      <div class="step-label">{{ labels[n - 1] }}</div>
    </div>
    <div class="step-line"></div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ current: number; labels: string[] }>();

function stepClass(n: number) {
  return {
    active: n === props.current,
    completed: n < props.current,
  };
}

const labels = props.labels.length ? props.labels : ['输入创意', '优化设置', '生成音乐'];
</script>

<style scoped>
</style>



