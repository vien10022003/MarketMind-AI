package com.example.marketmindai.model;

import com.google.gson.JsonObject;
import com.google.gson.JsonArray;

import java.util.ArrayList;
import java.util.List;

/**
 * Campaign model representing a marketing campaign
 */
public class Campaign {
    public String _id;
    public String campaign_id;
    public String status;           // "scheduled", "completed", "failed"
    public String execution_mode;   // "instant", "scheduled"
    public int total_briefs;
    public int total_posted;
    public int total_scheduled;
    public int total_failed;
    public String started_at;
    public String completed_at;
    public List<CampaignResult> execution_results;
    
    public Campaign() {
        execution_results = new ArrayList<>();
    }
    
    public Campaign(JsonObject json) {
        this();
        if (json.has("_id")) _id = json.get("_id").getAsString();
        if (json.has("campaign_id")) campaign_id = json.get("campaign_id").getAsString();
        if (json.has("status")) status = json.get("status").getAsString();
        if (json.has("execution_mode")) execution_mode = json.get("execution_mode").getAsString();
        if (json.has("total_briefs")) total_briefs = json.get("total_briefs").getAsInt();
        if (json.has("total_posted")) total_posted = json.get("total_posted").getAsInt();
        if (json.has("total_scheduled")) total_scheduled = json.get("total_scheduled").getAsInt();
        if (json.has("total_failed")) total_failed = json.get("total_failed").getAsInt();
        if (json.has("started_at")) started_at = json.get("started_at").getAsString();
        if (json.has("completed_at")) completed_at = json.get("completed_at").getAsString();
        
        // Parse execution results
        if (json.has("execution_results")) {
            JsonArray results = json.getAsJsonArray("execution_results");
            for (int i = 0; i < results.size(); i++) {
                execution_results.add(new CampaignResult(results.get(i).getAsJsonObject()));
            }
        }
    }
    
    public String getStatusLabel() {
        switch (status) {
            case "scheduled":
                return "⏳ Đang Chờ";
            case "completed":
                return "✅ Hoàn Tất";
            case "failed":
                return "❌ Lỗi";
            default:
                return status;
        }
    }
    
    public int getSuccessRate() {
        if (total_briefs == 0) return 0;
        return (int) Math.round((total_posted * 100.0) / total_briefs);
    }
    
    public String toJson() {
        return new com.google.gson.Gson().toJson(this);
    }
    
    /**
     * Campaign execution result for individual brief
     */
    public static class CampaignResult {
        public String brief_title;
        public String status;           // "success", "failed", "skipped"
        public String image_url;
        public boolean image_skipped;
        public boolean discord_sent;
        public String error;
        
        public CampaignResult() {}
        
        public CampaignResult(JsonObject json) {
            if (json.has("brief_title")) brief_title = json.get("brief_title").getAsString();
            if (json.has("status")) status = json.get("status").getAsString();
            if (json.has("image_url")) image_url = json.get("image_url").getAsString();
            if (json.has("image_skipped")) image_skipped = json.get("image_skipped").getAsBoolean();
            if (json.has("discord_sent")) discord_sent = json.get("discord_sent").getAsBoolean();
            if (json.has("error")) error = json.get("error").getAsString();
        }
    }
}
