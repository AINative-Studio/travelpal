import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import svgr from 'vite-plugin-svgr';
import { visualizer } from 'rollup-plugin-visualizer';

// Get the directory name in ES module
const __dirname = fileURLToPath(new URL('.', import.meta.url));

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables based on the current mode (development, production, etc.)
  const env = loadEnv(mode, process.cwd(), '');
  
  // Filter out any falsy plugins (like the visualizer conditional)

  return {
    plugins: [
      react({
        // Use the new JSX runtime
        jsxRuntime: 'automatic',
        // Enable Fast Refresh (enabled by default in Vite)
      }),
      // Enable SVG imports as React components
      svgr({
        svgrOptions: {
          icon: true,
        },
      }),
      // Bundle analyzer (only in production build)
      mode === 'analyze' &&
        visualizer({
          open: true,
          filename: 'dist/stats.html',
          gzipSize: true,
          brotliSize: true,
        }),
    ].filter(Boolean),

    // Base public path when served in production
    base: '/',

    // Development server configuration
    server: {
      port: 3000,
      host: true, // Listen on all network interfaces
      strictPort: true,
      open: true, // Open browser on server start
      proxy: {
        // Proxy API requests to our backend
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: true,
      chunkSizeWarningLimit: 1000, // in kB
      rollupOptions: {
        output: {
          manualChunks: {
            // Split vendor modules into separate chunks
            react: ['react', 'react-dom', 'react-router-dom'],
            vendor: ['axios', 'date-fns', 'zod'],
            ui: ['@headlessui/react', '@heroicons/react'],
          },
        },
      },
    },

    // Resolve imports
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@pages': resolve(__dirname, 'src/pages'),
        '@services': resolve(__dirname, 'src/services'),
        '@utils': resolve(__dirname, 'src/utils'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@styles': resolve(__dirname, 'src/styles'),
        '@hooks': resolve(__dirname, 'src/hooks'),
        '@context': resolve(__dirname, 'src/context'),
        '@types': resolve(__dirname, 'src/types'),
      },
    },

    // CSS configuration
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables";`,
        },
      },
      modules: {
        // Generate scoped class names in development for better debugging
        generateScopedName: mode === 'development' ? '[name]__[local]' : '[hash:base64:5]',
      },
    },

    // Test configuration
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'html'],
        all: true,
        include: ['src/**/*.{ts,tsx}'],
        exclude: [
          '**/*.d.ts',
          '**/*.stories.{ts,tsx}',
          '**/*.test.{ts,tsx}',
          '**/test-utils/*',
          '**/mocks/*',
          '**/__mocks__/*',
        ],
      },
    },
  };
});
