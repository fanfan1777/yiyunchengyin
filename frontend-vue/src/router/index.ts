import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import { useAuth } from '../composables/auth';

const HomeView = () => import('../views/HomeView.vue');
const AuthView = () => import('../views/AuthView.vue');
const AccountView = () => import('../views/AccountView.vue');

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
  { path: '/auth', name: 'auth', component: AuthView, meta: { guestOnly: true, fullPage: true } },
  { path: '/account', name: 'account', component: AccountView, meta: { requiresAuth: true } },
  { path: '/login', redirect: { name: 'auth' } },
  { path: '/register', redirect: { name: 'auth' } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to) => {
  const { state } = useAuth();
  if (to.meta.requiresAuth && !state.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }
});

export default router;



