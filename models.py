# models.py
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Ledger:
    """账本类"""
    id: Optional[int]
    name: str
    description: str
    created_at: datetime

@dataclass
class AssetRecord:
    """资产记录类"""
    id: Optional[int]
    ledger_id: int
    amount: float
    note: str
    period: str  # 盘点周期字段
    created_at: datetime

@dataclass
class LedgerSummary:
    """账本统计信息"""
    ledger: Ledger
    current_amount: float
    percentage: float