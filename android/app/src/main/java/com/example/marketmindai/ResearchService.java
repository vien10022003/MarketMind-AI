package com.example.marketmindai;

import android.util.Log;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
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
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/**
 * Research service for handling API calls to backend.
 * Supports streaming responses (NDJSON format).
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
     * Call Stage A research endpoint with streaming
     */
    public static void callStageAResearch(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/stage_a_research");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call marketing research endpoint with streaming (skips intent classification)
     */
    public static void callMarketingResearch(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/marketing");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call Stage B strategy endpoint with streaming
     */
    public static void callStageBStrategy(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/stage_b_strategy");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call Stage C campaign endpoint with streaming
     */
    public static void callStageCCampaign(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/stage_c_campaign");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Call Stage C scheduled campaign endpoint with streaming
     */
    public static void callStageCCampaignScheduled(
            android.content.Context context,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/stage_c_campaign_scheduled");
        callStreamingEndpoint(context, url, request, callback, errorCallback);
    }
    
    /**
     * Approve Stage B briefs (non-streaming)
     */
    public static void approveStageBBriefs(
            android.content.Context context,
            Map<String, Object> request
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/approve_stage_b_briefs");
        JsonObject jsonBody = gson.toJsonTree(request).getAsJsonObject();
        
        Request httpRequest = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .post(RequestBody.create(
                        gson.toJson(jsonBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        try (Response response = httpClient.newCall(httpRequest).execute()) {
            if (!response.isSuccessful()) {
                Log.w(TAG, "Approve briefs failed: " + response.code());
            }
        }
    }
    
    /**
     * List all conversations
     */
    public static List<Conversation> listConversations(
            android.content.Context context
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/conversations");
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .get()
                .build();
        
        Response response = httpClient.newCall(request).execute();
        String responseBody = response.body().string();
        
        if (!response.isSuccessful()) {
            throw new IOException("List conversations failed: " + responseBody);
        }
        
        // Parse response
        List<Conversation> conversations = gson.fromJson(
                responseBody,
                com.google.gson.reflect.TypeToken.getParameterized(
                        List.class,
                        Conversation.class
                ).getType()
        );
        
        return conversations;
    }
    
    /**
     * Get a specific conversation
     */
    public static Conversation getConversation(
            android.content.Context context,
            String conversationId
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/conversations/" + conversationId);
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .get()
                .build();
        
        Response response = httpClient.newCall(request).execute();
        String responseBody = response.body().string();
        
        if (!response.isSuccessful()) {
            throw new IOException("Get conversation failed: " + responseBody);
        }
        
        return gson.fromJson(responseBody, Conversation.class);
    }
    
    /**
     * Create a new conversation
     */
    public static Conversation createConversation(
            android.content.Context context,
            String title
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/conversations");
        
        JsonObject requestBody = new JsonObject();
        requestBody.addProperty("title", title != null ? title : "New Conversation");
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .post(RequestBody.create(
                        gson.toJson(requestBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        Response response = httpClient.newCall(request).execute();
        String responseBody = response.body().string();
        
        if (!response.isSuccessful()) {
            throw new IOException("Create conversation failed: " + responseBody);
        }
        
        return gson.fromJson(responseBody, Conversation.class);
    }
    
    /**
     * Save messages to conversation
     */
    public static void saveMessagesToConversation(
            android.content.Context context,
            String conversationId,
            List<ChatMessage> messages
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/conversations/" + conversationId + "/messages");
        
        JsonObject requestBody = new JsonObject();
        requestBody.add("messages", gson.toJsonTree(messages));
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .post(RequestBody.create(
                        gson.toJson(requestBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                Log.w(TAG, "Save messages failed: " + response.code());
            }
        }
    }
    
    /**
     * Delete a conversation
     */
    public static void deleteConversation(
            android.content.Context context,
            String conversationId
    ) throws IOException {
        String url = ApiConfig.getApiUrl("/api/conversations/" + conversationId);
        
        Request request = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .delete()
                .build();
        
        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                Log.w(TAG, "Delete conversation failed: " + response.code());
            }
        }
    }
    
    /**
     * Generic streaming endpoint handler
     */
    private static void callStreamingEndpoint(
            android.content.Context context,
            String url,
            Map<String, Object> request,
            StreamCallback callback,
            ErrorCallback errorCallback
    ) throws IOException {
        JsonObject jsonBody = gson.toJsonTree(request).getAsJsonObject();
        
        Request httpRequest = new Request.Builder()
                .url(url)
                .addHeader("Authorization", AuthService.getAuthHeader(context))
                .post(RequestBody.create(
                        gson.toJson(jsonBody),
                        MediaType.parse("application/json")
                ))
                .build();
        
        Response response = httpClient.newCall(httpRequest).execute();
        
        if (!response.isSuccessful()) {
            String errorMsg = response.body().string();
            Log.e(TAG, "Request failed: " + errorMsg);
            if (errorCallback != null) {
                errorCallback.onError("Request failed: " + errorMsg);
            }
            callback.onError("Request failed");
            return;
        }
        
        // Process NDJSON stream
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(response.body().byteStream())
        )) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isEmpty()) continue;
                
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
        } catch (IOException e) {
            Log.e(TAG, "Stream reading error: " + e.getMessage());
            if (errorCallback != null) {
                errorCallback.onError("Stream error: " + e.getMessage());
            }
            callback.onError("Stream error");
        }
    }
    
    /**
     * Error callback interface
     */
    public interface ErrorCallback {
        void onError(String error);
    }
}
