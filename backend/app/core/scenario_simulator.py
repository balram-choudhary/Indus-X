import math
import time
import base64
import numpy as np
import cv2
from typing import Dict, List, Tuple, Generator, Optional, Any
from app.core.perception import BBox, Detection
from app.core.reference_grid import ReferenceGridEvaluator

class ScenarioSimulator:
    """
    Edge Replay & Controlled Simulation Test Bench (Layer 1).
    Generates realistic industrial chassis inspection streams for Scenarios 0, 1, 2, 3
    with controlled physical perturbations (angle shift, low-lux, glare)
    and renders real-time visual CAD overlays.
    """
    WIDTH = 640
    HEIGHT = 480

    SCENARIOS = {
        0: {
            "name": "Scenario 0: Baseline Pass",
            "desc": "Standard assembly: All 4 M8 flange bolts seated; pristine surface finish.",
            "slots": {"A": "m8_flange_bolt", "B": "m8_flange_bolt", "C": "m8_flange_bolt", "D": "m8_flange_bolt"},
            "has_crack": False
        },
        1: {
            "name": "Scenario 1: Structural Absence",
            "desc": "Defective assembly: Bolt C MISSING at coordinate (x3, y3). Tests CAD reference grid absence logic.",
            "slots": {"A": "m8_flange_bolt", "B": "m8_flange_bolt", "C": None, "D": "m8_flange_bolt"},
            "has_crack": False
        },
        2: {
            "name": "Scenario 2: Wrong Component / Material",
            "desc": "Defective assembly: Uncoated Brass Nut installed at Slot C instead of Black-Oxide M8 flange bolt.",
            "slots": {"A": "m8_flange_bolt", "B": "m8_flange_bolt", "C": "brass_nut", "D": "m8_flange_bolt"},
            "has_crack": False
        },
        3: {
            "name": "Scenario 3: Surface Degradation",
            "desc": "Defective assembly: Hairline stamping stress crack across chassis plate center.",
            "slots": {"A": "m8_flange_bolt", "B": "m8_flange_bolt", "C": "m8_flange_bolt", "D": "m8_flange_bolt"},
            "has_crack": True
        }
    }

    def __init__(self):
        self.ref_evaluator = ReferenceGridEvaluator()

    def generate_frame(
        self,
        scenario_id: int,
        progress: float,          # 0.0 to 1.0 (part transiting left to right)
        perturbation: str = "standard"  # 'standard' | 'angle_stress' | 'low_light' | 'glare'
    ) -> Tuple[np.ndarray, BBox, List[Detection]]:
        """
        Synthesizes a high-fidelity visual industrial frame with moving conveyor,
        chassis plate, fastener fixtures, and any defects.
        """
        cfg = self.SCENARIOS.get(scenario_id, self.SCENARIOS[0])

        # 1. Base Conveyor Background (Dark Industrial Rubber)
        frame = np.full((self.HEIGHT, self.WIDTH, 3), (28, 30, 34), dtype=np.uint8)
        
        # Conveyor belt track markings
        cv2.line(frame, (0, 70), (self.WIDTH, 70), (45, 48, 55), 2)
        cv2.line(frame, (0, self.HEIGHT - 70), (self.WIDTH, self.HEIGHT - 70), (45, 48, 55), 2)
        
        # Conveyor roller slats moving
        slat_offset = int((progress * 300) % 40)
        for x in range(-40 + slat_offset, self.WIDTH + 40, 40):
            cv2.line(frame, (x, 70), (x, self.HEIGHT - 70), (36, 38, 44), 1)

        # 2. Moving Chassis Plate (Steel Grey with chamfered corners)
        # Transit starts at x = -100 and exits at x = 460
        travel_distance = self.WIDTH + 260
        chassis_center_x = int(-120 + (progress * travel_distance))
        chassis_center_y = self.HEIGHT // 2

        chassis_w = 260
        chassis_h = 200

        x1 = chassis_center_x - (chassis_w // 2)
        y1 = chassis_center_y - (chassis_h // 2)
        x2 = chassis_center_x + (chassis_w // 2)
        y2 = chassis_center_y + (chassis_h // 2)

        chassis_bbox = BBox(float(x1), float(y1), float(x2), float(y2))
        detections: List[Detection] = []

        # Render chassis if in view
        if x2 > 0 and x1 < self.WIDTH:
            # Steel plate
            cv2.rectangle(frame, (max(0, x1), max(0, y1)), (min(self.WIDTH, x2), min(self.HEIGHT, y2)), (75, 80, 88), -1)
            cv2.rectangle(frame, (max(0, x1), max(0, y1)), (min(self.WIDTH, x2), min(self.HEIGHT, y2)), (110, 115, 125), 2)
            
            # Central machined cutout
            cv2.circle(frame, (chassis_center_x, chassis_center_y), 34, (55, 58, 65), -1)
            cv2.circle(frame, (chassis_center_x, chassis_center_y), 34, (90, 95, 105), 1)

            # Chassis detection
            detections.append(Detection(
                label="chassis",
                confidence=0.96,
                bbox=chassis_bbox,
                track_id=47
            ))

            # 3. Render Slots A, B, C, D
            slot_coords = {
                "A": (x1 + int(0.24 * chassis_w), y1 + int(0.28 * chassis_h)),
                "B": (x1 + int(0.76 * chassis_w), y1 + int(0.28 * chassis_h)),
                "C": (x1 + int(0.24 * chassis_w), y1 + int(0.72 * chassis_h)),
                "D": (x1 + int(0.76 * chassis_w), y1 + int(0.72 * chassis_h)),
            }

            for s_id, (sx, sy) in slot_coords.items():
                part_type = cfg["slots"][s_id]

                # Drilled mounting hole base
                cv2.circle(frame, (sx, sy), 14, (40, 42, 48), -1)
                cv2.circle(frame, (sx, sy), 14, (70, 75, 85), 1)

                if part_type == "m8_flange_bolt":
                    # Black-Oxide M8 Flange Bolt (Dark Gunmetal with Hex Facet)
                    cv2.circle(frame, (sx, sy), 12, (20, 22, 25), -1)
                    cv2.circle(frame, (sx, sy), 7, (45, 50, 58), -1)
                    cv2.circle(frame, (sx, sy), 12, (80, 85, 95), 1)

                    b_box = BBox(sx - 15, sy - 15, sx + 15, sy + 15)
                    detections.append(Detection(
                        label="m8_flange_bolt",
                        confidence=0.94,
                        bbox=b_box,
                        slot_id=s_id,
                        track_id=100 + ord(s_id)
                    ))
                elif part_type == "brass_nut":
                    # Uncoated Golden Brass Nut
                    cv2.circle(frame, (sx, sy), 13, (35, 165, 218), -1)  # Golden Brass BGR
                    cv2.circle(frame, (sx, sy), 6, (20, 22, 25), -1)
                    cv2.circle(frame, (sx, sy), 13, (60, 200, 255), 2)

                    b_box = BBox(sx - 15, sy - 15, sx + 15, sy + 15)
                    detections.append(Detection(
                        label="brass_nut",
                        confidence=0.91,
                        bbox=b_box,
                        slot_id=s_id,
                        track_id=100 + ord(s_id)
                    ))
                else:
                    # Slot is EMPTY (Part absent). Nothing drawn.
                    pass

            # 4. Render Surface Crack if in Scenario 3
            if cfg["has_crack"]:
                cr_start_x = chassis_center_x - 30
                cr_start_y = chassis_center_y + 10
                # Jagged hairline crack
                pts = np.array([
                    [cr_start_x, cr_start_y],
                    [cr_start_x + 15, cr_start_y - 8],
                    [cr_start_x + 30, cr_start_y + 12],
                    [cr_start_x + 55, cr_start_y - 5],
                    [cr_start_x + 75, cr_start_y + 8]
                ], np.int32)
                cv2.polylines(frame, [pts], False, (15, 20, 220), 2, cv2.LINE_AA)
                cv2.polylines(frame, [pts], False, (20, 20, 20), 1, cv2.LINE_AA)

                crack_bbox = BBox(cr_start_x - 5, cr_start_y - 12, cr_start_x + 80, cr_start_y + 16)
                detections.append(Detection(
                    label="surface_crack",
                    confidence=0.88,
                    bbox=crack_bbox,
                    track_id=201
                ))

        # 5. Apply Perturbations
        if perturbation == "angle_stress":
            # Rotate frame by 14 degrees to simulate tilted camera
            M = cv2.getRotationMatrix2D((self.WIDTH / 2, self.HEIGHT / 2), 14, 0.95)
            frame = cv2.warpAffine(frame, M, (self.WIDTH, self.HEIGHT), borderValue=(20, 20, 24))
        elif perturbation == "low_light":
            # 45% illumination drop
            frame = cv2.multiply(frame, np.array([0.55, 0.55, 0.55]))
        elif perturbation == "glare":
            # Overhead specular reflection glare overlay
            glare_center = (self.WIDTH // 2, int(self.HEIGHT * 0.4))
            overlay = frame.copy()
            cv2.circle(overlay, glare_center, 90, (230, 240, 255), -1)
            cv2.addWeighted(overlay, 0.40, frame, 0.60, 0, frame)

        return frame, chassis_bbox, detections

    def draw_cad_overlay(
        self, 
        frame: np.ndarray, 
        chassis_bbox: BBox, 
        slot_status: Dict[str, Dict], 
        defect_findings: List[Any]
    ) -> np.ndarray:
        """
        Draws the high-precision CAD BOM Reference Grid overlay onto the frame.
        """
        out = frame.copy()
        if chassis_bbox.width <= 10 or chassis_bbox.height <= 10:
            return out

        x1 = int(chassis_bbox.x1)
        y1 = int(chassis_bbox.y1)
        x2 = int(chassis_bbox.x2)
        y2 = int(chassis_bbox.y2)

        # 1. Outer CAD Fiducial Box (Cyan tech-lines)
        cv2.rectangle(out, (x1, y1), (x2, y2), (220, 180, 0), 1, cv2.LINE_AA)
        
        # Corner brackets
        corner_len = 16
        for (cx, cy, dx, dy) in [(x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)]:
            cv2.line(out, (cx, cy), (cx + (dx * corner_len), cy), (0, 230, 255), 2)
            cv2.line(out, (cx, cy), (cx, cy + (dy * corner_len)), (0, 230, 255), 2)

        # 2. Reference Grid Targets for Slots A, B, C, D
        for s_id, s_info in slot_status.items():
            px, py = s_info["px_coord"]
            px, py = int(px), int(py)
            status = s_info["status"]

            if status == "PASS":
                color = (60, 220, 80)     # Neon Green
                tag = f"Slot {s_id} [OK]"
                cv2.circle(out, (px, py), 18, color, 1, cv2.LINE_AA)
                cv2.drawMarker(out, (px, py), color, cv2.MARKER_CROSS, 10, 1)
            elif status == "ABSENT":
                color = (30, 30, 240)     # Bright Red
                tag = f"Slot {s_id} [ABSENT]"
                cv2.circle(out, (px, py), 22, color, 2, cv2.LINE_AA)
                cv2.line(out, (px - 14, py - 14), (px + 14, py + 14), color, 2)
                cv2.line(out, (px - 14, py + 14), (px + 14, py - 14), color, 2)
            elif status == "WRONG_COMPONENT":
                color = (0, 140, 255)     # Amber Orange
                tag = f"Slot {s_id} [CLASS MISMATCH]"
                cv2.circle(out, (px, py), 20, color, 2, cv2.LINE_AA)
                cv2.drawMarker(out, (px, py), color, cv2.MARKER_DIAMOND, 12, 1)
            else:
                color = (180, 180, 180)   # Grey pending
                tag = f"Slot {s_id}"
                cv2.circle(out, (px, py), 16, color, 1, cv2.LINE_AA)

            # Label badge
            cv2.putText(out, tag, (px - 26, py - 24), cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1, cv2.LINE_AA)

        # 3. Surface defect badge if present
        for f in defect_findings:
            if f.defect_type == "SURFACE_ANOMALY" and f.bbox is not None:
                bx1, by1 = int(f.bbox.x1), int(f.bbox.y1)
                bx2, by2 = int(f.bbox.x2), int(f.bbox.y2)
                cv2.rectangle(out, (bx1, by1), (bx2, by2), (40, 40, 245), 2)
                cv2.putText(out, "SURFACE ANOMALY", (bx1, by1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (40, 40, 245), 1, cv2.LINE_AA)

        return out

    def frame_to_base64(self, frame: np.ndarray) -> str:
        success, encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not success:
            return ""
        return base64.b64encode(encoded.tobytes()).decode("utf-8")

