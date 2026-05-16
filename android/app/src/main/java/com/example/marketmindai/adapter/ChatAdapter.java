package com.example.marketmindai.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.R;
import com.example.marketmindai.model.ChatMessage;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

/**
 * Adapter for chat messages with multiple view types.
 * Supports user, assistant, status, error, and other message types.
 */
public class ChatAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {
    
    private static final String TAG = "ChatAdapter";
    
    // View type constants
    private static final int VIEW_TYPE_USER = 0;
    private static final int VIEW_TYPE_ASSISTANT = 1;
    private static final int VIEW_TYPE_STATUS = 2;
    private static final int VIEW_TYPE_ERROR = 3;
    
    private List<ChatMessage> messages;
    private SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm", Locale.getDefault());
    
    public ChatAdapter(List<ChatMessage> messages) {
        this.messages = messages;
    }
    
    @Override
    public int getItemViewType(int position) {
        ChatMessage msg = messages.get(position);
        
        switch (msg.type) {
            case "user":
                return VIEW_TYPE_USER;
            case "assistant":
            case "knowledge":
            case "completed":
                return VIEW_TYPE_ASSISTANT;
            case "status":
            case "clarification":
            case "plan":
            case "react_summary":
            case "evidence":
            case "report":
            case "strategy":
            case "campaign_results":
            case "stage_c_schedule_proposal":
            case "marketing_form":
                return VIEW_TYPE_STATUS; // Placeholder for now
            case "error":
                return VIEW_TYPE_ERROR;
            default:
                return VIEW_TYPE_ASSISTANT;
        }
    }
    
    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        
        switch (viewType) {
            case VIEW_TYPE_USER:
                View userView = inflater.inflate(R.layout.item_chat_user, parent, false);
                return new UserMessageVH(userView);
            case VIEW_TYPE_ASSISTANT:
                View assistantView = inflater.inflate(R.layout.item_chat_assistant, parent, false);
                return new AssistantMessageVH(assistantView);
            case VIEW_TYPE_STATUS:
                View statusView = inflater.inflate(R.layout.item_chat_status, parent, false);
                return new StatusMessageVH(statusView);
            case VIEW_TYPE_ERROR:
                View errorView = inflater.inflate(R.layout.item_chat_error, parent, false);
                return new ErrorMessageVH(errorView);
            default:
                View defaultView = inflater.inflate(R.layout.item_chat_assistant, parent, false);
                return new AssistantMessageVH(defaultView);
        }
    }
    
    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        ChatMessage message = messages.get(position);
        
        if (holder instanceof UserMessageVH) {
            ((UserMessageVH) holder).bind(message);
        } else if (holder instanceof AssistantMessageVH) {
            ((AssistantMessageVH) holder).bind(message);
        } else if (holder instanceof StatusMessageVH) {
            ((StatusMessageVH) holder).bind(message);
        } else if (holder instanceof ErrorMessageVH) {
            ((ErrorMessageVH) holder).bind(message);
        }
    }
    
    @Override
    public int getItemCount() {
        return messages.size();
    }
    
    /**
     * User message view holder
     */
    public class UserMessageVH extends RecyclerView.ViewHolder {
        private TextView tvContent;
        private TextView tvTime;
        
        public UserMessageVH(@NonNull View itemView) {
            super(itemView);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTime = itemView.findViewById(R.id.tv_message_time);
        }
        
        public void bind(ChatMessage msg) {
            tvContent.setText(msg.content);
            tvTime.setText(timeFormat.format(msg.timestamp));
        }
    }
    
    /**
     * Assistant message view holder
     */
    public class AssistantMessageVH extends RecyclerView.ViewHolder {
        private TextView tvContent;
        private TextView tvTime;
        
        public AssistantMessageVH(@NonNull View itemView) {
            super(itemView);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTime = itemView.findViewById(R.id.tv_message_time);
        }
        
        public void bind(ChatMessage msg) {
            tvContent.setText(msg.content);
            tvTime.setText(timeFormat.format(msg.timestamp));
        }
    }
    
    /**
     * Status/info message view holder
     */
    public class StatusMessageVH extends RecyclerView.ViewHolder {
        private ProgressBar pbStatus;
        private TextView tvMessage;
        
        public StatusMessageVH(@NonNull View itemView) {
            super(itemView);
            pbStatus = itemView.findViewById(R.id.pb_status);
            tvMessage = itemView.findViewById(R.id.tv_status_message);
        }
        
        public void bind(ChatMessage msg) {
            tvMessage.setText(msg.content);
            
            // Hide progress bar for non-ongoing statuses
            if (msg.type.equals("completed")) {
                pbStatus.setVisibility(View.GONE);
            } else {
                pbStatus.setVisibility(View.VISIBLE);
            }
        }
    }
    
    /**
     * Error message view holder
     */
    public class ErrorMessageVH extends RecyclerView.ViewHolder {
        private TextView tvError;
        
        public ErrorMessageVH(@NonNull View itemView) {
            super(itemView);
            tvError = itemView.findViewById(R.id.tv_error_message);
        }
        
        public void bind(ChatMessage msg) {
            tvError.setText(msg.content);
        }
    }
    
    /**
     * Update messages list and notify
     */
    public void updateMessages(List<ChatMessage> newMessages) {
        this.messages = newMessages;
        notifyDataSetChanged();
    }
    
    /**
     * Add a new message to the end
     */
    public void addMessage(ChatMessage message) {
        messages.add(message);
        notifyItemInserted(messages.size() - 1);
    }
}
