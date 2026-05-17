package com.example.marketmindai;

import android.util.Log;
import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.reflect.TypeToken;
import com.example.marketmindai.config.ApiConfig;
import com.example.marketmindai.model.ChatMessage;
import com.example.marketmindai.model.Conversation;
import com.example.marketmindai.model.StreamMessage;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Research service for handling API calls to backend.
 * Supports streaming responses (NDJSON format).
 * 
 * API endpoints match frontend config.ts:
 *   /api/research/stage_a
 *   /api/research/stage_a/marketing
 *   /api/strategy/stage_b
 *   /api/strategy/stage_b/approve
 *   /api/campaign/stage_c
 *   /api/campaign/stage_c/scheduled
 *   /api/conversations
 */
public class ResearchService {
    private static final String TAG = "ResearchService";
    private static final OkHttpClient httpClient = new OkHttpClient.Builder()
            .readTimeout(5, TimeUnit.MINUTES)
            .writeTimeout(5, TimeUnit.MINUTES)
            .connectTimeout(30, TimeUnit.SECONDS)
            .build();
    
    private static final Gson gson = new Gson();
    
    /**
     * Callback interface for streaming responses
     */
    public interface StreamCallback {
        void onMessage(StreamMessage msg);
        void onError(String error);
        void onComplete();
    }
    
    /**
     * Error callback interface
     */
    public interface ErrorCallback {
        void onError(String error);
    }
    
    // ────────────────────────────────────────────────────────────
    // Streaming Research Endpoints
    // ────────────────────────────────────────────────────────────
    
