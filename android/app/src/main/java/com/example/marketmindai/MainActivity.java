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
 * streaming message handling, ProcessLog grouping, and full pipeline
 * support (Stage A → Stage B → Stage C) — matching frontend App.tsx.
 */
public class MainActivity extends AppCompatActivity implements ChatAdapter.ChatActionListener {
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
    
    // Stage B/C state (mirrors frontend)
    private ChatMessage.ReportData lastReportData = null;
    private Map<String, Object> lastReportInput = null;
    private String lastMongodbId = null;
    private ChatMessage.StrategyData lastStrategy = null;
    
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
            getSupportActionBar().setTitle("MarketMind AI");
        }
    }
    
    private void setupChatRecyclerView() {
        LinearLayoutManager layoutManager = new LinearLayoutManager(this);
        layoutManager.setStackFromEnd(true);
        rvMessages.setLayoutManager(layoutManager);
        
        chatAdapter = new ChatAdapter(chatMessages);
        chatAdapter.setActionListener(this);
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
        View btnClose = drawerView.findViewById(R.id.btn_sidebar_close);
        
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
            drawerLayout.closeDrawer(GravityCompat.END);
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
                drawerLayout.closeDrawer(GravityCompat.END);
            });
        }
        
        // Campaigns button
        Button btnCampaigns = drawerView.findViewById(R.id.btn_drawer_campaigns);
        if (btnCampaigns != null) {
            btnCampaigns.setOnClickListener(v -> {
                startActivity(new Intent(this, CampaignManagementActivity.class));
                drawerLayout.closeDrawer(GravityCompat.END);
            });
        }
        
        // Logout button
        if (btnLogout != null) {
            btnLogout.setOnClickListener(v -> handleLogout());
        }
        
        // Close button
        if (btnClose != null) {
            btnClose.setOnClickListener(v -> drawerLayout.closeDrawer(GravityCompat.END));
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
        MenuItem menuDrawer = menu.add(Menu.NONE, 4, 1, "Menu");
        menuDrawer.setIcon(R.drawable.ic_menu);
        menuDrawer.setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == 4) {
            if (!drawerLayout.isDrawerOpen(GravityCompat.END)) {
                drawerLayout.openDrawer(GravityCompat.END);
            } else {
                drawerLayout.closeDrawer(GravityCompat.END);
            }
            return true;
        }
        return super.onOptionsItemSelected(item);
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        return false;
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
                "Xin chào! Tôi là MarketMind AI — trợ lý nghiên cứu thị trường thông minh. Hãy mô tả những gì bạn muốn tìm hiểu, tôi sẽ giúp bạn phân tích!",
                new Date()
        );
        chatMessages.add(welcomeMsg);
        refreshAdapter();
    }
    
    private void addMessage(ChatMessage msg) {
        chatMessages.add(msg);
        refreshAdapter();
        
        // Scroll to bottom
        if (chatAdapter.getItemCount() > 0) {
            rvMessages.smoothScrollToPosition(chatAdapter.getItemCount() - 1);
        }
        
        // Buffer for auto-save
        messagesSaveBuffer.add(msg);
        scheduleAutoSave();
    }
    
    /**
     * Rebuild segments and notify adapter.
     * This is the core method that enables ProcessLog grouping.
     */
    private void refreshAdapter() {
        chatAdapter.rebuildSegments(chatMessages);
        chatAdapter.notifyDataSetChanged();
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
        setLoadingState(true);
        
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
                
                // Save input for Stage B
                mainHandler.post(() -> lastReportInput = request);
                
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
                // Save report data for Stage B
                if (msg.report != null) {
                    lastReportData = msg.report;
                }
                break;
            case "completed":
                ChatMessage completedMsg = new ChatMessage(nextId(), "completed", msg.message, new Date());
                completedMsg.mongodbId = msg.mongodb_id;
                addMessage(completedMsg);
                lastMongodbId = msg.mongodb_id;
                setLoadingState(false);
                
                // Show Stage B proposal (mirrors frontend)
                ChatMessage.ReportData reportData = msg.report != null ? msg.report : lastReportData;
                if (reportData != null) {
                    ChatMessage proposalMsg = new ChatMessage(
                            nextId(),
                            "stage_b_proposal",
                            "Báo cáo nghiên cứu đã hoàn tất! Bạn có muốn lập chiến lược marketing dựa trên kết quả này không?",
                            new Date()
                    );
                    proposalMsg.stageBProposalData = new ChatMessage.StageBProposalData();
                    proposalMsg.stageBProposalData.report = reportData;
                    proposalMsg.stageBProposalData.mongodbId = msg.mongodb_id;
                    addMessage(proposalMsg);
                }
                break;
            
            // ─── Stage B ───
            case "stage_b_completed":
                if (msg.strategy != null) {
                    ChatMessage strategyMsg = new ChatMessage(nextId(), "strategy", msg.message, new Date());
                    strategyMsg.strategyData = msg.strategy;
                    addMessage(strategyMsg);
                    lastStrategy = msg.strategy;
                    
                    // Show content briefs
                    if (msg.strategy.content_briefs != null && !msg.strategy.content_briefs.isEmpty()) {
                        ChatMessage briefsMsg = new ChatMessage(
                                nextId(),
                                "content_briefs",
                                msg.strategy.content_briefs.size() + " content briefs đã sẵn sàng để review",
                                new Date()
                        );
                        briefsMsg.contentBriefsData = msg.strategy.content_briefs;
                        addMessage(briefsMsg);
                    }
                    
                    // Show Stage C proposal
                    ChatMessage stageCProposal = new ChatMessage(
                            nextId(),
                            "stage_c_schedule_proposal",
                            "Chiến lược marketing đã hoàn tất! Bạn có muốn thực thi chiến dịch marketing này không?",
                            new Date()
                    );
                    stageCProposal.stageCScheduleProposalData = new ChatMessage.StageCScheduleProposalData();
                    stageCProposal.stageCScheduleProposalData.briefs = msg.strategy.content_briefs != null
                            ? msg.strategy.content_briefs : new ArrayList<>();
                    stageCProposal.stageCScheduleProposalData.mongodbId = msg.mongodb_id;
                    addMessage(stageCProposal);
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
    // ChatAdapter.ChatActionListener implementation
    // (Marketing form, Stage B/C proposals)
    // ════════════════════════════════════════════
    
    @Override
    public void onMarketingFormSubmit(Map<String, Object> formData) {
        setLoadingState(true);
        addMessage(new ChatMessage(nextId(), "status", "Bắt đầu nghiên cứu thị trường...", new Date()));
        
        // Save form data for Stage B
        lastReportInput = formData;
        
        // Ensure llm_provider is set
        formData.put("llm_provider", selectedLLMProvider);
        
        executor.execute(() -> {
            try {
                ResearchService.callMarketingResearch(
                        this,
                        formData,
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
                                Log.d(TAG, "Marketing research stream completed");
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
    
    @Override
    public void onAcceptStageBProposal(ChatMessage.ReportData reportData, String mongodbId) {
        addMessage(new ChatMessage(nextId(), "status", "Bắt đầu lập chiến lược marketing...", new Date()));
        setLoadingState(true);
        
        executor.execute(() -> {
            try {
                Map<String, Object> request = new HashMap<>();
                request.put("stage_a_report", reportData);
                request.put("stage_a_input", lastReportInput != null ? lastReportInput : new HashMap<>());
                request.put("mongodb_id", mongodbId != null ? mongodbId : lastMongodbId);
                request.put("llm_provider", selectedLLMProvider);
                
                ResearchService.callStageBStrategy(
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
                                    addMessage(new ChatMessage(nextId(), "error", "Lỗi Stage B: " + error, new Date()));
                                    setLoadingState(false);
                                });
                            }
                            
                            @Override
                            public void onComplete() {
                                Log.d(TAG, "Stage B stream completed");
                            }
                        },
                        error -> mainHandler.post(() -> {
                            addMessage(new ChatMessage(nextId(), "error", error, new Date()));
                            setLoadingState(false);
                        })
                );
            } catch (Exception e) {
                mainHandler.post(() -> {
                    addMessage(new ChatMessage(nextId(), "error", "Lỗi Stage B: " + e.getMessage(), new Date()));
                    setLoadingState(false);
                });
            }
        });
    }
    
    @Override
    public void onAcceptStageCProposal(List<ChatMessage.ContentBrief> briefs, String mongodbId) {
        if (briefs == null || briefs.isEmpty()) {
            addMessage(new ChatMessage(nextId(), "error", "Không có brief nào để thực thi!", new Date()));
            return;
        }
        
        addMessage(new ChatMessage(
                nextId(), "status",
                "Bắt đầu thực thi chiến dịch: " + briefs.size() + " bài đăng...",
                new Date()
        ));
        setLoadingState(true);
        
        // Approve briefs first
        executor.execute(() -> {
            try {
                // Save approval to backend
                if (lastStrategy != null) {
                    Map<String, Object> approveRequest = new HashMap<>();
                    approveRequest.put("mongodb_id", mongodbId != null ? mongodbId : lastMongodbId);
                    approveRequest.put("strategy", lastStrategy);
                    approveRequest.put("approved_briefs", briefs);
                    ResearchService.approveStageBBriefs(this, approveRequest);
                }
                
                // Run Stage C
                Map<String, Object> request = new HashMap<>();
                request.put("approved_briefs", briefs);
                request.put("mongodb_stage_a_id", mongodbId != null ? mongodbId : lastMongodbId);
                request.put("llm_provider", selectedLLMProvider);
                
                ResearchService.callStageCCampaign(
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
                                    addMessage(new ChatMessage(nextId(), "error", "Lỗi Stage C: " + error, new Date()));
                                    setLoadingState(false);
                                });
                            }
                            
                            @Override
                            public void onComplete() {
                                Log.d(TAG, "Stage C stream completed");
                            }
                        },
                        error -> mainHandler.post(() -> {
                            addMessage(new ChatMessage(nextId(), "error", error, new Date()));
                            setLoadingState(false);
                        })
                );
            } catch (Exception e) {
                mainHandler.post(() -> {
                    addMessage(new ChatMessage(nextId(), "error", "Lỗi Stage C: " + e.getMessage(), new Date()));
                    setLoadingState(false);
                });
            }
        });
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
                    refreshAdapter();
                    messagesSaveBuffer.clear();
                    
                    // Show chat, hide welcome
                    layoutWelcomeHero.setVisibility(View.GONE);
                    rvMessages.setVisibility(View.VISIBLE);
                    
                    if (chatAdapter.getItemCount() > 0) {
                        rvMessages.scrollToPosition(chatAdapter.getItemCount() - 1);
                    }
                } else {
                    Toast.makeText(this, "Không thể tải cuộc hội thoại", Toast.LENGTH_SHORT).show();
                }
            });
        });
    }
    
    private void handleCreateNewConversation() {
        chatMessages.clear();
        refreshAdapter();
        msgIdCounter = 0;
        currentConversationId = null;
        messagesSaveBuffer.clear();
        
        // Reset Stage B/C state
        lastReportData = null;
        lastReportInput = null;
        lastMongodbId = null;
        lastStrategy = null;
        
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