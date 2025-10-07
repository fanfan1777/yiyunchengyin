<template>
  <div
    v-if="ui.state.notificationVisible"
    class="notification"
    :class="ui.state.notificationType"
    style="transform: translateX(0)"
  >
    {{ ui.state.notificationText }}
  </div>
</template>

<script setup lang="ts">
import { useUI } from '../composables/ui';
const ui = useUI();
</script>

<style scoped>
</style>



