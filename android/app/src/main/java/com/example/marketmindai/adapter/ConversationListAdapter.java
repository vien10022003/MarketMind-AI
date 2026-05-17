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
 * Adapter for conversation list in the sidebar drawer.
 * Shows conversation titles, message count, and timestamps.
 */
public class ConversationListAdapter extends RecyclerView.Adapter<ConversationListAdapter.ConversationVH> {
    
    private List<Conversation> conversations;
    private OnConversationClickListener clickListener;
    private OnDeleteClickListener deleteListener;
    private SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM HH:mm", Locale.getDefault());
    
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
    
    @NonNull
    @Override
    public ConversationVH onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_conversation, parent, false);
        return new ConversationVH(view);
    }
    
    @Override
    public void onBindViewHolder(@NonNull ConversationVH holder, int position) {
        holder.bind(conversations.get(position));
    }
    
    @Override
    public int getItemCount() {
        return conversations.size();
    }
    
    class ConversationVH extends RecyclerView.ViewHolder {
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
            tvPreview.setText(conversation.getLastMessagePreview());
            
            if (conversation.getUpdatedAt() != null) {
                tvTime.setText(dateFormat.format(conversation.getUpdatedAt()));
            } else if (conversation.getCreatedAt() != null) {
                tvTime.setText(dateFormat.format(conversation.getCreatedAt()));
            }
            
            itemView.setOnClickListener(v -> {
                if (clickListener != null && conversation.getConversationId() != null) {
                    clickListener.onConversationClick(conversation.getConversationId());
                }
            });
            
            btnDelete.setOnClickListener(v -> {
                if (deleteListener != null && conversation.getConversationId() != null) {
                    deleteListener.onDeleteClick(conversation.getConversationId());
                }
            });
        }
    }
    
    public void updateConversations(List<Conversation> newConversations) {
        this.conversations = newConversations;
        notifyDataSetChanged();
    }
    
    public void removeConversation(String conversationId) {
        for (int i = 0; i < conversations.size(); i++) {
            if (conversations.get(i).getConversationId() != null &&
                conversations.get(i).getConversationId().equals(conversationId)) {
                conversations.remove(i);
                notifyItemRemoved(i);
                break;
            }
        }
    }
}
