package com.example.marketmindai;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.auth.api.signin.GoogleSignIn;
import com.google.android.gms.auth.api.signin.GoogleSignInClient;
import com.google.android.gms.auth.api.signin.GoogleSignInOptions;
import com.google.android.gms.common.api.ApiException;
import com.google.android.gms.tasks.Task;
import com.google.android.gms.auth.api.signin.GoogleSignInAccount;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Authentication Activity for login and registration.
 * Handles username/password auth and Google Sign-In.
 * Features inline error display and loading states.
 */
public class AuthActivity extends AppCompatActivity {
    private static final String TAG = "AuthActivity";
    private static final int RC_SIGN_IN = 9001;
    
    private EditText etUsername, etPassword, etConfirmPassword, etFullName;
    private Button btnSubmit, btnToggleMode, btnGoogleSignIn;
    private TextView tvToggleText, tvTitle, tvError;
    private boolean isLoginMode = true;
    
    private GoogleSignInClient mGoogleSignInClient;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_auth);
        
        initViews();
        setupGoogleSignIn();
        setupListeners();
        updateUIForMode();
    }
    
    private void initViews() {
        tvTitle = findViewById(R.id.tv_auth_title);
        tvError = findViewById(R.id.tv_auth_error);
        etUsername = findViewById(R.id.et_username);
        etPassword = findViewById(R.id.et_password);
        etConfirmPassword = findViewById(R.id.et_confirm_password);
        etFullName = findViewById(R.id.et_full_name);
        btnSubmit = findViewById(R.id.btn_submit);
        btnToggleMode = findViewById(R.id.btn_toggle_mode);
        btnGoogleSignIn = findViewById(R.id.btn_google_signin);
        tvToggleText = findViewById(R.id.tv_toggle_text);
    }
    
    private void setupGoogleSignIn() {
        GoogleSignInOptions gso = new GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
                .requestEmail()
                .build();
        mGoogleSignInClient = GoogleSignIn.getClient(this, gso);
    }
    
    private void setupListeners() {
        btnSubmit.setOnClickListener(v -> handleSubmit());
        btnToggleMode.setOnClickListener(v -> toggleMode());
        btnGoogleSignIn.setOnClickListener(v -> handleGoogleSignIn());
    }
    
    private void toggleMode() {
        isLoginMode = !isLoginMode;
        updateUIForMode();
        clearFields();
        hideError();
    }
    
    private void updateUIForMode() {
        if (isLoginMode) {
            tvTitle.setText("Đăng nhập để bắt đầu");
            btnSubmit.setText("Đăng nhập");
            etConfirmPassword.setVisibility(View.GONE);
            etFullName.setVisibility(View.GONE);
            tvToggleText.setText("Chưa có tài khoản? ");
            btnToggleMode.setText("Đăng ký");
        } else {
            tvTitle.setText("Tạo tài khoản mới");
            btnSubmit.setText("Đăng ký");
            etConfirmPassword.setVisibility(View.VISIBLE);
            etFullName.setVisibility(View.VISIBLE);
            tvToggleText.setText("Đã có tài khoản? ");
            btnToggleMode.setText("Đăng nhập");
        }
    }
    
    private void handleSubmit() {
        hideError();
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();
        
        if (username.isEmpty()) {
            showError("Vui lòng nhập tên đăng nhập");
            return;
        }
        if (password.isEmpty()) {
            showError("Vui lòng nhập mật khẩu");
            return;
        }
        
        if (isLoginMode) {
            performLogin(username, password);
        } else {
            String confirmPassword = etConfirmPassword.getText().toString().trim();
            String fullName = etFullName.getText().toString().trim();
            
            if (fullName.isEmpty()) {
                showError("Vui lòng nhập họ và tên");
                return;
            }
            if (password.length() < 6) {
                showError("Mật khẩu phải có ít nhất 6 ký tự");
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
        setSubmitLoading(true, "Đang đăng nhập...");
        
        executor.execute(() -> {
            try {
                System.out.println(" aaaa response");
                AuthService.AuthResponse response = AuthService.login(this, username, password);
                System.out.println(" aaaa response");
                System.out.println(response);
                runOnUiThread(() -> {
                    setSubmitLoading(false, isLoginMode ? "Đăng nhập" : "Đăng ký");
                    if (response.success) {
                        navigateToMainActivity();
                    } else {
                        showError("Đăng nhập thất bại: " + response.message);
                    }
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    setSubmitLoading(false, isLoginMode ? "Đăng nhập" : "Đăng ký");
                    showError("Lỗi kết nối: " + e.getMessage());
                });
            }
        });
    }
    
    private void performRegister(String username, String password, String fullName) {
        setSubmitLoading(true, "Đang đăng ký...");
        
        executor.execute(() -> {
            try {
                AuthService.AuthResponse response = AuthService.register(this, username, password, fullName);
                runOnUiThread(() -> {
                    setSubmitLoading(false, isLoginMode ? "Đăng nhập" : "Đăng ký");
                    if (response.success) {
                        navigateToMainActivity();
                    } else {
                        showError("Đăng ký thất bại: " + response.message);
                    }
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    setSubmitLoading(false, isLoginMode ? "Đăng nhập" : "Đăng ký");
                    showError("Lỗi kết nối: " + e.getMessage());
                });
            }
        });
    }
    
    private void handleGoogleSignIn() {
        btnGoogleSignIn.setEnabled(false);
        btnGoogleSignIn.setText("Đang kết nối Google...");
        Intent signInIntent = mGoogleSignInClient.getSignInIntent();
        startActivityForResult(signInIntent, RC_SIGN_IN);
    }
    
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == RC_SIGN_IN) {
            Task<GoogleSignInAccount> task = GoogleSignIn.getSignedInAccountFromIntent(data);
            try {
                GoogleSignInAccount account = task.getResult(ApiException.class);
                if (account != null) {
                    String idToken = account.getIdToken();
                    String email = account.getEmail();
                    performGoogleLogin(idToken != null ? idToken : email);
                } else {
                    resetGoogleButton();
                    showError("Google Sign-In bị hủy");
                }
            } catch (ApiException e) {
                android.util.Log.e(TAG, "Google Sign-In failed: " + e.getStatusCode(), e);
                resetGoogleButton();
                showError("Google Sign-In lỗi: " + e.getStatusCode());
            }
        }
    }
    
    private void performGoogleLogin(String googleToken) {
        executor.execute(() -> {
            try {
                AuthService.AuthResponse response = AuthService.loginWithGoogle(this, googleToken);
                runOnUiThread(() -> {
                    resetGoogleButton();
                    if (response.success) {
                        navigateToMainActivity();
                    } else {
                        showError("Đăng nhập Google thất bại");
                    }
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    resetGoogleButton();
                    showError("Lỗi: " + e.getMessage());
                });
            }
        });
    }
    
    // ── UI Helpers ──
    
    private void setSubmitLoading(boolean loading, String text) {
        btnSubmit.setEnabled(!loading);
        btnSubmit.setText(text);
        etUsername.setEnabled(!loading);
        etPassword.setEnabled(!loading);
        etConfirmPassword.setEnabled(!loading);
        etFullName.setEnabled(!loading);
    }
    
    private void resetGoogleButton() {
        btnGoogleSignIn.setEnabled(true);
        btnGoogleSignIn.setText("🔑 Đăng nhập với Google");
    }
    
    private void showError(String message) {
        if (tvError != null) {
            tvError.setText(message);
            tvError.setVisibility(View.VISIBLE);
        } else {
            Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
        }
    }
    
    private void hideError() {
        if (tvError != null) {
            tvError.setVisibility(View.GONE);
        }
    }
    
    private void clearFields() {
        etUsername.setText("");
        etPassword.setText("");
        etConfirmPassword.setText("");
        etFullName.setText("");
    }
    
    private void navigateToMainActivity() {
        Intent intent = new Intent(this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdownNow();
    }
}
