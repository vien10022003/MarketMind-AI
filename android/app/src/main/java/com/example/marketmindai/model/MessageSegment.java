package com.example.marketmindai.model;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Groups consecutive process-log messages (status, plan, react_summary, evidence)
 * into a single collapsible segment — mirroring frontend ProcessLog.tsx behavior.
 *
 * A "single" segment contains exactly one non-process message.
 * A "process-log" segment contains 1+ consecutive process messages.
 */
public class MessageSegment {

    public enum Type {
        SINGLE,
        PROCESS_LOG
    }

    /** Message types that belong inside the process log (hidden until expanded) */
    public static final Set<String> PROCESS_LOG_TYPES = new HashSet<>(Arrays.asList(
            "status",
            "plan",
            "react_summary",
            "evidence"
    ));

    public Type type;
    public String key;
    public List<ChatMessage> messages;

    public MessageSegment(Type type, String key, List<ChatMessage> messages) {
        this.type = type;
        this.key = key;
        this.messages = messages;
    }

    /** Check if a message type belongs in the process log */
    public static boolean isProcessLogType(String msgType) {
        return PROCESS_LOG_TYPES.contains(msgType);
    }

    /**
     * Build segments from a flat list of chat messages.
     * Groups consecutive process-log messages together.
     * Mirrors frontend's groupedMessages useMemo logic.
     */
    public static List<MessageSegment> buildSegments(List<ChatMessage> chatMessages) {
        List<MessageSegment> segments = new ArrayList<>();
        List<ChatMessage> currentGroup = new ArrayList<>();

        for (ChatMessage msg : chatMessages) {
            if (isProcessLogType(msg.type)) {
                currentGroup.add(msg);
            } else {
                // Flush accumulated process-log group
                if (!currentGroup.isEmpty()) {
                    segments.add(new MessageSegment(
                            Type.PROCESS_LOG,
                            "plog-" + currentGroup.get(0).id,
                            new ArrayList<>(currentGroup)
                    ));
                    currentGroup.clear();
                }
                // Add single message
                List<ChatMessage> single = new ArrayList<>();
                single.add(msg);
                segments.add(new MessageSegment(Type.SINGLE, msg.id, single));
            }
        }

        // Flush remaining group
        if (!currentGroup.isEmpty()) {
            segments.add(new MessageSegment(
                    Type.PROCESS_LOG,
                    "plog-" + currentGroup.get(0).id,
                    new ArrayList<>(currentGroup)
            ));
        }

        return segments;
    }
}
