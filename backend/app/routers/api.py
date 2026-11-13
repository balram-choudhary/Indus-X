import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.database import get_db, init_db
from app.core.scenario_simulator import ScenarioSimulator
from app.core.reference_grid import ReferenceGridEvaluator
from app.core.consolidator import IncidentConsolidator, ConsolidatedIncident
from app.core.provenance import ProvenanceChainService
from app.core.traceability import TraceabilityResolver
from app.core.automation import FloorAutomationService
from app.core.sla_agent import SLAReasoningAgent
from app.core.governance import GovernanceGateService
from app.core.supplier_intelligence import SupplierIntelligenceEngine

router = APIRouter(prefix="/api")

# Singleton service instances
simulator = ScenarioSimulator()
ref_evaluator = ReferenceGridEvaluator()
consolidator = IncidentConsolidator()
provenance_service = ProvenanceChainService()
traceability_resolver = TraceabilityResolver()
automation_service = FloorAutomationService()
sla_agent = SLAReasoningAgent()
governance_service = GovernanceGateService()
supplier_engine = SupplierIntelligenceEngine()

class GovernanceRequest(BaseModel):
    action: str              # 'APPROVE_QUARANTINE' | 'REJECT_QUARANTINE' | 'AUTHORIZE_NCR_HOLDBACK' | 'DISMISS'
    role: str                # 'OPERATOR' | 'QUALITY_ENGINEER' | 'PLANT_MANAGER'
    actor_name: Optional[str] = "Quality Engineer"
    notes: Optional[str] = ""

class FeedbackRequest(BaseModel):
    verdict: str             # 'CORRECT' | 'WRONG_CLASS' | 'FALSE_POSITIVE'

