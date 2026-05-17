package com.example.marketmindai.config;

import android.content.Context;
import android.util.Log;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.IOException;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * Centralized API configuration. Fetches backend URL from Firebase Realtime Database.
 * Falls back to default ngrok URL if Firebase is unavailable.
 */
public class ApiConfig {
    private static final String TAG = "ApiConfig";
    
    // Ngrok URL fallback - update when you deploy
    private static final String DEFAULT_API_URL = "https://9f34-34-125-194-159.ngrok-free.app";
    
    // Firebase Realtime Database endpoint (same as Frontend)
    private static final String FIREBASE_API_URL = "https://vienvipvail-default-rtdb.firebaseio.com/api-graduation-ngrok.json";
    
    private static String apiUrl = DEFAULT_API_URL;
    private static boolean isInitialized = false;
    private static final Object lock = new Object();
    private static OnInitializedListener initializationListener;
    
    public interface OnInitializedListener {
        void onInitialized();
    }
    
    /**
     * Initialize backend URL from Firebase Realtime Database on app startup.
     * This method runs asynchronously in a background thread.
     * Falls back to default URL if Firebase is unavailable.
     */
    public static void initializeBackendUrl(Context context, OnInitializedListener listener) {
        initializationListener = listener;
        
        if (isInitialized) {
            if (listener != null) listener.onInitialized();
            return;
        }
        
        // Fetch from Firebase in background thread
        new Thread(() -> {
            try {
                Log.d(TAG, "📡 Fetching backend URL from Firebase...");
                
                OkHttpClient client = new OkHttpClient();
                Request request = new Request.Builder()
                        .url(FIREBASE_API_URL)
                        .build();
                
                try (Response response = client.newCall(request).execute()) {
                    if (!response.isSuccessful()) {
                        throw new IOException("HTTP error! status: " + response.code());
                    }
                    
                    String responseBody = response.body().string();
                    
                    // Parse Firebase response
                    String fetchedUrl = null;
                    if (responseBody.startsWith("\"")) {
                        // Firebase returns string directly: "https://..."
                        fetchedUrl = responseBody.replaceAll("^\"|\"$", "");
                    } else {
                        // Or wrapped in object: {"url": "https://...", "backend_url": "https://..."}
                        try {
                            JSONObject json = new JSONObject(responseBody);
                            if (json.has("url")) {
                                fetchedUrl = json.getString("url");
                            } else if (json.has("backend_url")) {
                                fetchedUrl = json.getString("backend_url");
                            }
                        } catch (JSONException e) {
                            Log.w(TAG, "Failed to parse JSON: " + e.getMessage());
                        }
                    }
                    
                    // Validate and use fetched URL
                    if (fetchedUrl != null && !fetchedUrl.isEmpty() &&
                            (fetchedUrl.startsWith("https://") || fetchedUrl.startsWith("http://"))) {
                        synchronized (lock) {
                            apiUrl = fetchedUrl;
                            isInitialized = true;
                            lock.notifyAll();
                            Log.d(TAG, "✅ Backend URL loaded from Firebase: " + apiUrl);
                        }
                    } else {
                        throw new IOException("Invalid URL from Firebase");
                    }
                }
            } catch (Exception e) {
                // Fallback to default URL
                synchronized (lock) {
                    apiUrl = DEFAULT_API_URL;
                    isInitialized = true;
                    lock.notifyAll();
                    Log.w(TAG, "⚠️ Failed to fetch backend URL from Firebase, using default: " + DEFAULT_API_URL, e);
                }
            }
            
            // Notify listener
            if (initializationListener != null) {
                initializationListener.onInitialized();
            }
        }).start();
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
