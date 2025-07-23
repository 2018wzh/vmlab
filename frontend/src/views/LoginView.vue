<template>
  <div>
    <h1>Login</h1>
    <form @submit.prevent="handleLogin">
      <input type="text" v-model="username" placeholder="Username" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../store/auth';

const username = ref('');
const password = ref('');
const authStore = useAuthStore();

const handleLogin = async () => {
  await authStore.login({ username: username.value, password: password.value });
};
</script>
