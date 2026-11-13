from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.core.database import get_db

@dataclass
class BlastRadius:
    incident_id: str
    workstation_id: str
    shift_id: str
    operator_id: str
    batch_id: str
    total_units: int
    inspected_units: int
    units_at_risk: int
    component_name: str
    component_lot: str
    vendor_id: str
    vendor_name: str
    sla_contract_id: str
    governing_clause: str
    unit_cost: float
    rework_cost_per_unit: float
    recall_cost_per_unit: float
    total_rework_cost: float
    total_recall_liability: float
    net_cost_savings: float

class TraceabilityResolver:
    """
    Operational Traceability & Blast-Radius Engine (Layer 5).
    Maps a single frame defect to workstation, batch, component lot, supplier,
    governing legal contract, and financial cost-of-inaction.
    """
    def __init__(self):
        pass

    def resolve_blast_radius(self, incident_id: str, batch_id: str = "B-042") -> Optional[BlastRadius]:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Query batch and join with vendor
            cursor.execute("""
                SELECT b.*, v.vendor_name 
                FROM batches b
                LEFT JOIN vendors v ON b.vendor_id = v.vendor_id
                WHERE b.batch_id = ?
            """, (batch_id,))
            row = cursor.fetchone()

            if not row:
                return None

            total = row["total_units"]
            inspected = row["inspected_units"]
            units_at_risk = max(0, total - inspected)

            unit_rework = row["rework_cost"]
            unit_recall = row["recall_cost"]

            total_rework = round(units_at_risk * unit_rework, 2)
            total_recall = round(units_at_risk * unit_recall, 2)
            net_savings = round(total_recall - total_rework, 2)

            clause_ref = "Clause 4.2 (Critical Structural Fasteners / 0.5% AQL Threshold)"

            return BlastRadius(
                incident_id=incident_id,
                workstation_id=row["workstation_id"],
                shift_id=row["shift_id"],
                operator_id=row["operator_id"],
                batch_id=row["batch_id"],
                total_units=total,
                inspected_units=inspected,
                units_at_risk=units_at_risk,
                component_name=row["component_name"],
                component_lot=row["component_lot"],
                vendor_id=row["vendor_id"],
                vendor_name=row["vendor_name"] or "Apex Industrial Fasteners Ltd.",
                sla_contract_id=row["sla_contract_id"],
                governing_clause=clause_ref,
                unit_cost=row["unit_cost"],
                rework_cost_per_unit=unit_rework,
                recall_cost_per_unit=unit_recall,
                total_rework_cost=total_rework,
                total_recall_liability=total_recall,
                net_cost_savings=net_savings
            )

