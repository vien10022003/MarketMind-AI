package com.example.marketmindai.model;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * Stream message model for parsing NDJSON responses from backend.
 * Each line in the response is a JSON object of this type.
 */
public class StreamMessage implements Serializable {
    public String status;
    public String message;
    
    // Response content
    public ChatMessage.PlanData plan;
    public ChatMessage.ReactSummaryData react_summary;
    public ChatMessage.EvidenceData evidence;
    public ChatMessage.ReportData report;
    public ChatMessage.StrategyData strategy;
    public ChatMessage.CampaignLogData campaign_log;
    
    // Additional fields
    public List<String> sources;
    public List<String> questions_for_user;
    public List<String> questions;  // Alternative name for questions_for_user
    public Map<String, Object> detected_info;
    public Map<String, Object> clarified_input;
    public Map<String, String> explanations;
    public String detected_prompt;
    public boolean auto_proceeding;
    public String note;
    public String mongodb_id;
    public Map<String, Object> evidence_count;
    
    public StreamMessage() {}
    
    public StreamMessage(String status, String message) {
        this.status = status;
        this.message = message;
    }
    
    // Getters and setters
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public ChatMessage.PlanData getPlan() { return plan; }
    public void setPlan(ChatMessage.PlanData plan) { this.plan = plan; }
    
    public ChatMessage.ReactSummaryData getReactSummary() { return react_summary; }
    public void setReactSummary(ChatMessage.ReactSummaryData react_summary) { this.react_summary = react_summary; }
    
    public ChatMessage.EvidenceData getEvidence() { return evidence; }
    public void setEvidence(ChatMessage.EvidenceData evidence) { this.evidence = evidence; }
    
    public ChatMessage.ReportData getReport() { return report; }
    public void setReport(ChatMessage.ReportData report) { this.report = report; }
    
    public ChatMessage.StrategyData getStrategy() { return strategy; }
    public void setStrategy(ChatMessage.StrategyData strategy) { this.strategy = strategy; }
    
    public ChatMessage.CampaignLogData getCampaignLog() { return campaign_log; }
    public void setCampaignLog(ChatMessage.CampaignLogData campaign_log) { this.campaign_log = campaign_log; }
    
    public String getMongodbId() { return mongodb_id; }
    public void setMongodbId(String mongodb_id) { this.mongodb_id = mongodb_id; }
}
