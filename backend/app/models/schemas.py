from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BaseInDB(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime] = None


class Alert(BaseInDB):
    rule_name: str
    severity: str
    mitre: Optional[List[str]] = []
    matched_events: Optional[List[dict]] = []
    description: Optional[str] = None


class Incident(BaseInDB):
    title: str
    description: Optional[str]
    status: str = "open"
    alerts: Optional[List[str]] = []


class IOC(BaseInDB):
    type: str
    value: str
    source: Optional[str]
    confidence: Optional[int] = 50
    tags: Optional[List[str]] = []


class DetectionRule(BaseInDB):
    name: str
    description: Optional[str]
    severity: str
    mitre: Optional[List[str]] = []
    sigma_rule: Optional[dict] = None
