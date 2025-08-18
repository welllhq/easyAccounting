# database.py
import sqlite3
import os
from typing import List, Optional
from datetime import datetime
from models import Ledger, AssetRecord, LedgerSummary

class Database:
    def __init__(self, db_path: str = "accounting.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建账本表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ledgers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建资产记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_id INTEGER,
                amount REAL NOT NULL,
                note TEXT,
                period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ledger_id) REFERENCES ledgers (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_ledger(self, ledger: Ledger) -> Ledger:
        """创建新账本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ledgers (name, description, created_at)
            VALUES (?, ?, ?)
        ''', (ledger.name, ledger.description, ledger.created_at or datetime.now()))
        
        ledger_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        ledger.id = ledger_id
        return ledger
    
    def get_all_ledgers(self) -> List[Ledger]:
        """获取所有账本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, description, created_at FROM ledgers')
        rows = cursor.fetchall()
        conn.close()
        
        return [Ledger(id=row[0], name=row[1], description=row[2], 
                      created_at=datetime.fromisoformat(row[3])) for row in rows]
    
    def delete_ledger(self, ledger_id: int):
        """删除账本"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM asset_records WHERE ledger_id = ?', (ledger_id,))
        cursor.execute('DELETE FROM ledgers WHERE id = ?', (ledger_id,))
        
        conn.commit()
        conn.close()
    
    def add_asset_record(self, record: AssetRecord) -> AssetRecord:
        """添加资产记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO asset_records (ledger_id, amount, note, period, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (record.ledger_id, record.amount, record.note, record.period, record.created_at or datetime.now()))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        record.id = record_id
        return record
    
    def get_latest_asset_records(self) -> List[AssetRecord]:
        """获取每个账本的最新记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        

        cursor.execute('''
                SELECT ar.id, ar.ledger_id, ar.amount, ar.note, ar.period, ar.created_at
                FROM asset_records ar
                INNER JOIN (
                    SELECT ledger_id, MAX(created_at) as max_date
                    FROM asset_records
                    GROUP BY ledger_id
                ) latest ON ar.ledger_id = latest.ledger_id AND ar.created_at = latest.max_date
            ''')


        
        rows = cursor.fetchall()
        conn.close()
        
        return [AssetRecord(id=row[0], ledger_id=row[1], amount=row[2], 
                           note=row[3], period=row[4], created_at=datetime.fromisoformat(row[5])) for row in rows]
    
    def get_ledger_history(self, ledger_id: int) -> List[AssetRecord]:
        """获取账本历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
       
        
        cursor.execute('''
                SELECT id, ledger_id, amount, note, period, created_at
                FROM asset_records
                WHERE ledger_id = ?
                ORDER BY created_at DESC
            ''', (ledger_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [AssetRecord(id=row[0], ledger_id=row[1], amount=row[2], 
                           note=row[3], period=row[4], created_at=datetime.fromisoformat(row[5])) for row in rows]
    
    def get_ledger_summaries(self) -> List[LedgerSummary]:
        """获取账本统计信息"""
        ledgers = self.get_all_ledgers()
        latest_records = self.get_latest_asset_records()
        
        # 创建ledger_id到最新记录的映射
        record_map = {record.ledger_id: record for record in latest_records}
        
        # 计算总资产
        total_amount = sum(record.amount for record in latest_records)
        
        # 构建账本统计信息
        summaries = []
        for ledger in ledgers:
            current_amount = record_map.get(ledger.id, AssetRecord(None, ledger.id, 0.0, "", "", datetime.now())).amount
            percentage = (current_amount / total_amount * 100) if total_amount > 0 else 0
            
            summaries.append(LedgerSummary(
                ledger=ledger,
                current_amount=current_amount,
                percentage=percentage
            ))
        
        return summaries
    
    def get_all_records(self) -> List[AssetRecord]:
        """获取所有资产记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                SELECT id, ledger_id, amount, note, period, created_at
                FROM asset_records
                ORDER BY created_at DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [AssetRecord(id=row[0], ledger_id=row[1], amount=row[2], 
                           note=row[3], period=row[4], created_at=datetime.fromisoformat(row[5])) for row in rows]