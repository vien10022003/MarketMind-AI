package com.example.marketmindai;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

/**
 * Authentication Activity for login and registration.
 * Handles username/password auth and Google Sign-In.
 */
public class AuthActivity extends AppCompatActivity {
    private static final String TAG = "AuthActivity";
    
    private EditText etUsername, etPassword, etConfirmPassword, etFullName;
    private Button btnSubmit, btnToggleMode, btnGoogleSignIn;
    private TextView tvToggleText, tvTitle;
    private boolean isLoginMode = true;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_auth);
        
        // Initialize views
        tvTitle = findViewById(R.id.tv_auth_title);
        etUsername = findViewById(R.id.et_username);
        etPassword = findViewById(R.id.et_password);
        etConfirmPassword = findViewById(R.id.et_confirm_password);
        etFullName = findViewById(R.id.et_full_name);
        btnSubmit = findViewById(R.id.btn_submit);
        btnToggleMode = findViewById(R.id.btn_toggle_mode);
        btnGoogleSignIn = findViewById(R.id.btn_google_signin);
        tvToggleText = findViewById(R.id.tv_toggle_text);
        
        // Set click listeners
        btnSubmit.setOnClickListener(v -> handleSubmit());
        btnToggleMode.setOnClickListener(v -> toggleMode());
        btnGoogleSignIn.setOnClickListener(v -> handleGoogleSignIn());
        
        // Set initial mode
        updateUIForMode();
    }
    
    private void toggleMode() {
        isLoginMode = !isLoginMode;
        updateUIForMode();
        clearFields();
    }
    
    private void updateUIForMode() {
        if (isLoginMode) {
            tvTitle.setText("Đăng Nhập");
            btnSubmit.setText(R.string.login);
            btnToggleMode.setText(R.string.dont_have_account);
            etConfirmPassword.setVisibility(android.view.View.GONE);
            etFullName.setVisibility(android.view.View.GONE);
            tvToggleText.setText(R.string.dont_have_account);
        } else {
            tvTitle.setText("Đăng Ký");
            btnSubmit.setText(R.string.register);
            btnToggleMode.setText(R.string.already_have_account);
            etConfirmPassword.setVisibility(android.view.View.VISIBLE);
            etFullName.setVisibility(android.view.View.VISIBLE);
            tvToggleText.setText(R.string.already_have_account);
        }
    }
    
    private void handleSubmit() {
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();
        
        // Validation
        if (username.isEmpty() || password.isEmpty()) {
            showError("Vui lòng nhập tên đăng nhập và mật khẩu");
            return;
        }
        
        if (isLoginMode) {
            performLogin(username, password);
        } else {
            String confirmPassword = etConfirmPassword.getText().toString().trim();
            String fullName = etFullName.getText().toString().trim();
            
            if (confirmPassword.isEmpty() || fullName.isEmpty()) {
                showError("Vui lòng nhập đầy đủ thông tin");
                return;
            }
            
            if (!password.equals(confirmPassword)) {
                showError("Mật khẩu không khớp");
                return;
            }
            
            performRegister(username, password, fullName);
        }
    }
    
    private void performLogin(String username, String password) {
        btnSubmit.setEnabled(false);
        btnSubmit.setText("Đang đăng nhập...");
        
        new Thread(() -> {
            try {
                AuthService.AuthResponse response = AuthService.login(this, username, password);
                runOnUiThread(() -> {
                    btnSubmit.setEnabled(true);
                    btnSubmit.setText(R.string.login);
                    
                    if (response.success) {
                        showSuccess("Đăng nhập thành công!");
                        navigateToMainActivity();
                    } else {
                        showError("Đăng nhập thất bại: " + response.message);
                    }
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    btnSubmit.setEnabled(true);
                    btnSubmit.setText(R.string.login);
                    showError("Lỗi: " + e.getMessage());
                });
            }
        }).start();
    }
    
    private void performRegister(String username, String password, String fullName) {
        btnSubmit.setEnabled(false);
        btnSubmit.setText("Đang đăng ký...");
        
        new Thread(() -> {
            try {
                AuthService.AuthResponse response = AuthService.register(this, username, password, fullName);
                runOnUiThread(() -> {
                    btnSubmit.setEnabled(true);
                    btnSubmit.setText(R.string.register);
                    
                    if (response.success) {
                        showSuccess("Đăng ký thành công!");
                        navigateToMainActivity();
                    } else {
                        showError("Đăng ký thất bại: " + response.message);
                    }
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    btnSubmit.setEnabled(true);
                    btnSubmit.setText(R.string.register);
                    showError("Lỗi: " + e.getMessage());
                });
            }
        }).start();
    }
    
    private void handleGoogleSignIn() {
        // TODO: Implement Google Sign-In SDK integration
        // For now, show a placeholder message
        showError("Google Sign-In sẽ được implement sau khi cấu hình Firebase");
    }
    
    private void clearFields() {
        etUsername.setText("");
        etPassword.setText("");
        etConfirmPassword.setText("");
        etFullName.setText("");
    }
    
    private void navigateToMainActivity() {
        Intent intent = new Intent(this, MainActivity.class);
        startActivity(intent);
        finish();
    }
    
    private void showError(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
    
    private void showSuccess(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
}
