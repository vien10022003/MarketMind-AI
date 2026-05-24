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
        if (json.has("_id") && !json.get("_id").isJsonNull()) _id = json.get("_id").getAsString();
        if (json.has("campaign_id") && !json.get("campaign_id").isJsonNull()) campaign_id = json.get("campaign_id").getAsString();
        if (json.has("status") && !json.get("status").isJsonNull()) status = json.get("status").getAsString();
        if (json.has("execution_mode") && !json.get("execution_mode").isJsonNull()) execution_mode = json.get("execution_mode").getAsString();
        if (json.has("total_briefs") && !json.get("total_briefs").isJsonNull()) total_briefs = json.get("total_briefs").getAsInt();
        if (json.has("total_posted") && !json.get("total_posted").isJsonNull()) total_posted = json.get("total_posted").getAsInt();
        else if (json.has("posted_count") && !json.get("posted_count").isJsonNull()) total_posted = json.get("posted_count").getAsInt();
        
        if (json.has("total_failed") && !json.get("total_failed").isJsonNull()) total_failed = json.get("total_failed").getAsInt();
        else if (json.has("failed_count") && !json.get("failed_count").isJsonNull()) total_failed = json.get("failed_count").getAsInt();
        
        // Backend returns "total_scheduled" as the total number of briefs
        if (json.has("total_scheduled") && !json.get("total_scheduled").isJsonNull()) {
            total_briefs = json.get("total_scheduled").getAsInt();
        }
        
        // Calculate pending (Chờ Post) dynamically
        total_scheduled = Math.max(0, total_briefs - total_posted - total_failed);
        if (json.has("started_at") && !json.get("started_at").isJsonNull()) started_at = json.get("started_at").getAsString();
        if (json.has("completed_at") && !json.get("completed_at").isJsonNull()) completed_at = json.get("completed_at").getAsString();
        
        // Parse execution results
        if (json.has("execution_results") && !json.get("execution_results").isJsonNull()) {
            JsonArray results = json.getAsJsonArray("execution_results");
            for (int i = 0; i < results.size(); i++) {
                execution_results.add(new CampaignResult(results.get(i).getAsJsonObject()));
            }
        }
    }
    
    public String getStatusLabel() {
        switch (status) {
            case "scheduled":
                return "Đang Chờ";
            case "completed":
                return "Hoàn Tất";
            case "failed":
                return "Lỗi";
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
            if (json.has("brief_title") && !json.get("brief_title").isJsonNull()) brief_title = json.get("brief_title").getAsString();
            if (json.has("status") && !json.get("status").isJsonNull()) status = json.get("status").getAsString();
            if (json.has("image_url") && !json.get("image_url").isJsonNull()) image_url = json.get("image_url").getAsString();
            if (json.has("image_skipped") && !json.get("image_skipped").isJsonNull()) image_skipped = json.get("image_skipped").getAsBoolean();
            if (json.has("discord_sent") && !json.get("discord_sent").isJsonNull()) discord_sent = json.get("discord_sent").getAsBoolean();
            if (json.has("error") && !json.get("error").isJsonNull()) error = json.get("error").getAsString();
        }
    }
}
