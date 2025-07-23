// frontend/src/plugins/vuetify.ts

// Styles
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Composables
import { createVuetify } from 'vuetify'
import { VBtn } from 'vuetify/components/VBtn'
import { VCard } from 'vuetify/components/VCard'
import { VTextField } from 'vuetify/components/VTextField'
import { VForm } from 'vuetify/components/VForm'
import { VContainer } from 'vuetify/components/VGrid'
import { VLayout } from 'vuetify/components/VLayout'
import { VMain } from 'vuetify/components/VMain'
import { VApp } from 'vuetify/components/VApp'
import { VAlert } from 'vuetify/components/VAlert'
import { VProgressCircular } from 'vuetify/components/VProgressCircular'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  aliases: {
    VBtn,
    VCard,
    VTextField,
    VForm,
    VContainer,
    VLayout,
    VMain,
    VApp,
    VAlert,
    VProgressCircular,
  },
  theme: {
    themes: {
      light: {
        colors: {
          primary: '#2196F3',
          secondary: '#FFC107',
          error: '#F44336',
          success: '#4CAF50',
          warning: '#FF9800',
          background: '#F5F5F5',
          surface: '#FFFFFF',
        },
      },
    },
  },
})
