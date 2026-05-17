package com.example.marketmindai.model;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * Conversation turn model for history.
 */
class ConversationTurn implements Serializable {
    public String role; // 'user' or 'assistant'
    public String content;
    
    public ConversationTurn(String role, String content) {
        this.role = role;
        this.content = content;
    }
}

/**
 * Research report model.
 */
class ResearchReport implements Serializable {
    public String title;
    public String summary;
    public List<ReportSection> sections;
    public Map<String, Object> metadata;
}

/**
 * Report section model.
 */
class ReportSection implements Serializable {
    public String title;
    public String content;
    public int order;
}

/**
 * Content brief model for Stage B/C.
 */
class ContentBrief implements Serializable {
    public String id;
    public String title;
    public String content;
    public String platform;
    public String tone;
    public boolean approved;
}

/**
 * Stage B output model.
 */
class StageBOutput implements Serializable {
    public String title;
    public Map<String, Object> swot;
    public Map<String, Object> usp;
    public Map<String, Object> persona;
    public Map<String, Object> pillars;
    public List<ContentBrief> content_briefs;
}

/**
 * Campaign log model for Stage C.
 */
class CampaignLog implements Serializable {
    public List<BriefExecution> briefs_executed;
    public int total_posts;
    public int successful_posts;
    public List<String> image_urls;
}

/**
 * Brief execution model.
 */
class BriefExecution implements Serializable {
    public String brief_id;
    public String title;
    public boolean success;
    public String message;
    public String image_url;
    public String post_url;
}
