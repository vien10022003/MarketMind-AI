package com.example.marketmindai;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.adapter.ChatAdapter;
import com.example.marketmindai.model.ChatMessage;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * Main chat activity with conversation sidebar and message display.
 * Handles message sending, receiving, and UI updates.
 */
public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";
    
    private DrawerLayout drawerLayout;
    private Toolbar toolbar;
    private RecyclerView rvMessages;
    private EditText etMessageInput;
    private Button btnSend;
    private LinearLayout layoutWelcomeHero;
    
    private ChatAdapter chatAdapter;
    private List<ChatMessage> chatMessages = new ArrayList<>();
    private boolean isLoading = false;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Initialize views
        drawerLayout = findViewById(R.id.drawer_layout);
        toolbar = findViewById(R.id.toolbar);
        rvMessages = findViewById(R.id.rv_messages);
        etMessageInput = findViewById(R.id.et_message_input);
        btnSend = findViewById(R.id.btn_send);
        layoutWelcomeHero = findViewById(R.id.layout_welcome_hero);
        
        // Setup toolbar
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setHomeAsUpIndicator(android.R.drawable.ic_menu_more);
        
        // Setup RecyclerView
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);
        
        chatAdapter = new ChatAdapter(chatMessages);
        rvMessages.setAdapter(chatAdapter);
        
        // Setup click listeners
        btnSend.setOnClickListener(v -> handleSendMessage());
        
        // Setup suggestion chips
        setupSuggestionChips();
        
        // Load initial welcome message
        addWelcomeMessage();
    }
    
    private void setupSuggestionChips() {
        Button chip1 = findViewById(R.id.chip_1);
        Button chip2 = findViewById(R.id.chip_2);
        Button chip3 = findViewById(R.id.chip_3);
        Button chip4 = findViewById(R.id.chip_4);
        
        chip1.setOnClickListener(v -> handleSendMessage("📊 Nghiên cứu thị trường trà sữa tại Việt Nam"));
        chip2.setOnClickListener(v -> handleSendMessage("🎯 Phân tích đối thủ ngành thương mại điện tử"));
        chip3.setOnClickListener(v -> handleSendMessage("📈 Xu hướng marketing 2026 cho startup"));
        chip4.setOnClickListener(v -> handleSendMessage("💡 Lập chiến lược quảng cáo cho sản phẩm mới"));
    }
    
    private void addWelcomeMessage() {
        ChatMessage welcomeMsg = new ChatMessage(
                "welcome-" + System.currentTimeMillis(),
                "assistant",
                "Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích! 🚀",
                new Date()
        );
        chatMessages.add(welcomeMsg);
        chatAdapter.notifyItemInserted(chatMessages.size() - 1);
    }
    
    private void handleSendMessage(String message) {
        etMessageInput.setText(message);
        handleSendMessage();
    }
    
    private void handleSendMessage() {
        String message = etMessageInput.getText().toString().trim();
        if (message.isEmpty() || isLoading) return;
        
        // Add user message
        ChatMessage userMsg = new ChatMessage(
                "msg-" + System.currentTimeMillis(),
                "user",
                message,
                new Date()
        );
        addMessage(userMsg);
        
        etMessageInput.setText("");
        
        // Hide welcome hero
        if (layoutWelcomeHero.getVisibility() == android.view.View.VISIBLE) {
            layoutWelcomeHero.setVisibility(android.view.View.GONE);
            rvMessages.setVisibility(android.view.View.VISIBLE);
        }
        
        // Show loading status
        isLoading = true;
        ChatMessage statusMsg = new ChatMessage(
                "status-" + System.currentTimeMillis(),
                "status",
                "🔍 Đang phân tích...",
                new Date()
        );
        addMessage(statusMsg);
        
        // Simulate API call (replace with real API call in Phase 4)
        new Thread(() -> {
            try {
                Thread.sleep(2000);
                runOnUiThread(() -> {
                    // Remove status message (in real implementation, update with response)
                    if (!chatMessages.isEmpty() && chatMessages.get(chatMessages.size() - 1).type.equals("status")) {
                        chatMessages.remove(chatMessages.size() - 1);
                        chatAdapter.notifyItemRemoved(chatMessages.size());
                    }
                    
                    // Add response
                    ChatMessage responseMsg = new ChatMessage(
                            "msg-" + System.currentTimeMillis(),
                            "assistant",
                            "Tôi đã nhận được câu hỏi của bạn. Chức năng này sẽ được kết nối với ResearchService trong Phase 4 để gọi đến backend.",
                            new Date()
                    );
                    addMessage(responseMsg);
                    isLoading = false;
                });
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
    
    private void addMessage(ChatMessage msg) {
        chatMessages.add(msg);
        chatAdapter.notifyItemInserted(chatMessages.size() - 1);
        rvMessages.smoothScrollToPosition(chatMessages.size() - 1);
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        if (!drawerLayout.isDrawerOpen(android.view.GravityCompat.START)) {
            drawerLayout.openDrawer(android.view.GravityCompat.START);
        } else {
            drawerLayout.closeDrawer(android.view.GravityCompat.START);
        }
        return true;
    }
}