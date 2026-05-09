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
        self.conversations.create_index("created_at", background=True)
        self.conversations.create_index("updated_at", background=True)

    def create_conversation(self, conversation_id: str, title: Optional[str] = None) -> dict:
        """Create a new conversation"""
        now = datetime.now().isoformat()
        doc = {
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

    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get a conversation by ID"""
        doc = self.conversations.find_one({"conversation_id": conversation_id})
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

    def get_recent_conversations(self, limit: int = 10) -> List[dict]:
        """Get most recent conversations (for sidebar/list)"""
        docs = list(
            self.conversations.find()
            .sort("updated_at", -1)
            .limit(limit)
        )
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs

    def list_conversations(self, skip: int = 0, limit: int = 20) -> tuple[List[dict], int]:
        """List conversations with pagination"""
        total = self.conversations.count_documents({})
        docs = list(
            self.conversations.find()
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs, total

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        result = self.conversations.delete_one({"conversation_id": conversation_id})
        return result.deleted_count > 0

    def update_title(self, conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        result = self.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"title": title, "updated_at": datetime.now().isoformat()}},
        )
        return result.modified_count > 0


def get_conversation_manager(db: Database) -> ConversationManager:
    """Factory function to create conversation manager"""
    return ConversationManager(db)
