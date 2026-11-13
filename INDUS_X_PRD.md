# INDUS-X — Product Requirements Document (PRD)

### Industrial Quality Intelligence, Closed-Loop Automation & Resolution Platform

---

| Field | Detail |
|-------|--------|
| **Document Version** | 2.0 — Competition-Ready |
| **Track Alignment** | ⚙️ Smart Industry & Automation (with Embedded Governance & FinTech Liability Resolution) |
| **Target Build Horizon** | 24–36 Hour Hackathon MVP (100% Software Architecture) |
| **Core Lifecycle** | See → Verify → Trace → Decide → Act → Learn |
| **Governance Mantra** | *"Autonomous where safe. Human-controlled where consequential."* |

---

## Table of Contents

1. [Executive Summary & Product Vision](#1-executive-summary--product-vision)
2. [Problem Statement — The Real Manufacturing Crisis](#2-problem-statement)
3. [The INDUS-X Solution — One-Line Pitch](#3-the-indus-x-solution)
4. [Competitive Differentiation Matrix](#4-competitive-differentiation)
5. [End-to-End System Architecture (8 Layers)](#5-system-architecture)
6. [Data Schema & API Contract](#6-data-schema--api-contract)
7. [User Interface — Command Center Design](#7-user-interface)
8. [3-Minute Demo Choreography](#8-demo-choreography)
9. [Non-Functional Requirements & Guardrails](#9-non-functional-requirements)
10. [Build Roadmap & Hour-by-Hour Sprint Plan](#10-build-roadmap)
11. [Risk Register & Mitigation Playbook](#11-risk-register)
12. [Judge Q&A Defense Playbook](#12-judge-qa-defense)

---


## 1. Executive Summary & Product Vision

### 1.1 What is INDUS-X?

INDUS-X is a **model-agnostic Industrial Quality Intelligence & Resolution Platform** that goes far beyond visual defect detection. It is the full operational pipeline that transforms a raw camera frame into a verified, traceable, legally defensible industrial decision — with closed-loop machine containment and human-governed financial resolution.

**The one-sentence pitch:**

> *"INDUS-X doesn't just find defects — it consolidates noisy camera feeds into single verified incidents, seals them with tamper-evident cryptographic provenance, maps the blast radius across batches and suppliers, triggers automated machine containment, and synthesizes contractual liability briefs for human-governed resolution."*

### 1.2 Why This Exists — The Post-Detection Crisis

In modern manufacturing, **detecting a defect on a camera feed is no longer the bottleneck**. The operational chaos that follows detection is where billions are lost:

#### Problem 1: Alert Floods Destroy Trust
A 30-FPS industrial camera watching a conveyor belt flags the **same moving defect 30 times** as it transits the field of view. Plant dashboards flood with duplicate alerts. Within weeks, operators develop "alert fatigue" and start ignoring the system entirely.

**Real-world data:** Studies show that when false/duplicate alert rates exceed 40%, operator response rates drop below 15%. The system becomes decoration.

#### Problem 2: Absence & Context Blindness
Standard object detectors (YOLO, SSD, Faster-RCNN) are trained to draw bounding boxes around objects that **are present**. They fundamentally cannot reason about:
- A missing structural fastener (there is no pixel pattern to detect — it's empty space)
- A wrong component that *looks* similar but has incorrect material/class
- Whether an assembly matches its CAD/BOM tolerance specification

**The technical paradox:** You cannot train a neural network to reliably detect "nothing." Every hackathon team that claims otherwise is either using negative-space hacks (unreliable) or lying.

#### Problem 3: The "Dead-End" Dashboard
Traditional quality dashboards turn red when defects spike. Then what? A human must:
1. Physically walk to the line to slow/stop the conveyor
2. Manually eject the defective part
3. Look up which batch this part belongs to
4. Check which supplier provided the raw component
5. Dig through contract PDFs to understand liability terms
6. Draft a non-conformance report by hand

**Time cost:** 45–90 minutes per incident. During which defective parts continue flowing downstream.

#### Problem 4: Vendor Liability Disputes Have No Evidence Chain
When a factory rejects a batch and attempts to claim against the supplier's SLA:
- The supplier argues the damage happened on the factory floor, not in their shipment
- The factory has a JPEG crop with no timestamp provenance, no chain of custody, no tamper-proof seal
- Disputes drag for weeks, costing both parties legal fees that exceed the batch value

**The gap:** No cryptographic link between the raw camera frame, the specific batch/lot number, the exact timestamp, and the governing contract clause.

### 1.3 The INDUS-X Value Proposition

| What Others Build | What INDUS-X Delivers |
|---|---|
| "We detect defects" | We turn messy visual signals into verified, traceable industrial decisions |
| 27 alerts for 1 defective part | 1 consolidated incident with peak evidence selection |
| A JPEG crop saved to disk | Tamper-evident hash chain with millisecond chain of custody |
| A red dashboard | Automated machine containment + human-gated batch quarantine |
| "Contact your supplier" | LLM-synthesized liability dossier citing exact contract sub-clauses |
| Raw defect counts per vendor | Volume-normalized, severity-weighted risk scoring with ISO 2859 switching |

---


## 2. Problem Statement — The Five Failure Modes

INDUS-X addresses five distinct failure modes that collectively represent the "last mile" gap in industrial quality systems:

| # | Failure Mode | Industry Impact | INDUS-X Response |
|---|---|---|---|
| F1 | **Alert Flooding** — Camera frame rate dictates alert volume | Operator alert fatigue → missed real defects | Deterministic 4-gate incident consolidation |
| F2 | **Absence Blindness** — Cannot detect missing components | Structural failures reach customers | Reference-grid spatial verification against CAD/BOM |
| F3 | **Evidence Fragility** — No tamper-proof chain of custody | Supplier disputes are unresolvable | Append-only SHA-256 hash chain with live verification |
| F4 | **Operational Dead-Ends** — Detection without action | 45-90 min manual response per incident | Closed-loop MQTT containment + blast-radius traceability |
| F5 | **Risk Blindness** — Raw defect counts penalize high-volume vendors | Unfair supplier scoring → broken relationships | Volume-normalized severity-weighted risk formulas |

---

## 3. The INDUS-X Solution — Architecture Overview

INDUS-X is organized as an **8-layer pipeline**, where each layer has a single responsibility and clean interfaces to adjacent layers:

```
┌─────────────────────────────────────────────────────────────┐
│                    INDUS-X ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Input & Controlled Simulation (Test Bench)        │
│      ↓                                                      │
│  Layer 2: Model-Agnostic Perception & Reference Verify      │
│      ↓                                                      │
│  Layer 3: Deterministic Incident Consolidation (Dedup)      │
│      ↓                                                      │
│  Layer 4: Tamper-Evident Provenance & Chain of Custody       │
│      ↓                                                      │
│  Layer 5: Operational Traceability & Blast-Radius Engine     │
│      ↓                                                      │
│  Layer 6: Closed-Loop Automation & LLM Reasoning            │
│      ↓                                                      │
│  Layer 7: Risk-Aware Governance & RBAC Human Gates           │
│      ↓                                                      │
│  Layer 8: Supplier Intelligence & ISO Switching (Learn)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Competitive Differentiation Matrix

| Dimension | Standard Hackathon CV Project | INDUS-X |
|---|---|---|
| **Core Focus** | "We trained YOLO to draw boxes around defects" | "We turn messy visual signals into verified, traceable industrial decisions" |
| **Missing Part Handling** | Claims YOLO detects "nothingness" (technically flawed) | Reference-Based Spatial Verification comparing expected CAD grid vs. observed state |
| **Alert Management** | 1 defective part across 27 frames = 27 database rows | Deterministic 4-gate consolidation merges 27 observations into 1 incident |
| **Evidence & Security** | Saves crop.jpg or claims a hash is "immutable" | Append-only SHA-256 hash chain with millisecond chain of custody + live tamper detection |
| **Automation Scope** | Passive charts or reckless "AI auto-deducts vendor money" | Closed-loop MQTT containment + risk-aware human gates for financial decisions |
| **AI/LLM Usage** | Generic chatbot wrapper or simple if/else rules | RAG-grounded SLA contract synthesis matching live evidence to legal agreements |
| **Analytics** | Raw defect counts per vendor (penalizes high-volume suppliers) | Volume-normalized, severity-weighted risk scoring + ISO 2859 AQL switching |
| **Explainability** | "Confidence: 0.87" (meaningless to operators) | Grad-CAM attention heatmap overlay on every evidence frame |
| **Business Impact** | No financial quantification | Real-time Cost-of-Inaction calculator (catch cost vs. recall cost) |
| **Feedback Loop** | None — model is static | Operator verdict capture for continuous accuracy tracking |

---


## 5. System Architecture — Layer-by-Layer Deep Specification

---

### Layer 1: Input & Controlled Simulation Layer (The Multi-Defect Test Bench)

**Location in Stack:** Top-level ingestion gateway between the Frontend Test Bench UI and the FastAPI Frame Streaming Engine.

**Purpose:** Eliminates stage hardware/lighting risks by providing a deterministic Edge Replay & Simulation Test Bench. Instead of relying on a single static demo, it streams **four distinct industrial scenarios** through the exact same backend pipeline.

#### The Four Scenarios

| Scenario | Physical Condition | What It Tests | Expected System Response |
|---|---|---|---|
| **S0: Baseline Pass** | Standard assembly with all 4 M8 structural fasteners seated, intact surface finish | Proves the system does NOT false-positive on good parts | No incident created. All 4 reference grid slots show ✓ PRESENT |
| **S1: Structural Absence** | Missing Bolt C at coordinate (x₃, y₃) | Tests reference-grid absence detection logic | STRUCTURAL_ABSENCE incident. Slot C shows ✗ ABSENT. Containment triggered |
| **S2: Wrong Component** | Uncoated brass nut installed in place of Black-Oxide M8 flange bolt | Tests class-mismatch verification | WRONG_COMPONENT incident. Slot C shows ⚠ CLASS MISMATCH |
| **S3: Surface Degradation** | Hairline stamping crack / surface scratch across chassis plate | Tests surface anomaly detection | SURFACE_ANOMALY incident. Internal region flagged with crack overlay |

#### Controlled Robustness Perturbations

The Test Bench includes a **Perturbation Toggle** with three synthetic stress modes:

| Perturbation | What It Simulates | Purpose |
|---|---|---|
| ±15° Camera Angle Shift | Misaligned inspection camera | Proves fiducial alignment normalizes perspective |
| Low-Lux Lighting Drop | Factory lighting failure / shadow zones | Proves model handles underexposed frames |
| Partial Glare Overlay | Reflective metal surfaces under overhead lights | Proves confidence thresholding filters glare artifacts |

**Why It Matters:** Directly neutralizes the judge critique *"You only built a one-trick missing bolt demo"* by proving that diverse physical failure modes flow seamlessly through a single unified architecture.

#### Technical Implementation

```python
class TestBenchService:
    SCENARIOS = {
        0: {"name": "Baseline Pass", "video": "scenario_0_pass.mp4", "expected_defects": 0},
        1: {"name": "Missing Bolt", "video": "scenario_1_missing.mp4", "expected_defects": 1},
        2: {"name": "Wrong Component", "video": "scenario_2_wrong.mp4", "expected_defects": 1},
        3: {"name": "Surface Crack", "video": "scenario_3_crack.mp4", "expected_defects": 1},
    }
    
    PERTURBATIONS = {
        "standard": {"angle_shift": 0, "lux_drop": 0, "glare": False},
        "angle_stress": {"angle_shift": 15, "lux_drop": 0, "glare": False},
        "low_light": {"angle_shift": 0, "lux_drop": 0.4, "glare": False},
        "glare": {"angle_shift": 0, "lux_drop": 0, "glare": True},
    }
    
    async def stream_scenario(self, scenario_id: int, perturbation: str = "standard"):
        """Stream video frames with optional perturbation applied."""
        config = self.SCENARIOS[scenario_id]
        perturb = self.PERTURBATIONS[perturbation]
        
        for frame in self.read_video(config["video"]):
            if perturb["angle_shift"]:
                frame = self.apply_rotation(frame, perturb["angle_shift"])
            if perturb["lux_drop"]:
                frame = self.apply_brightness(frame, 1.0 - perturb["lux_drop"])
            if perturb["glare"]:
                frame = self.apply_glare_overlay(frame)
            
            yield frame
```

---

### Layer 2: Model-Agnostic Perception & Reference Verification Layer

**Location in Stack:** Core Computer Vision pipeline (PerceptionAdapter + ReferenceGridEvaluator).

**Purpose:** Wraps the active detection model in a standardized interface and performs tri-modal defect evaluation using geometric constraint verification.

#### 2A: Modular Adapter Pattern

The platform is **completely decoupled** from the specific neural network:

```python
class BasePerceptionProvider(ABC):
    """Abstract interface — swap YOLO for any model without touching downstream code."""
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Returns standardized detections regardless of underlying model."""
        pass

class YOLOv11Adapter(BasePerceptionProvider):
    def __init__(self, weights_path: str = "yolov11n.pt"):
        self.model = YOLO(weights_path)
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        results = self.model(frame, conf=0.25)
        return [
            Detection(
                class_name=results.names[int(box.cls)],
                confidence=float(box.conf),
                bbox=box.xyxy[0].tolist(),
                centroid=self._compute_centroid(box.xyxy[0])
            )
            for box in results[0].boxes
        ]
```

**Why this matters to judges:** If asked *"what if we wanted to use a different model?"* — the answer is: *"Implement the 4-method BasePerceptionProvider interface. Zero downstream changes."*

#### 2B: Fiducial Alignment & Reference Grid Projection

The system does NOT try to detect "missing objects." Instead:

1. **Detect the outer chassis bounding box** — this is the fiducial anchor
2. **Normalize the coordinate space** to a unit grid relative to the chassis corners
3. **Project the Expected BOM/CAD Reference Template:**

```
Expected Grid = {A(x₁, y₁), B(x₂, y₂), C(x₃, y₃), D(x₄, y₄)}
```

4. **Compare observed detections against expected positions** using Euclidean distance and IoU matching

#### 2C: Tri-Modal Defect Evaluation

| Check Type | Logic | Trigger Condition |
|---|---|---|
| **Absence Check** | Compute IoU between observed fastener centroids and expected template coordinates | Slot C registers 0 valid detections across ≥ K consecutive frames while A, B, D are locked → `STRUCTURAL_ABSENCE` |
| **Class/Orientation Check** | If slot C is occupied but `observed_class ≠ expected_class` | Class mismatch detected → `WRONG_COMPONENT` |
| **Surface Anomaly Check** | Scan internal chassis regions for `surface_crack` or `scratch` bounding boxes above confidence threshold τ | Anomaly detected → `SURFACE_ANOMALY` |

```python
class ReferenceGridEvaluator:
    def __init__(self, expected_grid: Dict[str, Tuple[float, float]], 
                 expected_classes: Dict[str, str],
                 iou_threshold: float = 0.3,
                 absence_frame_threshold: int = 5):
        self.expected_grid = expected_grid      # {"A": (0.2, 0.3), "B": (0.8, 0.3), ...}
        self.expected_classes = expected_classes # {"A": "m8_bolt", "B": "m8_bolt", ...}
        self.iou_threshold = iou_threshold
        self.absence_counter = defaultdict(int)  # Tracks consecutive absent frames per slot
    
    def evaluate(self, detections: List[Detection], chassis_bbox: BBox) -> List[DefectFinding]:
        findings = []
        normalized_detections = self._normalize_to_chassis(detections, chassis_bbox)
        
        for slot_id, expected_pos in self.expected_grid.items():
            matched = self._find_closest_detection(expected_pos, normalized_detections)
            
            if matched is None:
                self.absence_counter[slot_id] += 1
                if self.absence_counter[slot_id] >= self.absence_frame_threshold:
                    findings.append(DefectFinding(
                        type="STRUCTURAL_ABSENCE",
                        slot=slot_id,
                        confidence=1.0,  # Geometric certainty, not model confidence
                        message=f"Slot {slot_id}: No fastener detected for "
                                f"{self.absence_counter[slot_id]} consecutive frames"
                    ))
            elif matched.class_name != self.expected_classes[slot_id]:
                findings.append(DefectFinding(
                    type="WRONG_COMPONENT",
                    slot=slot_id,
                    confidence=matched.confidence,
                    observed_class=matched.class_name,
                    expected_class=self.expected_classes[slot_id]
                ))
            else:
                self.absence_counter[slot_id] = 0  # Reset on valid detection
        
        # Surface anomaly scan (independent of grid)
        for det in detections:
            if det.class_name in ("surface_crack", "scratch") and det.confidence > 0.4:
                findings.append(DefectFinding(
                    type="SURFACE_ANOMALY",
                    confidence=det.confidence,
                    bbox=det.bbox
                ))
        
        return findings
```

**Why It Is Superior:** Solves the fundamental computer vision paradox of "detecting absence." Instead of hallucinating bounding boxes over empty space, it uses geometric constraint verification grounded in manufacturing CAD tolerances.

---

### Layer 3: Deterministic Incident Consolidation Engine

**Location in Stack:** State machine immediately downstream of Layer 2 (IncidentConsolidator).

**Purpose:** Prevents camera frame rate from dictating operational alert volume.

#### The Core Problem This Solves

A part takes ~1 second to transit the camera's field of view at typical conveyor speed. At 30 FPS, that's **27–30 frames** containing the same defect. Without consolidation, the system creates 27–30 database rows, 27–30 alerts, and 27–30 notifications for what is **one physical defect on one physical part.**

#### The 4-Gate Consolidation Pipeline

```
Raw Frame Detection
    ↓
Gate 1: Track Identity (ByteTrack assigns persistent track_id)
    ↓
Gate 2: Spatial Overlap (IoU > 0.5 across consecutive frames)
    ↓
Gate 3: Temporal Persistence (≥ 5 consecutive anomalous frames required)
    ↓
Gate 4: Peak Evidence Selection (top 3 frames by sharpness + confidence)
    ↓
OUTPUT: 1 Consolidated Quality Incident (e.g., QI-0041)
```

**Gate 1 — Track Identity:** ByteTrack assigns a persistent `track_id` to each physical assembly entering the inspection zone. All detections with the same `track_id` are candidates for consolidation.

**Gate 2 — Spatial Overlap:** Consecutive-frame bounding boxes must overlap with IoU > 0.5. This filters out cases where two different parts are in the field of view simultaneously.

**Gate 3 — Temporal Persistence:** Requires ≥ 5 consecutive anomalous frames to filter out:
- Motion blur artifacts (1–2 frame glitches)
- Transient occlusions (hand passing over camera)
- Lighting flicker (1–3 frame exposure changes)

**Gate 4 — Peak Evidence Selection:** Buffers ALL anomalous frames (e.g., 27) as the part transits. When the part exits the ROI, selects the **top 3 frames** with highest Laplacian variance (sharpness) × confidence score. These 3 frames become the incident's evidence package.

#### Live Telemetry

The consolidation ratio is computed dynamically, not hardcoded:

```
Alert Noise Reduction = ((N_raw_frames - 1) / N_raw_frames) × 100%

Example: 27 raw detections → 1 incident = ((27 - 1) / 27) × 100% = 96.3%
```

```python
class IncidentConsolidator:
    def __init__(self, iou_threshold=0.5, min_consecutive=5, top_k_evidence=3):
        self.active_tracks: Dict[str, TrackBuffer] = {}
        self.iou_threshold = iou_threshold
        self.min_consecutive = min_consecutive
        self.top_k = top_k_evidence
        self.total_raw_detections = 0
        self.total_consolidated_incidents = 0
    
    def process_frame(self, track_id: str, detection: Detection, frame: np.ndarray) -> Optional[ConsolidatedIncident]:
        self.total_raw_detections += 1
        
        if track_id not in self.active_tracks:
            self.active_tracks[track_id] = TrackBuffer(track_id)
        
        buffer = self.active_tracks[track_id]
        
        # Gate 2: Spatial overlap check
        if buffer.last_bbox and self._compute_iou(buffer.last_bbox, detection.bbox) < self.iou_threshold:
            return None  # Different spatial region — not the same defect
        
        buffer.add_frame(detection, frame)
        
        # Check if part has exited ROI
        if buffer.frames_since_last_detection > 10:
            return self._finalize_track(buffer)
        
        return None
    
    def _finalize_track(self, buffer: TrackBuffer) -> Optional[ConsolidatedIncident]:
        # Gate 3: Temporal persistence
        if buffer.consecutive_anomalous_frames < self.min_consecutive:
            return None  # Transient noise — discard
        
        # Gate 4: Peak evidence selection
        evidence_frames = sorted(
            buffer.anomalous_frames,
            key=lambda f: f.sharpness * f.confidence,
            reverse=True
        )[:self.top_k]
        
        self.total_consolidated_incidents += 1
        
        return ConsolidatedIncident(
            incident_id=self._generate_id(),
            track_id=buffer.track_id,
            raw_frame_count=buffer.total_frames,
            evidence_frames=evidence_frames,
            defect_type=buffer.dominant_defect_type,
            confidence_avg=buffer.avg_confidence,
            noise_reduction_pct=((buffer.total_frames - 1) / buffer.total_frames) * 100
        )
    
    @property
    def live_noise_reduction(self) -> float:
        if self.total_raw_detections == 0:
            return 0.0
        return ((self.total_raw_detections - self.total_consolidated_incidents) 
                / self.total_raw_detections) * 100
```

---

### Layer 4: Tamper-Evident Provenance & Chain of Custody

**Location in Stack:** Cryptographic sealing service between the Incident Engine and the SQLite Ledger (ProvenanceChainService).

**Purpose:** Converts raw pixel crops into legally defensible supply-chain evidence.

#### Why This Matters

When a factory rejects a batch and claims against the supplier's SLA, the supplier's first defense is: *"Prove that image wasn't altered. Prove the timestamp is real. Prove the defect wasn't introduced on your floor after our delivery."*

Without cryptographic provenance, the factory has a JPEG and a prayer.

#### Evidence Package Assembly

Each consolidated incident is sealed with:

| Field | Content | Purpose |
|---|---|---|
| `incident_id` | QI-0041 | Unique identifier |
| `timestamp_iso` | 2026-10-31T13:15:42.871Z | Millisecond-precision ISO-8601 |
| `camera_id` | CAM-INSPECT-03 | Which physical camera captured it |
| `workstation_id` | CELL-03 | Which assembly station |
| `frame_sha256` | SHA-256 of raw frame bytes | Proves image hasn't been altered |
| `crop_sha256` | SHA-256 of evidence crop bytes | Proves crop matches source frame |
| `metadata_json` | Full detection metadata | Defect type, confidence, coordinates |
| `prev_hash` | Hash of previous block | Creates unbreakable chain link |

#### Append-Only Hash Chain Construction

Each block is cryptographically linked to all preceding blocks:

```
Hₙ = SHA256(IncidentIDₙ ‖ Timestampₙ ‖ CameraIDₙ ‖ SHA256(ImageBytesₙ) ‖ MetadataJSONₙ ‖ Hₙ₋₁)
```

If ANY historical block is tampered with (even 1 character changed), every subsequent hash becomes invalid. The chain is broken.

```
Block #0 (GENESIS)  →  Block #1  →  Block #2  →  ...  →  Block #14
   H₀                    H₁            H₂                    H₁₄
                          ↑              ↑                      ↑
                     includes H₀    includes H₁           includes H₁₃
```

#### Live Verification & Tamper Simulation

**Verify Endpoint:** Recomputes the entire hash chain from GENESIS_BLOCK to Hₙ. If every recomputed hash matches the stored hash, the chain is intact. If any mismatch is found, it pinpoints the exact block number where tampering occurred.

**Tamper Simulator (Demo Feature):** During live judging, pressing "Simulate Tamper" alters a historical record by 1 character. The verifier immediately reports:

```
❌ INTEGRITY BREACH DETECTED AT BLOCK #7
   Expected: 0x4c91a8...e704
   Found:    0x9f3b21...c882
   All blocks after #7 are invalidated.
```

```python
class ProvenanceChainService:
    def __init__(self, db: Database):
        self.db = db
    
    def seal_incident(self, incident: ConsolidatedIncident, 
                      frame_bytes: bytes) -> ProvenanceBlock:
        prev_block = self.db.get_latest_block()
        prev_hash = prev_block.curr_hash if prev_block else "GENESIS_BLOCK_0x0000"
        
        frame_hash = hashlib.sha256(frame_bytes).hexdigest()
        metadata_json = json.dumps(incident.to_metadata(), sort_keys=True)
        
        chain_input = (
            f"{incident.incident_id}|"
            f"{incident.timestamp_iso}|"
            f"{incident.camera_id}|"
            f"{frame_hash}|"
            f"{metadata_json}|"
            f"{prev_hash}"
        )
        curr_hash = hashlib.sha256(chain_input.encode()).hexdigest()
        
        block = ProvenanceBlock(
            block_index=prev_block.block_index + 1 if prev_block else 0,
            incident_id=incident.incident_id,
            timestamp_iso=incident.timestamp_iso,
            camera_id=incident.camera_id,
            frame_sha256=frame_hash,
            metadata_json=metadata_json,
            prev_hash=prev_hash,
            curr_hash=curr_hash
        )
        
        self.db.insert_block(block)
        return block
    
    def verify_chain(self) -> ChainVerificationResult:
        blocks = self.db.get_all_blocks_ordered()
        
        for i, block in enumerate(blocks):
            # Recompute hash from stored fields
            expected_prev = blocks[i-1].curr_hash if i > 0 else "GENESIS_BLOCK_0x0000"
            
            if block.prev_hash != expected_prev:
                return ChainVerificationResult(
                    valid=False, total_blocks=len(blocks),
                    breach_at_block=block.block_index,
                    message=f"INTEGRITY BREACH AT BLOCK #{block.block_index}"
                )
            
            recomputed = self._compute_hash(block, expected_prev)
            if recomputed != block.curr_hash:
                return ChainVerificationResult(
                    valid=False, total_blocks=len(blocks),
                    breach_at_block=block.block_index,
                    message=f"HASH MISMATCH AT BLOCK #{block.block_index}"
                )
        
        return ChainVerificationResult(
            valid=True, total_blocks=len(blocks),
            message=f"ALL {len(blocks)} BLOCKS VERIFIED — CHAIN INTACT"
        )
```

#### Millisecond Chain of Custody Log

Every state transition is recorded with actor attribution:

```
QI-0041 Chain of Custody:
├─ 13:15:42.871  DETECTED      by SYSTEM_AUTO     (Camera CAM-INSPECT-03)
├─ 13:15:43.102  CONSOLIDATED  by SYSTEM_AUTO     (27 frames → 1 incident)
├─ 13:15:43.187  SEALED        by SYSTEM_AUTO     (Block #14, Hash 0x4c91..e704)
├─ 13:15:43.201  CONTAINMENT   by SYSTEM_AUTO     (Diverter #03 pulsed)
├─ 13:15:43.340  ROUTED        by SYSTEM_AUTO     (Tier-2 Governance Queue)
├─ 13:16:12.000  APPROVED      by QE-Sarah-Chen   (Batch B-042 quarantined)
└─ 13:18:45.000  NCR_ISSUED    by PM-Raj-Patel    (SQC-882 to Vendor-X)
```

---


### Layer 5: Operational Traceability & Blast-Radius Engine

**Location in Stack:** Relational context resolver querying the Factory MES & Procurement schema (TraceabilityResolver).

**Purpose:** Connects a visual defect on a single part to its full enterprise blast radius.

#### The Blast-Radius Trace

When incident QI-0041 is consolidated, the system automatically resolves the full impact chain:

```
Visual Trigger: Incident QI-0041 (Missing M8 Fastener)
    ↓
Workstation & Shift: Assembly-Cell-03 | Shift-B | Operator ID: OP-19
    ↓
Production Batch: Batch B-042 (500 Units Total, 112 Inspected, 388 In-Flight)
    ↓
Component Lot: Sub-Lot #M8-9941 (Black Oxide Flange Bolt)
    ↓
Upstream Supplier: Vendor-X (Apex Industrial Fasteners Ltd.)
    ↓
Governing SLA Contract: Master Supply Agreement MSA-2026-09, Clause 4.2
    ↓
Financial Exposure: 388 in-flight units × $28.50/unit rework = $11,058
```

#### Why This Layer Matters

Without traceability, a "missing bolt" is a quality department's problem. WITH traceability, it's:
- A **production** problem (388 uninspected units may be defective)
- A **procurement** problem (Vendor-X supplied the lot)
- A **financial** problem (\$11,058 exposure if not contained)
- A **legal** problem (MSA Clause 4.2 governs this exact failure mode)

This is what transforms INDUS-X from a "CV project" into an "enterprise platform."

---

### Layer 6: Closed-Loop Automation & Contextual Reasoning

**Location in Stack:** Dual-path execution engine (ResolutionOrchestrator).

**Purpose:** Takes two simultaneous actions — immediate physical containment (deterministic) and contractual liability analysis (LLM-powered).

#### Path A: Deterministic Closed-Loop Floor Automation

The moment QI-0041 is consolidated, the system dispatches simulated industrial control commands:

| Command | Target | Action | Trigger Rule |
|---|---|---|---|
| `ACTUATOR_CMD` | Pneumatic Diverter Arm #03 | PULSE — eject unit to rework spur | Any consolidated incident |
| `CONVEYOR_CMD` | Line Conveyor Motor | THROTTLE — 1.2 m/s → 0.6 m/s | ≥ 2 incidents within 60 seconds |
| `CNC_OFFSET_CMD` | Station-03 Torque Head | FLAG — schedule calibration check | Structural absence type |

```python
class FloorAutomationService:
    def dispatch_containment(self, incident: ConsolidatedIncident) -> List[MQTTCommand]:
        commands = []
        
        # Always: Eject the defective unit
        commands.append(MQTTCommand(
            topic="factory/cell-03/diverter",
            payload={"action": "PULSE_EJECT", "incident_id": incident.incident_id},
            risk_tier=1  # Autonomous — single unit, reversible
        ))
        
        # Conditional: Throttle line if pattern detected
        recent_incidents = self.db.count_incidents_last_n_seconds(60)
        if recent_incidents >= 2:
            commands.append(MQTTCommand(
                topic="factory/conveyor/speed",
                payload={"action": "THROTTLE", "target_speed": 0.6, "reason": "multi_incident_pattern"},
                risk_tier=2  # Requires human approval
            ))
        
        # Conditional: Flag station for calibration
        if incident.defect_type == "STRUCTURAL_ABSENCE":
            commands.append(MQTTCommand(
                topic="factory/cell-03/maintenance",
                payload={"action": "FLAG_CALIBRATION", "component": "torque_head"},
                risk_tier=1
            ))
        
        return commands
```

**Important note on honesty:** In the hackathon context, these MQTT commands are **simulated** — they write to a log and display in the UI. The system does not connect to real PLCs. The message schema is designed to match real industrial protocols (Siemens S7 / Allen-Bradley format) so the architecture is production-portable.

#### Path B: RAG-Grounded LLM Contract Reasoning

**Why an LLM is required here:** Deterministic code handles math, tracking, and hash chains. But it **cannot** read unstructured legal contract language like:

> *"4.2 Critical Structural Components: Supplier warrants that all Class-A structural fasteners shall conform to DIN 6921 M8 flange bolt specification with black-oxide coating per MIL-DTL-13924. The Acceptable Quality Level for critical structural defects shall not exceed 0.5% per lot under ISO 2859-1 Level II single sampling. Non-conformance authorizes Buyer to quarantine affected lots and apply invoice holdback of 15% on the affected purchase order pending resolution..."*

And synthesize a structured liability assessment that matches specific evidence to specific contract sub-clauses.

#### RAG Architecture (Not Hardcoded Lookup)

```python
class SLAReasoningAgent:
    def __init__(self, llm_client, vector_store):
        self.llm = llm_client
        self.vector_store = vector_store  # ChromaDB with chunked contract text
    
    async def generate_liability_dossier(self, incident: ConsolidatedIncident,
                                          batch_context: BatchContext) -> LiabilityDossier:
        # Step 1: Retrieve relevant contract clauses via semantic search
        query = (f"liability for {incident.defect_type} defect in "
                 f"{batch_context.component_name} from {batch_context.vendor_name}")
        
        relevant_clauses = self.vector_store.query(query, n_results=5)
        
        # Step 2: Construct grounded prompt with evidence + retrieved clauses
        prompt = f"""You are a Quality Liability Assessment Agent.

EVIDENCE (from tamper-evident provenance chain):
- Incident: {incident.incident_id}
- Defect Type: {incident.defect_type}
- Confidence: {incident.confidence_avg:.2f}
- Provenance Hash: {incident.provenance_hash}
- Batch: {batch_context.batch_id} ({batch_context.total_units} units, {batch_context.inspected} inspected)
- Supplier: {batch_context.vendor_name}

RELEVANT CONTRACT CLAUSES (retrieved from MSA):
{self._format_clauses(relevant_clauses)}

TASK: Produce a structured Liability Assessment with:
1. Which specific clause(s) are breached and why
2. Whether the observed defect rate exceeds the contractual AQL threshold
3. Recommended containment actions
4. Recommended financial remedies per contract terms
5. Cite exact clause numbers and quote relevant language

If evidence is insufficient to determine breach, state that explicitly."""
        
        response = await self.llm.generate(prompt)
        return self._parse_dossier(response, relevant_clauses)
```

**Offline Fallback:** For venue Wi-Fi failure, the system maintains a **cached response library** for each scenario. The UI shows `[CACHED]` indicator to maintain honesty.

---

### Layer 7: Risk-Aware Governance & RBAC Human Gates

**Location in Stack:** Policy enforcement middleware between Layer 6 recommendations and database mutations (GovernanceGateService).

**Purpose:** Enforces the core architectural principle: **"Autonomous where safe. Human-controlled where consequential."**

#### Three-Tier Risk Model

| Tier | Risk Level | Action Scope | Execution Mode | Required RBAC Role |
|---|---|---|---|---|
| **Tier 1** | Low | Log incident, seal hash, pulse diverter for single-unit ejection, alert operator | 100% Autonomous (zero latency) | `SYSTEM_AUTO` |
| **Tier 2** | Medium | Quarantine full Batch B-042 (500 units), throttle line speed, schedule maintenance | Agent Recommends → 1-Click Human Gate | `QUALITY_ENGINEER` |
| **Tier 3** | High | Dispatch Supplier Quality Case (SQC-882), apply contractual invoice holdback | Agent Synthesizes Dossier → Authorized Sign-Off | `PLANT_MANAGER` |

#### Why This Matters

Most hackathon projects do one of two things:
1. **Passive:** Display everything, automate nothing → *"So your system just shows charts?"*
2. **Reckless:** Automate everything including financial decisions → *"Your AI auto-deducts money from vendors?"*

INDUS-X threads the needle: **fast where speed matters (eject the part in <1 second), careful where consequences matter (never auto-hold an invoice).**

#### Role Switcher UI

The top bar includes an interactive Role Switcher: `[Operator] [Quality Engineer] [Plant Manager]`

When judges switch roles, they see buttons **lock and unlock** based on authority level:

```
Role: Operator
├─ [View Incident Details]     ✅ Enabled
├─ [Approve Batch Quarantine]  🔒 Locked — requires Quality Engineer
└─ [Authorize Invoice Hold]    🔒 Locked — requires Plant Manager

Role: Quality Engineer  
├─ [View Incident Details]     ✅ Enabled
├─ [Approve Batch Quarantine]  ✅ Enabled — APPROVE / REJECT
└─ [Authorize Invoice Hold]    🔒 Locked — requires Plant Manager

Role: Plant Manager
├─ [View Incident Details]     ✅ Enabled
├─ [Approve Batch Quarantine]  ✅ Enabled
└─ [Authorize Invoice Hold]    ✅ Enabled — AUTHORIZE / REJECT
```

Every approval/rejection is recorded into the Chain of Custody log with timestamp and actor identity.

---

### Layer 8: Supplier Intelligence & ISO Switching (The "Learn" Stage)

**Location in Stack:** Analytical aggregation engine across historical and current records (SupplierIntelligenceEngine).

**Purpose:** Turns isolated defect detections into macro supply-chain intelligence and closes the feedback loop.

#### 8A: Cross-Incident Pattern Correlation

The system connects incidents across production runs:

```
Batch B-038 (Monday):    Surface crack         → Vendor-X
Batch B-040 (Wednesday): Wrong fastener class   → Vendor-X  
Batch B-042 (Today):     Missing structural bolt → Vendor-X

⚠️ ALERT: Cross-Batch Pattern Detected
   Vendor-X: 3 quality incidents / 2 component families / 5 production batches
   Pattern escalation: Surface → Wrong Part → Missing Part (SEVERITY INCREASING)
```

#### 8B: Volume-Normalized, Severity-Weighted Risk Scoring

**The problem with raw counts:** Vendor-A had 8 minor scratches across 10,000 units. Vendor-X had 3 structural defects across 500 units. Raw counts say Vendor-A is worse (8 > 3). Reality says Vendor-X is catastrophically worse.

**INDUS-X Risk Formula:**

```
Risk Score = min(100, α × (Σ(Defectᵢ × w_severity_i) / Total_Units_Shipped × 1000) + β × BatchRecurrenceRate)
```

**Severity weights grounded in FMEA (Failure Mode and Effects Analysis):**

| Defect Type | FMEA Severity (1-10) | Weight | Justification |
|---|---|---|---|
| Structural Absence | 9 (safety-critical) | 3.0 | Missing fastener → structural failure → injury risk |
| Wrong Component | 6 (functional degradation) | 2.0 | Wrong material → premature wear → field return |
| Surface Scratch | 3 (cosmetic) | 1.0 | Visual defect → customer complaint → no safety impact |

**Computed example:**

```
Vendor-X: (3×3.0 + 0×2.0 + 0×1.0) / 500 × 1000 = 18.0
           + β × 0.60 (3 incidents in 5 batches) = 18.0 + 60.0 = 78.0/100

Vendor-A: (0×3.0 + 0×2.0 + 8×1.0) / 10000 × 1000 = 0.8  
           + β × 0.10 (1 incident pattern) = 0.8 + 10.0 = 10.8/100
```

Vendor-X scores 78/100 (high risk). Vendor-A scores 10.8/100 (low risk). The formula correctly identifies the real threat.

#### 8C: ISO 2859 / AQL Automated Inspection Switching

When Vendor-X crosses a Risk Score threshold of 75/100, INDUS-X triggers a deterministic ISO 2859-1 switching rule:

```
Vendor-X Risk Score: 78/100 (exceeds threshold of 75)
    ↓
ACTION: Escalate upcoming Batch B-043 from:
    NORMAL INSPECTION → TIGHTENED PRE-LINE AUDIT (Level II)
    
Meaning: Instead of sampling 80 units from the next 500-unit batch,
         sample 125 units under tightened acceptance criteria.
```

**Why ISO 2859 instead of "AI prediction":** Every hackathon team claims "predictive AI" for defect forecasting. These claims are scientifically indefensible with 3-5 data points. ISO 2859-1 is a **60-year-old international standard** used by every major manufacturer. It's deterministic, auditable, and legally recognized. Judges with industrial experience will respect this choice.

#### 8D: Operator Feedback Loop (Closing "Learn")

After an incident is resolved, the system captures operator feedback:

```
┌─────────────────────────────────────────────┐
│  Incident QI-0041 has been resolved.        │
│                                             │
│  Was this classification correct?           │
│                                             │
│  [✓ Correct]  [Wrong Class]  [False Pos.]   │
└─────────────────────────────────────────────┘
```

This feedback is logged and displayed as a **Model Accuracy Tracker**:

| Metric | Value | Trend |
|---|---|---|
| Confirmed True Positives | 94.2% | — |
| Operator-Reported False Positives | 5.8% | ↓ Improving |
| Total Operator Verdicts | 47 | — |

**Note:** The system does NOT automatically retrain the model based on feedback (that would be irresponsible in a hackathon). It captures the signal for future retraining, demonstrating **MLOps awareness**.

#### 8E: Cost-of-Inaction Calculator

Each incident displays a real-time economic impact calculation:

```
┌─────────────────────────────────────────────┐
│  💰 Economic Impact — QI-0041               │
│                                             │
│  If this defect reached the customer:       │
│  → 388 at-risk units × $36.50 recall cost   │
│  → Total recall liability: $14,162          │
│                                             │
│  Cost of catching it now:                   │
│  → Rework cost: 388 × $4.20 = $1,630       │
│                                             │
│  ✅ NET SAVINGS: $12,532                    │
│  📊 Cumulative Session Savings: $41,460     │
└─────────────────────────────────────────────┘
```

**Formula:**

```
Savings = (Units_at_risk × Unit_recall_cost) - (Units_at_risk × Unit_rework_cost)
```

---


## 6. Data Schema & API Contract

### 6.1 Core SQLite Tables (5 Tables)

```sql
-- Table 1: Quality Incidents
CREATE TABLE incidents (
    id              TEXT PRIMARY KEY,           -- e.g., "QI-0041"
    scenario_type   INTEGER NOT NULL,           -- 0=Pass, 1=Absence, 2=WrongPart, 3=Crack
    defect_class    TEXT,                        -- "STRUCTURAL_ABSENCE" | "WRONG_COMPONENT" | "SURFACE_ANOMALY"
    raw_frame_count INTEGER DEFAULT 0,          -- Total raw detections before consolidation
    confidence_avg  REAL,                       -- Average confidence across evidence frames
    best_frame_path TEXT,                       -- Path to highest-quality evidence frame
    crop_path       TEXT,                       -- Path to anomaly crop
    heatmap_path    TEXT,                       -- Path to Grad-CAM explainability overlay
    batch_id        TEXT REFERENCES batches(batch_id),
    vendor_id       TEXT REFERENCES vendors(vendor_id),
    status          TEXT DEFAULT 'OPEN',        -- OPEN | CONSOLIDATED | QUARANTINED | NCR_ISSUED | CLOSED
    risk_tier       INTEGER DEFAULT 1,          -- 1=Low, 2=Medium, 3=High
    cost_if_missed  REAL,                       -- Calculated recall liability
    cost_if_caught  REAL,                       -- Calculated rework cost
    net_savings     REAL,                       -- cost_if_missed - cost_if_caught
    created_at      TEXT NOT NULL,              -- ISO-8601 millisecond timestamp
    resolved_at     TEXT,
    resolved_by     TEXT,
    operator_verdict TEXT                        -- "CORRECT" | "WRONG_CLASS" | "FALSE_POSITIVE" | NULL
);

-- Table 2: Provenance Hash Chain
CREATE TABLE provenance_chain (
    block_index     INTEGER PRIMARY KEY,
    incident_id     TEXT NOT NULL REFERENCES incidents(id),
    timestamp_iso   TEXT NOT NULL,
    camera_id       TEXT NOT NULL,
    frame_sha256    TEXT NOT NULL,
    metadata_json   TEXT NOT NULL,
    prev_hash       TEXT NOT NULL,
    curr_hash       TEXT NOT NULL
);

-- Table 3: Batches & Traceability
CREATE TABLE batches (
    batch_id        TEXT PRIMARY KEY,           -- e.g., "B-042"
    component_name  TEXT NOT NULL,              -- e.g., "M8 Black Oxide Flange Bolt"
    component_lot   TEXT,                       -- e.g., "M8-9941"
    workstation_id  TEXT NOT NULL,              -- e.g., "CELL-03"
    shift_id        TEXT,                       -- e.g., "SHIFT-B"
    operator_id     TEXT,                       -- e.g., "OP-19"
    vendor_id       TEXT REFERENCES vendors(vendor_id),
    total_units     INTEGER NOT NULL,
    inspected_units INTEGER DEFAULT 0,
    defective_units INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'IN_PRODUCTION', -- IN_PRODUCTION | QUARANTINED | RELEASED | REJECTED
    sla_contract_id TEXT,                       -- e.g., "MSA-2026-09"
    unit_cost       REAL DEFAULT 28.50,
    rework_cost     REAL DEFAULT 4.20,
    recall_cost     REAL DEFAULT 36.50
);

-- Table 4: Vendors / Suppliers
CREATE TABLE vendors (
    vendor_id               TEXT PRIMARY KEY,
    vendor_name             TEXT NOT NULL,
    total_units_shipped     INTEGER DEFAULT 0,
    total_incidents         INTEGER DEFAULT 0,
    structural_incidents    INTEGER DEFAULT 0,
    wrong_component_incidents INTEGER DEFAULT 0,
    surface_incidents       INTEGER DEFAULT 0,
    batch_recurrence_rate   REAL DEFAULT 0.0,
    normalized_risk_score   REAL DEFAULT 0.0,
    inspection_regime       TEXT DEFAULT 'NORMAL',  -- NORMAL | TIGHTENED_ISO_LVL_2
    last_incident_date      TEXT,
    risk_trend              TEXT DEFAULT 'STABLE'    -- STABLE | INCREASING | DECREASING
);

-- Table 5: Chain of Custody Log
CREATE TABLE custody_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id     TEXT NOT NULL REFERENCES incidents(id),
    timestamp_iso   TEXT NOT NULL,
    state_from      TEXT,
    state_to        TEXT NOT NULL,
    action          TEXT NOT NULL,
    actor           TEXT NOT NULL,               -- "SYSTEM_AUTO" or user identity
    actor_role      TEXT NOT NULL,               -- "SYSTEM" | "OPERATOR" | "QUALITY_ENGINEER" | "PLANT_MANAGER"
    notes           TEXT,
    mqtt_payload    TEXT                          -- JSON of any automation command dispatched
);
```

### 6.2 Core FastAPI Endpoints

| Method | Endpoint | Purpose | Auth Level |
|--------|----------|---------|------------|
| `POST` | `/api/inspect/run/{scenario_id}` | Stream scenario frames via SSE, run full pipeline, return live telemetry | Any |
| `GET` | `/api/inspect/telemetry` | Get current session stats (raw detections, incidents, noise reduction) | Any |
| `GET` | `/api/incidents` | List all incidents with filtering by status, defect type, vendor | Any |
| `GET` | `/api/incidents/{id}` | Get full incident detail including evidence frames | Any |
| `GET` | `/api/incidents/{id}/dossier` | Get traceability tree + MQTT log + LLM liability dossier | Any |
| `POST` | `/api/incidents/{id}/feedback` | Submit operator verdict (correct/wrong/false-positive) | Operator+ |
| `POST` | `/api/governance/{id}/decide` | Submit governance decision (approve/reject quarantine, NCR, holdback) | Per Tier |
| `GET` | `/api/provenance/verify` | Recompute and verify full SHA-256 hash chain | Any |
| `POST` | `/api/provenance/simulate-tamper` | Mutate a record to demo tamper detection (demo only) | Any |
| `GET` | `/api/vendors` | List all vendors with risk scores and inspection regimes | Any |
| `GET` | `/api/vendors/{id}/risk-history` | Get vendor risk score trend over time | Any |
| `GET` | `/api/analytics/cost-savings` | Get cumulative cost-of-inaction savings | Any |
| `GET` | `/api/analytics/model-accuracy` | Get operator feedback accuracy metrics | Any |

### 6.3 WebSocket Channels

| Channel | Purpose | Payload |
|---------|---------|---------|
| `ws://localhost:8000/ws/video/{scenario_id}` | Live video stream with detection overlays | Base64-encoded annotated frames |
| `ws://localhost:8000/ws/telemetry` | Real-time pipeline metrics | JSON with frame count, incident count, noise reduction %, latency |
| `ws://localhost:8000/ws/alerts` | Push notifications for new incidents and governance actions | JSON incident summaries |

---

## 7. User Interface — Command Center Design

### 7.1 Layout Philosophy

Single-screen, zero-scroll, dark-mode industrial command center divided into **4 synchronized quadrants** with a persistent top pipeline bar and role switcher.

### 7.2 Wireframe Specification

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  INDUS-X │ Industrial Quality Intelligence & Resolution      [Role: Quality Engineer ▾]  │
│  Pipeline: [1.SEE] ──► [2.VERIFY] ──► [3.TRACE] ──► [4.DECIDE & ACT] ──► [5.LEARN]     │
│  Mode: [● INDUS-X Mode] [○ Standard Mode — Split Comparison]                            │
├───────────────────────────────────────────┬───────────────────────────────────────────────┤
│  Q1: MULTI-DEFECT TEST BENCH             │  Q2: CONSOLIDATION & PROVENANCE               │
│                                          │                                               │
│  Scenarios:                              │  Active Incident: QI-0041 [CONSOLIDATED]      │
│  [0:Normal] [1:Missing] [2:Wrong] [3:Crack] │                                            │
│                                          │  Frame Dedup: 27 Raw → 1 Record               │
│  ┌──────────────────────────────────┐    │  Live Noise Reduction: 96.3% (810ms)          │
│  │  [Video Feed]                    │    │                                               │
│  │  + CAD Reference Grid Overlay    │    │  Hash Chain: Block #14 [✓ VERIFIED]           │
│  │  + Detection Bounding Boxes      │    │  Prev: 0x8f3a..91b2                           │
│  │  + Grad-CAM Heatmap Toggle       │    │  Curr: 0x4c91..e704                           │
│  │                                  │    │  [Verify Chain] [Simulate Tamper]             │
│  │  Slot A [✓]      Slot B [✓]     │    │                                               │
│  │  Slot C [✗ ABS]   Slot D [✓]    │    │  Closed-Loop MQTT Containment:                │
│  └──────────────────────────────────┘    │  └─ Diverter #03: PULSED (Part Ejected)       │
│                                          │  └─ Conveyor: NOMINAL (no throttle needed)    │
│  Perturbation: [Standard ▾]             │                                               │
│  [▶ Run Scenario]  [⏸ Pause]            │  Explainability: [Toggle Heatmap]             │
├───────────────────────────────────────────┼───────────────────────────────────────────────┤
│  Q3: TRACEABILITY & SLA GOVERNANCE       │  Q4: SUPPLIER RISK INTELLIGENCE               │
│                                          │                                               │
│  Blast Radius:                           │  ⚠️ EMERGING PATTERN: Vendor-X (Apex Ltd)     │
│  QI-0041 → Batch B-042 → Station-03     │  3 Incidents / 2 Part Families / 5 Runs       │
│  → Vendor-X → MSA Clause 4.2            │                                               │
│                                          │  Volume-Normalized Risk Scores:               │
│  💰 Cost of Inaction:                    │  ┌─────────────────────────────────────┐      │
│  Recall liability:  $14,162              │  │ Vendor-X (Apex):      78/100 ██████▓│      │
│  Rework cost:       $1,630               │  │ Vendor-A (Steelworks): 14/100 ██    │      │
│  NET SAVINGS:       $12,532              │  │ Vendor-B (Precision):  22/100 ███   │      │
│                                          │  └─────────────────────────────────────┘      │
│  SLA Reasoning Agent:                    │                                               │
│  "Structural absence violates Cl. 4.2   │  ISO 2859 Switching:                          │
│   (0.5% Critical AQL). Recommend Batch  │  Batch B-043 escalated:                       │
│   B-042 Quarantine & Supplier NCR."     │  NORMAL → TIGHTENED PRE-LINE AUDIT II         │
│  [SOURCE: MSA-2026-09, §4.2, Score:0.94]│                                               │
│                                          │  Model Accuracy (Operator Feedback):          │
│  Tier-2 Governance Gate:                 │  True Positives: 94.2%                        │
│  [✓ APPROVE QUARANTINE & NCR] [REJECT]   │  False Positives: 5.8% (↓ improving)         │
│                                          │                                               │
│  Cumulative Savings: $41,460             │  [📊 Open Benchmark Metrics]                  │
└───────────────────────────────────────────┴───────────────────────────────────────────────┘
```

### 7.3 Split Comparison Mode (Dumb vs. Smart)

Toggle `[Standard Mode — Split Comparison]` to run the SAME video through two paths simultaneously:

| Standard Mode (Left Half) | INDUS-X Mode (Right Half) |
|---|---|
| 27 alerts flooding the alert list in real-time | 1 consolidated incident with peak evidence |
| No hash chain, no provenance | Hash chain block #14 verified |
| "Defect detected" — no context | Full blast radius to vendor + contract |
| Red dashboard, no automated action | Diverter pulsed, containment dispatched |
| No financial quantification | \$12,532 net savings calculated |

**Why this is the most powerful demo technique:** Before/after, side by side, same data. The contrast is visceral.

---


## 8. 3-Minute Demo Choreography

Every second of the pitch is planned. No dead air, no "let me just..." moments.

### The Script

| Time | Action | What Judges See | What You Say |
|---|---|---|---|
| 0:00–0:15 | **Problem Hook** | Slide or spoken intro (no slides needed if UI is ready) | *"A 30-FPS camera watching a conveyor belt creates 27 duplicate alerts for a single defective part. Operators ignore them. Suppliers dispute the evidence. Factories lose millions. INDUS-X fixes everything after detection."* |
| 0:15–0:30 | **Architecture Flash** | Point to the pipeline bar: SEE → VERIFY → TRACE → DECIDE → ACT → LEARN | *"Our platform is 8 layers. Watch them fire in sequence."* |
| 0:30–1:00 | **Scenario 0 (Baseline)** | Click [0: Normal]. Video plays. All 4 grid slots show ✓. Zero incidents created. | *"First — our system does NOT false-positive. All bolts present, all checks pass, no incident."* |
| 1:00–1:45 | **Scenario 1 (Missing Bolt)** | Click [1: Missing Bolt]. Video plays. Slot C shows ✗ ABSENT. Counter shows "27 raw → 1 incident." Noise reduction: 96.3%. Hash chain seals Block #14. Diverter pulses. | *"Now watch: 27 raw detections for one moving part — consolidated into a single verified incident. The hash chain seals tamper-evident provenance in real-time. The diverter auto-ejects the part."* |
| 1:45–2:15 | **Blast Radius + Cost** | Q3 lights up: QI-0041 → Batch B-042 → Vendor-X → MSA Clause 4.2. Cost of Inaction shows \$12,532 savings. LLM dossier appears with [SOURCE] citations. | *"One defect traces to 388 at-risk units, a specific supplier contract, and a $12,000 savings. Our LLM reads the actual contract and cites the exact clause that's breached."* |
| 2:15–2:30 | **Governance Gate** | Switch Role to Plant Manager. All buttons unlock. Click APPROVE. Chain of Custody log updates. | *"Autonomous where safe — the diverter fired instantly. Human-controlled where consequential — batch quarantine requires Quality Engineer approval, invoice holdback requires Plant Manager sign-off."* |
| 2:30–2:45 | **Tamper Demo** | Click [Simulate Tamper]. Verifier immediately shows "BREACH AT BLOCK #7." | *"And if anyone tampers with historical evidence — we catch it in under a second. Every hash is chained to every previous hash."* |
| 2:45–3:00 | **Supplier Intelligence** | Q4 shows Vendor-X at 78/100 risk score. ISO switching escalates B-043 to Tightened. Model accuracy shows 94.2%. | *"Three incidents across five batches. Volume-normalized risk scoring — not raw counts. ISO 2859 automatically tightens inspection. And operators can flag false positives to track model accuracy over time."* |

### Backup Scenarios (For Q&A)

If judges ask to see more, you have **Scenario 2 (Wrong Component)** and **Scenario 3 (Surface Crack)** ready. These prove the platform handles diverse failure modes through the same pipeline.

If judges ask about robustness, toggle the **Perturbation** dropdown to show the system handles angle shifts, low light, and glare.

---

## 9. Non-Functional Requirements & Guardrails

### 9.1 What We Build

| Requirement | Specification | Rationale |
|---|---|---|
| **100% Offline Execution** | Every model weight (yolov11n.pt), video clip, SQLite database, vector store, and LLM response cache resides locally | Venue Wi-Fi failure has zero impact on demo |
| **Dynamic Metrics Only** | Every number on the dashboard is calculated from the active test run | No hardcoded benchmarks — judges can verify |
| **Latency Budget** | Full pipeline (frame → incident → hash → display) completes in < 1.5 seconds | 3-minute pitch never stalls waiting for processing |
| **Single-Command Startup** | `python run.py` or `docker compose up` launches the entire platform | No multi-terminal setup during demo |
| **Deterministic Demo** | Same scenario always produces same results (seeded batch data, consistent model weights) | Eliminates "it worked on my machine" risk |

### 9.2 What We Do NOT Build (Explicit Scope Boundaries)

| We Do NOT | Why | What We Say If Asked |
|---|---|---|
| Connect to real PLCs/SCADA | No hardware at venue | *"The MQTT schema matches Siemens S7 payloads — it's protocol-portable"* |
| Retrain models from feedback | Irresponsible in 36 hours | *"We capture the signal. Retraining requires validation cycles we respect."* |
| Claim "predictive AI" | Indefensible with 3-5 data points | *"We use ISO 2859 — a 60-year international standard. Deterministic and auditable."* |
| Use real blockchain | Overkill, slow, buzzword bait | *"Append-only hash chain gives identical tamper-evidence without the overhead."* |
| Auto-execute financial decisions | Ethically wrong | *"Our governance model requires human sign-off for any financial action."* |
| Process live camera feeds | Unreliable at venue with lighting/angle variance | *"Our architecture supports live input. We use controlled test sequences for demo reliability."* |

---

## 10. Build Roadmap — 36-Hour Sprint Plan

### Phase 1: Foundation (Hours 0–8)

| Task | Owner Hint | Hours | Deliverable |
|---|---|---|---|
| Project scaffolding (FastAPI + React/Next.js + SQLite) | Backend | 1 | Running skeleton with hot reload |
| YOLOv11 adapter + inference pipeline | ML | 3 | Working detection on test frames |
| Reference grid evaluator (absence + class mismatch) | ML | 3 | Tri-modal defect findings |
| Test bench video player + scenario selector | Frontend | 1 | Scenario buttons stream frames |

**Milestone at Hour 8:** Can run a scenario, get detections, and see defect findings in console.

### Phase 2: Core Intelligence (Hours 8–18)

| Task | Owner Hint | Hours | Deliverable |
|---|---|---|---|
| Incident consolidation engine (4-gate pipeline) | Backend | 4 | 27 frames → 1 incident with live telemetry |
| Provenance hash chain service | Backend | 3 | Blocks sealed, verify + tamper sim working |
| Traceability resolver (batch → vendor → contract lookup) | Backend | 2 | Full blast-radius trace from incident ID |
| Database seeding (batches, vendors, contracts) | Backend | 1 | Realistic factory data populated |

**Milestone at Hour 18:** Full pipeline runs end-to-end. Incident created, hash sealed, traceability resolved.

### Phase 3: Automation & Intelligence (Hours 18–26)

| Task | Owner Hint | Hours | Deliverable |
|---|---|---|---|
| MQTT floor automation simulation | Backend | 1 | Containment commands logged and displayed |
| LLM liability agent + ChromaDB RAG | Backend/ML | 4 | Contract clause retrieval + dossier generation |
| Governance gate service + RBAC | Backend | 2 | Tier 1/2/3 enforcement with role checks |
| Supplier risk scoring + ISO switching | Backend | 2 | Volume-normalized scores, regime escalation |

**Milestone at Hour 26:** Automation dispatches, LLM generates dossiers, governance gates enforce roles.

### Phase 4: UI & Polish (Hours 26–34)

| Task | Owner Hint | Hours | Deliverable |
|---|---|---|---|
| 4-quadrant command center layout | Frontend | 3 | Dark-mode industrial dashboard |
| Q1: Video feed + CAD overlay + heatmap toggle | Frontend | 2 | Live annotated video with explainability |
| Q2: Consolidation metrics + provenance display | Frontend | 1 | Real-time noise reduction + hash chain |
| Q3: Traceability tree + cost calculator + governance buttons | Frontend | 1 | Blast radius + savings + approve/reject |
| Q4: Risk scores + ISO switching + model accuracy | Frontend | 1 | Bar charts + regime badges + feedback stats |

**Milestone at Hour 34:** Full UI working. All 4 quadrants populated with live data.

### Phase 5: Demo Hardening (Hours 34–36)

| Task | Everyone | Hours | Deliverable |
|---|---|---|---|
| End-to-end demo rehearsal (all 4 scenarios) | All | 1 | Smooth 3-minute run-through |
| Edge case testing + crash recovery | All | 0.5 | No scenario crashes the app |
| Split comparison mode (if time) | Frontend | 0.5 | Standard vs. INDUS-X side-by-side |

---

## 11. Risk Register & Mitigation Playbook

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **YOLOv11 doesn't detect custom defect classes well** | Medium | Critical | Use YOLOv11n pretrained on COCO + fine-tune on 50-100 annotated frames. Fallback: hardcoded detection zones for demo. |
| **LLM API unavailable (no Wi-Fi)** | High | Medium | Pre-cache all LLM responses for each scenario. Show `[CACHED]` badge for honesty. |
| **Frontend takes too long** | Medium | High | Start with a minimal functional UI (even terminal-based). Polish in Phase 4. |
| **Hash chain verification is slow with many blocks** | Low | Low | SQLite handles 1000+ blocks in <100ms. Not a real concern. |
| **Model produces false positives on Scenario 0** | Medium | High | Tune confidence threshold τ. Add 3-frame persistence filter. Test extensively. |
| **Demo laptop GPU is weak** | Medium | Medium | Use YOLOv11n (nano). Process at 5-10 FPS, not 30. Quality > speed for demo. |
| **Team member unavailable** | Low | Critical | Every layer has a documented interface. Any member can pick up another's work. |

---

## 12. Judge Q&A Defense Playbook

### Technical Questions

| Question | Defense |
|---|---|
| *"How do you detect a missing bolt if there's nothing to detect?"* | *"We don't detect absence — we verify presence. The reference grid defines where bolts SHOULD be. When a slot has zero detections for 5+ consecutive frames while adjacent slots are confirmed, we flag structural absence. It's geometric constraint verification, not hallucination."* |
| *"What if I use a different model?"* | *"The BasePerceptionProvider interface takes 4 methods to implement. Swap YOLO for EfficientDet, Detectron2, or even a cloud API. Zero downstream changes."* |
| *"Aren't your numbers hardcoded?"* | *"Run any scenario right now. Every metric — noise reduction, latency, cost savings — is computed live from the stream. Change the video and the numbers change."* |
| *"Is this actually a blockchain?"* | *"No, and deliberately not. A blockchain requires distributed consensus which adds latency and complexity we don't need. An append-only hash chain provides identical tamper-evidence guarantees for a single-authority system. Want to see? [clicks Simulate Tamper]"* |
| *"How does your AI prediction work?"* | *"We don't claim AI prediction — that's indefensible with limited data. We use ISO 2859-1, a 60-year international standard for acceptance sampling. When a vendor crosses our risk threshold, we escalate inspection deterministically. Auditable, legally recognized, scientifically sound."* |

### Business Questions

| Question | Defense |
|---|---|
| *"What's the ROI?"* | *"Look at Q3 — this single incident saved $12,532 by catching it at rework cost instead of recall cost. Across today's session, cumulative savings are $41,460. In a real factory running 24/7, multiply by 300 production days."* |
| *"Who's your customer?"* | *"Any discrete manufacturer running visual inspection — automotive, electronics, aerospace. The immediate pain is Tier 1/2 automotive suppliers who face chargebacks from OEMs and need provenance to dispute."* |
| *"What about existing solutions like Cognex or Keyence?"* | *"They stop at detection. They'll tell you 'defect found.' They won't consolidate alerts, trace to suppliers, generate liability dossiers, or enforce governance tiers. INDUS-X is the operational layer that sits DOWNSTREAM of any detection system — including theirs."* |

### Ethical Questions

| Question | Defense |
|---|---|
| *"What if the AI is wrong and you eject a good part?"* | *"Tier 1 single-unit ejection is the lowest-cost error — that part goes to a rework spur for human re-inspection, not to scrap. The 5-frame persistence filter minimizes false ejections. And our operator feedback loop tracks false positive rate so we know exactly how often this happens."* |
| *"Should AI be making financial decisions about suppliers?"* | *"It shouldn't, and ours doesn't. The LLM synthesizes a dossier and recommends. The governance gate requires a Plant Manager's explicit sign-off before any invoice holdback. Every approval is logged in the chain of custody with actor identity and timestamp."* |

---

## Appendix A: Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Backend API | FastAPI (Python) | Async, fast, WebSocket support, excellent for ML integration |
| Computer Vision | YOLOv11n (Ultralytics) | Nano model for laptop GPU, well-documented, fast inference |
| Object Tracking | ByteTrack | Lightweight, high-accuracy multi-object tracking |
| Database | SQLite | Zero-config, file-based, perfect for offline demo |
| Vector Store | ChromaDB | Runs locally, no server required, Python-native |
| LLM | Gemini API (with cached fallback) | Powerful reasoning, or local Ollama as backup |
| Frontend | React + Tailwind CSS (dark mode) | Component-based, rapid prototyping, industrial aesthetic |
| Hashing | Python hashlib (SHA-256) | Standard library, no dependencies |
| Explainability | pytorch-grad-cam | Attention heatmaps on YOLO backbone |
| Video Processing | OpenCV | Industry standard, handles all codecs |

## Appendix B: Seed Data Samples

### Vendor Seed Data

```json
[
  {
    "vendor_id": "VND-X",
    "vendor_name": "Apex Industrial Fasteners Ltd.",
    "total_units_shipped": 5000,
    "structural_incidents": 2,
    "wrong_component_incidents": 1,
    "surface_incidents": 0,
    "normalized_risk_score": 62.0,
    "inspection_regime": "NORMAL"
  },
  {
    "vendor_id": "VND-A",
    "vendor_name": "Steelworks Component Supply Co.",
    "total_units_shipped": 10000,
    "structural_incidents": 0,
    "wrong_component_incidents": 0,
    "surface_incidents": 8,
    "normalized_risk_score": 10.8,
    "inspection_regime": "NORMAL"
  }
]
```

### Contract Clause Seed (for RAG)

```text
MASTER SUPPLY AGREEMENT MSA-2026-09
Between: Meridian Manufacturing Corp. ("Buyer") 
And: Apex Industrial Fasteners Ltd. ("Supplier")

Section 4: Quality Assurance & Acceptance Criteria

4.1 General Quality Standard
Supplier warrants that all components delivered shall conform to the specifications 
set forth in Exhibit A (Component Specifications) and shall be free from defects in 
material and workmanship.

4.2 Critical Structural Components  
All Class-A structural fasteners shall conform to DIN 6921 M8 flange bolt 
specification with black-oxide coating per MIL-DTL-13924. The Acceptable Quality 
Level (AQL) for critical structural defects shall not exceed 0.5% per lot under 
ISO 2859-1 Level II single sampling plan. Non-conformance authorizes Buyer to:
  (a) Quarantine the affected lot and all in-transit shipments from the same 
      production run;
  (b) Apply invoice holdback of 15% on the affected purchase order pending 
      resolution of formal Supplier Quality Case;
  (c) Escalate incoming inspection to Tightened Inspection per ISO 2859-1 
      switching rules for subsequent 5 lots.

4.3 Surface Finish & Cosmetic Standards
Surface defects (scratches, tool marks, discoloration) shall not exceed 1.0% AQL 
under normal inspection. Cosmetic non-conformances do not trigger structural hold 
procedures but are tracked for vendor scorecard review.
```

---

## Appendix C: Key Formulas Reference

**Incident Consolidation Noise Reduction:**
```
Noise_Reduction = ((Raw_Frames - 1) / Raw_Frames) × 100%
```

**Supplier Risk Score (Volume-Normalized, Severity-Weighted):**
```
Risk = min(100, α × (Σ(Defectᵢ × w_severity_i) / Total_Shipped × 1000) + β × Recurrence)

Where:
  α = 1.0 (unit scaling factor)
  β = 100.0 (recurrence amplification)
  w_structural = 3.0 (FMEA severity 9 → safety-critical)
  w_wrong_component = 2.0 (FMEA severity 6 → functional)
  w_surface = 1.0 (FMEA severity 3 → cosmetic)
  Recurrence = incidents_in_window / batches_in_window
```

**Cost of Inaction:**
```
Recall_Liability = Units_at_risk × Unit_recall_cost
Rework_Cost = Units_at_risk × Unit_rework_cost
Net_Savings = Recall_Liability - Rework_Cost
```

**Hash Chain:**
```
Hₙ = SHA256(IDₙ ‖ Timestampₙ ‖ CameraIDₙ ‖ SHA256(ImageBytesₙ) ‖ MetadataJSONₙ ‖ Hₙ₋₁)
```

---

*Document Version 2.0 — Competition-Ready*
*INDUS-X: See → Verify → Trace → Decide → Act → Learn*
*"Autonomous where safe. Human-controlled where consequential."*
