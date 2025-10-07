<template>
  <div v-if="ui.state.loadingVisible" class="loading-overlay" style="display: flex; align-items: center; justify-content: center;">
    <div class="loading-spinner">
      <div class="spinner"></div>
      <p class="loading-text">{{ ui.state.loadingText }}</p>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { useUI } from '../composables/ui';
const ui = useUI();
</script>

<style scoped>
</style>



