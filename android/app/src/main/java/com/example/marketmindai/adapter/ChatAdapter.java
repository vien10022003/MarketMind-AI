package com.example.marketmindai.adapter;

import android.animation.ValueAnimator;
import android.text.method.LinkMovementMethod;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.marketmindai.R;
import com.example.marketmindai.model.ChatMessage;
import com.example.marketmindai.model.MessageSegment;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import io.noties.markwon.Markwon;

/**
 * Multi-type adapter for chat messages with ProcessLog grouping.
 * Operates on MessageSegment list (grouped messages).
 * 
 * Handles:
 * - User messages (right-aligned bubble)
 * - Assistant/knowledge messages (left-aligned with markdown)
 * - Status/progress messages (center with spinner)
 * - Error messages (red banner)
 * - Plan, Report, Strategy, Campaign messages (card-style)
 * - ProcessLog groups (collapsible, showing latest status)
 * - Marketing form (input card)
 * - Stage B proposal (accept/decline)
 * - Stage C schedule proposal (accept/decline)
 */
public class ChatAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {
    
    private static final int VIEW_TYPE_USER = 0;
    private static final int VIEW_TYPE_ASSISTANT = 1;
    private static final int VIEW_TYPE_STATUS = 2;
    private static final int VIEW_TYPE_ERROR = 3;
    private static final int VIEW_TYPE_PLAN = 4;
    private static final int VIEW_TYPE_REPORT = 5;
    private static final int VIEW_TYPE_STRATEGY = 6;
    private static final int VIEW_TYPE_PROCESS_LOG = 7;
    private static final int VIEW_TYPE_MARKETING_FORM = 8;
    private static final int VIEW_TYPE_PROPOSAL = 9;
    private static final int VIEW_TYPE_SCHEDULE_PROPOSAL = 10;
    
    private List<MessageSegment> segments = new ArrayList<>();
    private SimpleDateFormat timeFormat = new SimpleDateFormat("HH:mm", Locale.getDefault());
    private Markwon markwon;
    private ChatActionListener actionListener;
    
    /**
     * Callback interface for chat actions (forms, proposals).
     * Implemented by MainActivity.
     */
    public interface ChatActionListener {
        void onMarketingFormSubmit(Map<String, Object> formData);
        void onAcceptStageBProposal(ChatMessage.ReportData reportData, String mongodbId);
        void onAcceptStageCProposal(List<ChatMessage.ContentBrief> briefs, String mongodbId);
    }
    
    public ChatAdapter(List<ChatMessage> messages) {
        rebuildSegments(messages);
    }
    
    public void setActionListener(ChatActionListener listener) {
        this.actionListener = listener;
    }
    
    /**
     * Rebuild segments from flat message list.
     * Call this whenever the message list changes.
     */
    public void rebuildSegments(List<ChatMessage> messages) {
        this.segments = MessageSegment.buildSegments(messages);
    }
    
    @Override
    public int getItemViewType(int position) {
        MessageSegment segment = segments.get(position);
        
        // Process log group
        if (segment.type == MessageSegment.Type.PROCESS_LOG) {
            return VIEW_TYPE_PROCESS_LOG;
        }
        
        // Single message — determine by type
        ChatMessage msg = segment.messages.get(0);
        switch (msg.type) {
            case "user":
                return VIEW_TYPE_USER;
            case "marketing_form":
                return VIEW_TYPE_MARKETING_FORM;
            case "stage_b_proposal":
                return VIEW_TYPE_PROPOSAL;
            case "stage_c_schedule_proposal":
                return VIEW_TYPE_SCHEDULE_PROPOSAL;
            case "assistant":
            case "knowledge":
            case "completed":
            case "clarification":
            case "campaign_results":
            case "content_briefs":
                return VIEW_TYPE_ASSISTANT;
            case "plan":
                return VIEW_TYPE_PLAN;
            case "report":
            case "react_summary":
            case "evidence":
                return VIEW_TYPE_REPORT;
            case "strategy":
                return VIEW_TYPE_STRATEGY;
            case "error":
                return VIEW_TYPE_ERROR;
            case "status":
            default:
                return VIEW_TYPE_STATUS;
        }
    }
    
