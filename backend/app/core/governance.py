import time
from typing import Dict, Any, Optional
from app.core.database import get_db

ROLES = {
    "OPERATOR": {"level": 1, "label": "Station Line Operator"},
    "QUALITY_ENGINEER": {"level": 2, "label": "Certified Quality Engineer (QE)"},
    "PLANT_MANAGER": {"level": 3, "label": "Plant Operations / Finance Director"}
}

class GovernanceGateService:
    """
    Risk-Aware Governance & Role-Based Human Gate (RBAC - Layer 7).
    Enforces the core rule: 'Autonomous where safe. Human-controlled where consequential.'
    """
    def __init__(self):
        pass

    def evaluate_authorization(self, action_tier: int, role: str) -> bool:
        user_role = role.upper()
        if user_role not in ROLES:
            return False
        return ROLES[user_role]["level"] >= action_tier

    def execute_governance_decision(
        self,
        incident_id: str,
        action: str,          # 'APPROVE_QUARANTINE' | 'REJECT_QUARANTINE' | 'AUTHORIZE_NCR_HOLDBACK' | 'DISMISS'
        role: str,
        actor_name: str = "Authorized Personnel",
        notes: str = ""
    ) -> Dict[str, Any]:
        user_role = role.upper()
        ts = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

        # Determine required tier
        if action in ("APPROVE_QUARANTINE", "REJECT_QUARANTINE"):
            required_tier = 2  # Quality Engineer+
            target_status = "QUARANTINED" if action == "APPROVE_QUARANTINE" else "RELEASED_OVERRIDE"
        elif action in ("AUTHORIZE_NCR_HOLDBACK", "REJECT_HOLDBACK"):
            required_tier = 3  # Plant Manager+
            target_status = "NCR_ISSUED" if action == "AUTHORIZE_NCR_HOLDBACK" else "QUARANTINED"
        else:
            required_tier = 1
            target_status = "CLOSED"

        if not self.evaluate_authorization(required_tier, user_role):
            return {
                "success": False,
                "error": f"Access Denied: Action '{action}' requires Role Tier {required_tier} ({list(ROLES.keys())[required_tier-1]}). Current role: {user_role}."
            }

        with get_db() as conn:
            cursor = conn.cursor()
            
            # Fetch current incident status
            cursor.execute("SELECT status, batch_id, vendor_id FROM incidents WHERE id = ?", (incident_id,))
            inc = cursor.fetchone()
            if not inc:
                return {"success": False, "error": f"Incident {incident_id} not found."}

            old_status = inc["status"]
            batch_id = inc["batch_id"] or "B-042"

            # Update Incident
            cursor.execute("""
                UPDATE incidents 
                SET status = ?, resolved_at = ?, resolved_by = ?
                WHERE id = ?
            """, (target_status, ts, f"{actor_name} ({user_role})", incident_id))

            # If Batch quarantine approved, update batch status
            if action == "APPROVE_QUARANTINE":
                cursor.execute("UPDATE batches SET status = 'QUARANTINED' WHERE batch_id = ?", (batch_id,))

            # Append to immutable Chain of Custody log
            cursor.execute("""
                INSERT INTO custody_log (incident_id, timestamp_iso, state_from, state_to,
                                         action, actor, actor_role, notes, mqtt_payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                incident_id,
                ts,
                old_status,
                target_status,
                action,
                actor_name,
                user_role,
                notes or f"Human Gate Action executed by {user_role}: {action}",
                None
            ))

            conn.commit()

        return {
            "success": True,
            "incident_id": incident_id,
            "old_status": old_status,
            "new_status": target_status,
            "authorized_by": f"{actor_name} ({user_role})",
            "timestamp": ts,
            "message": f"Governance Action '{action}' executed and signed into Chain of Custody."
        }

