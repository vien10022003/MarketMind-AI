package com.example.marketmindai.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.R;
import com.example.marketmindai.model.Conversation;

import java.text.SimpleDateFormat;
import java.util.List;
import java.util.Locale;

/**
 * Adapter for conversation list in sidebar.
 * Shows conversation titles, previews, and timestamps.
 */
public class ConversationListAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {
    
    private static final String TAG = "ConversationListAdapter";
    private static final int VIEW_TYPE_CONVERSATION = 0;
    private static final int VIEW_TYPE_NEW_CHAT = 1;
    
    private List<Conversation> conversations;
    private OnConversationClickListener clickListener;
    private OnDeleteClickListener deleteListener;
    private SimpleDateFormat dateFormat = new SimpleDateFormat("HH:mm", Locale.getDefault());
    
    public interface OnConversationClickListener {
        void onConversationClick(String conversationId);
    }
    
    public interface OnDeleteClickListener {
        void onDeleteClick(String conversationId);
    }
    
    public ConversationListAdapter(List<Conversation> conversations) {
        this.conversations = conversations;
    }
    
    public void setClickListener(OnConversationClickListener listener) {
        this.clickListener = listener;
    }
    
    public void setDeleteListener(OnDeleteClickListener listener) {
        this.deleteListener = listener;
    }
    
    @Override
    public int getItemViewType(int position) {
        // First item is "New Chat" button
        return position == 0 ? VIEW_TYPE_NEW_CHAT : VIEW_TYPE_CONVERSATION;
    }
    
    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        
        if (viewType == VIEW_TYPE_NEW_CHAT) {
            View view = inflater.inflate(R.layout.item_conversation_new, parent, false);
            return new NewChatVH(view);
        } else {
            View view = inflater.inflate(R.layout.item_conversation, parent, false);
            return new ConversationVH(view);
        }
    }
    
    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        if (holder instanceof ConversationVH && position > 0) {
            ((ConversationVH) holder).bind(conversations.get(position - 1));
        } else if (holder instanceof NewChatVH) {
            ((NewChatVH) holder).bind();
        }
    }
    
    @Override
    public int getItemCount() {
        // +1 for "New Chat" button
        return conversations.size() + 1;
    }
    
    /**
     * Conversation item view holder
     */
    private class ConversationVH extends RecyclerView.ViewHolder {
        private TextView tvTitle;
        private TextView tvPreview;
        private TextView tvTime;
        private ImageButton btnDelete;
        
        public ConversationVH(@NonNull View itemView) {
            super(itemView);
            tvTitle = itemView.findViewById(R.id.tv_conversation_title);
            tvPreview = itemView.findViewById(R.id.tv_conversation_preview);
            tvTime = itemView.findViewById(R.id.tv_conversation_time);
            btnDelete = itemView.findViewById(R.id.btn_delete_conversation);
        }
        
        public void bind(Conversation conversation) {
            tvTitle.setText(conversation.getTitle());
            
            String preview = conversation.getLastMessagePreview();
            if (preview != null && !preview.isEmpty()) {
                tvPreview.setText(preview);
            } else {
                tvPreview.setText("Chưa có tin nhắn");
            }
            
            if (conversation.getUpdatedAt() != null) {
                tvTime.setText(dateFormat.format(conversation.getUpdatedAt()));
            }
            
            // Click to select conversation
            itemView.setOnClickListener(v -> {
                if (clickListener != null) {
                    clickListener.onConversationClick(conversation.getConversationId());
                }
            });
            
            // Delete button
            btnDelete.setOnClickListener(v -> {
                if (deleteListener != null) {
                    deleteListener.onDeleteClick(conversation.getConversationId());
                }
            });
        }
    }
    
    /**
     * New chat button view holder
     */
    private class NewChatVH extends RecyclerView.ViewHolder {
        public NewChatVH(@NonNull View itemView) {
            super(itemView);
        }
        
        public void bind() {
            itemView.setOnClickListener(v -> {
                if (clickListener != null) {
                    clickListener.onConversationClick(null); // null means create new
                }
            });
        }
    }
    
    public void updateConversations(List<Conversation> newConversations) {
        this.conversations = newConversations;
        notifyDataSetChanged();
    }
    
    public void addConversation(Conversation conversation) {
        conversations.add(0, conversation);
        notifyItemInserted(1); // +1 for new chat button
    }
    
    public void removeConversation(String conversationId) {
        for (int i = 0; i < conversations.size(); i++) {
            if (conversations.get(i).getConversationId().equals(conversationId)) {
                conversations.remove(i);
                notifyItemRemoved(i + 1);
                break;
            }
        }
    }
}
