import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 8083,
    // Docker su Windows: eventi inotify non passano via bind-mount,
    // serve il polling per il file watching (HMR).
    watch: {
      usePolling: true,
      interval: 1000,
    },
  },
});
