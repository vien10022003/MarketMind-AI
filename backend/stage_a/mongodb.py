"""
MongoDB Integration Module
Handles storage and retrieval of research reports
"""

import os
from datetime import datetime
from typing import Any, Dict, Optional
import pymongo
from rich import print as rprint

from .data_models import StageAOutput


class MongoDBManager:
    """MongoDB connection and operations manager"""
    
    def __init__(self, uri: Optional[str] = None):
        self.uri = uri or os.getenv("MONGO_URI", "")
        self.client = None
        self.db = None
        self.collection = None
        
        if self.uri:
            self._connect()
        else:
            rprint("[yellow]⚠️ No MONGO_URI provided[/yellow]")
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            
            self.db = self.client['marketmind_ai']
            self.collection = self.db['stage_a_reports']
            
            rprint("[green]✅ MongoDB connection successful[/green]")
        except Exception as e:
            rprint(f"[red]✗ MongoDB connection failed: {e}[/red]")
            self.client = None
    
    def save_report(
        self,
        metadata: Dict[str, Any],
        output_data: StageAOutput
    ) -> Optional[str]:
        """Save report to MongoDB"""
        if not self.client or not self.collection:
            rprint("[yellow]⚠️ MongoDB not connected. Skipping save.[/yellow]")
            return None
        
        try:
            doc = {
                "timestamp": metadata.get("timestamp", datetime.now().isoformat()),
                "input_config": metadata.get("input", {}),
                "report": {
                    "tong_quan_thi_truong": output_data.tong_quan_thi_truong,
                    "phan_tich_doi_thu": output_data.phan_tich_doi_thu,
                    "xu_huong_nganh": output_data.xu_huong_nganh,
                    "phan_khuc_va_insight_khach_hang": output_data.phan_khuc_va_insight_khach_hang,
                    "citations": [c.model_dump() for c in output_data.citations]
                },
                "metrics": metadata.get("react_summary", {})
            }
            
            result = self.collection.insert_one(doc)
            doc_id = str(result.inserted_id)
            
            rprint(f"[green]✅ Document saved to MongoDB: {doc_id}[/green]")
            return doc_id
            
        except Exception as e:
            rprint(f"[red]✗ Failed to save to MongoDB: {e}[/red]")
            return None
    
    def find_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Find report by ID"""
        if not self.client or not self.collection:
            return None
        
        try:
            from pymongo.objectid import ObjectId
            return self.collection.find_one({"_id": ObjectId(report_id)})
        except Exception as e:
            rprint(f"[red]✗ Failed to find report: {e}[/red]")
            return None
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            rprint("[yellow]MongoDB connection closed[/yellow]")
