"""
main.py
CLI entry point.

Usage:
    python src/main.py --input path/to/video.mp4 --output-dir results/

Run `python src/main.py --help` for all options.
"""

import argparse
import sys
import time
from pathlib import Path

import cv2

from detector import VehicleDetector
from tracker import CentroidTracker
from reporter import ReportWriter, annotate_frame


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect, track, and count vehicles in a traffic video from the command line."
    )
    parser.add_argument("--input", required=True, help="Path to the input video file.")
    parser.add_argument(
        "--output-dir", default="results",
        help="Directory to write the annotated video, CSV log, and JSON summary (default: results/)."
    )
    parser.add_argument(
        "--line-position", type=float, default=0.6,
        help="Vertical position of the counting line as a fraction of frame height, 0-1 (default: 0.6)."
    )
    parser.add_argument(
        "--confidence", type=float, default=0.4,
        help="Minimum detection confidence, 0-1 (default: 0.4)."
    )
    parser.add_argument(
        "--model", default="yolov8n.pt",
        help="Path or name of the YOLO model weights (default: yolov8n.pt, auto-downloaded on first run)."
    )
    parser.add_argument(
        "--skip-frames", type=int, default=1,
        help="Run detection every Nth frame to trade accuracy for speed (default: 1, i.e. every frame)."
    )
    parser.add_argument(
        "--no-video-output", action="store_true",
        help="Skip writing the annotated output video (CSV/JSON reports are still written)."
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input video not found: {input_path}", file=sys.stderr)
        return 1

    if not (0.0 < args.line_position < 1.0):
        print("Error: --line-position must be between 0 and 1", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        print(f"Error: could not open video file: {input_path}", file=sys.stderr)
        return 1

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    line_y = int(height * args.line_position)

    print(f"Loading model '{args.model}' ...")
    try:
        detector = VehicleDetector(model_path=args.model, confidence=args.confidence)
    except Exception as exc:
        print(f"Error: failed to load model: {exc}", file=sys.stderr)
        cap.release()
        return 1

    tracker = CentroidTracker(line_y=line_y)
    report = ReportWriter(
        csv_path=str(output_dir / "frame_log.csv"),
        json_path=str(output_dir / "summary.json"),
    )

    video_writer = None
    if not args.no_video_output:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            str(output_dir / "annotated_output.mp4"), fourcc, fps, (width, height)
        )

    frame_number = 0
    start_time = time.time()
    last_detections = []

    print("Processing video... (this may take a while on CPU)")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_number += 1

        if frame_number % max(args.skip_frames, 1) == 0 or frame_number == 1:
            last_detections = detector.detect(frame)

        tracks = tracker.update(last_detections)
        report.log_frame(frame_number, fps, tracker.counts, tracker.total_counted)

        if video_writer is not None:
            annotated = annotate_frame(frame, tracks, line_y, tracker.total_counted, tracker.counts)
            video_writer.write(annotated)

        if frame_number % 50 == 0:
            print(f"  ...processed {frame_number} frames, running total: {tracker.total_counted}")

    duration_sec = frame_number / fps if fps else 0
    cap.release()
    if video_writer is not None:
        video_writer.release()

    report.write_csv()
    report.write_summary_json(
        total_counted=tracker.total_counted,
        counts_by_class=tracker.counts,
        video_path=str(input_path),
        frames_processed=frame_number,
        duration_sec=duration_sec,
    )

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.1f}s. Frames processed: {frame_number}")
    print(f"Total vehicles counted: {tracker.total_counted}")
    print(f"Breakdown: {tracker.counts}")
    print(f"Reports written to: {output_dir.resolve()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
