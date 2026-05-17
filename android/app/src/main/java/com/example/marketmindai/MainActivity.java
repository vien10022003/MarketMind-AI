package com.example.marketmindai;

import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.adapter.ChatAdapter;
import com.example.marketmindai.adapter.ConversationListAdapter;
import com.example.marketmindai.model.ChatMessage;
import com.example.marketmindai.model.Conversation;
import com.example.marketmindai.model.StreamMessage;

import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Main chat activity with conversation sidebar, real backend connection,
 * streaming message handling, and user management.
 */
public class MainActivity extends AppCompatActivity {
    private static final String TAG = "MainActivity";
    
    // UI elements
    private DrawerLayout drawerLayout;
    private Toolbar toolbar;
    private RecyclerView rvMessages;
    private EditText etMessageInput;
    private Button btnSend;
    private ScrollView layoutWelcomeHero;
    private TextView tvUserName;
    private Button btnLogout;
    private Button btnNewChat;
    private RecyclerView rvConversations;
    
    // Adapters
    private ChatAdapter chatAdapter;
    private ConversationListAdapter conversationAdapter;
    
    // Data
    private List<ChatMessage> chatMessages = new ArrayList<>();
    private List<Conversation> conversations = new ArrayList<>();
    
    // State
    private boolean isLoading = false;
    private String currentConversationId = null;
    private String selectedLLMProvider = "llama";
    private List<ChatMessage> messagesSaveBuffer = new ArrayList<>();
    
