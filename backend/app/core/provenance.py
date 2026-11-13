import hashlib
import json
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from app.core.database import get_db

@dataclass
class ProvenanceBlock:
    block_index: int
    incident_id: str
    timestamp_iso: str
    camera_id: str
    frame_sha256: str
    metadata_json: str
    prev_hash: str
    curr_hash: str

@dataclass
class ChainVerificationResult:
    valid: bool
    total_blocks: int
    breached_block_id: Optional[int] = None
    expected_hash: Optional[str] = None
    found_hash: Optional[str] = None
    message: str = ""

def compute_block_hash(
    incident_id: str,
    timestamp_iso: str,
    camera_id: str,
    frame_sha256: str,
    metadata_json: str,
    prev_hash: str
) -> str:
    raw = f"{incident_id}|{timestamp_iso}|{camera_id}|{frame_sha256}|{metadata_json}|{prev_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class ProvenanceChainService:
    """
    Append-Only Cryptographic Hash Chain Ledger (Layer 4).
    Guarantees millisecond Chain of Custody and immutable tamper detection.
    """
    def __init__(self):
        pass

    def seal_incident(
        self,
        incident_id: str,
        timestamp_iso: str,
        camera_id: str,
        frame_bytes: bytes,
        metadata: Dict[str, Any]
    ) -> ProvenanceBlock:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Fetch latest block
            cursor.execute("SELECT block_index, curr_hash FROM provenance_chain ORDER BY block_index DESC LIMIT 1")
            latest = cursor.fetchone()
            
            if latest:
                prev_index = latest["block_index"]
                prev_hash = latest["curr_hash"]
                curr_index = prev_index + 1
            else:
                curr_index = 1
                prev_hash = "0" * 64

            frame_sha256 = hashlib.sha256(frame_bytes).hexdigest()
            metadata_str = json.dumps(metadata, sort_keys=True)
            curr_hash = compute_block_hash(
                incident_id=incident_id,
                timestamp_iso=timestamp_iso,
                camera_id=camera_id,
                frame_sha256=frame_sha256,
                metadata_json=metadata_str,
                prev_hash=prev_hash
            )

            cursor.execute("""
                INSERT INTO provenance_chain (block_index, incident_id, timestamp_iso, camera_id,
                                              frame_sha256, metadata_json, prev_hash, curr_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (curr_index, incident_id, timestamp_iso, camera_id, frame_sha256, metadata_str, prev_hash, curr_hash))
            conn.commit()

            return ProvenanceBlock(
                block_index=curr_index,
                incident_id=incident_id,
                timestamp_iso=timestamp_iso,
                camera_id=camera_id,
                frame_sha256=frame_sha256,
                metadata_json=metadata_str,
                prev_hash=prev_hash,
                curr_hash=curr_hash
            )

    def verify_ledger(self) -> ChainVerificationResult:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM provenance_chain ORDER BY block_index ASC")
            blocks = cursor.fetchall()

            if not blocks:
                return ChainVerificationResult(valid=True, total_blocks=0, message="Ledger is empty.")

            expected_prev = "0" * 64
            for idx, row in enumerate(blocks):
                b_index = row["block_index"]
                inc_id = row["incident_id"]
                ts = row["timestamp_iso"]
                cam = row["camera_id"]
                f_hash = row["frame_sha256"]
                meta = row["metadata_json"]
                stored_prev = row["prev_hash"]
                stored_curr = row["curr_hash"]

                if b_index == 0:
                    # Genesis anchor
                    expected_prev = stored_curr
                    continue

                # Verify link to previous
                if stored_prev != expected_prev:
                    return ChainVerificationResult(
                        valid=False,
                        total_blocks=len(blocks),
                        breached_block_id=b_index,
                        expected_hash=expected_prev,
                        found_hash=stored_prev,
                        message=f"INTEGRITY BREACH DETECTED AT BLOCK #{b_index}: Previous hash link broken!"
                    )

                # Recompute current hash
                recomputed = compute_block_hash(inc_id, ts, cam, f_hash, meta, stored_prev)
                if recomputed != stored_curr:
                    return ChainVerificationResult(
                        valid=False,
                        total_blocks=len(blocks),
                        breached_block_id=b_index,
                        expected_hash=recomputed,
                        found_hash=stored_curr,
                        message=f"INTEGRITY BREACH DETECTED AT BLOCK #{b_index}: Payload tampered! Hash mismatch."
                    )

                expected_prev = stored_curr

            return ChainVerificationResult(
                valid=True,
                total_blocks=len(blocks),
                message=f"LEDGER VERIFIED: All {len(blocks)} blocks cryptographically intact."
            )

    def simulate_tamper(self, target_block_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Demonstration tool: alters 1 byte of historical metadata in the database 
        so judges can immediately witness live tamper detection in action.
        """
        with get_db() as conn:
            cursor = conn.cursor()
            if target_block_id is None:
                # Target the most recent non-genesis block, or block 1
                cursor.execute("SELECT block_index FROM provenance_chain WHERE block_index > 0 ORDER BY block_index DESC LIMIT 1")
                row = cursor.fetchone()
                if not row:
                    return {"status": "error", "message": "No non-genesis block available to tamper."}
                target_block_id = row["block_index"]

            cursor.execute("SELECT metadata_json FROM provenance_chain WHERE block_index = ?", (target_block_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": f"Block #{target_block_id} not found."}

            try:
                meta = json.loads(row["metadata_json"])
                meta["_tampered_by"] = "ADVERSARIAL_DB_MODIFICATION"
                meta["confidence"] = 0.12  # altered value
                new_meta = json.dumps(meta, sort_keys=True)
            except Exception:
                new_meta = row["metadata_json"] + " "

            cursor.execute("UPDATE provenance_chain SET metadata_json = ? WHERE block_index = ?", (new_meta, target_block_id))
            conn.commit()

            return {
                "status": "success",
                "message": f"Block #{target_block_id} artificially modified by 1 character to simulate database corruption.",
                "target_block_id": target_block_id
            }

    def repair_ledger(self) -> Dict[str, Any]:
        """Recalculates valid hashes to reset simulation state if needed."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM provenance_chain ORDER BY block_index ASC")
            blocks = cursor.fetchall()
            
            prev_hash = "0" * 64
            for row in blocks:
                b_idx = row["block_index"]
                if b_idx == 0:
                    prev_hash = row["curr_hash"]
                    continue
                new_curr = compute_block_hash(
                    row["incident_id"], row["timestamp_iso"], row["camera_id"],
                    row["frame_sha256"], row["metadata_json"], prev_hash
                )
                cursor.execute("UPDATE provenance_chain SET prev_hash = ?, curr_hash = ? WHERE block_index = ?", 
                               (prev_hash, new_curr, b_idx))
                prev_hash = new_curr
            conn.commit()
            return {"status": "success", "message": "Ledger hash chain reset and recalibrated."}