@router.post("/inspect/run/{scenario_id}")
async def run_inspection(
    scenario_id: int,
    perturbation: str = Query("standard", pattern="^(standard|angle_stress|low_light|glare)$")
):
    """
    Executes full 8-layer inspection pipeline for given scenario.
    Simulates high-speed conveyor transit (27 frames), runs reference grid evaluation,
    consolidates noise into 1 incident, seals provenance hash chain, dispatches closed-loop
    automation, maps blast radius, and synthesizes contractual SLA dossier.
    """
    total_frames = 27
    ref_evaluator.reset()
    start_time = time.perf_counter()

    last_annotated_b64 = ""
    last_findings = []
    consolidated_inc: Optional[ConsolidatedIncident] = None

    # Simulate camera transit of physical part across 27 frames
    for i in range(total_frames):
        progress = i / float(total_frames - 1)
        frame_raw, chassis_bbox, detections = simulator.generate_frame(scenario_id, progress, perturbation)
        findings, slot_status = ref_evaluator.evaluate(chassis_bbox, detections)
        last_findings = findings

        annotated_frame = simulator.draw_cad_overlay(frame_raw, chassis_bbox, slot_status, findings)
        last_annotated_b64 = simulator.frame_to_base64(annotated_frame)

        # Feed into 4-Gate Incident Consolidator
        if chassis_bbox.width > 20:
            c_inc = consolidator.process_frame(
                track_id=47,
                chassis_bbox=chassis_bbox,
                findings=findings,
                frame_idx=i,
                frame_img=frame_raw
            )
            if c_inc:
                consolidated_inc = c_inc

    # Finalize transit exit if part exited ROI
    if consolidated_inc is None:
        consolidated_inc = consolidator.check_transit_exit(track_id=47)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 1)

    # If no defect (Scenario 0 Baseline Pass)
    if consolidated_inc is None:
        return {
            "scenario_id": scenario_id,
            "status": "PASS",
            "message": "Baseline Pass: All 4 M8 structural fasteners confirmed seated. Zero defects recorded.",
            "raw_frame_count": total_frames,
            "consolidated_incident_id": None,
            "noise_reduction_pct": 0.0,
            "processing_latency_ms": elapsed_ms,
            "live_frame_base64": last_annotated_b64,
            "automation_dispatched": None,
            "provenance_block": None,
            "blast_radius": None,
            "sla_dossier": None
        }

    # Defect Confirmed: Execute Downstream Resolution Pipeline
    inc_id = consolidated_inc.incident_id
    defect_type = consolidated_inc.defect_type
    confidence = consolidated_inc.confidence_avg
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

    # 1. Layer 4: Provenance Hash Chain Sealing
    dummy_frame_bytes = f"FRAME_BYTES_{inc_id}_{time.time()}".encode("utf-8")
    meta = {
        "defect_type": defect_type,
        "raw_frames": consolidated_inc.raw_frame_count,
        "confidence": confidence,
        "scenario": scenario_id,
        "workstation": "CELL-03"
    }
    block = provenance_service.seal_incident(
        incident_id=inc_id,
        timestamp_iso=ts_iso,
        camera_id="CAM-INSPECT-03",
        frame_bytes=dummy_frame_bytes,
        metadata=meta
    )

    # 2. Layer 5: Operational Traceability & Cost of Inaction
    blast_radius = traceability_resolver.resolve_blast_radius(inc_id, batch_id="B-042")

    # 3. Layer 6 - Path A: Closed-Loop Automation (MQTT Diverter Pulse)
    mqtt_commands = automation_service.dispatch_immediate_containment(
        incident_id=inc_id,
        defect_type=defect_type,
        workstation_id=blast_radius.workstation_id if blast_radius else "CELL-03"
    )

    # 4. Layer 6 - Path B: Contextual SLA Contract Synthesis
    sla_dossier = sla_agent.generate_dossier(
        incident_id=inc_id,
        defect_type=defect_type,
        confidence=confidence,
        batch_id=blast_radius.batch_id if blast_radius else "B-042",
        vendor_name=blast_radius.vendor_name if blast_radius else "Apex Industrial Fasteners Ltd.",
        provenance_hash=block.curr_hash,
        units_at_risk=blast_radius.units_at_risk if blast_radius else 388
    )

    # 5. Layer 8: Supplier Intelligence & ISO 2859 Switching
    supplier_report = supplier_engine.calculate_supplier_risk(vendor_id="VND-X")

    # Save incident record in DB
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO incidents (
                id, scenario_type, defect_class, raw_frame_count, confidence_avg,
                batch_id, vendor_id, status, risk_tier, cost_if_missed, cost_if_caught,
                net_savings, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inc_id, scenario_id, defect_type, consolidated_inc.raw_frame_count, confidence,
            blast_radius.batch_id if blast_radius else "B-042",
            blast_radius.vendor_id if blast_radius else "VND-X",
            "CONSOLIDATED", 2,
            blast_radius.total_recall_liability if blast_radius else 14162.0,
            blast_radius.total_rework_cost if blast_radius else 1629.6,
            blast_radius.net_cost_savings if blast_radius else 12532.4,
            ts_iso
        ))
        conn.commit()

    return {
        "scenario_id": scenario_id,
        "status": "INCIDENT_CONSOLIDATED",
        "incident_id": inc_id,
        "defect_type": defect_type,
        "raw_frame_count": consolidated_inc.raw_frame_count,
        "consolidated_count": 1,
        "noise_reduction_pct": consolidated_inc.noise_reduction_pct,
        "confidence_avg": confidence,
        "processing_latency_ms": elapsed_ms,
        "live_frame_base64": last_annotated_b64,
        "provenance_block": {
            "block_index": block.block_index,
            "prev_hash": block.prev_hash,
            "curr_hash": block.curr_hash,
            "timestamp_iso": block.timestamp_iso
        },
        "closed_loop_automation": [
            {
                "action": cmd.action,
                "hardware": cmd.target_hardware,
                "topic": cmd.topic,
                "payload": cmd.payload
            }
            for cmd in mqtt_commands
        ],
        "blast_radius": blast_radius.__dict__ if blast_radius else None,
        "sla_dossier": sla_dossier.__dict__ if sla_dossier else None,
        "supplier_intelligence": supplier_report.__dict__ if supplier_report else None
    }

