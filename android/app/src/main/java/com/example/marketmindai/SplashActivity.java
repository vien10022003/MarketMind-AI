package com.example.marketmindai;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.example.marketmindai.config.ApiConfig;

/**
 * Splash screen: initializes backend URL from Firebase,
 * then routes to Auth or Main based on saved token.
 */
public class SplashActivity extends AppCompatActivity {
    private static final String TAG = "SplashActivity";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);
        
        // Initialize API config from Firebase
        ApiConfig.initializeBackendUrl(this, () -> {
            // Run navigation on UI thread
            new Handler(Looper.getMainLooper()).post(this::checkAuthAndNavigate);
        });
    }
    
    private void checkAuthAndNavigate() {
        boolean isAuthenticated = AuthService.isAuthenticated(this);
        Log.d(TAG, "Authenticated: " + isAuthenticated + ", API: " + ApiConfig.getApiUrl());
        
        Intent intent;
        if (isAuthenticated) {
            intent = new Intent(this, MainActivity.class);
        } else {
            intent = new Intent(this, AuthActivity.class);
        }
        
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}
