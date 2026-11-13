# INDUS-X ← SmartRoad AI: Codebase Reuse Analysis & Build Plan

## TL;DR — Can You Reuse This Code?

**YES — roughly 60-65% of the architecture is directly transferable.** The SmartRoad AI project is a road hazard detection platform with YOLO + ByteTrack + incident clustering + SQLite persistence + Streamlit dashboard. The domain is completely different (roads vs. factory floor), but the engineering patterns are almost identical to what INDUS-X needs.

---

## What SmartRoad AI Already Has (That INDUS-X Needs)

| SmartRoad Component | File | What It Does | INDUS-X Equivalent |
|---|---|---|---|
| ✅ **YOLO Detection Adapter** | `smartroad/detector.py` | Wraps YOLOv8 with standardized `Detection` dataclass, supports ByteTrack tracking, multi-model loading | → Rename to `PerceptionAdapter`. Change model to YOLOv11. Same pattern. |
| ✅ **ByteTrack Object Tracking** | `detector.py` line 42 | `model.track(frame, persist=True, tracker="bytetrack.yaml")` — persistent track IDs across frames | → **Use as-is.** This is exactly your incident consolidation Gate 1. |
| ✅ **Motion Analysis** | `smartroad/motion.py` | Tracks centroid movement per track_id, computes speed/direction | → Adapt for conveyor belt direction. Use for "part entering/exiting ROI" detection. |
| ✅ **Incident Clustering** | `smartroad/reporting.py` (`HazardTracker` + `_ActiveIncident`) | Groups frame-level detections into incidents using class, bbox overlap, centroid proximity, missed-frame tolerance | → **This IS your 4-gate consolidation engine.** Rename and add IoU threshold + peak evidence selection. |
| ✅ **SQLite Incident Database** | `smartroad/reporting.py` (`IncidentDatabase`) | Full CRUD: `incidents` table, `incident_audit` table, `submissions` table, status workflow, duplicate detection | → **Massive reuse.** Add `provenance_chain`, `batches`, `vendors` tables. Keep the audit trail pattern. |
| ✅ **Evidence Storage** | `reporting.py` | Saves snapshots (annotated JPG), crops (defect region), and MP4 evidence clips per incident | → **Direct reuse.** Your "best evidence frame" + "anomaly crop" + "evidence clip" are exactly these. |
| ✅ **Severity Scoring** | `reporting.py` (`severity_for()`) | Calculates severity from confidence + box area + class type | → Adapt for FMEA-based severity weights (structural=3.0, wrong=2.0, surface=1.0) |
| ✅ **SLA Tracking** | `reporting.py` (`calculate_sla_due_date`, `evaluate_sla`) | Due date calculation, overdue detection, countdown timers | → Repurpose for vendor SLA/contract compliance tracking |
| ✅ **Status Workflow** | `reporting.py` (`STATUSES`, `ALLOWED_TRANSITIONS`) | Enforced status transitions: New → Verified → Dispatched → Closed | → Map to your governance tiers: OPEN → CONSOLIDATED → QUARANTINED → NCR_ISSUED → CLOSED |
| ✅ **Audit Trail** | `reporting.py` (`incident_audit` table) | Records every status change with actor, action, timestamp, notes | → **This IS your Chain of Custody log.** Same pattern, add RBAC role. |
| ✅ **Video Processing Pipeline** | `smartroad/pipeline.py` (`RoadAnalyzer`) | Frame-by-frame processing with detection, tracking, annotation, safety analysis, evidence collection | → **Core architecture reuse.** Replace road safety logic with reference grid + consolidation. |
| ✅ **Frame Annotation** | `pipeline.py` (`_annotate()`) | Draws bounding boxes, labels, confidence, track IDs, safety event banners on frames | → Adapt colors/labels for industrial context. Add CAD grid overlay. |
| ✅ **Streamlit Dashboard** | `app.py` (1519 lines!) | Full dark-mode dashboard with video upload, detection display, incident queue, status management, exports | → **Huge head start.** Restructure into 4-quadrant layout. Keep the dark theme, metric cards, incident review patterns. |
| ✅ **Content Hashing** | `app.py` + `reporting.py` | SHA-256 hash of uploaded media for deduplication | → Extend into your full provenance hash CHAIN. The hashing infra is already there. |
| ✅ **Notification System** | `reporting.py` (`notifications` table) | In-app notifications with severity, category, recipient type | → Reuse for operator/QE/PM alert routing |
| ✅ **EXIF/Telemetry Extraction** | `smartroad/telemetry.py` | Extracts GPS, timestamp, camera info from media files | → Repurpose for camera_id, workstation_id, timestamp extraction |
| ✅ **PDF Report Generation** | `reporting.py` (`generate_pdf_report`) | ReportLab-based PDF export of incidents | → Adapt for Supplier NCR / Liability Dossier PDF export |
| ✅ **CSV/JSON Export** | `reporting.py` (`export_incidents`) | Data export functionality | → Reuse for compliance exports |
| ✅ **Model Weights** | `yolov8n.pt` (6.5MB) | Pretrained COCO model | → Replace with YOLOv11n or fine-tuned industrial weights |