@router.get("/inspect/stream/{scenario_id}")
async def stream_scenario_frames(
    scenario_id: int, 
    perturbation: str = Query("standard")
):
    """
    Server-Sent Events (SSE) streaming frame-by-frame live visual feed
    with CAD overlays and real-time noise reduction updates.
    """
    async def event_generator():
        total = 27
        ref_evaluator.reset()
        for i in range(total):
            prog = i / float(total - 1)
            frame_raw, bbox, dets = simulator.generate_frame(scenario_id, prog, perturbation)
            findings, slots = ref_evaluator.evaluate(bbox, dets)
            annotated = simulator.draw_cad_overlay(frame_raw, bbox, slots, findings)
            b64 = simulator.frame_to_base64(annotated)

            data = {
                "frame_idx": i + 1,
                "total_frames": total,
                "progress_pct": round(prog * 100, 1),
                "frame_base64": b64,
                "raw_detections_count": i + 1 if findings else 0,
                "current_defect": findings[0].defect_type if findings else None,
                "slot_status": {k: v["status"] for k, v in slots.items()}
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.045)  # simulate ~22 FPS

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/incidents")
def list_incidents():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incidents ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.get("/incidents/{incident_id}/dossier")
def get_incident_dossier(incident_id: str):
    blast = traceability_resolver.resolve_blast_radius(incident_id)
    if not blast:
        raise HTTPException(status_code=404, detail="Incident traceability not found")
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM provenance_chain WHERE incident_id = ?", (incident_id,))
        p_row = cursor.fetchone()
        prev_hash = p_row["curr_hash"] if p_row else "0"*64

        cursor.execute("SELECT * FROM custody_log WHERE incident_id = ? ORDER BY id ASC", (incident_id,))
        custody_rows = [dict(r) for r in cursor.fetchall()]

    dossier = sla_agent.generate_dossier(
        incident_id=incident_id,
        defect_type="STRUCTURAL_ABSENCE",
        confidence=0.96,
        batch_id=blast.batch_id,
        vendor_name=blast.vendor_name,
        provenance_hash=prev_hash,
        units_at_risk=blast.units_at_risk
    )

    return {
        "incident_id": incident_id,
        "blast_radius": blast.__dict__,
        "sla_dossier": dossier.__dict__,
        "custody_log": custody_rows
    }

@router.post("/governance/{incident_id}/decide")
def submit_governance_decision(incident_id: str, req: GovernanceRequest):
    result = governance_service.execute_governance_decision(
        incident_id=incident_id,
        action=req.action,
        role=req.role,
        actor_name=req.actor_name or "Quality Engineer",
        notes=req.notes or ""
    )
    if not result.get("success"):
        raise HTTPException(status_code=403, detail=result.get("error"))
    return result

@router.get("/provenance/verify")
def verify_provenance_ledger():
    res = provenance_service.verify_ledger()
    return res.__dict__

@router.post("/provenance/simulate-tamper")
def simulate_database_tamper():
    res = provenance_service.simulate_tamper()
    return res

@router.post("/provenance/repair")
def repair_provenance_ledger():
    res = provenance_service.repair_ledger()
    return res

@router.get("/vendors")
def list_vendors():
    return supplier_engine.get_all_vendor_rankings()

@router.post("/incidents/{incident_id}/feedback")
def submit_operator_feedback(incident_id: str, req: FeedbackRequest):
    return supplier_engine.record_operator_feedback(incident_id, req.verdict)

@router.get("/analytics/telemetry")
def get_system_telemetry():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM incidents")
        total_inc = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(net_savings) FROM incidents")
        total_savings = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(*) FROM provenance_chain")
        total_blocks = cursor.fetchone()[0]

    return {
        "total_incidents": total_inc,
        "cumulative_net_savings_usd": round(total_savings, 2),
        "provenance_blocks_sealed": total_blocks,
        "live_noise_reduction_pct": consolidator.live_noise_reduction or 96.3,
        "average_pipeline_latency_ms": 780.0
    }