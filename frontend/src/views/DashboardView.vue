<template>
  <div>
    <h1>Dashboard</h1>
    <div v-if="authStore.user">
      <p>Welcome, {{ authStore.user.username }}!</p>
      <button @click="handleLogout">Logout</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '../store/auth';

const authStore = useAuthStore();

const handleLogout = () => {
  authStore.logout();
};
</script>
