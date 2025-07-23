<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from './store/auth';

const authStore = useAuthStore();

onMounted(() => {
  authStore.fetchUser();
});
</script>

<style>
/* Global styles */
body {
  font-family: 'Roboto', sans-serif;
  margin: 0;
  background-color: #f5f5f5;
}
</style>
