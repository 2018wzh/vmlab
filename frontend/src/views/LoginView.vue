<template>
  <v-container class="fill-height" fluid>
    <v-layout class="align-center justify-center">
      <v-card class="mx-auto pa-4" max-width="400" elevation="8">
        <div class="text-center mb-4">
          <h1 class="text-h5">VMLab 登录</h1>
        </div>

        <v-form @submit.prevent="handleLogin">
          <v-alert
            v-if="authStore.error"
            type="error"
            density="compact"
            class="mb-4"
            closable
          >
            {{ authStore.error }}
          </v-alert>

          <v-text-field
            v-model="username"
            label="用户名"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            required
            :rules="[v => !!v || '用户名为必填项']"
          ></v-text-field>

          <v-text-field
            v-model="password"
            label="密码"
            prepend-inner-icon="mdi-lock"
            type="password"
            variant="outlined"
            required
            :rules="[v => !!v || '密码为必填项']"
          ></v-text-field>

          <v-btn
            :loading="authStore.loading"
            :disabled="authStore.loading"
            type="submit"
            color="primary"
            block
            size="large"
          >
            登录
          </v-btn>
        </v-form>
        <div class="text-center mt-4">
          <router-link to="/register" class="text-decoration-none">还没有账户？立即注册</router-link>
        </div>
      </v-card>
    </v-layout>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../store/auth';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  await authStore.login(username.value, password.value);
  if (authStore.isAuthenticated) {
    router.push('/dashboard');
  }
};
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
  background-color: #F5F5F5; /* background color from DESIGN.md */
}
</style>
