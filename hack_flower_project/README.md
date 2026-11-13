# SmartRoad AI

Road-scene detection and potential safety-event analysis for images and recorded videos.

## Current working scope

- YOLO image detection and annotated image output.
- Video inference with persistent ByteTrack IDs and annotated MP4 output.
- Image-coordinate movement state and direction estimates for tracked road users.
- Optional second road-hazard model, running alongside the road-user model.
- Optional plate detection, OCR, and best-effort plate-to-vehicle track association.
- Streamlit upload dashboard with detection counts, tracked-object totals, alert-frame rates, and downloadable annotated videos.
- Explainable starter rules for people or configured hazard classes in an estimated roadway region.
- Local hazard incident clustering with persistent SQLite records, evidence snapshots/crops, and short clips.
- A local review workflow with estimated severity, status changes, and CSV/JSON/PDF exports.
- Optional number-plate detection using separate custom weights, followed by optional Tesseract OCR.

The default `yolov8n.pt` model is pretrained on COCO. It can detect common classes such as cars, people, buses, trucks, motorcycles, and bicycles. It does **not** reliably detect potholes, debris, or number plates. Those require suitable custom weights and evaluation data. The dashboard checks class names and warns when the selected weights cannot make a road-hazard assessment. Safety alerts are heuristics and are not accident prediction or a substitute for human review.

## Setup

Use Python 3.10–3.12 in a virtual environment, then install the dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ultralytics downloads the default model weights on first use. To use custom weights, set `SMARTROAD_MODEL` or pass `--model`. Set `SMARTROAD_HAZARD_MODEL` or pass `--hazard-model` for a second custom hazard model. It runs alongside the road-user model, so hazard training does not replace common vehicle/person detection. Set `SMARTROAD_PLATE_MODEL` or pass `--plate-model` for a dedicated plate detector. OCR uses the optional `pytesseract` Python package and also requires the Tesseract executable installed on the machine.

## Run

Analyze an image:

```bash
python main.py path/to/road.jpg
```

Analyze a video with tracking:

```bash
python main.py path/to/road.mp4 --show
```

Add custom model weights when available:

```bash
python main.py path/to/road.mp4 --model yolov8n.pt --hazard-model runs/detect/train/weights/best.pt --plate-model path/to/plate_weights.pt
```

Open the dashboard:

```bash
streamlit run app.py
```

By default, annotated outputs are saved next to the input as `annotated_<filename>`.

## Safety region and interpretation

The starter roadway polygon is a trapezoid covering the lower part of the frame. Hazard detections are reported even when outside this estimated region; each alert says whether the box fell inside or outside it. The region should be calibrated before interpreting the location as roadway. A “pedestrian-vehicle risk” means a person and a vehicle were both detected in this region; the current implementation does not estimate time-to-collision. “Vehicle moving toward road hazard” compares tracked image-space distances to a tracked hazard and is a visual heuristic. Direction is expressed in image coordinates (up/down/left/right), not compass directions. Stopped-vehicle detection uses tracked positions over video time and is also a heuristic.

## Planned model development

1. Establish a repeatable baseline on common road objects.
2. Collect and annotate a licensed, representative road-hazard dataset.
3. Fine-tune YOLO for selected hazards and evaluate precision, recall, and mAP on held-out data.
4. Add a dedicated plate detector and measure OCR performance under known conditions.
5. Calibrate the road region and refine tracking-based safety rules for each intended camera setup.

Do not report model accuracy or OCR performance until measured on a documented evaluation set.

## Local incident review and evidence

Video and image analysis accepts optional road, city/area, landmark, and coordinates. The app requires an explicit Analyze/Submit click. It stores a SHA-256 content hash for each upload and refuses to create a second submission for identical media; completed no-hazard analyses are recorded too. Video detections are clustered across adjacent frames using class, bounding-box overlap, and centroid proximity. Each finalized group gets a `PWD-HAZ-...` ticket, annotated snapshot, padded crop, and an MP4 evidence clip when OpenCV can create it. Records and status changes are stored in `data/reports/reports.db`; evidence is stored under `data/reports/`. Existing records are migrated when the app starts. Older rows without a media hash cannot be fingerprinted retroactively, so if an upload filename matches a legacy row, the app pauses submission to avoid likely repeats. Rename a genuinely different file before submitting it.

For cross-upload repeat hints, the app compares open incidents of the same hazard type from the last 90 days. It flags reports within 50 metres when both have coordinates, or with the same normalized road and landmark when coordinates are absent. These are review candidates only; the app never automatically merges or rejects a separate report. Broad location-only matches are intentionally not flagged. Use precise coordinates or road plus landmark for useful matching.

The review section is local only. The status flow is enforced in order: New Submission → Verified → Work-Order Dispatched → Repaired & Closed. Verification requires a staff note; dispatch requires an assignee, work-order reference, and target date; closure requires repair notes or evidence. Staff actions are written to an audit table. Work-order and closure details are included in incident exports. “Work-Order Dispatched” changes only the local record; it does not contact an agency or dispatch a crew. Severity and lane position are image-based triage estimates, not engineering measurements. Clustering can merge nearby hazards or split one after a long occlusion. Clips target approximately three seconds and can be shorter near video boundaries or if video writing fails. CSV and JSON exports include local evidence paths. PDF export requires ReportLab (`pip install reportlab`). Queue exports respect the active filters.

### Municipal portal access

The municipal tab is locked until server-side environment variables are configured. In PowerShell, set the credentials in the same terminal used to launch Streamlit, then restart the app:

```powershell
$env:SMARTROAD_PWD_USERNAME = "pwd-staff"
$env:SMARTROAD_PWD_PASSWORD = "choose-a-long-unique-password"
streamlit run app.py
```

Do not put real credentials in source control or share the app publicly with this single-credential prototype. For a network or public deployment, place it behind a maintained identity provider/reverse proxy with TLS, per-user roles, and operational security controls; the built-in gate is intended for a local demonstration, not a standalone production authentication system.

Video OCR is sampled and aggregated by vehicle tracking ID using approximate string consensus. Tracking changes, visibility, OCR errors, and camera quality can affect the result; review uncertain readings before use. Uploads and evidence stay local unless manually exported. No external dispatch or Open311 submission is implemented.

## Fine-tune and evaluate

Prepare images and YOLO-format labels, then copy `data/road_hazards.example.yaml` to a dataset YAML whose `path` points to your dataset. Ensure the class IDs and `names` match your annotations.

```bash
python train.py --data data/road_hazards.yaml --model yolov8n.pt --epochs 50
python evaluate.py --data data/road_hazards.yaml --weights runs/detect/train/weights/best.pt
```

Training runs and metrics are produced by Ultralytics. Use the saved `best.pt` with `python main.py ... --model runs/detect/train/weights/best.pt` or enter the path in the dashboard. Dataset licensing, annotation quality, and a held-out test split are part of the model result.
