<template>
  <div class="container" style="max-width:520px;">
    <div class="main-content" style="padding:32px; border-radius:16px;">
      <div style="text-align:center; margin-bottom:20px;">
        <h2 style="margin:0 0 8px 0; font-weight:700; color:#333;">创建新账户</h2>
        <p style="color:#666;">注册后开始你的音乐创作之旅</p>
      </div>

      <form @submit.prevent="onSubmit">
        <div class="input-group">
          <label>用户名</label>
          <input v-model.trim="username" type="text" placeholder="请输入用户名" required
                 style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" />
        </div>
        <div class="input-group">
          <label>邮箱</label>
          <input v-model.trim="email" type="email" placeholder="请输入邮箱" required
                 style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" />
        </div>
        <div class="input-group">
          <label>密码</label>
          <input v-model.trim="password" type="password" placeholder="请输入密码" required
                 style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" />
        </div>
        <button type="submit" class="continue-btn" style="width:100%;margin-top:6px;">
          <i class="fas fa-user-plus"></i> 注册
        </button>
      </form>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:16px;color:#666;">
        <span>已有账号？<router-link to="/login">去登录</router-link></span>
        <span><router-link to="/">返回首页</router-link></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUI } from '../composables/ui';

const router = useRouter();
const ui = useUI();
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

const username = ref('');
const email = ref('');
const password = ref('');

async function onSubmit() {
  try {
    ui.showLoading('正在注册...');
    const res = await fetch(`${API_BASE}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: username.value, email: email.value, password: password.value }) });
    const json = await res.json();
    ui.hideLoading();
    if (json.success) {
      ui.showNotification('注册成功，正在跳转登录...', 'success');
      setTimeout(() => router.push('/login'), 1000);
    } else {
      ui.showNotification(json.message || '注册失败', 'error');
    }
  } catch (e: any) {
    ui.hideLoading(); ui.showNotification('网络错误，请稍后重试', 'error');
  }
}
</script>

<style scoped>
</style>


