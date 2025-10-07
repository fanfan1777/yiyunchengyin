<template>
  <div class="container" style="max-width:720px;">
    <div class="main-content" style="padding:0; overflow:hidden;">
      <div class="auth-split">
        <div class="auth-panel">
          <h2 style="margin:0 0 8px 0; color:#333; font-weight:700; display:flex; align-items:center; gap:10px;">
            <i class="fas fa-user-circle"></i> 欢迎使用 · 意韵成音
          </h2>
          <p style="color:#666;">登录或注册，开启你的音乐创作</p>

          <div class="input-tabs" style="margin-top:16px;">
            <button class="tab-btn" :class="{active: tab==='login'}" @click="tab='login'">
              <i class="fas fa-sign-in-alt"></i> 登录
            </button>
            <button class="tab-btn" :class="{active: tab==='register'}" @click="tab='register'">
              <i class="fas fa-user-plus"></i> 注册
            </button>
          </div>

          <div class="tab-content" :class="{active: tab==='login'}" style="margin-top:16px;">
            <form @submit.prevent="submitLogin">
              <div class="input-group"><label>用户名</label>
                <input v-model.trim="loginForm.username" type="text" placeholder="请输入用户名"
                       style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" required />
              </div>
              <div class="input-group"><label>密码</label>
                <input v-model.trim="loginForm.password" type="password" placeholder="请输入密码"
                       style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" required />
              </div>
              <button type="submit" class="continue-btn" style="width:100%; margin-top:6px;">
                <i class="fas fa-sign-in-alt"></i> 登录
              </button>
            </form>
          </div>

          <div class="tab-content" :class="{active: tab==='register'}" style="margin-top:16px;">
            <form @submit.prevent="submitRegister">
              <div class="input-group"><label>用户名</label>
                <input v-model.trim="registerForm.username" type="text" placeholder="请输入用户名"
                       style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" required />
              </div>
              <div class="input-group"><label>邮箱</label>
                <input v-model.trim="registerForm.email" type="email" placeholder="请输入邮箱"
                       style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" required />
              </div>
              <div class="input-group"><label>密码</label>
                <input v-model.trim="registerForm.password" type="password" placeholder="请输入密码"
                       style="width:100%;padding:12px 14px;border:2px solid #e9ecef;border-radius:12px;outline:none;" required />
              </div>
              <button type="submit" class="continue-btn" style="width:100%; margin-top:6px;">
                <i class="fas fa-user-plus"></i> 注册
              </button>
            </form>
          </div>
        </div>

        <div class="auth-aside">
          <h3 style="color:#333;">功能亮点</h3>
          <p style="color:#666;">意韵成音将文字/图片中的情感与语义转化为可感知的音乐表达。</p>
          <ul style="color:#555; line-height:1.8; padding-left:20px;">
            <li>多模态输入：文字与图片一键分析</li>
            <li>智能澄清：问答式完善音乐要素</li>
            <li>可控生成：时长、音色、乐器灵活配置</li>
            <li>即刻创作：一键生成音乐与歌词</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUI } from '../composables/ui';
import { useAuth } from '../composables/auth';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';
const tab = ref<'login'|'register'>('login');
const loginForm = ref({ username: '', password: '' });
const registerForm = ref({ username: '', email: '', password: '' });
const router = useRouter();
const route = useRoute();
const ui = useUI();
const auth = useAuth();

async function submitLogin() {
  try {
    ui.showLoading('正在登录...');
    const res = await fetch(`${API_BASE}/login`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(loginForm.value) });
    const json = await res.json();
    ui.hideLoading();
    if (json.success) {
      auth.login(loginForm.value.username);
      ui.showNotification('登录成功', 'success');
      const redirect = String(route.query.redirect || '/');
      router.replace(redirect);
    } else { ui.showNotification(json.message || '登录失败', 'error'); }
  } catch (e:any) { ui.hideLoading(); ui.showNotification('登录失败：网络或服务器错误', 'error'); }
}

async function submitRegister() {
  try {
    ui.showLoading('正在注册...');
    const res = await fetch(`${API_BASE}/register`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(registerForm.value) });
    const json = await res.json();
    ui.hideLoading();
    if (json.success) {
      ui.showNotification('注册成功，请登录', 'success');
      tab.value = 'login';
      loginForm.value.username = registerForm.value.username;
    } else { ui.showNotification(json.message || '注册失败', 'error'); }
  } catch (e:any) { ui.hideLoading(); ui.showNotification('注册失败：网络或服务器错误', 'error'); }
}
</script>

<style scoped>
</style>


