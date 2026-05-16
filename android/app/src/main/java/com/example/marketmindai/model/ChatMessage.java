package com.example.marketmindai.model;

import java.io.Serializable;
import java.util.Date;
import java.util.Map;

/**
 * Chat message model matching TypeScript ChatMessage interface.
 * Represents all types of messages in the chat system.
 */
public class ChatMessage implements Serializable {
    public String id;
    public String type; // 'user', 'assistant', 'status', 'error', 'clarification', 'plan', etc.
    public String content;
    public Date timestamp;
    
    // Optional payloads for different message types
    public ClarificationData clarificationData;
    public PlanData planData;
    public ReactSummaryData reactSummaryData;
    public EvidenceData evidenceData;
    public ReportData reportData;
    public KnowledgeData knowledgeData;
    public MarketingFormData marketingFormData;
    public StrategyData strategyData;
    public CampaignLogData campaignLogData;
    public StageBProposalData stageBProposalData;
    public StageCScheduleProposalData stageCScheduleProposalData;
    public String mongodbId; // For completed messages
    
    public ChatMessage(String id, String type, String content, Date timestamp) {
        this.id = id;
        this.type = type;
        this.content = content;
        this.timestamp = timestamp;
    }
    
    // Getters and setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    
    public Date getTimestamp() { return timestamp; }
    public void setTimestamp(Date timestamp) { this.timestamp = timestamp; }
    
    // Nested data classes for different message types
    
    public static class ClarificationData implements Serializable {
        public String detected_info;
        public java.util.List<String> questions_for_user;
        public Map<String, Object> clarified_input;
        public Map<String, String> explanations;
        public boolean auto_proceeding;
        public String note;
    }
    
    public static class PlanData implements Serializable {
        public java.util.List<PlanStep> steps;
        public String summary;
    }
    
    public static class PlanStep implements Serializable {
        public int order;
        public String name;
        public String description;
        public java.util.List<String> sources;
    }
    
    public static class ReactSummaryData implements Serializable {
        public int total_thoughts;
        public int total_tools_used;
        public double total_cost;
        public long total_duration_ms;
        public java.util.List<ReactStep> steps;
    }
    
    public static class ReactStep implements Serializable {
        public int order;
        public String name;
        public String reasoning;
        public String action;
        public String observation;
    }
    
    public static class EvidenceData implements Serializable {
        public java.util.List<Evidence> items;
    }
    
    public static class Evidence implements Serializable {
        public String type;
        public String title;
        public String content;
        public String source;
    }
    
    public static class ReportData implements Serializable {
        public String title;
        public String summary;
        public java.util.List<ReportSection> sections;
        public java.util.Map<String, Object> metadata;
    }
    
    public static class ReportSection implements Serializable {
        public String title;
        public String content;
        public int order;
    }
    
    public static class KnowledgeData implements Serializable {
        public String answer;
        public java.util.List<Source> sources;
    }
    
    public static class Source implements Serializable {
        public String title;
        public String url;
    }
    
    public static class MarketingFormData implements Serializable {
        public String detected_prompt;
    }
    
    public static class StrategyData implements Serializable {
        public String title;
        public SWOT swot;
        public USP usp;
        public Persona persona;
        public Pillars pillars;
        public java.util.List<ContentBrief> content_briefs;
    }
    
    public static class SWOT implements Serializable {
        public java.util.List<String> strengths;
        public java.util.List<String> weaknesses;
        public java.util.List<String> opportunities;
        public java.util.List<String> threats;
    }
    
    public static class USP implements Serializable {
        public String core_benefit;
        public java.util.List<String> differentiators;
        public String tagline;
    }
    
    public static class Persona implements Serializable {
        public String name;
        public String age;
        public String occupation;
        public java.util.List<String> pain_points;
        public java.util.List<String> goals;
    }
    
    public static class Pillars implements Serializable {
        public java.util.List<String> marketing_pillars;
        public java.util.List<String> content_themes;
    }
    
    public static class ContentBrief implements Serializable {
        public String id;
        public String title;
        public String content;
        public String platform;
        public String tone;
        public boolean approved;
    }
    
    public static class CampaignLogData implements Serializable {
        public java.util.List<BriefExecution> briefs_executed;
        public int total_posts;
        public int successful_posts;
        public java.util.List<String> image_urls;
    }
    
    public static class BriefExecution implements Serializable {
        public String brief_id;
        public String title;
        public boolean success;
        public String message;
        public String image_url;
        public String post_url;
    }
    
    public static class StageBProposalData implements Serializable {
        public ReportData report;
        public String mongodbId;
    }
    
    public static class StageCScheduleProposalData implements Serializable {
        public java.util.List<ContentBrief> briefs;
        public String mongodbId;
    }
}
