package com.example.marketmindai.model;

import java.io.Serializable;
import java.util.List;

/**
 * Research request model for API calls.
 */
public class ResearchRequest implements Serializable {
    public String user_prompt;
    public List<ConversationTurn> conversation_history;
    public String llm_provider; // 'llama', 'gemini-2.5', 'gemini-3.1'
    
    public ResearchRequest() {}
    
    public ResearchRequest(String user_prompt, String llm_provider) {
        this.user_prompt = user_prompt;
        this.llm_provider = llm_provider;
    }
}
