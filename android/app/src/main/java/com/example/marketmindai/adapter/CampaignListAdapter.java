package com.example.marketmindai.adapter;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.R;
import com.example.marketmindai.model.Campaign;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Adapter for displaying campaigns in a list
 */
public class CampaignListAdapter extends RecyclerView.Adapter<CampaignListAdapter.CampaignViewHolder> {
    private List<Campaign> campaigns;
    private OnCampaignClickListener clickListener;
    
    public interface OnCampaignClickListener {
        void onCampaignClick(Campaign campaign);
    }
    
    public CampaignListAdapter(List<Campaign> campaigns) {
        this.campaigns = campaigns;
    }
    
    public void setOnClickListener(OnCampaignClickListener listener) {
        this.clickListener = listener;
    }
    
    public void updateCampaigns(List<Campaign> newCampaigns) {
        campaigns.clear();
        campaigns.addAll(newCampaigns);
        notifyDataSetChanged();
    }
    
    @NonNull
    @Override
    public CampaignViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_campaign, parent, false);
        return new CampaignViewHolder(view);
    }
    
    @Override
    public void onBindViewHolder(@NonNull CampaignViewHolder holder, int position) {
        Campaign campaign = campaigns.get(position);
        holder.bind(campaign, clickListener);
    }
    
    @Override
    public int getItemCount() {
        return campaigns.size();
    }
    
    public static class CampaignViewHolder extends RecyclerView.ViewHolder {
        private TextView tvCampaignId;
        private TextView tvStatus;
        private TextView tvStartDate;
        private TextView tvStats;
        private LinearLayout itemContainer;
        
        public CampaignViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCampaignId = itemView.findViewById(R.id.tv_campaign_id);
            tvStatus = itemView.findViewById(R.id.tv_campaign_status);
            tvStartDate = itemView.findViewById(R.id.tv_campaign_date);
            tvStats = itemView.findViewById(R.id.tv_campaign_stats);
            itemContainer = itemView.findViewById(R.id.item_campaign_container);
        }
        
        public void bind(Campaign campaign, OnCampaignClickListener clickListener) {
            // Campaign ID
            tvCampaignId.setText(campaign.campaign_id != null ? 
                campaign.campaign_id.substring(0, Math.min(8, campaign.campaign_id.length())) + "..." 
                : "N/A");
            
            // Status with color
            tvStatus.setText(campaign.getStatusLabel());
            int statusColor = getStatusColor(campaign.status);
            tvStatus.setTextColor(statusColor);
            
            // Set background tint with alpha (approx 15% opacity)
            tvStatus.setBackgroundTintList(android.content.res.ColorStateList.valueOf(
                android.graphics.Color.argb(38, 
                    android.graphics.Color.red(statusColor),
                    android.graphics.Color.green(statusColor),
                    android.graphics.Color.blue(statusColor))
            ));
            
            // Date
            String dateStr = formatDate(campaign.started_at);
            tvStartDate.setText(dateStr);
            
            // Stats
            String stats = String.format(
                "%d/%d đã đăng | %d lỗi",
                campaign.total_posted,
                campaign.total_briefs,
                campaign.total_failed
            );
            tvStats.setText(stats);
            
            // Click listener
            if (clickListener != null) {
                itemContainer.setOnClickListener(v -> clickListener.onCampaignClick(campaign));
            }
        }
        
        private String formatDate(String dateStr) {
            try {
                long timestamp = Long.parseLong(dateStr);
                Date date = new Date(timestamp);
                SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.US);
                return sdf.format(date);
            } catch (Exception e) {
                return dateStr;
            }
        }
        
        private int getStatusColor(String status) {
            switch (status) {
                case "scheduled":
                    return 0xFFF39C12; // Orange
                case "completed":
                    return 0xFF27AE60; // Green
                case "failed":
                    return 0xFFE74C3C; // Red
                default:
                    return 0xFF95A5A6; // Gray
            }
        }
    }
}
