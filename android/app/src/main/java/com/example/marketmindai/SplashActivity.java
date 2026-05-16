package com.example.marketmindai;

import android.content.Intent;
import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import com.example.marketmindai.config.ApiConfig;

/**
 * Splash screen activity displayed on app startup.
 * Initializes Firebase config and checks authentication status.
 */
public class SplashActivity extends AppCompatActivity {
    private static final String TAG = "SplashActivity";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);
        
        // Initialize API config from Firebase
        ApiConfig.initializeBackendUrl(this, () -> {
            // After Firebase config is initialized, check auth and navigate
            checkAuthAndNavigate();
        });
        
        // Also wait a bit for Firebase to complete (max 10 seconds)
        new Thread(() -> {
            try {
                ApiConfig.waitForInitialization();
            } catch (Exception e) {
                android.util.Log.w(TAG, "Timeout waiting for Firebase config", e);
            }
        }).start();
    }
    
    private void checkAuthAndNavigate() {
        // Check if user has valid authentication token
        boolean isAuthenticated = AuthService.isAuthenticated(this);
        
        Intent intent;
        if (isAuthenticated) {
            // Token exists and might be valid, go to MainActivity
            intent = new Intent(this, MainActivity.class);
        } else {
            // No token, go to AuthActivity
            intent = new Intent(this, AuthActivity.class);
        }
        
        startActivity(intent);
        finish();
    }
}
