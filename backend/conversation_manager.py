"""
Conversation Manager - Persist and retrieve chat history
Saves entire conversation threads to MongoDB for continuity
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from pymongo.collection import Collection
from pymongo.database import Database


class ChatMessageDoc(BaseModel):
    """A single chat message in the conversation"""
    id: str
    type: str  # 'user', 'assistant', 'status', 'report', 'strategy', 'content_briefs', 'stage_b_proposal', 'stage_c_proposal', 'stage_c_schedule_proposal', 'campaign_results', 'schedule_manager', etc.
    content: str
    timestamp: str  # ISO 8601
    # Optional payload fields for structured data
    mongodbId: Optional[str] = None
    clarificationData: Optional[dict] = None
    planData: Optional[dict] = None
    reactSummaryData: Optional[dict] = None
    evidenceData: Optional[dict] = None
    reportData: Optional[dict] = None
    strategyData: Optional[dict] = None
    contentBriefsData: Optional[list] = None
    stageBProposalData: Optional[dict] = None
    stageCProposalData: Optional[dict] = None
    stageCScheduleProposalData: Optional[dict] = None
    campaignLogData: Optional[dict] = None
    scheduleManagerData: Optional[dict] = None
    knowledgeData: Optional[dict] = None
    marketingFormData: Optional[dict] = None


class ConversationDoc(BaseModel):
    """A complete conversation thread"""
    user_id: Optional[str] = Field(default=None, description="User ID for multi-user support")
    conversation_id: str = Field(description="Unique conversation ID")
    title: Optional[str] = Field(default=None, description="User-given title or auto-generated")
    messages: List[ChatMessageDoc] = Field(default_factory=list, description="All messages in order")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_message_at: Optional[str] = Field(default=None)
    message_count: int = Field(default=0)
    # Stage context
    stage_a_data: Optional[dict] = None
    stage_b_data: Optional[dict] = None
    stage_c_data: Optional[dict] = None


class ConversationManager:
    """Manages conversation persistence in MongoDB"""

    def __init__(self, db: Database):
        self.db = db
        self.conversations: Collection = db["conversations"]
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create indexes for efficient queries"""
        self.conversations.create_index("conversation_id", unique=True)
        self.conversations.create_index("user_id", background=True)
        self.conversations.create_index([("user_id", 1), ("created_at", -1)], background=True)
        self.conversations.create_index("created_at", background=True)
        self.conversations.create_index("updated_at", background=True)

    def create_conversation(self, conversation_id: str, title: Optional[str] = None, user_id: Optional[str] = None) -> dict:
        """Create a new conversation
        
        Args:
            conversation_id: Unique conversation ID
            title: Optional conversation title
            user_id: Optional user ID for multi-user support
        """
        now = datetime.now().isoformat()
        doc = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "title": title or f"Conversation {conversation_id[:8]}",
            "messages": [],
            "created_at": now,
            "updated_at": now,
            "last_message_at": None,
            "message_count": 0,
            "stage_a_data": None,
            "stage_b_data": None,
            "stage_c_data": None,
        }
        result = self.conversations.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    def get_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """Get a conversation by ID
        
        Args:
            conversation_id: Conversation ID to retrieve
            user_id: Optional user ID for security validation
        """
        query = {"conversation_id": conversation_id}
        if user_id:
            query["user_id"] = user_id  # Only return if user owns it
        
        doc = self.conversations.find_one(query)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def save_message(self, conversation_id: str, message: ChatMessageDoc) -> bool:
        """Add a message to conversation and update metadata"""
        now = datetime.now().isoformat()
        result = self.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": message.dict()},
                "$set": {
                    "updated_at": now,
                    "last_message_at": now,
                },
                "$inc": {"message_count": 1},
            },
        )
        return result.modified_count > 0

    def save_batch_messages(self, conversation_id: str, messages: List[ChatMessageDoc]) -> bool:
        """Add multiple messages at once"""
        if not messages:
            return False
        now = datetime.now().isoformat()
        result = self.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$push": {"messages": {"$each": [m.dict() for m in messages]}},
                "$set": {
                    "updated_at": now,
                    "last_message_at": now,
                },
                "$inc": {"message_count": len(messages)},
            },
        )
        return result.modified_count > 0

    def update_stage_data(self, conversation_id: str, stage: str, data: dict) -> bool:
        """Store stage-specific data (A, B, or C)"""
        field = f"stage_{stage}_data"
        result = self.conversations.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    field: data,
                    "updated_at": datetime.now().isoformat(),
                }
            },
        )
        return result.modified_count > 0

    def get_recent_conversations(self, limit: int = 10, user_id: Optional[str] = None) -> List[dict]:
        """Get most recent conversations (for sidebar/list)
        
        Args:
            limit: Maximum number of conversations to return
            user_id: Optional user ID to filter conversations by owner
        """
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        docs = list(
            self.conversations.find(query)
            .sort("updated_at", -1)
            .limit(limit)
        )
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    def list_conversations(self, skip: int = 0, limit: int = 20, user_id: Optional[str] = None) -> tuple[List[dict], int]:
        """List conversations with pagination
        
        Args:
            skip: Number of conversations to skip
            limit: Maximum number of conversations to return
            user_id: Optional user ID to filter conversations by owner
        """
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        total = self.conversations.count_documents(query)
        docs = list(
            self.conversations.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs, total

    def delete_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a conversation
        
        Args:
            conversation_id: Conversation ID to delete
            user_id: Optional user ID to ensure only owner can delete
        """
        query = {"conversation_id": conversation_id}
        if user_id:
            query["user_id"] = user_id
        
        result = self.conversations.delete_one(query)
        return result.deleted_count > 0

    def update_title(self, conversation_id: str, title: str, user_id: Optional[str] = None) -> bool:
        """Update conversation title
        
        Args:
            conversation_id: Conversation ID to update
            title: New title
            user_id: Optional user ID to ensure only owner can update
        """
        query = {"conversation_id": conversation_id}
        if user_id:
            query["user_id"] = user_id
        
        result = self.conversations.update_one(
            query,
            {"$set": {"title": title, "updated_at": datetime.now().isoformat()}},
        )
        return result.modified_count > 0


def get_conversation_manager(db: Database) -> ConversationManager:
    """Factory function to create conversation manager"""
    return ConversationManager(db)
