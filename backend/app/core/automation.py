import json
import time
from dataclasses import dataclass
from typing import Dict, List, Any
from app.core.database import get_db

@dataclass
class MQTTCommand:
    topic: str
    action: str
    target_hardware: str
    payload: Dict[str, Any]
    risk_tier: int
    timestamp_iso: str
    status: str = "DISPATCHED"

class FloorAutomationService:
    """
    Closed-Loop Industrial Automation Controller (Layer 6 - Path A).
    Simulates standard industrial control protocols (MQTT / OPC-UA / Siemens S7 payloads)
    for immediate deterministic containment without human lag.
    """
    def __init__(self):
        self.dispatched_commands: List[MQTTCommand] = []

    def dispatch_immediate_containment(
        self, 
        incident_id: str, 
        defect_type: str, 
        workstation_id: str = "CELL-03"
    ) -> List[MQTTCommand]:
        ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        commands: List[MQTTCommand] = []

        # 1. Pneumatic Diverter Arm (Always fire: Eject single defective unit to rework spur)
        diverter_cmd = MQTTCommand(
            topic=f"factory/{workstation_id.lower()}/actuators/diverter_03",
            action="PULSE_EJECT",
            target_hardware="Pneumatic Diverter Arm #03 (Festo DSBC-32)",
            payload={
                "command": "ACTUATOR_PULSE",
                "incident_id": incident_id,
                "deflection_duration_ms": 350,
                "destination_spur": "REWORK_TRAY_A",
                "timestamp": ts
            },
            risk_tier=1,
            timestamp_iso=ts
        )
        commands.append(diverter_cmd)

        # 2. Check if Line Throttle is needed (if multi-incident frequency detected)
        conveyor_cmd = MQTTCommand(
            topic="factory/main_line/conveyor/drive_vfd",
            action="SPEED_NOMINAL",
            target_hardware="Main Line Conveyor Inverter (Siemens Micromaster 440)",
            payload={
                "command": "SPEED_STATUS",
                "velocity_m_s": 1.2,
                "status": "NOMINAL_MONITORING"
            },
            risk_tier=1,
            timestamp_iso=ts
        )
        commands.append(conveyor_cmd)

        # 3. CNC / Tool Offset Maintenance Calibration Flag
        if defect_type in ("STRUCTURAL_ABSENCE", "WRONG_COMPONENT"):
            tool_cmd = MQTTCommand(
                topic=f"factory/{workstation_id.lower()}/toolhead/calibration",
                action="FLAG_CALIBRATION",
                target_hardware="Automated Multi-Spindle Screwdriver Head Station-03",
                payload={
                    "command": "SCHEDULE_HEAD_CHECK",
                    "reason": f"Defect pattern {defect_type} recorded at Slot C",
                    "inspection_priority": "NEXT_SHIFT_CHANGEOVER"
                },
                risk_tier=1,
                timestamp_iso=ts
            )
            commands.append(tool_cmd)

        # Record to Chain of Custody & audit log
        self._log_containment_execution(incident_id, commands)
        self.dispatched_commands.extend(commands)
        return commands

    def _log_containment_execution(self, incident_id: str, commands: List[MQTTCommand]):
        with get_db() as conn:
            cursor = conn.cursor()
            for cmd in commands:
                cursor.execute("""
                    INSERT INTO custody_log (incident_id, timestamp_iso, state_from, state_to,
                                             action, actor, actor_role, notes, mqtt_payload)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident_id,
                    cmd.timestamp_iso,
                    "CONSOLIDATED",
                    "CONTAINED_PHYSICAL",
                    cmd.action,
                    "SYSTEM_AUTO_PLC",
                    "SYSTEM",
                    f"Dispatched closed-loop containment to {cmd.target_hardware}",
                    json.dumps(cmd.payload)
                ))
            conn.commit()

