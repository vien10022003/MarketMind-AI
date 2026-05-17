package com.example.marketmindai;

import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.adapter.CampaignListAdapter;
import com.example.marketmindai.model.Campaign;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Campaign Management Activity
 * View and manage campaigns with status filtering
 */
public class CampaignManagementActivity extends AppCompatActivity {
    private static final String TAG = "CampaignManagement";
    
    // UI elements
    private Toolbar toolbar;
    private RecyclerView rvCampaigns;
    private ProgressBar progressBar;
    private TextView tvNoCampaigns;
    private LinearLayout filterButtons;
    private Button btnFilterAll;
    private Button btnFilterActive;
    private Button btnFilterCompleted;
    private Button btnRefresh;
    
    // Adapter
    private CampaignListAdapter campaignAdapter;
    
    // Data
    private List<Campaign> campaigns = new ArrayList<>();
    private String currentFilter = "all"; // "all", "active", "completed"
    
    // Threading
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_campaign_management);
        
        initViews();
        setupToolbar();
        setupRecyclerView();
        setupFilterButtons();
        
        loadCampaigns();
    }
    
    private void initViews() {
        toolbar = findViewById(R.id.toolbar);
        rvCampaigns = findViewById(R.id.rv_campaigns);
        progressBar = findViewById(R.id.progress_bar);
        tvNoCampaigns = findViewById(R.id.tv_no_campaigns);
        filterButtons = findViewById(R.id.filter_buttons);
        btnFilterAll = findViewById(R.id.btn_filter_all);
        btnFilterActive = findViewById(R.id.btn_filter_active);
        btnFilterCompleted = findViewById(R.id.btn_filter_completed);
        btnRefresh = findViewById(R.id.btn_refresh);
    }
    
    private void setupToolbar() {
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setTitle("Quản Lý Chiến Dịch");
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
    }
    
    private void setupRecyclerView() {
        rvCampaigns.setLayoutManager(new LinearLayoutManager(this));
        campaignAdapter = new CampaignListAdapter(campaigns);
        rvCampaigns.setAdapter(campaignAdapter);
        
        // Click listener for campaign details
        campaignAdapter.setOnClickListener(campaign -> {
            Intent intent = new Intent(this, CampaignDetailActivity.class);
            intent.putExtra("campaign_id", campaign.campaign_id);
            intent.putExtra("campaign_json", campaign.toJson());
            startActivity(intent);
        });
    }
    
    private void setupFilterButtons() {
        btnFilterAll.setOnClickListener(v -> filterCampaigns("all"));
        btnFilterActive.setOnClickListener(v -> filterCampaigns("active"));
        btnFilterCompleted.setOnClickListener(v -> filterCampaigns("completed"));
        btnRefresh.setOnClickListener(v -> loadCampaigns());
    }
    
    private void loadCampaigns() {
        progressBar.setVisibility(View.VISIBLE);
        
        executor.execute(() -> {
            try {
                // Load active campaigns
                List<Campaign> activeCampaigns = ResearchService.getScheduledCampaigns(
                    CampaignManagementActivity.this,
                    "scheduled"
                );
                
                // Load completed campaigns
                List<Campaign> completedCampaigns = ResearchService.getScheduledCampaigns(
                    CampaignManagementActivity.this,
                    "completed"
                );
                
                mainHandler.post(() -> {
                    campaigns.clear();
                    if (activeCampaigns != null) {
                        campaigns.addAll(activeCampaigns);
                    }
                    if (completedCampaigns != null) {
                        campaigns.addAll(completedCampaigns);
                    }
                    
                    campaignAdapter.notifyDataSetChanged();
                    updateEmptyState();
                    progressBar.setVisibility(View.GONE);
                });
            } catch (Exception e) {
                Log.e(TAG, "Load campaigns error: " + e.getMessage());
                mainHandler.post(() -> {
                    Toast.makeText(this, "Lỗi tải chiến dịch: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    progressBar.setVisibility(View.GONE);
                });
            }
        });
    }
    
    private void filterCampaigns(String filter) {
        currentFilter = filter;
        updateFilterButtonStates();
        
        // Update adapter data based on filter
        List<Campaign> filtered = new ArrayList<>();
        
        for (Campaign campaign : campaigns) {
            if (filter.equals("all")) {
                filtered.add(campaign);
            } else if (filter.equals("active") && "scheduled".equals(campaign.status)) {
                filtered.add(campaign);
            } else if (filter.equals("completed") && "completed".equals(campaign.status)) {
                filtered.add(campaign);
            }
        }
        
        campaignAdapter.updateCampaigns(filtered);
        updateEmptyState();
    }
    
    private void updateFilterButtonStates() {
        boolean isAll = currentFilter.equals("all");
        boolean isActive = currentFilter.equals("active");
        boolean isCompleted = currentFilter.equals("completed");
        
        btnFilterAll.setSelected(isAll);
        btnFilterActive.setSelected(isActive);
        btnFilterCompleted.setSelected(isCompleted);
    }
    
    private void updateEmptyState() {
        if (campaignAdapter.getItemCount() == 0) {
            tvNoCampaigns.setVisibility(View.VISIBLE);
            rvCampaigns.setVisibility(View.GONE);
        } else {
            tvNoCampaigns.setVisibility(View.GONE);
            rvCampaigns.setVisibility(View.VISIBLE);
        }
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Refresh campaigns when returning to this activity
        loadCampaigns();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdownNow();
    }
}
