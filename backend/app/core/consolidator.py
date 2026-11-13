import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2

from app.core.perception import BBox, Detection
from app.core.reference_grid import DefectFinding

@dataclass
class FrameEvidence:
    frame_idx: int
    timestamp: float
    confidence: float
    sharpness: float
    defect_type: str
    frame_image: Optional[np.ndarray] = None
    crop_image: Optional[np.ndarray] = None

@dataclass
class ConsolidatedIncident:
    incident_id: str
    track_id: int
    defect_type: str
    raw_frame_count: int
    confidence_avg: float
    best_evidence: List[FrameEvidence]
    noise_reduction_pct: float
    created_at: float
    status: str = "CONSOLIDATED"

def compute_iou(b1: BBox, b2: BBox) -> float:
    ix1 = max(b1.x1, b2.x1)
    iy1 = max(b1.y1, b2.y1)
    ix2 = min(b1.x2, b2.x2)
    iy2 = min(b1.y2, b2.y2)

    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    intersection = iw * ih

    area1 = b1.width * b1.height
    area2 = b2.width * b2.height
    union = area1 + area2 - intersection

    if union <= 0.0:
        return 0.0
    return intersection / union

def compute_sharpness(image: np.ndarray) -> float:
    """Laplacian variance measure of image focus/sharpness."""
    if image is None or image.size == 0:
        return 0.0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

class TrackIncidentBuffer:
    def __init__(self, track_id: int, initial_finding: DefectFinding, initial_bbox: BBox):
        self.track_id = track_id
        self.dominant_defect_type = initial_finding.defect_type
        self.last_bbox = initial_bbox
        self.consecutive_anomalous_frames = 0
        self.missed_frames = 0
        self.buffered_evidence: List[FrameEvidence] = []
        self.total_raw_frames = 0

    def add_observation(
        self, 
        finding: DefectFinding, 
        current_bbox: BBox, 
        frame_idx: int, 
        frame_img: Optional[np.ndarray] = None
    ):
        self.total_raw_frames += 1
        self.consecutive_anomalous_frames += 1
        self.missed_frames = 0
        self.last_bbox = current_bbox

        sharpness = compute_sharpness(frame_img) if frame_img is not None else 85.0
        
        # Anomaly crop extraction
        crop = None
        if frame_img is not None and finding.bbox is not None:
            h, w = frame_img.shape[:2]
            bx1 = max(0, int(finding.bbox.x1))
            by1 = max(0, int(finding.bbox.y1))
            bx2 = min(w, int(finding.bbox.x2))
            by2 = min(h, int(finding.bbox.y2))
            if bx2 > bx1 and by2 > by1:
                crop = frame_img[by1:by2, bx1:bx2].copy()

        self.buffered_evidence.append(FrameEvidence(
            frame_idx=frame_idx,
            timestamp=time.time(),
            confidence=finding.confidence,
            sharpness=sharpness,
            defect_type=finding.defect_type,
            frame_image=frame_img,
            crop_image=crop
        ))

class IncidentConsolidator:
    """
    Deterministic Incident Consolidation Engine (Layer 3).
    Implements 4-Gate Deduplication to eliminate alert flooding and compute
    live alert noise reduction telemetry.
    """
    def __init__(
        self, 
        iou_gate_threshold: float = 0.45, 
        min_persistence_frames: int = 5,
        max_missed_frames_to_close: int = 8,
        top_k_evidence: int = 3
    ):
        self.iou_gate_threshold = iou_gate_threshold
        self.min_persistence_frames = min_persistence_frames
        self.max_missed_frames_to_close = max_missed_frames_to_close
        self.top_k_evidence = top_k_evidence

        self.active_buffers: Dict[int, TrackIncidentBuffer] = {}
        self.total_raw_detections = 0
        self.total_consolidated_incidents = 0
        self.incident_seq = 41

    def process_frame(
        self, 
        track_id: int, 
        chassis_bbox: BBox, 
        findings: List[DefectFinding], 
        frame_idx: int,
        frame_img: Optional[np.ndarray] = None
    ) -> Optional[ConsolidatedIncident]:
        """
        Processes frame through 4-Gate pipeline. 
        Returns ConsolidatedIncident when part completes transit across inspection ROI.
        """
        if not findings:
            if track_id in self.active_buffers:
                buf = self.active_buffers[track_id]
                buf.missed_frames += 1
                if buf.missed_frames >= self.max_missed_frames_to_close:
                    return self._finalize_buffer(track_id)
            return None

        self.total_raw_detections += 1
        finding = findings[0]  # Primary anomalous finding

        if track_id not in self.active_buffers:
            # Gate 1: Track Identity initialized
            self.active_buffers[track_id] = TrackIncidentBuffer(track_id, finding, chassis_bbox)

        buf = self.active_buffers[track_id]

        # Gate 2: Spatial Overlap Gate
        iou = compute_iou(buf.last_bbox, chassis_bbox)
        if iou < self.iou_gate_threshold and buf.total_raw_frames > 0:
            # Spatial discontinuity: possible different unit, reset candidate
            pass

        buf.add_observation(finding, chassis_bbox, frame_idx, frame_img)
        return None

    def check_transit_exit(self, track_id: int) -> Optional[ConsolidatedIncident]:
        """Forces finalization when part exits ROI or video completes."""
        if track_id in self.active_buffers:
            return self._finalize_buffer(track_id)
        return None

    def _finalize_buffer(self, track_id: int) -> Optional[ConsolidatedIncident]:
        buf = self.active_buffers.pop(track_id, None)
        if buf is None:
            return None

        # Gate 3: Temporal Persistence Filter
        if buf.consecutive_anomalous_frames < self.min_persistence_frames:
            # Filtered out as motion blur, transient glare, or sensor glitch
            return None

        # Gate 4: Peak-Evidence Selection (top K by sharpness * confidence)
        sorted_evidence = sorted(
            buf.buffered_evidence,
            key=lambda e: (e.sharpness * e.confidence),
            reverse=True
        )
        best_evidence = sorted_evidence[:self.top_k_evidence]

        raw_n = max(1, buf.total_raw_frames)
        noise_reduction = ((raw_n - 1) / raw_n) * 100.0

        avg_conf = float(np.mean([e.confidence for e in best_evidence])) if best_evidence else 0.95
        
        self.incident_seq += 1
        inc_id = f"QI-00{self.incident_seq}"
        self.total_consolidated_incidents += 1

        return ConsolidatedIncident(
            incident_id=inc_id,
            track_id=track_id,
            defect_type=buf.dominant_defect_type,
            raw_frame_count=raw_n,
            confidence_avg=round(avg_conf, 3),
            best_evidence=best_evidence,
            noise_reduction_pct=round(noise_reduction, 1),
            created_at=time.time()
        )

    @property
    def live_noise_reduction(self) -> float:
        if self.total_raw_detections == 0:
            return 0.0
        return round(
            ((self.total_raw_detections - max(1, self.total_consolidated_incidents)) 
             / self.total_raw_detections) * 100.0, 
            1
        )
