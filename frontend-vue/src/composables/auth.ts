import { reactive, readonly } from 'vue';

type AuthState = {
  isAuthenticated: boolean;
  username: string | null;
};

const STORAGE_KEY = 'yycy_auth_v1';

function loadInitial(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { isAuthenticated: false, username: null };
    const parsed = JSON.parse(raw);
    return {
      isAuthenticated: Boolean(parsed.isAuthenticated),
      username: parsed.username ?? null,
    };
  } catch {
    return { isAuthenticated: false, username: null };
  }
}

const state = reactive<AuthState>(loadInitial());

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

export function useAuth() {
  function login(username: string) {
    state.isAuthenticated = true;
    state.username = username;
    persist();
  }

  function logout() {
    state.isAuthenticated = false;
    state.username = null;
    persist();
  }

  return {
    state: readonly(state),
    login,
    logout,
  };
}


