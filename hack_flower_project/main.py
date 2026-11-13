"""Command-line entry point for SmartRoad AI image and video analysis."""

import argparse
from pathlib import Path
import subprocess
import sys

import cv2

from smartroad import auto_detect_models
from smartroad.pipeline import RoadAnalyzer


def parse_args():
    detected = auto_detect_models()
    parser = argparse.ArgumentParser(description="Detect road users and potential safety events.")
    parser.add_argument("input", type=Path, nargs="?", help="Path to an image or video; omit to open the dashboard")
    parser.add_argument("--output", type=Path, help="Output file (default: annotated_<name>)")
    parser.add_argument("--model", default=None, help="Ultralytics YOLO weights (default: yolov8n.pt)")
    parser.add_argument("--plate-model", default=detected.get("plate_model"),
                        help="Number-plate detector weights (auto-detected: %(default)s)")
    parser.add_argument("--hazard-model", default=detected.get("hazard_model"),
                        help="Road-hazard detector weights (auto-detected: %(default)s)")
    parser.add_argument("--conf", type=float, default=0.25, help="Detection confidence threshold")
    parser.add_argument("--show", action="store_true", help="Display annotated video while processing")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.input is None:
        app_path = Path(__file__).with_name("app.py")
        raise SystemExit(subprocess.call([sys.executable, "-m", "streamlit", "run", str(app_path)]))
    if not args.input.is_file():
        raise SystemExit(f"Input file not found: {args.input}")
    output = args.output or args.input.with_name(f"annotated_{args.input.name}")

    print("SmartRoad AI — loading models…")
    print(f"  Main model:   {args.model or 'yolov8n.pt'}")
    print(f"  Hazard model: {args.hazard_model or '(none)'}")
    print(f"  Plate model:  {args.plate_model or '(none)'}")
    print(f"  Confidence:   {args.conf}")

    analyzer = RoadAnalyzer(
        model_path=args.model,
        plate_model_path=args.plate_model,
        confidence=args.conf,
        hazard_model_path=args.hazard_model,
    )
    suffix = args.input.suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}:
        result = analyzer.process_image(args.input)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), result.annotated_frame)
        print(f"\nSaved annotated image: {output}")
        print(f"Detections: {len(result.detections)}")
        for det in result.detections:
            print(f"  {det.label:20s} {det.confidence:.0%}  box={det.box}")
        for event in result.events:
            print(f"[{event.severity.upper()}] {event.title}: {event.details}")
        if result.plate_texts:
            print(f"Plates read: {', '.join(result.plate_texts)}")
    else:
        summary = analyzer.process_video(args.input, output, show=args.show)
        print(f"\nSaved annotated video: {output}")
        print(f"Frames: {summary.frames_processed}; average processing: {summary.average_fps:.1f} FPS")
        print(f"Unique tracked IDs: {summary.unique_tracks}")
        if summary.hazard_detection_counts:
            print("Road hazards detected:")
            for label, count in sorted(summary.hazard_detection_counts.items()):
                print(f"  {label:25s} {count} frame detections")
        if summary.plate_texts:
            print(f"Plates read: {', '.join(summary.plate_texts)}")
        if summary.event_frame_counts:
            print("Safety events:")
            for title, count in sorted(summary.event_frame_counts.items()):
                print(f"  {title:35s} {count} frames")


if __name__ == "__main__":
    main()