    // Threading
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());
    
    // Auto-save timer
    private final Handler saveHandler = new Handler(Looper.getMainLooper());
    private Runnable saveRunnable;
    
    private int msgIdCounter = 0;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initViews();
        setupToolbar();
        setupChatRecyclerView();
        setupDrawer();
        setupInputBar();
        setupSuggestionChips();
        
        addWelcomeMessage();
        loadConversations();
    }
    
    // ════════════════════════════════════════════
    // Initialization
    // ════════════════════════════════════════════
    
    private void initViews() {
        drawerLayout = findViewById(R.id.drawer_layout);
        toolbar = findViewById(R.id.toolbar);
        rvMessages = findViewById(R.id.rv_messages);
        etMessageInput = findViewById(R.id.et_message_input);
        btnSend = findViewById(R.id.btn_send);
        layoutWelcomeHero = findViewById(R.id.layout_welcome_hero);
    }
    
    private void setupToolbar() {
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setHomeAsUpIndicator(android.R.drawable.ic_menu_more);
            getSupportActionBar().setTitle("MarketMind AI");
        }
    }
    
    private void setupChatRecyclerView() {
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);
        
        chatAdapter = new ChatAdapter(chatMessages);
        rvMessages.setAdapter(chatAdapter);
    }
    
    private void setupDrawer() {
        // Find drawer views
        View drawerContent = findViewById(R.id.drawer_content);
        
        // Inflate drawer layout into the FrameLayout
        View drawerView = getLayoutInflater().inflate(
                R.layout.fragment_conversation_drawer, 
                (android.view.ViewGroup) drawerContent, 
                true
        );
        
        // Setup user info
        tvUserName = drawerView.findViewById(R.id.tv_drawer_user_name);
        btnLogout = drawerView.findViewById(R.id.btn_drawer_logout);
        btnNewChat = drawerView.findViewById(R.id.btn_drawer_new_chat);
        rvConversations = drawerView.findViewById(R.id.rv_conversations);
        Button btnClose = drawerView.findViewById(R.id.btn_sidebar_close);
        
        // Display user name
        AuthService.User user = AuthService.getUser(this);
        if (user != null && tvUserName != null) {
            String displayName = (user.name != null && !user.name.isEmpty()) ? user.name : user.username;
            tvUserName.setText(displayName);
        }
        
        // Setup conversation list
        conversationAdapter = new ConversationListAdapter(conversations);
        rvConversations.setLayoutManager(new LinearLayoutManager(this));
        rvConversations.setAdapter(conversationAdapter);
        
        // Conversation click handler
        conversationAdapter.setClickListener(conversationId -> {
            if (conversationId == null) {
                // "New Chat" clicked
                handleCreateNewConversation();
            } else {
                handleLoadConversation(conversationId);
            }
            drawerLayout.closeDrawer(GravityCompat.START);
        });
        
        // Delete handler
        conversationAdapter.setDeleteListener(conversationId -> {
            new AlertDialog.Builder(this)
                    .setTitle("Xóa cuộc trò chuyện")
                    .setMessage("Bạn có chắc muốn xóa cuộc trò chuyện này?")
                    .setPositiveButton("Xóa", (d, w) -> handleDeleteConversation(conversationId))
                    .setNegativeButton("Hủy", null)
                    .show();
        });
        
        // New chat button
        if (btnNewChat != null) {
            btnNewChat.setOnClickListener(v -> {
                handleCreateNewConversation();
                drawerLayout.closeDrawer(GravityCompat.START);
            });
        }
        
        // Logout button
        if (btnLogout != null) {
            btnLogout.setOnClickListener(v -> handleLogout());
        }
        
        // Close button
        if (btnClose != null) {
            btnClose.setOnClickListener(v -> drawerLayout.closeDrawer(GravityCompat.START));
        }
    }
    
    private void setupInputBar() {
        btnSend.setOnClickListener(v -> handleSendMessage());
        
        // Enter key sends message
        etMessageInput.setOnEditorActionListener((v, actionId, event) -> {
            handleSendMessage();
            return true;
        });
    }
    
    private void setupSuggestionChips() {
        Button chip1 = findViewById(R.id.chip_1);
        Button chip2 = findViewById(R.id.chip_2);
        Button chip3 = findViewById(R.id.chip_3);
        Button chip4 = findViewById(R.id.chip_4);
        
        chip1.setOnClickListener(v -> sendFromChip("Nghiên cứu thị trường trà sữa tại Việt Nam"));
        chip2.setOnClickListener(v -> sendFromChip("Phân tích đối thủ ngành thương mại điện tử"));
        chip3.setOnClickListener(v -> sendFromChip("Xu hướng marketing 2026 cho startup"));
        chip4.setOnClickListener(v -> sendFromChip("Lập chiến lược quảng cáo cho sản phẩm mới"));
    }
    
    private void sendFromChip(String text) {
        etMessageInput.setText(text);
        handleSendMessage();
    }
    
    // ════════════════════════════════════════════
    // Toolbar Menu
    // ════════════════════════════════════════════
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // New Chat
        MenuItem newChatItem = menu.add(Menu.NONE, 1, 1, "✨ Mới");
        newChatItem.setShowAsAction(MenuItem.SHOW_AS_ACTION_IF_ROOM);
        
        // Logout
        MenuItem logoutItem = menu.add(Menu.NONE, 2, 2, "Đăng xuất");
        logoutItem.setShowAsAction(MenuItem.SHOW_AS_ACTION_NEVER);
        
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case 1: // New Chat
                handleCreateNewConversation();
                return true;
            case 2: // Logout
                handleLogout();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        if (!drawerLayout.isDrawerOpen(GravityCompat.START)) {
            drawerLayout.openDrawer(GravityCompat.START);
        } else {
            drawerLayout.closeDrawer(GravityCompat.START);
        }
        return true;
    }
    
    // ════════════════════════════════════════════
    // Message Handling
    // ════════════════════════════════════════════
    
    private String nextId() {
        return "msg-" + (++msgIdCounter) + "-" + System.currentTimeMillis();
    }
    
    private void addWelcomeMessage() {
        ChatMessage welcomeMsg = new ChatMessage(
                "welcome",
                "assistant",
                "Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích! 🚀",
                new Date()
        );
        chatMessages.add(welcomeMsg);
        chatAdapter.notifyItemInserted(chatMessages.size() - 1);
    }
    
    private void addMessage(ChatMessage msg) {
        chatMessages.add(msg);
        chatAdapter.notifyItemInserted(chatMessages.size() - 1);
        rvMessages.smoothScrollToPosition(chatMessages.size() - 1);
        
        // Buffer for auto-save
        messagesSaveBuffer.add(msg);
        scheduleAutoSave();
    }
    
    private void scheduleAutoSave() {
        if (currentConversationId == null || messagesSaveBuffer.isEmpty()) return;
        
        // Cancel previous save
        if (saveRunnable != null) {
            saveHandler.removeCallbacks(saveRunnable);
        }
        
        // Schedule save after 3 seconds of inactivity
        saveRunnable = () -> {
            if (!messagesSaveBuffer.isEmpty() && currentConversationId != null) {
                List<ChatMessage> toSave = new ArrayList<>(messagesSaveBuffer);
                messagesSaveBuffer.clear();
                String convId = currentConversationId;
                
                executor.execute(() -> {
                    ResearchService.saveMessagesToConversation(this, convId, toSave);
                });
            }
        };
        saveHandler.postDelayed(saveRunnable, 3000);
    }
    
    // ════════════════════════════════════════════
    // Send Message → Backend
    // ════════════════════════════════════════════
    
    private void handleSendMessage() {
        String text = etMessageInput.getText().toString().trim();
        if (text.isEmpty() || isLoading) return;
        
        // Add user bubble
        ChatMessage userMsg = new ChatMessage(nextId(), "user", text, new Date());
        addMessage(userMsg);
        etMessageInput.setText("");
        
        // Hide welcome hero
        if (layoutWelcomeHero.getVisibility() == View.VISIBLE) {
            layoutWelcomeHero.setVisibility(View.GONE);
            rvMessages.setVisibility(View.VISIBLE);
        }
        
        // Set loading
        isLoading = true;
        btnSend.setEnabled(false);
        etMessageInput.setEnabled(false);
        
        // Create conversation if needed, then send
        executor.execute(() -> {
            try {
                // Create conversation on first message
                if (currentConversationId == null) {
                    Conversation conv = ResearchService.createConversation(this, text, null);
                    if (conv != null && conv.getConversationId() != null) {
                        currentConversationId = conv.getConversationId();
                        // Refresh sidebar
                        mainHandler.post(this::loadConversations);
                    }
                }
                
                // Build request
                Map<String, Object> request = new HashMap<>();
                request.put("user_prompt", text);
                request.put("llm_provider", selectedLLMProvider);
                
                // Build conversation history
                List<Map<String, String>> history = buildConversationHistory();
                request.put("conversation_history", history);
                
                // Call backend with streaming
                ResearchService.callStageAResearch(
                        this,
                        request,
                        new ResearchService.StreamCallback() {
                            @Override
                            public void onMessage(StreamMessage msg) {
                                mainHandler.post(() -> handleStreamMessage(msg));
                            }
                            
                            @Override
                            public void onError(String error) {
                                mainHandler.post(() -> {
                                    addMessage(new ChatMessage(nextId(), "error", "Lỗi: " + error, new Date()));
                                    setLoadingState(false);
                                });
                            }
                            
                            @Override
                            public void onComplete() {
                                Log.d(TAG, "Stream completed");
                            }
                        },
                        error -> mainHandler.post(() -> {
                            addMessage(new ChatMessage(nextId(), "error", error, new Date()));
                            setLoadingState(false);
                        })
                );
            } catch (Exception e) {
                mainHandler.post(() -> {
                    addMessage(new ChatMessage(nextId(), "error", "Lỗi: " + e.getMessage(), new Date()));
                    setLoadingState(false);
                });
            }
        });
    }
    
    private List<Map<String, String>> buildConversationHistory() {
        List<Map<String, String>> turns = new ArrayList<>();
        for (ChatMessage msg : chatMessages) {
            if ("user".equals(msg.type)) {
                Map<String, String> turn = new HashMap<>();
                turn.put("role", "user");
                turn.put("content", msg.content);
                turns.add(turn);
            } else if ("assistant".equals(msg.type) || "knowledge".equals(msg.type)) {
                Map<String, String> turn = new HashMap<>();
                turn.put("role", "assistant");
                turn.put("content", msg.content);
                turns.add(turn);
            }
        }
        // Return last 6 turns (3 pairs)
        int maxTurns = 6;
        if (turns.size() > maxTurns) {
            return turns.subList(turns.size() - maxTurns, turns.size());
        }
        return turns;
    }
    
    // ════════════════════════════════════════════
    // Stream Message Handler (mirrors frontend handleStreamMessage)
    // ════════════════════════════════════════════
    
    private void handleStreamMessage(StreamMessage msg) {
        if (msg == null || msg.status == null) return;
        
        switch (msg.status) {
            // ─── Chat response ───
            case "chat_response":
                addMessage(new ChatMessage(nextId(), "assistant", msg.message, new Date()));
                setLoadingState(false);
                break;
            
            // ─── Knowledge path ───
            case "knowledge_searching":
                addMessage(new ChatMessage(nextId(), "status", msg.message, new Date()));
                break;
            case "knowledge_response":
                ChatMessage knowledgeMsg = new ChatMessage(nextId(), "knowledge", msg.message, new Date());
                if (msg.sources != null) {
                    knowledgeMsg.knowledgeData = new ChatMessage.KnowledgeData();
                    knowledgeMsg.knowledgeData.answer = msg.message;
                    knowledgeMsg.knowledgeData.sources = new ArrayList<>();
                    for (String src : msg.sources) {
                        ChatMessage.Source source = new ChatMessage.Source();
                        source.url = src;
                        source.title = src;
                        knowledgeMsg.knowledgeData.sources.add(source);
                    }
                }
                addMessage(knowledgeMsg);
                setLoadingState(false);
                break;
            
            // ─── Marketing form ───
            case "show_marketing_form":
                ChatMessage formMsg = new ChatMessage(nextId(), "marketing_form", msg.message, new Date());
                formMsg.marketingFormData = new ChatMessage.MarketingFormData();
                formMsg.marketingFormData.detected_prompt = msg.detected_prompt != null ? msg.detected_prompt : "";
                addMessage(formMsg);
                setLoadingState(false);
                break;
            
            // ─── Research pipeline events ───
            case "clarification_provided":
                addMessage(new ChatMessage(nextId(), "clarification", msg.message, new Date()));
                setLoadingState(false);
                break;
            case "plan_completed":
                ChatMessage planMsg = new ChatMessage(nextId(), "plan", msg.message, new Date());
                planMsg.planData = msg.plan;
                addMessage(planMsg);
                break;
            case "react_completed":
                ChatMessage reactMsg = new ChatMessage(nextId(), "react_summary", msg.message, new Date());
                reactMsg.reactSummaryData = msg.react_summary;
                addMessage(reactMsg);
                break;
            case "evidence_ready":
                ChatMessage evidenceMsg = new ChatMessage(nextId(), "evidence", msg.message, new Date());
                evidenceMsg.evidenceData = msg.evidence;
                addMessage(evidenceMsg);
                break;
            case "report_ready":
                ChatMessage reportMsg = new ChatMessage(nextId(), "report", msg.message, new Date());
                reportMsg.reportData = msg.report;
                addMessage(reportMsg);
                break;
            case "completed":
                ChatMessage completedMsg = new ChatMessage(nextId(), "completed", msg.message, new Date());
                completedMsg.mongodbId = msg.mongodb_id;
                addMessage(completedMsg);
                setLoadingState(false);
                break;
            
            // ─── Stage B ───
            case "stage_b_completed":
                if (msg.strategy != null) {
                    ChatMessage strategyMsg = new ChatMessage(nextId(), "strategy", msg.message, new Date());
                    strategyMsg.strategyData = msg.strategy;
                    addMessage(strategyMsg);
                }
                setLoadingState(false);
                break;
            
            // ─── Stage C ───
            case "stage_c_completed":
                if (msg.campaign_log != null) {
                    ChatMessage campMsg = new ChatMessage(nextId(), "campaign_results", msg.message, new Date());
                    campMsg.campaignLogData = msg.campaign_log;
                    addMessage(campMsg);
                }
                setLoadingState(false);
                break;
            
            // ─── Errors ───
            case "error":
                addMessage(new ChatMessage(nextId(), "error", msg.message, new Date()));
                setLoadingState(false);
                break;
            
            // ─── Progress / Status ───
            case "progress":
            case "starting":
            case "stage_b_starting":
            case "stage_c_starting":
            case "swot_completed":
            case "usp_completed":
            case "persona_completed":
            case "pillars_completed":
            case "campaign_plan_completed":
            case "briefs_generated":
            case "brief_executing":
            case "image_generating":
            case "image_generated":
            case "discord_posting":
            case "discord_posted":
            case "discord_post_failed":
                addMessage(new ChatMessage(nextId(), "status", msg.message, new Date()));
                break;
            
            default:
                if (msg.message != null && !msg.message.isEmpty()) {
                    addMessage(new ChatMessage(nextId(), "status", msg.message, new Date()));
                }
                break;
        }
    }
    
    private void setLoadingState(boolean loading) {
        isLoading = loading;
        btnSend.setEnabled(!loading);
        etMessageInput.setEnabled(!loading);
        
        if (!loading) {
            etMessageInput.requestFocus();
        }
    }
    
    // ════════════════════════════════════════════
    // Conversation Management
    // ════════════════════════════════════════════
    
    private void loadConversations() {
        executor.execute(() -> {
            List<Conversation> convs = ResearchService.listConversations(this, 0, 20);
            mainHandler.post(() -> {
                conversations.clear();
                conversations.addAll(convs);
                conversationAdapter.updateConversations(conversations);
            });
        });
    }
    
    private void handleLoadConversation(String conversationId) {
        executor.execute(() -> {
            Conversation conv = ResearchService.getConversation(this, conversationId);
            mainHandler.post(() -> {
                if (conv != null && conv.getMessages() != null) {
                    currentConversationId = conversationId;
                    chatMessages.clear();
                    chatMessages.addAll(conv.getMessages());
                    chatAdapter.notifyDataSetChanged();
                    messagesSaveBuffer.clear();
                    
                    // Show chat, hide welcome
                    layoutWelcomeHero.setVisibility(View.GONE);
                    rvMessages.setVisibility(View.VISIBLE);
                    
                    if (!chatMessages.isEmpty()) {
                        rvMessages.scrollToPosition(chatMessages.size() - 1);
                    }
                } else {
                    Toast.makeText(this, "Không thể tải cuộc hội thoại", Toast.LENGTH_SHORT).show();
                }
            });
        });
    }
    
    private void handleCreateNewConversation() {
        chatMessages.clear();
        chatAdapter.notifyDataSetChanged();
        msgIdCounter = 0;
        currentConversationId = null;
        messagesSaveBuffer.clear();
        
        addWelcomeMessage();
        layoutWelcomeHero.setVisibility(View.VISIBLE);
        rvMessages.setVisibility(View.GONE);
        etMessageInput.setText("");
    }
    
    private void handleDeleteConversation(String conversationId) {
        executor.execute(() -> {
            boolean success = ResearchService.deleteConversation(this, conversationId);
            mainHandler.post(() -> {
                if (success) {
                    conversationAdapter.removeConversation(conversationId);
                    if (conversationId.equals(currentConversationId)) {
                        handleCreateNewConversation();
                    }
                    Toast.makeText(this, "Đã xóa cuộc trò chuyện", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(this, "Không thể xóa cuộc trò chuyện", Toast.LENGTH_SHORT).show();
                }
            });
        });
    }
    
    // ════════════════════════════════════════════
    // Logout
    // ════════════════════════════════════════════
    
    private void handleLogout() {
        new AlertDialog.Builder(this)
                .setTitle("Đăng xuất")
                .setMessage("Bạn có chắc muốn đăng xuất?")
                .setPositiveButton("Đăng xuất", (d, w) -> {
                    AuthService.logout(this);
                    Intent intent = new Intent(this, AuthActivity.class);
                    intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
                    startActivity(intent);
                    finish();
                })
                .setNegativeButton("Hủy", null)
                .show();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Refresh conversation list when returning to this activity
        loadConversations();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdownNow();
        if (saveRunnable != null) {
            saveHandler.removeCallbacks(saveRunnable);
        }
    }
}