    /**
     * Call Stage A research endpoint with streaming
     * Matches frontend: /api/research/stage_a
     */
    public static void callStageAResearch(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) {
        String url = ApiConfig.getApiUrl("/api/research/stage_a");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call marketing research endpoint with streaming (skips intent classification)
     * Matches frontend: /api/research/stage_a/marketing
     */
    public static void callMarketingResearch(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) {
        String url = ApiConfig.getApiUrl("/api/research/stage_a/marketing");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call Stage B strategy endpoint with streaming
     * Matches frontend: /api/strategy/stage_b
     */
    public static void callStageBStrategy(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) {
        String url = ApiConfig.getApiUrl("/api/strategy/stage_b");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call Stage C campaign endpoint with streaming
     * Matches frontend: /api/campaign/stage_c
     */
    public static void callStageCCampaign(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) {
        String url = ApiConfig.getApiUrl("/api/campaign/stage_c");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call Stage C scheduled campaign endpoint with streaming
     * Matches frontend: /api/campaign/stage_c/scheduled
     */
    public static void callStageCCampaignScheduled(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) {
        String url = ApiConfig.getApiUrl("/api/campaign/stage_c/scheduled");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Approve Stage B briefs (non-streaming)
     * Matches frontend: /api/strategy/stage_b/approve
     */
    public static void approveStageBBriefs(
            android.content.Context context,
            Map<String, Object> request
    ) {
        String url = ApiConfig.getApiUrl("/api/strategy/stage_b/approve");
        String authHeader = AuthService.getAuthHeader(context);
        
        Request.Builder builder = new Request.Builder()
                .url(url)
                .addHeader("ngrok-skip-browser-warning", "true")
                .post(RequestBody.create(
                        gson.toJson(request),
                        MediaType.parse("application/json")
                ));
        
        if (authHeader != null) {
            builder.addHeader("Authorization", authHeader);
        }
        
        try (Response response = httpClient.newCall(builder.build()).execute()) {
            if (!response.isSuccessful()) {
                Log.w(TAG, "Approve briefs failed: " + response.code());
            }
        } catch (IOException e) {
            Log.e(TAG, "Approve briefs error: " + e.getMessage());
        }
    }
    
    // ────────────────────────────────────────────────────────────
    // Conversation History APIs
    // Backend returns wrapped format: { "status": "success", "data": { ... } }
    // ────────────────────────────────────────────────────────────
    
    /**
     * List all conversations.
     * Response format: { "status": "...", "data": { "conversations": [...], "total": N } }
     */
    public static List<Conversation> listConversations(
            android.content.Context context,
            int skip,
            int limit
    ) {
        try {
            String url = ApiConfig.getApiUrl("/api/conversations?skip=" + skip + "&limit=" + limit);
            String authHeader = AuthService.getAuthHeader(context);
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .get();
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            Response response = httpClient.newCall(builder.build()).execute();
            String responseBody = response.body() != null ? response.body().string() : "";
            
            if (!response.isSuccessful()) {
                Log.w(TAG, "List conversations failed: " + response.code() + " - " + responseBody);
                return new ArrayList<>();
            }
            System.out.println("aaaaaaa jsonResponse");
            // Parse wrapped response: { "data": { "conversations": [...] } }
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            System.out.println(jsonResponse);
            if (jsonResponse != null && jsonResponse.has("data")) {
                JsonObject data = jsonResponse.getAsJsonObject("data");
                if (data != null && data.has("conversations")) {
                    JsonArray convArray = data.getAsJsonArray("conversations");
                    if (convArray != null) {
                        return gson.fromJson(convArray, new TypeToken<List<Conversation>>(){}.getType());
                    }
                }
            }
            
            return new ArrayList<>();
        } catch (Exception e) {
            Log.e(TAG, "List conversations error: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    /**
     * Get a specific conversation with messages.
     * Response format: { "status": "...", "data": { "conversation_id": "...", "messages": [...] } }
     */
    public static Conversation getConversation(
            android.content.Context context,
            String conversationId
    ) {
        try {
            String url = ApiConfig.getApiUrl("/api/conversations/" + conversationId);
            String authHeader = AuthService.getAuthHeader(context);
            
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .get();
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            Response response = httpClient.newCall(builder.build()).execute();
            String responseBody = response.body() != null ? response.body().string() : "";
            
            if (!response.isSuccessful()) {
                Log.w(TAG, "Get conversation failed: " + response.code());
                return null;
            }
            
            // Parse wrapped response: { "data": { ... } }
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            if (jsonResponse != null && jsonResponse.has("data")) {
                JsonObject data = jsonResponse.getAsJsonObject("data");
                if (data != null) {
                    return gson.fromJson(data, Conversation.class);
                }
            }
            
            return null;
        } catch (Exception e) {
            Log.e(TAG, "Get conversation error: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Create a new conversation.
     * Response format: { "status": "...", "data": { "conversation_id": "..." } }
     */
    public static Conversation createConversation(
            android.content.Context context,
            String firstMessage,
            String title
    ) {
        try {
            String url = ApiConfig.getApiUrl("/api/conversations");
            String authHeader = AuthService.getAuthHeader(context);
            
            JsonObject requestBody = new JsonObject();
            if (firstMessage != null) requestBody.addProperty("first_message", firstMessage);
            if (title != null) requestBody.addProperty("title", title);
            
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .post(RequestBody.create(
                            gson.toJson(requestBody),
                            MediaType.parse("application/json")
                    ));
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            Response response = httpClient.newCall(builder.build()).execute();
            String responseBody = response.body() != null ? response.body().string() : "";
            
            if (!response.isSuccessful()) {
                Log.w(TAG, "Create conversation failed: " + response.code());
                return null;
            }
            
            // Parse wrapped response: { "data": { ... } }
            JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
            if (jsonResponse != null && jsonResponse.has("data")) {
                JsonObject data = jsonResponse.getAsJsonObject("data");
                if (data != null) {
                    return gson.fromJson(data, Conversation.class);
                }
            }
            
            return null;
        } catch (Exception e) {
            Log.e(TAG, "Create conversation error: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * Save messages to conversation
     */
    public static boolean saveMessagesToConversation(
            android.content.Context context,
            String conversationId,
            List<ChatMessage> messages
    ) {
        try {
            String url = ApiConfig.getApiUrl("/api/conversations/" + conversationId + "/messages");
            String authHeader = AuthService.getAuthHeader(context);
            
            JsonObject requestBody = new JsonObject();
            requestBody.add("messages", gson.toJsonTree(messages));
            
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .post(RequestBody.create(
                            gson.toJson(requestBody),
                            MediaType.parse("application/json")
                    ));
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            try (Response response = httpClient.newCall(builder.build()).execute()) {
                if (!response.isSuccessful()) {
                    Log.w(TAG, "Save messages failed: " + response.code());
                    return false;
                }
                return true;
            }
        } catch (Exception e) {
            Log.e(TAG, "Save messages error: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Delete a conversation
     */
    public static boolean deleteConversation(
            android.content.Context context,
            String conversationId
    ) {
        try {
            String url = ApiConfig.getApiUrl("/api/conversations/" + conversationId);
            String authHeader = AuthService.getAuthHeader(context);
            
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .delete();
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            try (Response response = httpClient.newCall(builder.build()).execute()) {
                if (!response.isSuccessful()) {
                    Log.w(TAG, "Delete conversation failed: " + response.code());
                    return false;
                }
                return true;
            }
        } catch (Exception e) {
            Log.e(TAG, "Delete conversation error: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Get scheduled campaigns
     */
    public static JsonArray getScheduledCampaigns(
            android.content.Context context,
            String status
    ) {
        try {
            String url = status != null
                    ? ApiConfig.getApiUrl("/api/stage-c/scheduler/campaigns?status=" + status)
                    : ApiConfig.getApiUrl("/api/stage-c/scheduler/campaigns");
            String authHeader = AuthService.getAuthHeader(context);
            
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .get();
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            Response response = httpClient.newCall(builder.build()).execute();
            String responseBody = response.body() != null ? response.body().string() : "";
            
            if (response.isSuccessful()) {
                JsonObject jsonResponse = gson.fromJson(responseBody, JsonObject.class);
                if (jsonResponse != null && jsonResponse.has("data")) {
                    JsonObject data = jsonResponse.getAsJsonObject("data");
                    if (data != null && data.has("campaigns")) {
                        return data.getAsJsonArray("campaigns");
                    }
                }
            }
            return new JsonArray();
        } catch (Exception e) {
            Log.e(TAG, "Get campaigns error: " + e.getMessage());
            return new JsonArray();
        }
    }
    
    // ────────────────────────────────────────────────────────────
    // Streaming Engine
    // ────────────────────────────────────────────────────────────
    
    /**
     * Generic streaming endpoint handler with NDJSON parsing.
     * Runs synchronously — must be called from a background thread.
     */
    private static void callStreamingEndpoint(
            android.content.Context context,
            String url,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) {
        try {
            String authHeader = AuthService.getAuthHeader(context);
            
            Request.Builder builder = new Request.Builder()
                    .url(url)
                    .addHeader("ngrok-skip-browser-warning", "true")
                    .addHeader("Content-Type", "application/json")
                    .post(RequestBody.create(
                            gson.toJson(request),
                            MediaType.parse("application/json")
                    ));
            
            if (authHeader != null) {
                builder.addHeader("Authorization", authHeader);
            }
            
            Log.d(TAG, "API call: " + url);
            Response response = httpClient.newCall(builder.build()).execute();
            
            if (!response.isSuccessful()) {
                String errorMsg = "Unknown error";
                try {
                    if (response.body() != null) {
                        errorMsg = response.body().string();
                    }
                } catch (Exception e) {
                    Log.w(TAG, "Failed to read error response body: " + e.getMessage());
                }
                Log.e(TAG, "Request failed: " + response.code() + " - " + errorMsg);
                if (errorCallback != null) errorCallback.onError("Request failed: " + errorMsg);
                callback.onError("Request failed: " + response.code());
                return;
            }
            
            if (response.body() == null) {
                callback.onError("Empty response body");
                return;
            }
            
            // Process NDJSON stream line by line
            try (BufferedReader reader = new BufferedReader(
                    new InputStreamReader(response.body().byteStream())
            )) {
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.trim().isEmpty()) continue;
                    
                    try {
                        StreamMessage msg = gson.fromJson(line, StreamMessage.class);
                        if (msg != null) {
                            callback.onMessage(msg);
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "Failed to parse stream message: " + e.getMessage());
                    }
                }
                callback.onComplete();
            }
        } catch (IOException e) {
            Log.e(TAG, "Stream error: " + e.getMessage());
            if (errorCallback != null) errorCallback.onError("Stream error: " + e.getMessage());
            callback.onError("Stream error: " + e.getMessage());
        }
    }
}