---

## What SmartRoad AI Does NOT Have (Must Build New)

| INDUS-X Feature | Effort | Notes |
|---|---|---|
| **Reference Grid Evaluator** | 4-5h | New module. Detect chassis → normalize coordinates → project expected bolt positions → absence/mismatch check. No equivalent in SmartRoad. |
| **Provenance Hash CHAIN** | 3h | SmartRoad has single-file SHA-256 hashing. You need to extend this into an append-only CHAIN where each block links to the previous. |
| **Vendor/Batch/Contract Tables** | 2h | New seed data tables. SmartRoad has `incidents` but no supply chain schema. |
| **LLM Contract Reasoning Agent** | 4h | Completely new. RAG with ChromaDB + Gemini/GPT. No LLM integration in SmartRoad. |
| **RBAC Role Switcher** | 2h | SmartRoad has basic auth (env var username/password). You need Operator/QE/PM role switching with button locking. |
| **MQTT Automation Simulation** | 1h | New. Simple log-based simulation of diverter/conveyor commands. |
| **Supplier Risk Scoring** | 2h | New formula engine. Volume-normalized, severity-weighted scoring + ISO 2859 switching. |
| **Cost-of-Inaction Calculator** | 1h | New. Simple math on batch data. |
| **Grad-CAM Heatmap** | 2h | New. Requires `pytorch-grad-cam` integration. |
| **Split Comparison Mode** | 2h | New UI feature. Side-by-side standard vs INDUS-X view. |
| **Operator Feedback Loop** | 1.5h | New. Simple modal + accuracy tracking table. |
| **4-Quadrant Dashboard Layout** | 4h | SmartRoad's Streamlit is tab-based. You need to restructure into synchronized quadrants. |

---

## File-by-File Reuse Map

```
hack_flower_project/                    INDUS-X Equivalent
├── smartroad/                          → indusx/
│   ├── __init__.py                     → ✅ COPY + rename imports
│   ├── detector.py                     → ✅ COPY → perception.py (rename YoloDetector → PerceptionAdapter)
│   ├── motion.py                       → ✅ COPY → motion.py (adapt for conveyor direction)
│   ├── pipeline.py                     → ⚡ HEAVY ADAPT → pipeline.py (replace road logic with factory logic)
│   ├── plates.py                       → ❌ DELETE (not needed)
│   ├── reporting.py                    → ⚡ HEAVY ADAPT → reporting.py (keep DB + incidents, add provenance chain)
│   ├── safety.py                       → ⚡ REPLACE → reference_grid.py (replace road polygon with CAD grid)
│   └── telemetry.py                    → ✅ LIGHT ADAPT → telemetry.py (camera/station metadata)
├── app.py                              → ⚡ HEAVY ADAPT → app.py (restructure to 4-quadrant industrial UI)
├── main.py                             → ✅ COPY + rename
├── train.py                            → ✅ COPY (for fine-tuning)
├── evaluate.py                         → ✅ COPY
├── requirements.txt                    → ✅ COPY + add chromadb, google-genai
├── yolov8n.pt                          → ⚡ REPLACE with yolov11n.pt or custom industrial weights
├── pothole_hazards.pt                  → ❌ DELETE (road-specific)
├── license_plate.pt                    → ❌ DELETE (not needed)
└── data/                               → ✅ RESTRUCTURE
    └── reports/                        → data/
        ├── reports.db                  → indusx.db (add new tables)
        ├── snapshots/                  → evidence/frames/
        ├── crops/                      → evidence/crops/
        └── clips/                      → evidence/clips/
```

