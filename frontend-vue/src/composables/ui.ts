import { reactive, readonly } from 'vue';

type NotificationType = 'success' | 'error' | 'info' | 'warning';

const state = reactive({
  loadingVisible: false,
  loadingText: '加载中...',
  notificationVisible: false,
  notificationText: '',
  notificationType: 'info' as NotificationType,
});

function showLoading(text = '加载中...') {
  state.loadingText = text;
  state.loadingVisible = true;
}

function hideLoading() {
  state.loadingVisible = false;
}

function showNotification(message: string, type: NotificationType = 'info', timeout = 3000) {
  state.notificationText = message;
  state.notificationType = type;
  state.notificationVisible = true;
  if (timeout > 0) {
    setTimeout(() => {
      state.notificationVisible = false;
    }, timeout);
  }
}

export function useUI() {
  return {
    state: readonly(state),
    showLoading,
    hideLoading,
    showNotification,
  };
}



