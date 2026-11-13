"""Evaluate a trained YOLO checkpoint on the validation split."""

import argparse

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Evaluate SmartRoad YOLO weights")
    parser.add_argument("--data", required=True, help="Ultralytics dataset YAML")
    parser.add_argument("--weights", required=True, help="Path to trained .pt weights")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default=None)
    args = parser.parse_args()
    options = {"data": args.data, "imgsz": args.imgsz, "split": "val", "plots": True}
    if args.device:
        options["device"] = args.device
    metrics = YOLO(args.weights).val(**options)
    box = metrics.box
    print(f"Precision: {box.mp:.4f}")
    print(f"Recall:    {box.mr:.4f}")
    print(f"mAP@50:    {box.map50:.4f}")
    print(f"mAP@50:95: {box.map:.4f}")


if __name__ == "__main__":
    main()