---

## What You Need to Make This Project LIVE

### Step 1: Copy & Rename (30 minutes)

```
1. Copy hack_flower_project/ → indusx/
2. Rename smartroad/ → indusx_core/
3. Delete: license_plate.pt, pothole_hazards.pt, plates.py
4. Replace road-specific video clips with factory scenario videos
5. Update all imports: smartroad.xxx → indusx_core.xxx
```

### Step 2: Adapt detector.py → perception.py (1 hour)

What to change:
- Rename `YoloDetector` → `PerceptionAdapter`
- Change default model from `yolov8n.pt` → `yolov11n.pt`
- Remove plate model support
- Keep hazard model slot → use for "surface defect" secondary model
- Keep ByteTrack tracking exactly as-is
- Add defect-class constants: `STRUCTURAL`, `WRONG_COMPONENT`, `SURFACE_ANOMALY`

### Step 3: Build reference_grid.py (NEW — 4 hours)

This is the **one completely new module** with no SmartRoad equivalent:

```python
class ReferenceGridEvaluator:
    """Compare observed detections against expected CAD/BOM positions."""
    
    def __init__(self, expected_grid, expected_classes, iou_threshold=0.3, absence_frames=5):
        self.expected_grid = expected_grid
        self.expected_classes = expected_classes
        self.absence_counter = defaultdict(int)
    
    def evaluate(self, detections, chassis_bbox):
        # 1. Normalize detection coordinates to chassis-relative space
        # 2. For each expected slot, find closest detection
        # 3. If no match for 5+ frames → STRUCTURAL_ABSENCE
        # 4. If match but wrong class → WRONG_COMPONENT
        # 5. Check for surface anomalies in non-slot regions
        ...
```

### Step 4: Adapt reporting.py (3 hours)

What to keep:
- `IncidentDatabase` class (90% reusable)
- `_ActiveIncident` dataclass
- `HazardTracker` → rename to `IncidentConsolidator`
- `incident_audit` table → becomes Chain of Custody log
- `severity_for()` → adapt to FMEA weights
- SLA tracking functions
- Evidence storage (snapshots, crops, clips)
- PDF/CSV export

What to add:
- `provenance_chain` table + `ProvenanceChainService`
- `batches` table with seed data
- `vendors` table with seed data  
- `custody_log` table (extend existing `incident_audit`)
- Hash chain: `seal_incident()`, `verify_chain()`, `simulate_tamper()`
- Vendor risk score calculation
- ISO 2859 switching logic

### Step 5: Adapt pipeline.py (3 hours)

What to keep:
- `RoadAnalyzer` → rename to `InspectionPipeline`
- `process_frame()` flow: detect → enrich → analyze → annotate
- `process_video()` flow: frame loop → tracking → incident collection → evidence
- `FrameResult` dataclass
- `VideoSummary` dataclass (add consolidation metrics)
- Frame annotation function (change colors/labels)

What to change:
- Replace `SafetyAnalyzer` calls with `ReferenceGridEvaluator`
- Replace road polygon with CAD reference grid overlay
- Add consolidation telemetry (raw count, incident count, noise reduction %)
- Add provenance sealing in the frame loop
- Remove plate-related code

### Step 6: Build provenance.py (NEW — 3 hours)

```python
class ProvenanceChainService:
    def seal_incident(self, incident, frame_bytes) -> ProvenanceBlock: ...
    def verify_chain(self) -> ChainVerificationResult: ...
    def simulate_tamper(self, block_index) -> None: ...
```

### Step 7: Build llm_agent.py (NEW — 4 hours)

```python
class SLAReasoningAgent:
    def __init__(self, vector_store, llm_client): ...
    async def generate_dossier(self, incident, batch_context) -> LiabilityDossier: ...
```

