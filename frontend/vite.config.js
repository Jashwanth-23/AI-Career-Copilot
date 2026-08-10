import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * vite.config.js - Vite Configuration Placeholder
 * 
 * Future Responsibility:
 * - Configures React plugin integration
 * - Configures API proxy for backend communication during local development
 * - Configures path aliases for cleaner imports
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
