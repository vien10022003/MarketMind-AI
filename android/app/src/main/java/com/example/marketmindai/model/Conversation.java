package com.example.marketmindai.model;

import java.io.Serializable;
import java.util.Date;
import java.util.List;

/**
 * Conversation model for storing conversation metadata.
 */
public class Conversation implements Serializable {
    public String conversation_id;
    public String title;
    public String user_id;
    public Date created_at;
    public Date updated_at;
    public List<ChatMessage> messages;
    public String last_message_preview;
    
    public Conversation() {}
    
    public Conversation(String conversation_id, String title) {
        this.conversation_id = conversation_id;
        this.title = title;
        this.created_at = new Date();
        this.updated_at = new Date();
    }
    
    // Getters and setters
    public String getConversationId() { return conversation_id; }
    public void setConversationId(String id) { this.conversation_id = id; }
    
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    
    public String getUserId() { return user_id; }
    public void setUserId(String userId) { this.user_id = userId; }
    
    public Date getCreatedAt() { return created_at; }
    public void setCreatedAt(Date date) { this.created_at = date; }
    
    public Date getUpdatedAt() { return updated_at; }
    public void setUpdatedAt(Date date) { this.updated_at = date; }
    
    public List<ChatMessage> getMessages() { return messages; }
    public void setMessages(List<ChatMessage> messages) { this.messages = messages; }
    
    public String getLastMessagePreview() { return last_message_preview; }
    public void setLastMessagePreview(String preview) { this.last_message_preview = preview; }
}