    private Markwon getMarkwon(android.content.Context context) {
        if (markwon == null) {
            markwon = Markwon.create(context);
        }
        return markwon;
    }
    
    @NonNull
    @Override
    public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        switch (viewType) {
            case VIEW_TYPE_USER:
                return new UserMessageVH(inflater.inflate(R.layout.item_chat_user, parent, false));
            case VIEW_TYPE_ASSISTANT:
                return new AssistantMessageVH(inflater.inflate(R.layout.item_chat_assistant, parent, false));
            case VIEW_TYPE_PLAN:
                return new CardMessageVH(inflater.inflate(R.layout.item_chat_plan, parent, false));
            case VIEW_TYPE_REPORT:
                return new CardMessageVH(inflater.inflate(R.layout.item_chat_report, parent, false));
            case VIEW_TYPE_STRATEGY:
                return new CardMessageVH(inflater.inflate(R.layout.item_chat_strategy, parent, false));
            case VIEW_TYPE_ERROR:
                return new ErrorMessageVH(inflater.inflate(R.layout.item_chat_error, parent, false));
            case VIEW_TYPE_PROCESS_LOG:
                return new ProcessLogVH(inflater.inflate(R.layout.item_chat_process_log, parent, false));
            case VIEW_TYPE_MARKETING_FORM:
                return new MarketingFormVH(inflater.inflate(R.layout.item_chat_marketing_form, parent, false));
            case VIEW_TYPE_PROPOSAL:
                return new ProposalVH(inflater.inflate(R.layout.item_chat_proposal, parent, false));
            case VIEW_TYPE_SCHEDULE_PROPOSAL:
                return new ScheduleProposalVH(inflater.inflate(R.layout.item_chat_schedule_proposal, parent, false));
            default:
                return new StatusMessageVH(inflater.inflate(R.layout.item_chat_status, parent, false));
        }
    }
    
    @Override
    public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int position) {
        MessageSegment segment = segments.get(position);
        
        if (holder instanceof ProcessLogVH) {
            ((ProcessLogVH) holder).bind(segment);
        } else if (holder instanceof MarketingFormVH) {
            ((MarketingFormVH) holder).bind(segment.messages.get(0));
        } else if (holder instanceof ProposalVH) {
            ((ProposalVH) holder).bind(segment.messages.get(0));
        } else if (holder instanceof ScheduleProposalVH) {
            ((ScheduleProposalVH) holder).bind(segment.messages.get(0));
        } else {
            // Single message types
            ChatMessage message = segment.messages.get(0);
            if (holder instanceof UserMessageVH) {
                ((UserMessageVH) holder).bind(message);
            } else if (holder instanceof AssistantMessageVH) {
                ((AssistantMessageVH) holder).bind(message);
            } else if (holder instanceof CardMessageVH) {
                ((CardMessageVH) holder).bind(message);
            } else if (holder instanceof StatusMessageVH) {
                ((StatusMessageVH) holder).bind(message);
            } else if (holder instanceof ErrorMessageVH) {
                ((ErrorMessageVH) holder).bind(message);
            }
        }
    }
    
    @Override
    public int getItemCount() {
        return segments.size();
    }
    
    // ════════════════════════════════════════════
    // User Message (Right-aligned)
    // ════════════════════════════════════════════
    
    public class UserMessageVH extends RecyclerView.ViewHolder {
        private TextView tvContent, tvTime;
        
        public UserMessageVH(@NonNull View itemView) {
            super(itemView);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTime = itemView.findViewById(R.id.tv_message_time);
        }
        
        public void bind(ChatMessage msg) {
            tvContent.setText(msg.content);
            if (msg.timestamp != null && tvTime != null) {
                tvTime.setText(timeFormat.format(msg.timestamp));
            }
        }
    }
    
    // ════════════════════════════════════════════
    // Assistant Message (Left-aligned, Markdown)
    // ════════════════════════════════════════════
    
    public class AssistantMessageVH extends RecyclerView.ViewHolder {
        private TextView tvContent, tvTime;
        
        public AssistantMessageVH(@NonNull View itemView) {
            super(itemView);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTime = itemView.findViewById(R.id.tv_message_time);
        }
        
        public void bind(ChatMessage msg) {
            Markwon mw = getMarkwon(itemView.getContext());
            
            String displayText = msg.content;
            
            // For knowledge type, append sources
            if ("knowledge".equals(msg.type) && msg.knowledgeData != null) {
                StringBuilder sb = new StringBuilder(msg.knowledgeData.answer != null ? msg.knowledgeData.answer : msg.content);
                if (msg.knowledgeData.sources != null && !msg.knowledgeData.sources.isEmpty()) {
                    sb.append("\n\n📚 **Nguồn tham khảo:**\n");
                    for (ChatMessage.Source src : msg.knowledgeData.sources) {
                        sb.append("• [").append(src.title).append("](").append(src.url).append(")\n");
                    }
                }
                displayText = sb.toString();
            }
            
            // For campaign_results, build summary text
            if ("campaign_results".equals(msg.type) && msg.campaignLogData != null) {
                StringBuilder sb = new StringBuilder("**Kết quả chiến dịch**\n\n");
                sb.append("✅ Thành công: **").append(msg.campaignLogData.successful_posts).append("/").append(msg.campaignLogData.total_posts).append("** bài đăng\n\n");
                if (msg.campaignLogData.briefs_executed != null) {
                    for (ChatMessage.BriefExecution brief : msg.campaignLogData.briefs_executed) {
                        String icon = brief.success ? "✅" : "❌";
                        sb.append(icon).append(" ").append(brief.title != null ? brief.title : "Bài đăng").append("\n");
                        if (brief.message != null) sb.append("   _").append(brief.message).append("_\n");
                    }
                }
                displayText = sb.toString();
            }
            
            // For marketing_form, show form instruction
            if ("marketing_form".equals(msg.type)) {
                displayText = "**Biểu mẫu Marketing**\n\n" + msg.content +
                        "\n\n_Vui lòng nhập thông tin chiến dịch marketing vào ô chat để tiếp tục._";
            }
            
            // For completed, show completion icon
            if ("completed".equals(msg.type)) {
                displayText = "✅ " + msg.content;
            }
            
            // For content_briefs, show brief summary
            if ("content_briefs".equals(msg.type) && msg.contentBriefsData != null) {
                StringBuilder sb = new StringBuilder("**📝 Content Briefs**\n\n");
                for (int i = 0; i < msg.contentBriefsData.size(); i++) {
                    ChatMessage.ContentBrief brief = msg.contentBriefsData.get(i);
                    sb.append("**").append(i + 1).append(". ").append(brief.title != null ? brief.title : "Brief").append("**\n");
                    if (brief.platform != null) sb.append("📱 ").append(brief.platform);
                    if (brief.tone != null) sb.append(" · 🎨 ").append(brief.tone);
                    sb.append("\n");
                    if (brief.content != null) sb.append(brief.content).append("\n");
                    sb.append("\n");
                }
                displayText = sb.toString();
            }
            
            mw.setMarkdown(tvContent, displayText != null ? displayText : "");
            tvContent.setMovementMethod(LinkMovementMethod.getInstance());
            
            if (msg.timestamp != null && tvTime != null) {
                tvTime.setText(timeFormat.format(msg.timestamp));
            }
        }
    }
    
    // ════════════════════════════════════════════
    // Card Messages (Plan, Report, Strategy)
    // ════════════════════════════════════════════
    
    public class CardMessageVH extends RecyclerView.ViewHolder {
        private TextView tvContent, tvTitle;
        
        public CardMessageVH(@NonNull View itemView) {
            super(itemView);
            tvContent = itemView.findViewById(R.id.tv_message_content);
            tvTitle = itemView.findViewById(R.id.tv_card_title);
        }
        
        public void bind(ChatMessage msg) {
            Markwon mw = getMarkwon(itemView.getContext());
            
            String title = "";
            String body = msg.content != null ? msg.content : "";
            
            switch (msg.type) {
                case "plan":
                    title = "📋 Kế hoạch nghiên cứu";
                    if (msg.planData != null && msg.planData.steps != null) {
                        StringBuilder sb = new StringBuilder();
                        if (msg.planData.summary != null) sb.append(msg.planData.summary).append("\n\n");
                        for (ChatMessage.PlanStep step : msg.planData.getTypedSteps()) {
                            sb.append("**").append(step.order).append(". ").append(step.name).append("**\n");
                            sb.append(step.description).append("\n\n");
                        }
                        body = sb.toString();
                    }
                    break;
                    
                case "report":
                    title = "Báo cáo nghiên cứu";
                    if (msg.reportData != null) {
                        StringBuilder sb = new StringBuilder();
                        if (msg.reportData.title != null) sb.append("# ").append(msg.reportData.title).append("\n\n");
                        if (msg.reportData.summary != null) sb.append(msg.reportData.summary).append("\n\n");
                        if (msg.reportData.sections != null) {
                            for (ChatMessage.ReportSection section : msg.reportData.sections) {
                                if (section.title != null) sb.append("## ").append(section.title).append("\n\n");
                                if (section.content != null) sb.append(section.content).append("\n\n");
                            }
                        }
                        body = sb.toString();
                    }
                    break;
                    
                case "react_summary":
                    title = "🧠 Tóm tắt quá trình phân tích";
                    if (msg.reactSummaryData != null) {
                        StringBuilder sb = new StringBuilder();
                        sb.append("🔄 **").append(msg.reactSummaryData.total_thoughts).append("** bước suy luận | ");
                        sb.append("🔧 **").append(msg.reactSummaryData.total_tools_used).append("** công cụ\n\n");
                        if (msg.reactSummaryData.steps != null) {
                            for (ChatMessage.ReactStep step : msg.reactSummaryData.steps) {
                                sb.append("**").append(step.order).append(". ").append(step.name).append("**\n");
                                if (step.reasoning != null) sb.append("💭 ").append(step.reasoning).append("\n");
                                if (step.action != null) sb.append("🔧 ").append(step.action).append("\n");
                                if (step.observation != null) sb.append("👁 ").append(step.observation).append("\n");
                                sb.append("\n");
                            }
                        }
                        body = sb.toString();
                    }
                    break;
                    
                case "evidence":
                    title = "📎 Bằng chứng thu thập";
                    if (msg.evidenceData != null && msg.evidenceData.items != null) {
                        StringBuilder sb = new StringBuilder();
                        for (ChatMessage.Evidence ev : msg.evidenceData.items) {
                            sb.append("**").append(ev.title != null ? ev.title : "Bằng chứng").append("**\n");
                            if (ev.content != null) sb.append(ev.content).append("\n");
                            if (ev.source != null) sb.append("_Nguồn: ").append(ev.source).append("_\n");
                            sb.append("\n");
                        }
                        body = sb.toString();
                    }
                    break;
                    
                case "strategy":
                    title = "Chiến lược marketing";
                    if (msg.strategyData != null) {
                        StringBuilder sb = new StringBuilder();
                        if (msg.strategyData.title != null) sb.append("**").append(msg.strategyData.title).append("**\n\n");
                        
                        // SWOT
                        if (msg.strategyData.swot != null) {
                            sb.append("### SWOT Analysis\n\n");
                            ChatMessage.SWOT swot = msg.strategyData.swot;
                            if (swot.strengths != null) { sb.append("**💪 Điểm mạnh:**\n"); for (String s : swot.strengths) sb.append("• ").append(s).append("\n"); sb.append("\n"); }
                            if (swot.weaknesses != null) { sb.append("**⚠️ Điểm yếu:**\n"); for (String s : swot.weaknesses) sb.append("• ").append(s).append("\n"); sb.append("\n"); }
                            if (swot.opportunities != null) { sb.append("**🌟 Cơ hội:**\n"); for (String s : swot.opportunities) sb.append("• ").append(s).append("\n"); sb.append("\n"); }
                            if (swot.threats != null) { sb.append("**🔴 Thách thức:**\n"); for (String s : swot.threats) sb.append("• ").append(s).append("\n"); sb.append("\n"); }
                        }
                        
                        // USP
                        if (msg.strategyData.usp != null) {
                            sb.append("### USP\n\n");
                            if (msg.strategyData.usp.core_benefit != null) sb.append("**Lợi ích cốt lõi:** ").append(msg.strategyData.usp.core_benefit).append("\n");
                            if (msg.strategyData.usp.tagline != null) sb.append("**Tagline:** _").append(msg.strategyData.usp.tagline).append("_\n\n");
                        }
                        
                        // Persona
                        if (msg.strategyData.persona != null) {
                            sb.append("### Persona\n\n");
                            ChatMessage.Persona p = msg.strategyData.persona;
                            if (p.name != null) sb.append("**").append(p.name).append("**");
                            if (p.age != null) sb.append(" — ").append(p.age);
                            sb.append("\n");
                            if (p.occupation != null) sb.append("Nghề nghiệp: ").append(p.occupation).append("\n");
                            if (p.pain_points != null) { sb.append("**Pain points:**\n"); for (String s : p.pain_points) sb.append("• ").append(s).append("\n"); }
                            if (p.goals != null) { sb.append("**Mục tiêu:**\n"); for (String s : p.goals) sb.append("• ").append(s).append("\n"); }
                            sb.append("\n");
                        }
                        
                        body = sb.toString();
                    }
                    break;
            }
            
            if (tvTitle != null) tvTitle.setText(title);
            mw.setMarkdown(tvContent, body);
            tvContent.setMovementMethod(LinkMovementMethod.getInstance());
        }
    }
    
    // ════════════════════════════════════════════
    // Status Message (Center, with spinner)
    // ════════════════════════════════════════════
    
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
            // Show spinner for active statuses
            if ("completed".equals(msg.type)) {
                pbStatus.setVisibility(View.GONE);
            } else {
                pbStatus.setVisibility(View.VISIBLE);
            }
        }
    }
    
    // ════════════════════════════════════════════
    // Error Message
    // ════════════════════════════════════════════
    
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
    
    // ════════════════════════════════════════════
    // Process Log (Collapsible group)
    // Mirrors frontend ProcessLog.tsx
    // ════════════════════════════════════════════
    
    public class ProcessLogVH extends RecyclerView.ViewHolder {
        private View layoutHeader;
        private TextView tvCurrent, tvCount, tvChevron;
        private LinearLayout layoutBody, layoutTimeline;
        private boolean isExpanded = false;
        
        public ProcessLogVH(@NonNull View itemView) {
            super(itemView);
            layoutHeader = itemView.findViewById(R.id.layout_process_log_header);
            tvCurrent = itemView.findViewById(R.id.tv_process_log_current);
            tvCount = itemView.findViewById(R.id.tv_process_log_count);
            tvChevron = itemView.findViewById(R.id.tv_process_log_chevron);
            layoutBody = itemView.findViewById(R.id.layout_process_log_body);
            layoutTimeline = itemView.findViewById(R.id.layout_timeline_entries);
        }
        
        public void bind(MessageSegment segment) {
            List<ChatMessage> messages = segment.messages;
            
            // Find latest status message to display
            ChatMessage latestStatus = null;
            int statusCount = 0;
            boolean hasDetailMessages = false;
            
            for (int i = messages.size() - 1; i >= 0; i--) {
                ChatMessage m = messages.get(i);
                if ("status".equals(m.type)) {
                    if (latestStatus == null) latestStatus = m;
                    statusCount++;
                } else {
                    hasDetailMessages = true;
                }
            }
            
            // Set header text
            String headerText = latestStatus != null ? latestStatus.content : messages.get(messages.size() - 1).content;
            tvCurrent.setText(headerText);
            
            // Step count
            String countText = statusCount + " bước" + (hasDetailMessages ? " · có chi tiết" : "");
            tvCount.setText(countText);
            
            // Reset expand state
            isExpanded = false;
            layoutBody.setVisibility(View.GONE);
            tvChevron.setRotation(0);
            
            // Click to expand/collapse
            layoutHeader.setOnClickListener(v -> {
                isExpanded = !isExpanded;
                
                if (isExpanded) {
                    // Build timeline entries
                    buildTimelineEntries(messages);
                    layoutBody.setVisibility(View.VISIBLE);
                    tvChevron.animate().rotation(180).setDuration(200).start();
                } else {
                    layoutBody.setVisibility(View.GONE);
                    tvChevron.animate().rotation(0).setDuration(200).start();
                }
            });
        }
        
        private void buildTimelineEntries(List<ChatMessage> messages) {
            layoutTimeline.removeAllViews();
            android.content.Context ctx = itemView.getContext();
            Markwon mw = getMarkwon(ctx);
            
            for (ChatMessage msg : messages) {
                // Create entry row
                LinearLayout entryRow = new LinearLayout(ctx);
                entryRow.setOrientation(LinearLayout.HORIZONTAL);
                entryRow.setGravity(android.view.Gravity.TOP);
                LinearLayout.LayoutParams rowParams = new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        LinearLayout.LayoutParams.WRAP_CONTENT
                );
                rowParams.bottomMargin = dpToPx(ctx, 6);
                entryRow.setLayoutParams(rowParams);
                
                // Timeline dot
                View dot = new View(ctx);
                int dotSize = dpToPx(ctx, 8);
                LinearLayout.LayoutParams dotParams = new LinearLayout.LayoutParams(dotSize, dotSize);
                dotParams.topMargin = dpToPx(ctx, 5);
                dotParams.setMarginEnd(dpToPx(ctx, 10));
                dot.setLayoutParams(dotParams);
                
                // Color dot by message type
                int dotColor;
                switch (msg.type) {
                    case "plan": dotColor = ctx.getResources().getColor(R.color.accent_plan, null); break;
                    case "react_summary": dotColor = ctx.getResources().getColor(R.color.accent_react, null); break;
                    case "evidence": dotColor = ctx.getResources().getColor(R.color.accent_evidence, null); break;
                    default: dotColor = ctx.getResources().getColor(R.color.accent_primary, null); break;
                }
                
                android.graphics.drawable.GradientDrawable dotBg = new android.graphics.drawable.GradientDrawable();
                dotBg.setShape(android.graphics.drawable.GradientDrawable.OVAL);
                dotBg.setColor(dotColor);
                dot.setBackground(dotBg);
                
                entryRow.addView(dot);
                
                // Message text
                TextView tvText = new TextView(ctx);
                tvText.setLayoutParams(new LinearLayout.LayoutParams(
                        0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f
                ));
                tvText.setTextSize(12);
                tvText.setTextColor(ctx.getResources().getColor(R.color.text_secondary, null));
                
                // For card-type messages inside process log, render with markdown
                if ("plan".equals(msg.type) || "react_summary".equals(msg.type) || "evidence".equals(msg.type)) {
                    String cardBody = buildCardBody(msg);
                    mw.setMarkdown(tvText, cardBody);
                    tvText.setMovementMethod(LinkMovementMethod.getInstance());
                } else {
                    tvText.setText(msg.content);
                }
                
                entryRow.addView(tvText);
                layoutTimeline.addView(entryRow);
            }
        }
        
        /** Build card-type message body text for inside process log */
        private String buildCardBody(ChatMessage msg) {
            switch (msg.type) {
                case "plan":
                    if (msg.planData != null && msg.planData.steps != null) {
                        StringBuilder sb = new StringBuilder("**📋 Kế hoạch nghiên cứu**\n");
                        if (msg.planData.summary != null) sb.append(msg.planData.summary).append("\n");
                        for (ChatMessage.PlanStep step : msg.planData.getTypedSteps()) {
                            sb.append("**").append(step.order).append(".** ").append(step.name).append("\n");
                        }
                        return sb.toString();
                    }
                    break;
                case "react_summary":
                    if (msg.reactSummaryData != null) {
                        StringBuilder sb = new StringBuilder("**🧠 Phân tích:** ");
                        sb.append(msg.reactSummaryData.total_thoughts).append(" bước · ");
                        sb.append(msg.reactSummaryData.total_tools_used).append(" công cụ\n");
                        return sb.toString();
                    }
                    break;
                case "evidence":
                    if (msg.evidenceData != null && msg.evidenceData.items != null) {
                        StringBuilder sb = new StringBuilder("**📎 Bằng chứng:** ");
                        sb.append(msg.evidenceData.items.size()).append(" nguồn\n");
                        return sb.toString();
                    }
                    break;
            }
            return msg.content != null ? msg.content : "";
        }
        
        private int dpToPx(android.content.Context ctx, int dp) {
            return (int) (dp * ctx.getResources().getDisplayMetrics().density + 0.5f);
        }
    }
    
    // ════════════════════════════════════════════
    // Marketing Form (Input card with submit)
    // ════════════════════════════════════════════
    
    public class MarketingFormVH extends RecyclerView.ViewHolder {
        private TextView tvDescription;
        private EditText etUserPrompt, etBanChatSanPham, etKhachHangMucTieu, etGiaTriCotLoi, etGiaCaChinhSach;
        private Button btnSubmit, btnCancel;
        private boolean isSubmitted = false;
        
        public MarketingFormVH(@NonNull View itemView) {
            super(itemView);
            tvDescription = itemView.findViewById(R.id.tv_form_description);
            etUserPrompt = itemView.findViewById(R.id.et_user_prompt);
            etBanChatSanPham = itemView.findViewById(R.id.et_ban_chat_san_pham);
            etKhachHangMucTieu = itemView.findViewById(R.id.et_khach_hang_muc_tieu);
            etGiaTriCotLoi = itemView.findViewById(R.id.et_gia_tri_cot_loi);
            etGiaCaChinhSach = itemView.findViewById(R.id.et_gia_ca_chinh_sach);
            btnSubmit = itemView.findViewById(R.id.btn_form_submit);
            btnCancel = itemView.findViewById(R.id.btn_form_cancel);
        }
        
        public void bind(ChatMessage msg) {
            // Set description from message content
            if (msg.content != null && !msg.content.isEmpty() && tvDescription != null) {
                tvDescription.setText(msg.content);
            }
            
            // Pre-fill user_prompt from detected prompt
            if (msg.marketingFormData != null && msg.marketingFormData.detected_prompt != null
                    && !msg.marketingFormData.detected_prompt.isEmpty()) {
                etUserPrompt.setText(msg.marketingFormData.detected_prompt);
            }
            
            // Reset state on rebind
            setFormEnabled(!isSubmitted);
            
            btnSubmit.setOnClickListener(v -> {
                if (isSubmitted || actionListener == null) return;
                
                String userPrompt = etUserPrompt.getText().toString().trim();
                if (userPrompt.isEmpty()) {
                    etUserPrompt.setError("Vui lòng nhập yêu cầu nghiên cứu");
                    return;
                }
                
                isSubmitted = true;
                setFormEnabled(false);
                
                // Build form data matching frontend ResearchRequest field names exactly
                Map<String, Object> formData = new HashMap<>();
                formData.put("user_prompt", userPrompt);
                
                String banChat = etBanChatSanPham.getText().toString().trim();
                if (!banChat.isEmpty()) formData.put("ban_chat_san_pham", banChat);
                
                String khachHang = etKhachHangMucTieu.getText().toString().trim();
                if (!khachHang.isEmpty()) formData.put("khach_hang_muc_tieu", khachHang);
                
                String giaTri = etGiaTriCotLoi.getText().toString().trim();
                if (!giaTri.isEmpty()) formData.put("gia_tri_cot_loi", giaTri);
                
                String giaCa = etGiaCaChinhSach.getText().toString().trim();
                if (!giaCa.isEmpty()) formData.put("gia_ca_chinh_sach", giaCa);
                
                actionListener.onMarketingFormSubmit(formData);
            });
            
            btnCancel.setOnClickListener(v -> {
                // Clear all fields
                etUserPrompt.setText("");
                etBanChatSanPham.setText("");
                etKhachHangMucTieu.setText("");
                etGiaTriCotLoi.setText("");
                etGiaCaChinhSach.setText("");
            });
        }
        
        private void setFormEnabled(boolean enabled) {
            etUserPrompt.setEnabled(enabled);
            etBanChatSanPham.setEnabled(enabled);
            etKhachHangMucTieu.setEnabled(enabled);
            etGiaTriCotLoi.setEnabled(enabled);
            etGiaCaChinhSach.setEnabled(enabled);
            btnSubmit.setEnabled(enabled);
            btnSubmit.setAlpha(enabled ? 1.0f : 0.5f);
        }
    }
    
    // ════════════════════════════════════════════
    // Stage B Proposal (Accept/Decline)
    // ════════════════════════════════════════════
    
    public class ProposalVH extends RecyclerView.ViewHolder {
        private Button btnAccept, btnDecline;
        private boolean isActioned = false;
        
        public ProposalVH(@NonNull View itemView) {
            super(itemView);
            btnAccept = itemView.findViewById(R.id.btn_proposal_accept);
            btnDecline = itemView.findViewById(R.id.btn_proposal_decline);
        }
        
        public void bind(ChatMessage msg) {
            // Reset
            btnAccept.setEnabled(!isActioned);
            btnDecline.setEnabled(!isActioned);
            btnAccept.setAlpha(!isActioned ? 1.0f : 0.5f);
            
            // Update button text to match frontend
            btnAccept.setText("Lập Chiến Lược");
            
            btnAccept.setOnClickListener(v -> {
                if (isActioned || actionListener == null) return;
                isActioned = true;
                btnAccept.setEnabled(false);
                btnDecline.setEnabled(false);
                btnAccept.setAlpha(0.5f);
                
                if (msg.stageBProposalData != null) {
                    actionListener.onAcceptStageBProposal(
                            msg.stageBProposalData.report,
                            msg.stageBProposalData.mongodbId
                    );
                }
            });
            
            btnDecline.setOnClickListener(v -> {
                isActioned = true;
                btnAccept.setEnabled(false);
                btnDecline.setEnabled(false);
                btnAccept.setAlpha(0.5f);
            });
        }
    }
    
    // ════════════════════════════════════════════
    // Stage C Schedule Proposal (Accept/Decline)
    // ════════════════════════════════════════════
    
    public class ScheduleProposalVH extends RecyclerView.ViewHolder {
        private Button btnConfirm, btnCancel;
        private boolean isActioned = false;
        
        public ScheduleProposalVH(@NonNull View itemView) {
            super(itemView);
            btnConfirm = itemView.findViewById(R.id.btn_schedule_confirm);
            btnCancel = itemView.findViewById(R.id.btn_schedule_cancel);
        }
        
        public void bind(ChatMessage msg) {
            // Reset
            btnConfirm.setEnabled(!isActioned);
            btnCancel.setEnabled(!isActioned);
            btnConfirm.setAlpha(!isActioned ? 1.0f : 0.5f);
            
            // Update button text
            btnConfirm.setText("Thực Thi Chiến Dịch");
            
            btnConfirm.setOnClickListener(v -> {
                if (isActioned || actionListener == null) return;
                isActioned = true;
                btnConfirm.setEnabled(false);
                btnCancel.setEnabled(false);
                btnConfirm.setAlpha(0.5f);
                
                if (msg.stageCScheduleProposalData != null) {
                    actionListener.onAcceptStageCProposal(
                            msg.stageCScheduleProposalData.briefs,
                            msg.stageCScheduleProposalData.mongodbId
                    );
                }
            });
            
            btnCancel.setOnClickListener(v -> {
                isActioned = true;
                btnConfirm.setEnabled(false);
                btnCancel.setEnabled(false);
                btnConfirm.setAlpha(0.5f);
            });
        }
    }
    
    // ════════════════════════════════════════════
    // Public helpers
    // ════════════════════════════════════════════
    
    public void updateMessages(List<ChatMessage> newMessages) {
        rebuildSegments(newMessages);
        notifyDataSetChanged();
    }
    
    public void addMessage(ChatMessage message) {
        // Not used directly anymore — use updateMessages or rebuild after adding
    }
}
