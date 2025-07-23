import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify'; // Import Vuetify
import './style.css';
import '@mdi/font/css/materialdesignicons.css';


const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(vuetify); // Use Vuetify

app.mount('#app');