### Step 8: Adapt app.py → 4-Quadrant Dashboard (5 hours)

What to keep from SmartRoad:
- Dark-mode CSS theme (lines 35-200+) — **excellent styling, reuse everything**
- Metric card HTML components
- Video upload + processing flow
- Incident queue display pattern
- Status transition workflow
- Evidence display (snapshots, crops, clips)
- PDF/CSV export buttons
- Notification display

What to restructure:
- Change from tab-based layout → 4-quadrant `st.columns([1,1])` layout
- Q1: Video feed + scenario selector + CAD overlay
- Q2: Consolidation metrics + provenance display + tamper buttons
- Q3: Traceability tree + cost calculator + governance buttons
- Q4: Vendor risk scores + ISO switching + model accuracy
- Add role switcher in sidebar/header
- Add split comparison toggle

### Step 9: Seed Data & Scenarios (2 hours)

- Create 4 factory scenario video clips (or use annotated test images)
- Seed `batches` table with B-038 through B-043
- Seed `vendors` table with Vendor-X, Vendor-A, Vendor-B
- Create MSA-2026-09 contract text file for RAG
- Pre-cache LLM responses for offline demo

### Step 10: Integration & Testing (3 hours)

- End-to-end test: scenario → detection → consolidation → hash → trace → automation → governance
- Test all 4 scenarios
- Test role switching
- Test tamper simulation
- Rehearse 3-minute demo

---

## Updated Requirements.txt

```
# Core (from SmartRoad — keep)
ultralytics>=8.3.0
opencv-python>=4.10.0
numpy>=1.26.0
streamlit>=1.40.0
reportlab>=4.2.0

# Remove (not needed for INDUS-X)
# easyocr>=1.7.0
# pytesseract>=0.3.13

# Add for INDUS-X
chromadb>=0.4.0            # RAG vector store for contract clauses
google-genai>=1.0.0        # Gemini API for LLM reasoning (or openai)
pytorch-grad-cam>=1.5.0    # Explainability heatmaps
Pillow>=10.0.0             # Image processing
```

---

## Estimated Total Build Time

| Phase | Hours | What |
|---|---|---|
| Copy, rename, cleanup | 0.5h | File restructuring |
| Adapt detector/perception | 1h | Model swap + rename |
| **Build reference grid (NEW)** | **4h** | Core differentiator — no SmartRoad equivalent |
| Adapt reporting + add provenance | 3h | Extend existing DB + add hash chain |
| Adapt pipeline | 3h | Replace road logic with factory logic |
| **Build LLM agent (NEW)** | **4h** | RAG + contract reasoning |
| Build MQTT simulation | 1h | Simple log commands |
| Build vendor risk scoring | 2h | Formula + ISO switching |
| Adapt dashboard to 4-quadrant | 5h | Major UI restructure |
| Seed data + scenarios | 2h | Videos, DB data, contract text |
| Integration + testing | 3h | End-to-end + demo rehearsal |
| **TOTAL** | **~28.5h** | Fits in 36-hour hackathon ✅ |

> [!IMPORTANT]
> Without SmartRoad's code, this would be a **45-50 hour** build. The reuse saves you **~17-20 hours** — that's the difference between finishing and not finishing.

---

## The 5 Files That Save You The Most Time

1. **`reporting.py` (1068 lines)** — Saves ~8 hours. Full SQLite incident DB, evidence storage, audit trail, status workflow, exports. This is 40% of your backend.

2. **`app.py` (1519 lines)** — Saves ~6 hours. Complete dark-mode Streamlit dashboard with video processing, incident display, status management. This is your entire frontend skeleton.

3. **`pipeline.py` (334 lines)** — Saves ~3 hours. Frame-by-frame video processing with tracking, annotation, and evidence collection. This is your core processing loop.

4. **`detector.py` (76 lines)** — Saves ~2 hours. Clean YOLO adapter with ByteTrack, multi-model support, standardized Detection dataclass.

5. **`motion.py` (52 lines)** — Saves ~1 hour. Track-based motion analysis. Adapt for conveyor movement detection.
