import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        port: 3000,
        proxy: {
            // Proxy API requests to backend on port 8000
            '/generate-post': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/approve-post': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/linkedin': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/images': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
            '/static': {
                target: 'http://localhost:8000',
                changeOrigin: true,
            },
        },
    },
    build: {
        outDir: 'dist',
        sourcemap: true,
    },
});
