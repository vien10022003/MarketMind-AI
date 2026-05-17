package com.example.marketmindai;

import android.os.Bundle;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.example.marketmindai.model.Campaign;
import com.google.gson.Gson;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Campaign Detail Activity
 * Shows detailed information about a specific campaign
 */
public class CampaignDetailActivity extends AppCompatActivity {
    private static final String TAG = "CampaignDetail";
    
    // UI elements
    private Toolbar toolbar;
    private ScrollView scrollView;
    private ProgressBar progressBar;
    private Campaign campaign;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_campaign_detail);
        
        initViews();
        setupToolbar();
        loadCampaignFromIntent();
        displayCampaignDetails();
    }
    
    private void initViews() {
        toolbar = findViewById(R.id.toolbar);
        scrollView = findViewById(R.id.scroll_view);
        progressBar = findViewById(R.id.progress_bar);
    }
    
    private void setupToolbar() {
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Chi Tiết Chiến Dịch");
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
    }
    
    private void loadCampaignFromIntent() {
        String campaignJson = getIntent().getStringExtra("campaign_json");
        if (campaignJson != null) {
            campaign = new Gson().fromJson(campaignJson, Campaign.class);
        }
    }
    
    private void displayCampaignDetails() {
        if (campaign == null) {
            LinearLayout container = findViewById(R.id.detail_container);
            TextView tvError = new TextView(this);
            tvError.setText("Không thể tải dữ liệu chiến dịch");
            tvError.setTextSize(16);
            tvError.setTextColor(0xFFE74C3C);
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.setMargins(16, 16, 16, 16);
            tvError.setLayoutParams(params);
            container.addView(tvError);
            progressBar.setVisibility(android.view.View.GONE);
            return;
        }
        
        LinearLayout container = findViewById(R.id.detail_container);
        container.removeAllViews();
        
        // ─── Campaign Header ───
        addSectionHeader(container, "📊 Thông Tin Chiến Dịch");
        addDetail(container, "ID:", campaign.campaign_id);
        addDetail(container, "Trạng Thái:", campaign.getStatusLabel());
        addDetail(container, "Chế Độ:", campaign.execution_mode);
        addDetail(container, "Bắt đầu:", formatDate(campaign.started_at));
        if (campaign.completed_at != null) {
            addDetail(container, "Hoàn tất:", formatDate(campaign.completed_at));
        }
        
        // ─── Statistics ───
        addSectionHeader(container, "📈 Thống Kê");
        addStatRow(container, "✅ Thành công", campaign.total_posted, 0xFF27AE60);
        addStatRow(container, "❌ Thất bại", campaign.total_failed, 0xFFE74C3C);
        addStatRow(container, "⏳ Đang chờ", campaign.total_scheduled, 0xFFF39C12);
        
        // Success rate
        int successRate = campaign.getSuccessRate();
        LinearLayout statsRow = new LinearLayout(this);
        statsRow.setOrientation(LinearLayout.HORIZONTAL);
        statsRow.setPadding(16, 12, 16, 12);
        
        TextView tvRate = new TextView(this);
        tvRate.setText("📊 Tỷ lệ thành công:");
        tvRate.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        
        TextView tvRateValue = new TextView(this);
        tvRateValue.setText(successRate + "%");
        tvRateValue.setTextSize(16);
        tvRateValue.setTextColor(0xFF3b82f6);
        tvRateValue.setTypeface(null, android.graphics.Typeface.BOLD);
        
        statsRow.addView(tvRate);
        statsRow.addView(tvRateValue);
        container.addView(statsRow);
        
        // ─── Execution Results ───
        if (campaign.execution_results != null && !campaign.execution_results.isEmpty()) {
            addSectionHeader(container, "🎬 Kết Quả Thực Thi");
            for (Campaign.CampaignResult result : campaign.execution_results) {
                addResultItem(container, result);
            }
        }
        
        progressBar.setVisibility(android.view.View.GONE);
    }
    
    private void addSectionHeader(LinearLayout container, String title) {
        TextView tv = new TextView(this);
        tv.setText(title);
        tv.setTextSize(16);
        tv.setTextColor(0xFF3b82f6);
        tv.setTypeface(null, android.graphics.Typeface.BOLD);
        tv.setPadding(16, 20, 16, 12);
        container.addView(tv);
    }
    
    private void addDetail(LinearLayout container, String label, String value) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(16, 8, 16, 8);
        
        TextView tvLabel = new TextView(this);
        tvLabel.setText(label);
        tvLabel.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        tvLabel.setTextColor(0xFF666666);
        
        TextView tvValue = new TextView(this);
        tvValue.setText(value);
        tvValue.setTextColor(0xFF333333);
        tvValue.setTypeface(null, android.graphics.Typeface.BOLD);
        
        row.addView(tvLabel);
        row.addView(tvValue);
        container.addView(row);
    }
    
    private void addStatRow(LinearLayout container, String label, int value, int color) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setPadding(16, 12, 16, 12);
        
        TextView tvLabel = new TextView(this);
        tvLabel.setText(label);
        tvLabel.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        
        TextView tvValue = new TextView(this);
        tvValue.setText(String.valueOf(value));
        tvValue.setTextSize(18);
        tvValue.setTextColor(color);
        tvValue.setTypeface(null, android.graphics.Typeface.BOLD);
        
        row.addView(tvLabel);
        row.addView(tvValue);
        container.addView(row);
    }
    
    private void addResultItem(LinearLayout container, Campaign.CampaignResult result) {
        LinearLayout itemLayout = new LinearLayout(this);
        itemLayout.setOrientation(LinearLayout.VERTICAL);
        itemLayout.setPadding(12, 12, 12, 12);
        itemLayout.setBackgroundColor(0xFFF5F5F5);
        
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(8, 8, 8, 8);
        itemLayout.setLayoutParams(params);
        
        // Result header with status
        LinearLayout headerRow = new LinearLayout(this);
        headerRow.setOrientation(LinearLayout.HORIZONTAL);
        
        String statusEmoji = "success".equals(result.status) ? "✅" : "failed".equals(result.status) ? "❌" : "⏭️";
        
        TextView tvStatus = new TextView(this);
        tvStatus.setText(statusEmoji);
        tvStatus.setTextSize(18);
        tvStatus.setPadding(0, 0, 8, 0);
        
        TextView tvTitle = new TextView(this);
        tvTitle.setText(result.brief_title);
        tvTitle.setTextSize(14);
        tvTitle.setTypeface(null, android.graphics.Typeface.BOLD);
        tvTitle.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1));
        
        headerRow.addView(tvStatus);
        headerRow.addView(tvTitle);
        itemLayout.addView(headerRow);
        
        // Details
        if (result.image_skipped) {
            TextView tvImageSkipped = new TextView(this);
            tvImageSkipped.setText("🖼️ Ảnh bị bỏ qua");
            tvImageSkipped.setTextSize(12);
            tvImageSkipped.setTextColor(0xFFF39C12);
            tvImageSkipped.setPadding(26, 4, 0, 4);
            itemLayout.addView(tvImageSkipped);
        }
        
        if (result.discord_sent) {
            TextView tvDiscord = new TextView(this);
            tvDiscord.setText("📤 Discord: Đã gửi");
            tvDiscord.setTextSize(12);
            tvDiscord.setTextColor(0xFF27AE60);
            tvDiscord.setPadding(26, 4, 0, 4);
            itemLayout.addView(tvDiscord);
        }
        
        if (result.error != null && !result.error.isEmpty()) {
            TextView tvError = new TextView(this);
            tvError.setText("⚠️ " + result.error);
            tvError.setTextSize(12);
            tvError.setTextColor(0xFFE74C3C);
            tvError.setPadding(26, 4, 0, 4);
            itemLayout.addView(tvError);
        }
        
        container.addView(itemLayout);
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
    
    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
}
