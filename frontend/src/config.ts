/**
 * Application Configuration
 * Chỉnh sửa các tham số dưới đây để phù hợp với môi trường của bạn
 */

// ========================================
// 🌐 BACKEND URL CONFIGURATION
// ========================================
// Option 1: Local development (Backend chạy trên localhost)
const BACKEND_LOCAL = 'http://127.0.0.1:5000';

// Option 2: Ngrok tunnel (Backend expose qua ngrok)
// Lấy từ output khi chạy notebook: "✅ API PUBLIC URL: https://xxx-ngrok.com"
const BACKEND_NGROK = 'https://27e1-34-125-45-161.ngrok-free.app';  // ← Thay bằng URL thực tế

// Chọn một trong hai:
const ACTIVE_BACKEND_URL = BACKEND_NGROK;  // ← Đổi thành BACKEND_NGROK nếu dùng ngrok

// ========================================

export const config = {
  // Backend API Configuration
  api: {
    baseURL: ACTIVE_BACKEND_URL,
    endpoints: {
      stageAResearch: '/api/research/stage_a',
    },
    timeout: 300000, // 5 minutes in milliseconds
  },

  // Application Settings
  app: {
    name: 'MarketMind AI',
    version: '1.0.0',
  },

  // UI Configuration
  ui: {
    // Progress panel max height
    progressMaxHeight: 400,
    // Auto-scroll progress messages
    autoScroll: true,
    // Loading animation speed
    animationDuration: 300,
  },

  // Feature Flags
  features: {
    // Enable streaming progress display
    enableStreaming: true,
    // Show citations in report
    showCitations: true,
    // Enable export functionality
    enableExport: false,
  },

  // Development
  isDevelopment: import.meta.env.MODE === 'development',
  isProduction: import.meta.env.MODE === 'production',
};

// Export helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${config.api.baseURL}${endpoint}`;
};
