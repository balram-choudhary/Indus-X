"""Fine-tune a YOLO detector on an annotated dataset described by a data YAML."""

import argparse

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Fine-tune YOLO for road-scene or hazard classes")
    parser.add_argument("--data", required=True, help="Ultralytics dataset YAML")
    parser.add_argument("--model", default="yolov8n.pt", help="Pretrained model or existing checkpoint")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--device", default=None, help="For example 0, cpu, or mps")
    args = parser.parse_args()
    options = {"data": args.data, "epochs": args.epochs, "imgsz": args.imgsz, "batch": args.batch}
    if args.device:
        options["device"] = args.device
    YOLO(args.model).train(**options)


if __name__ == "__main__":
    main()
