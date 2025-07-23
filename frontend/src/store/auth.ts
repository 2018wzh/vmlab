import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';
import router from '../router';

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('accessToken') || '');
  const refreshToken = ref(localStorage.getItem('refreshToken') || '');
  const user = ref(null);

  const isAuthenticated = computed(() => !!accessToken.value);

  async function login(credentials) {
    try {
      const response = await api.post('/auth/login/', credentials);
      accessToken.value = response.data.access;
      refreshToken.value = response.data.refresh;
      localStorage.setItem('accessToken', accessToken.value);
      localStorage.setItem('refreshToken', refreshToken.value);
      await fetchUser();
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      // Handle error (e.g., show a notification)
    }
  }

  function logout() {
    accessToken.value = '';
    refreshToken.value = '';
    user.value = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    router.push('/login');
  }

  async function fetchUser() {
    if (accessToken.value) {
      try {
        const response = await api.get('/auth/user/profile/');
        user.value = response.data;
      } catch (error) {
        console.error('Failed to fetch user:', error);
        if (error.response && error.response.status === 401) {
          // Token might be expired, try to refresh it
          await refreshAccessToken();
        }
      }
    }
  }

  async function refreshAccessToken() {
    try {
      const response = await api.post('/auth/refresh/', { refresh: refreshToken.value });
      accessToken.value = response.data.access;
      localStorage.setItem('accessToken', accessToken.value);
      await fetchUser(); // Retry fetching user with new token
    } catch (error) {
      console.error('Failed to refresh token:', error);
      logout(); // If refresh fails, log out the user
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    login,
    logout,
    fetchUser,
    refreshAccessToken,
  };
});
