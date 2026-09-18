"""
reporter.py
Module 3: Reporting & Analytics

Responsible for everything the user actually looks at after a run:
  - an annotated output video (boxes, IDs, running count overlay)
  - a per-frame CSV log (frame number, timestamp, running counts)
  - a final JSON summary (totals per vehicle class, run metadata)
"""

import csv
import json
import time
from pathlib import Path
from typing import Dict, List

import cv2

from tracker import Track


class ReportWriter:
    def __init__(self, csv_path: str, json_path: str):
        self.csv_path = Path(csv_path)
        self.json_path = Path(json_path)
        self._csv_rows: List[Dict] = []
        self._start_time = time.time()

    def log_frame(self, frame_number: int, fps: float, counts: Dict[str, int], total: int) -> None:
        row = {
            "frame": frame_number,
            "timestamp_sec": round(frame_number / fps, 2) if fps else 0,
            "total_count": total,
        }
        row.update(counts)
        self._csv_rows.append(row)

    def write_csv(self) -> None:
        if not self._csv_rows:
            fieldnames = ["frame", "timestamp_sec", "total_count"]
        else:
            fieldnames = sorted({key for row in self._csv_rows for key in row.keys()})
            # keep a stable, readable column order
            preferred = ["frame", "timestamp_sec", "total_count"]
            fieldnames = preferred + [f for f in fieldnames if f not in preferred]

        with open(self.csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self._csv_rows:
                writer.writerow(row)

    def write_summary_json(
        self,
        total_counted: int,
        counts_by_class: Dict[str, int],
        video_path: str,
        frames_processed: int,
        duration_sec: float,
    ) -> None:
        summary = {
            "video_source": video_path,
            "frames_processed": frames_processed,
            "video_duration_sec": round(duration_sec, 2),
            "processing_time_sec": round(time.time() - self._start_time, 2),
            "total_vehicles_counted": total_counted,
            "counts_by_class": counts_by_class,
        }
        with open(self.json_path, "w") as f:
            json.dump(summary, f, indent=2)


def annotate_frame(frame, tracks: List[Track], line_y: int, total_counted: int, counts: Dict[str, int]):
    """Draw the counting line, all live tracks, and a running-count overlay onto the frame."""
    height, width = frame.shape[:2]

    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 255), 2)

    for track in tracks:
        x, y = track.centroid
        color = (0, 200, 0) if track.counted else (255, 140, 0)
        cv2.circle(frame, (x, y), 4, color, -1)
        label = f"ID {track.track_id} {track.class_name}"
        cv2.putText(frame, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    overlay_lines = [f"Total: {total_counted}"] + [f"{k}: {v}" for k, v in counts.items()]
    for i, line in enumerate(overlay_lines):
        cv2.putText(
            frame, line, (10, 25 + i * 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
        )

    return frame
