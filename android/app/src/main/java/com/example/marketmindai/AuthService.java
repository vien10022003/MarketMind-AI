package com.example.marketmindai;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonObject;

import com.example.marketmindai.config.ApiConfig;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * Authentication service for handling login, registration, token management.
 * Tokens are stored in SharedPreferences.
 */
public class AuthService {
    private static final String TAG = "AuthService";
    private static final String PREFS_NAME = "com.example.marketmindai.auth";
    private static final String KEY_TOKEN = "auth_token";
    private static final String KEY_USER = "auth_user";
    private static final String KEY_EXPIRES_AT = "token_expires_at";
    
    private static OkHttpClient httpClient = new OkHttpClient();
    private static Gson gson = new Gson();
    
    /**
     * User model for storing in SharedPreferences
     */
    public static class User {
        public String username;
        public String name;
        public String email;
        
        public User(String username, String name, String email) {
            this.username = username;
            this.name = name;
            this.email = email;
        }
    }
    
    /**
     * Check if user is currently authenticated (has valid token)
     */
    public static boolean isAuthenticated(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String token = prefs.getString(KEY_TOKEN, null);
        
        if (token == null || token.isEmpty()) {
            return false;
        }
        
        // Check if token has expired
        long expiresAt = prefs.getLong(KEY_EXPIRES_AT, 0);
        return System.currentTimeMillis() < expiresAt;
    }
    
    /**
     * Login with username and password
     */
    public static AuthResponse login(Context context, String username, String password) throws Exception {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("username", username);
        requestBody.addProperty("password", password);
        
        String url = ApiConfig.getApiUrl("/api/auth/login");
        Log.d(TAG, "Logging in to: " + url);
        
        Request request = new Request.Builder()
                .url(url)
                .post(RequestBody.create(
                        gson.toJson(requestBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        Response response = httpClient.newCall(request).execute();
        String responseBody = response.body().string();
        
        if (!response.isSuccessful()) {
            throw new Exception("Login failed: " + responseBody);
        }
        
        JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
        
        // Extract token and user info with null checks
        if (jsonResponse == null || !jsonResponse.has("access_token") || !jsonResponse.has("username")) {
            throw new Exception("Invalid login response: missing access_token or username");
        }
        
        String token = jsonResponse.get("access_token").getAsString();
        String userName = jsonResponse.get("username").getAsString();
        String name = jsonResponse.has("name") && jsonResponse.get("name") != null ? jsonResponse.get("name").getAsString() : userName;
        String email = jsonResponse.has("email") && jsonResponse.get("email") != null ? jsonResponse.get("email").getAsString() : "";
        
        // Save token and user
        saveToken(context, token, userName, name, email);
        
        return new AuthResponse(true, "Login successful", token, new User(userName, name, email));
    }
    
    /**
     * Register new user
     */
    public static AuthResponse register(Context context, String username, String password, String name) throws Exception {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("username", username);
        requestBody.addProperty("password", password);
        requestBody.addProperty("name", name);
        
        String url = ApiConfig.getApiUrl("/api/auth/register");
        Log.d(TAG, "Registering to: " + url);
        
        Request request = new Request.Builder()
                .url(url)
                .post(RequestBody.create(
                        gson.toJson(requestBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        Response response = httpClient.newCall(request).execute();
        String responseBody = response.body().string();
        
        if (!response.isSuccessful()) {
            throw new Exception("Registration failed: " + responseBody);
        }
        
        JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
        
        // Extract token with null check
        if (jsonResponse == null || !jsonResponse.has("access_token")) {
            throw new Exception("Invalid registration response: missing access_token");
        }
        
        String token = jsonResponse.get("access_token").getAsString();
        
        // Save token and user
        saveToken(context, token, username, name, "");
        
        return new AuthResponse(true, "Registration successful", token, new User(username, name, ""));
    }
    
    /**
     * Login with Google token
     */
    public static AuthResponse loginWithGoogle(Context context, String googleToken) throws Exception {
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("google_token", googleToken);
        
        String url = ApiConfig.getApiUrl("/api/auth/google-login");
        Log.d(TAG, "Logging in with Google to: " + url);
        
        Request request = new Request.Builder()
                .url(url)
                .post(RequestBody.create(
                        gson.toJson(requestBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        Response response = httpClient.newCall(request).execute();
        String responseBody = response.body().string();
        
        if (!response.isSuccessful()) {
            throw new Exception("Google login failed: " + responseBody);
        }
        
        JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
        
        // Extract token and user info with null checks
        if (jsonResponse == null || !jsonResponse.has("access_token") || !jsonResponse.has("username")) {
            throw new Exception("Invalid Google login response: missing access_token or username");
        }
        
        String token = jsonResponse.get("access_token").getAsString();
        String username = jsonResponse.get("username").getAsString();
        String name = jsonResponse.has("name") && jsonResponse.get("name") != null ? jsonResponse.get("name").getAsString() : username;
        String email = jsonResponse.has("email") && jsonResponse.get("email") != null ? jsonResponse.get("email").getAsString() : "";
        
        saveToken(context, token, username, name, email);
        
        return new AuthResponse(true, "Google login successful", token, new User(username, name, email));
    }
    
    /**
     * Verify if current token is still valid
     */
    public static boolean verifyToken(Context context) throws Exception {
        String token = getToken(context);
        if (token == null) return false;
        
        String url = ApiConfig.getApiUrl("/api/auth/verify-token");
        Log.d(TAG, "Verifying token to: " + url);
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", "Bearer " + token)
                .post(RequestBody.create("", MediaType.parse("application/json")))
                .build();
        
        Response response = httpClient.newCall(request).execute();
        
        if (response.isSuccessful()) {
            Log.d(TAG, "Token is valid");
            return true;
        } else {
            Log.w(TAG, "Token verification failed");
            return false;
        }
    }
    
    /**
     * Save token to SharedPreferences
     */
    private static void saveToken(Context context, String token, String username, String name, String email) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit();
        
        editor.putString(KEY_TOKEN, token);
        
        User user = new User(username, name, email);
        editor.putString(KEY_USER, gson.toJson(user));
        
        // Token expires in 24 hours
        long expiresAt = System.currentTimeMillis() + (24 * 60 * 60 * 1000);
        editor.putLong(KEY_EXPIRES_AT, expiresAt);
        
        editor.apply();
        Log.d(TAG, "Token saved for user: " + username);
    }
    
    /**
     * Get current auth token
     */
    public static String getToken(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        return prefs.getString(KEY_TOKEN, null);
    }
    
    /**
     * Get "Authorization" header value
     */
    public static String getAuthHeader(Context context) {
        String token = getToken(context);
        if (token == null) return null;
        return "Bearer " + token;
    }
    
    /**
     * Get logged-in user info
     */
    public static User getUser(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String userJson = prefs.getString(KEY_USER, null);
        if (userJson == null) return null;
        return gson.fromJson(userJson, User.class);
    }
    
    /**
     * Logout — clear token and user
     */
    public static void logout(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit();
        editor.remove(KEY_TOKEN);
        editor.remove(KEY_USER);
        editor.remove(KEY_EXPIRES_AT);
        editor.apply();
        Log.d(TAG, "User logged out");
    }
    
    /**
     * Response model for auth operations
     */
    public static class AuthResponse {
        public boolean success;
        public String message;
        public String token;
        public User user;
        
        public AuthResponse(boolean success, String message, String token, User user) {
            this.success = success;
            this.message = message;
            this.token = token;
            this.user = user;
        }
    }
}
