/**
 * Application Configuration
 * Chỉnh sửa các tham số dưới đây để phù hợp với môi trường của bạn
 */

// ========================================
// 🌐 BACKEND URL CONFIGURATION
// ========================================
// Option 1: Local development (Backend chạy trên localhost)
// const BACKEND_LOCAL = 'http://127.0.0.1:5000';

// Option 2: Ngrok tunnel (Backend expose qua ngrok)
// Lấy từ output khi chạy notebook: "✅ API PUBLIC URL: https://xxx-ngrok.com"
const BACKEND_NGROK = 'https://9f34-34-125-194-159.ngrok-free.app';  // ← Thay bằng URL thực tế

// Firebase URL to fetch dynamic backend URL
const FIREBASE_API_URL = 'https://vienvipvail-default-rtdb.firebaseio.com/api-graduation-ngrok.json';

// Default backend URL (will be overridden by Firebase if available)
let ACTIVE_BACKEND_URL = BACKEND_NGROK;

// ========================================

export const config = {
  // Backend API Configuration
  api: {
    baseURL: ACTIVE_BACKEND_URL,
    endpoints: {
      stageAResearch: '/api/research/stage_a',
      stageBStrategy: '/api/strategy/stage_b',
      stageBApprove: '/api/strategy/stage_b/approve',
      stageCCampaign: '/api/campaign/stage_c',
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

/**
 * Fetch backend URL from Firebase on app startup
 * This allows updating the ngrok URL without redeploying the frontend
 */
export const initializeBackendUrl = async (): Promise<void> => {
  try {
    console.log('📡 Fetching backend URL from Firebase...');
    const response = await fetch(FIREBASE_API_URL);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Firebase returns the ngrok URL directly or wrapped in an object
    const backendUrl = typeof data === 'string' ? data : data.url || data.backend_url;
    
    if (backendUrl && backendUrl.startsWith('https://') || backendUrl.startsWith('http://')) {
      ACTIVE_BACKEND_URL = backendUrl;
      config.api.baseURL = ACTIVE_BACKEND_URL;
      console.log(`✅ Backend URL loaded from Firebase: ${ACTIVE_BACKEND_URL}`);
    } else {
      console.warn('⚠️ Invalid URL from Firebase, using default:',ACTIVE_BACKEND_URL);
    }
  } catch (error) {
    console.warn('⚠️ Failed to fetch backend URL from Firebase:', error);
    console.log(`📌 Using default backend URL: ${ACTIVE_BACKEND_URL}`);
    // Will continue with default ACTIVE_BACKEND_URL
  }
};
