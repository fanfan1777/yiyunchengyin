<template>
  <div class="container" style="max-width:520px;">
    <div class="main-content" style="padding:32px; border-radius:16px;">
      <div style="text-align:center; margin-bottom:20px;">
        <h2 style="margin:0 0 8px 0; font-weight:700; color:#333;">欢迎回来</h2>
        <p style="color:#666;">登录以继续使用 意韵成音</p>
      </div>

      <form @submit.prevent="onSubmit">
        <div class="input-group">
          <label>用户名</label>
          <input v-model.trim="username" type="text" placeholder="请输入用户名" required
                 style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" />
        </div>
        <div class="input-group">
          <label>密码</label>
          <input v-model.trim="password" type="password" placeholder="请输入密码" required
                 style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" />
        </div>
        <button type="submit" class="continue-btn" style="width:100%;margin-top:6px;">
          <i class="fas fa-sign-in-alt"></i> 登录
        </button>
      </form>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;color:#666;">
        <span>没有账号？<router-link to="/register">去注册</router-link></span>
        <span><router-link to="/">返回首页</router-link></span>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUI } from '../composables/ui';
import { useAuth } from '../composables/auth';

const router = useRouter();
const route = useRoute();
const ui = useUI();
const auth = useAuth();
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

const username = ref('');
const password = ref('');

async function onSubmit() {
  try {
    ui.showLoading('正在登录...');
    const res = await fetch(`${API_BASE}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: username.value, password: password.value }) });
    const json = await res.json();
    ui.hideLoading();
    if (json.success) {
      ui.showNotification('登录成功，正在跳转...', 'success');
      auth.login(username.value);
      const redirect = String(route.query.redirect || '/')
      setTimeout(() => router.replace(redirect), 600);
    } else {
      ui.showNotification(json.message || '登录失败', 'error');
    }
  } catch (e: any) {
    ui.hideLoading(); ui.showNotification('网络错误，请稍后重试', 'error');
  }
}
</script>

<style scoped>
</style>


