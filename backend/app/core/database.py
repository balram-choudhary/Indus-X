import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

DB_PATH = Path("C:/hack_project_1/backend/data/indusx.db")

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Quality Incidents Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            scenario_type INTEGER NOT NULL,
            defect_class TEXT NOT NULL,
            raw_frame_count INTEGER DEFAULT 0,
            confidence_avg REAL DEFAULT 0.0,
            best_frame_path TEXT,
            crop_path TEXT,
            heatmap_path TEXT,
            batch_id TEXT,
            vendor_id TEXT,
            status TEXT DEFAULT 'OPEN',
            risk_tier INTEGER DEFAULT 1,
            cost_if_missed REAL DEFAULT 0.0,
            cost_if_caught REAL DEFAULT 0.0,
            net_savings REAL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            resolved_by TEXT,
            operator_verdict TEXT
        )
        """)

        # 2. Provenance Hash Chain (Append-only Ledger)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS provenance_chain (
            block_index INTEGER PRIMARY KEY,
            incident_id TEXT NOT NULL,
            timestamp_iso TEXT NOT NULL,
            camera_id TEXT NOT NULL,
            frame_sha256 TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            curr_hash TEXT NOT NULL
        )
        """)

        # 3. Batches & Traceability Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches (
            batch_id TEXT PRIMARY KEY,
            component_name TEXT NOT NULL,
            component_lot TEXT NOT NULL,
            workstation_id TEXT NOT NULL,
            shift_id TEXT NOT NULL,
            operator_id TEXT NOT NULL,
            vendor_id TEXT NOT NULL,
            total_units INTEGER NOT NULL,
            inspected_units INTEGER DEFAULT 0,
            defective_units INTEGER DEFAULT 0,
            status TEXT DEFAULT 'IN_PRODUCTION',
            sla_contract_id TEXT NOT NULL,
            unit_cost REAL DEFAULT 28.50,
            rework_cost REAL DEFAULT 4.20,
            recall_cost REAL DEFAULT 36.50
        )
        """)

        # 4. Vendors & Risk Profile Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id TEXT PRIMARY KEY,
            vendor_name TEXT NOT NULL,
            total_units_shipped INTEGER DEFAULT 0,
            total_incidents INTEGER DEFAULT 0,
            structural_incidents INTEGER DEFAULT 0,
            wrong_component_incidents INTEGER DEFAULT 0,
            surface_incidents INTEGER DEFAULT 0,
            batch_recurrence_rate REAL DEFAULT 0.0,
            normalized_risk_score REAL DEFAULT 0.0,
            inspection_regime TEXT DEFAULT 'NORMAL',
            last_incident_date TEXT,
            risk_trend TEXT DEFAULT 'STABLE'
        )
        """)

        # 5. Chain of Custody & Governance Audit Log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS custody_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            timestamp_iso TEXT NOT NULL,
            state_from TEXT,
            state_to TEXT NOT NULL,
            action TEXT NOT NULL,
            actor TEXT NOT NULL,
            actor_role TEXT NOT NULL,
            notes TEXT,
            mqtt_payload TEXT
        )
        """)
        
        conn.commit()
    seed_initial_data()

def seed_initial_data():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if vendors exist
        cursor.execute("SELECT COUNT(*) FROM vendors")
        if cursor.fetchone()[0] == 0:
            vendors_seed = [
                ("VND-X", "Apex Industrial Fasteners Ltd.", 500, 2, 2, 0, 0, 0.40, 62.0, "NORMAL", "2026-10-28T09:12:00Z", "INCREASING"),
                ("VND-A", "Steelworks Component Supply Co.", 10000, 8, 0, 0, 8, 0.05, 14.2, "NORMAL", "2026-10-30T14:40:00Z", "STABLE"),
                ("VND-B", "Precision Fasteners & Shims Pvt.", 3200, 1, 0, 1, 0, 0.10, 22.5, "NORMAL", "2026-10-25T11:20:00Z", "STABLE")
            ]
            cursor.executemany("""
                INSERT INTO vendors (vendor_id, vendor_name, total_units_shipped, total_incidents, 
                                     structural_incidents, wrong_component_incidents, surface_incidents, 
                                     batch_recurrence_rate, normalized_risk_score, inspection_regime, 
                                     last_incident_date, risk_trend)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, vendors_seed)

        # Check if batches exist
        cursor.execute("SELECT COUNT(*) FROM batches")
        if cursor.fetchone()[0] == 0:
            batches_seed = [
                ("B-038", "M8 Stamped Chassis Mount", "CH-8802", "CELL-01", "SHIFT-A", "OP-04", "VND-X", 500, 500, 1, "RELEASED", "MSA-2026-09", 28.50, 4.20, 36.50),
                ("B-040", "M8 Black Oxide Flange Bolt", "M8-9890", "CELL-02", "SHIFT-A", "OP-11", "VND-X", 500, 500, 1, "RELEASED", "MSA-2026-09", 28.50, 4.20, 36.50),
                ("B-042", "M8 Black Oxide Flange Bolt", "M8-9941", "CELL-03", "SHIFT-B", "OP-19", "VND-X", 500, 112, 1, "IN_PRODUCTION", "MSA-2026-09", 28.50, 4.20, 36.50),
                ("B-043", "M8 Black Oxide Flange Bolt", "M8-9955", "CELL-03", "SHIFT-C", "OP-22", "VND-X", 500, 0, 0, "QUEUED", "MSA-2026-09", 28.50, 4.20, 36.50)
            ]
            cursor.executemany("""
                INSERT INTO batches (batch_id, component_name, component_lot, workstation_id, shift_id, 
                                     operator_id, vendor_id, total_units, inspected_units, defective_units, 
                                     status, sla_contract_id, unit_cost, rework_cost, recall_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batches_seed)

        # Seed Genesis Block in provenance chain if empty
        cursor.execute("SELECT COUNT(*) FROM provenance_chain")
        if cursor.fetchone()[0] == 0:
            genesis_curr = "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
            cursor.execute("""
                INSERT INTO provenance_chain (block_index, incident_id, timestamp_iso, camera_id, 
                                              frame_sha256, metadata_json, prev_hash, curr_hash)
                VALUES (0, 'GENESIS', '2026-10-31T00:00:00.000Z', 'SYS-ROOT', '0'*64, '{"init": "INDUS-X ROOT ANCHOR"}', '0'*64, ?)
            """, (genesis_curr,))
            
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized & seeded successfully.")
