<template>
  <div class="topbar" v-if="show">
    <div class="topbar-content">
      <router-link to="/" class="brand"><i class="fas fa-music"></i> 意韵成音</router-link>
      <div class="spacer"></div>
      <template v-if="auth.state.isAuthenticated">
        <span class="user">你好，{{ auth.state.username }}</span>
        <button class="back-btn" @click="toAccount">账户</button>
        <button class="skip-btn" @click="onLogout">退出</button>
      </template>
      <template v-else>
        <router-link class="continue-btn" to="/auth">登录 / 注册</router-link>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '../composables/auth';

const route = useRoute();
const router = useRouter();
const auth = useAuth();
const show = computed(() => true);

function onLogout() {
  auth.logout();
  router.replace({ name: 'auth' });
}

function toAccount() {
  router.push({ name: 'account' });
}
</script>

<style scoped>
.topbar { position: sticky; top: 0; z-index: 50; background: var(--topbar-bg); backdrop-filter: blur(12px); border-bottom: 1px solid var(--topbar-border); }
.topbar-content { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; gap: 10px; padding: 10px 20px; }
.brand { font-weight: 700; color: var(--text); text-decoration: none; }
.brand i { color: #FDE047; margin-right: 8px; }
.spacer { flex: 1; }
.user { color: var(--text); margin-right: 8px; }

/* 顶栏按钮采用暗色风格，避免白块突兀 */
.back-btn, .skip-btn { 
  background: transparent; 
  color: var(--text); 
  border: 1px solid var(--border); 
  padding: 6px 14px; 
  border-radius: 10px; 
}
.back-btn:hover { 
  border-color: var(--primary); 
  background: rgba(139,92,246,0.12); 
}
.skip-btn { 
  background: linear-gradient(135deg, var(--primary-end), var(--primary-start));
  border: none;
  color: #0b1020;
}
.skip-btn:hover { 
  filter: brightness(1.05);
}
</style>


