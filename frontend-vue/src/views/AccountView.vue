<template>
  <div class="container" style="max-width:800px;">
    <div class="main-content">
      <h2 style="margin-bottom:10px; color:#333;">账户中心</h2>
      <p style="color:#666;">查看当前登录信息与快速操作。</p>

      <div class="music-info-section" style="margin-top:16px;">
        <div class="details-grid">
          <div class="detail-item">
            <div class="detail-label">用户名</div>
            <div class="detail-value">{{ auth.state.username || '-' }}</div>
          </div>
          <div class="detail-item">
            <div class="detail-label">登录状态</div>
            <div class="detail-value">{{ auth.state.isAuthenticated ? '已登录' : '未登录' }}</div>
          </div>
        </div>
        <div class="page-actions" style="margin-top:24px;">
          <button class="skip-btn" @click="logout"><i class="fas fa-sign-out-alt"></i> 退出登录</button>
          <button class="back-btn" @click="goHome"><i class="fas fa-home"></i> 返回首页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/auth';

const router = useRouter();
const auth = useAuth();

function logout() { auth.logout(); router.replace({ name: 'auth' }); }
function goHome() { router.push({ name: 'home' }); }
</script>

<style scoped>
</style>


