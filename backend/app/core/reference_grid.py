import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from app.core.perception import Detection, BBox

@dataclass
class DefectFinding:
    defect_type: str        # 'STRUCTURAL_ABSENCE' | 'WRONG_COMPONENT' | 'SURFACE_ANOMALY'
    slot_id: Optional[str]  # 'A', 'B', 'C', 'D'
    confidence: float
    observed_class: Optional[str]
    expected_class: Optional[str]
    bbox: Optional[BBox]
    description: str

class ReferenceGridEvaluator:
    """
    Solves the 'detecting absence' paradox by projecting CAD/BOM tolerance coordinates
    onto the detected chassis fiducial boundary and computing geometric spatial presence.
    """
    def __init__(
        self,
        expected_grid: Optional[Dict[str, Tuple[float, float]]] = None,
        expected_classes: Optional[Dict[str, str]] = None,
        match_radius_ratio: float = 0.16,
        absence_frame_threshold: int = 5
    ):
        # Normalized coordinates relative to chassis boundary (x_ratio, y_ratio)
        self.expected_grid = expected_grid or {
            "A": (0.24, 0.28),
            "B": (0.76, 0.28),
            "C": (0.24, 0.72),
            "D": (0.76, 0.72),
        }
        self.expected_classes = expected_classes or {
            "A": "m8_flange_bolt",
            "B": "m8_flange_bolt",
            "C": "m8_flange_bolt",
            "D": "m8_flange_bolt",
        }
        self.match_radius_ratio = match_radius_ratio
        self.absence_frame_threshold = absence_frame_threshold
        self.absence_counters: Dict[str, int] = {k: 0 for k in self.expected_grid}

    def reset(self):
        for k in self.absence_counters:
            self.absence_counters[k] = 0

    def evaluate(
        self, 
        chassis_bbox: BBox, 
        detections: List[Detection]
    ) -> Tuple[List[DefectFinding], Dict[str, Dict]]:
        """
        Projects reference grid onto chassis bounding box and evaluates 4 slots + surface.
        Returns (defect_findings, slot_status_map).
        """
        findings: List[DefectFinding] = []
        slot_status: Dict[str, Dict] = {}

        cw = chassis_bbox.width
        ch = chassis_bbox.height
        cx1 = chassis_bbox.x1
        cy1 = chassis_bbox.y1

        # Check each expected bolt slot
        for slot_id, (norm_x, norm_y) in self.expected_grid.items():
            expected_px_x = cx1 + (norm_x * cw)
            expected_px_y = cy1 + (norm_y * ch)
            expected_cls = self.expected_classes[slot_id]

            # Search for observed detection matching this slot centroid
            matched_det: Optional[Detection] = None
            min_dist = float("inf")

            for det in detections:
                if det.label == "chassis":
                    continue
                dcx, dcy = det.bbox.centroid
                dist = math.hypot(dcx - expected_px_x, dcy - expected_px_y)
                radius_thresh = self.match_radius_ratio * math.hypot(cw, ch)

                if dist < radius_thresh and dist < min_dist:
                    min_dist = dist
                    matched_det = det

            if matched_det is None:
                self.absence_counters[slot_id] += 1
                is_confirmed_absence = self.absence_counters[slot_id] >= self.absence_frame_threshold
                
                slot_status[slot_id] = {
                    "status": "ABSENT" if is_confirmed_absence else "POTENTIAL_ABSENT",
                    "observed": None,
                    "expected": expected_cls,
                    "px_coord": (expected_px_x, expected_px_y),
                    "consecutive_misses": self.absence_counters[slot_id]
                }

                if is_confirmed_absence:
                    findings.append(DefectFinding(
                        defect_type="STRUCTURAL_ABSENCE",
                        slot_id=slot_id,
                        confidence=0.98,
                        observed_class=None,
                        expected_class=expected_cls,
                        bbox=BBox(expected_px_x - 18, expected_px_y - 18, expected_px_x + 18, expected_px_y + 18),
                        description=f"Slot {slot_id}: Expected {expected_cls} absent for {self.absence_counters[slot_id]} consecutive frames (CAD reference violated)."
                    ))
            else:
                self.absence_counters[slot_id] = 0
                observed_label = matched_det.label

                # Check Class Mismatch (e.g. brass nut instead of black-oxide flange bolt)
                if observed_label != expected_cls:
                    slot_status[slot_id] = {
                        "status": "WRONG_COMPONENT",
                        "observed": observed_label,
                        "expected": expected_cls,
                        "px_coord": (expected_px_x, expected_px_y),
                        "confidence": matched_det.confidence
                    }
                    findings.append(DefectFinding(
                        defect_type="WRONG_COMPONENT",
                        slot_id=slot_id,
                        confidence=matched_det.confidence,
                        observed_class=observed_label,
                        expected_class=expected_cls,
                        bbox=matched_det.bbox,
                        description=f"Slot {slot_id}: Class mismatch! Observed {observed_label} but CAD specification requires {expected_cls}."
                    ))
                else:
                    slot_status[slot_id] = {
                        "status": "PASS",
                        "observed": observed_label,
                        "expected": expected_cls,
                        "px_coord": (expected_px_x, expected_px_y),
                        "confidence": matched_det.confidence
                    }

        # Check Surface Anomalies (cracks, scratches, dents within chassis zone)
        for det in detections:
            if det.label in ("surface_crack", "scratch", "fracture", "stamping_crack"):
                findings.append(DefectFinding(
                    defect_type="SURFACE_ANOMALY",
                    slot_id=None,
                    confidence=det.confidence,
                    observed_class=det.label,
                    expected_class="intact_surface",
                    bbox=det.bbox,
                    description=f"Material Surface Degradation detected ({det.label}) with confidence {det.confidence:.2f}."
                ))

        return findings, slot_status

