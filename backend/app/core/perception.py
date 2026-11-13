from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import numpy as np

@dataclass
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def centroid(self) -> Tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def to_list(self) -> List[float]:
        return [self.x1, self.y1, self.x2, self.y2]

@dataclass
class Detection:
    label: str
    confidence: float
    bbox: BBox
    track_id: Optional[int] = None
    slot_id: Optional[str] = None
    sharpness: float = 0.0

class BasePerceptionProvider(ABC):
    """Abstract interface decoupling model weights from INDUS-X platform logic."""
    @abstractmethod
    def detect(self, frame: np.ndarray, tracking: bool = False) -> List[Detection]:
        pass

class YOLOPerceptionAdapter(BasePerceptionProvider):
    """
    Standardized adapter wrapping YOLO models with standardized output format.
    Includes robust fallback for offline or headless environments.
    """
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.35):
        self.confidence_threshold = confidence_threshold
        self.model = None
        try:
            from ultralytics import YOLO
            # Try to load custom or local weights if available
            path = model_path or "yolov8n.pt"
            self.model = YOLO(path)
        except Exception:
            self.model = None

    def detect(self, frame: np.ndarray, tracking: bool = False) -> List[Detection]:
        if self.model is None or frame is None:
            return []

        try:
            if tracking:
                results = self.model.track(frame, persist=True, tracker="bytetrack.yaml", 
                                           conf=self.confidence_threshold, verbose=False)
            else:
                results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
            
            detections: List[Detection] = []
            if not results or not len(results):
                return detections

            r = results[0]
            names = r.names
            if r.boxes is not None:
                for box in r.boxes:
                    cls_id = int(box.cls[0].item())
                    coords = box.xyxy[0].tolist()
                    conf = float(box.conf[0].item())
                    t_id = int(box.id[0].item()) if getattr(box, "id", None) is not None else None
                    label = names.get(cls_id, str(cls_id)) if isinstance(names, dict) else str(names[cls_id])
                    
                    bbox = BBox(coords[0], coords[1], coords[2], coords[3])
                    detections.append(Detection(
                        label=label.lower(),
                        confidence=conf,
                        bbox=bbox,
                        track_id=t_id
                    ))
            return detections
        except Exception:
            return []

