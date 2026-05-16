package com.example.marketmindai.config;

import android.content.Context;
import com.google.firebase.remoteconfig.FirebaseRemoteConfig;
import com.google.firebase.remoteconfig.FirebaseRemoteConfigSettings;

/**
 * Centralized API configuration. Fetches backend URL from Firebase Remote Config.
 * Falls back to default ngrok URL if Firebase is unavailable.
 */
public class ApiConfig {
    private static final String TAG = "ApiConfig";
    private static final String DEFAULT_API_URL = "http://localhost:5000";
    private static final String FIREBASE_KEY_API_URL = "api_url";
    
    private static String apiUrl = DEFAULT_API_URL;
    private static boolean isInitialized = false;
    private static final Object lock = new Object();
    private static OnInitializedListener initializationListener;
    
    public interface OnInitializedListener {
        void onInitialized();
    }
    
    /**
     * Initialize backend URL from Firebase Remote Config on app startup.
     * This method is non-blocking but sets a flag when complete.
     */
    public static void initializeBackendUrl(Context context, OnInitializedListener listener) {
        initializationListener = listener;
        
        if (isInitialized) {
            if (listener != null) listener.onInitialized();
            return;
        }
        
        FirebaseRemoteConfig firebaseRemoteConfig = FirebaseRemoteConfig.getInstance();
        
        // Set minimum fetch interval to 1 hour (3600 seconds)
        FirebaseRemoteConfigSettings configSettings = new FirebaseRemoteConfigSettings.Builder()
                .setMinimumFetchIntervalInSeconds(3600)
                .build();
        firebaseRemoteConfig.setConfigSettingsAsync(configSettings);
        
        // Set default values
        firebaseRemoteConfig.setDefaultsAsync(
                java.util.Collections.singletonMap(FIREBASE_KEY_API_URL, DEFAULT_API_URL)
        );
        
        // Fetch from Firebase asynchronously
        firebaseRemoteConfig.fetchAndActivate()
                .addOnCompleteListener(task -> {
                    synchronized (lock) {
                        if (task.isSuccessful()) {
                            String fetchedUrl = firebaseRemoteConfig.getString(FIREBASE_KEY_API_URL);
                            if (fetchedUrl != null && !fetchedUrl.isEmpty()) {
                                apiUrl = fetchedUrl;
                                android.util.Log.d(TAG, "API URL fetched from Firebase: " + apiUrl);
                            }
                        } else {
                            // Use default on failure
                            android.util.Log.w(TAG, "Failed to fetch from Firebase, using default URL");
                        }
                        isInitialized = true;
                        lock.notifyAll();
                        
                        if (initializationListener != null) {
                            initializationListener.onInitialized();
                        }
                    }
                });
    }
    
    /**
     * Block until API URL is initialized. Timeout after 10 seconds.
     */
    public static void waitForInitialization() {
        synchronized (lock) {
            long endTime = System.currentTimeMillis() + 10000; // 10 second timeout
            while (!isInitialized && System.currentTimeMillis() < endTime) {
                try {
                    lock.wait(1000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
    }
    
    /**
     * Get the initialized API base URL.
     */
    public static String getApiUrl() {
        return apiUrl;
    }
    
    /**
     * Build full URL for an endpoint.
     * Example: getApiUrl("/api/auth/login") returns "http://backend.com/api/auth/login"
     */
    public static String getApiUrl(String endpoint) {
        String base = getApiUrl();
        if (!endpoint.startsWith("/")) {
            endpoint = "/" + endpoint;
        }
        return base + endpoint;
    }
    
    /**
     * Check if initialization is complete.
     */
    public static boolean isInitialized() {
        return isInitialized;
    }
}
