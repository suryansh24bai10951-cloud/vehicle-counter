"""
tracker.py
Module 2: Tracking & Counting

This is the core original algorithm of the project. YOLOv8n only tells us
*what* is in a single frame -- it has no concept of identity across frames.
This module assigns a persistent ID to each vehicle as it moves through the
video, and counts each vehicle exactly once when its centroid crosses a
user-defined virtual counting line.

Algorithm: greedy centroid tracking.
  1. Each tracked object stores its last known centroid and a class name.
  2. On every new frame, we compute the Euclidean distance between every
     existing tracked centroid and every new detection centroid.
  3. We greedily match the closest pairs first, provided the distance is
     under `max_distance` (an object can't teleport across the frame
     between two consecutive frames).
  4. Unmatched existing tracks get a "disappeared" strike; after
     `max_disappeared` consecutive misses, the track is dropped.
  5. Unmatched detections become brand-new tracks with a fresh ID.
  6. After updating positions, we check whether any track's centroid just
     crossed the counting line (comparing previous vs. current y position
     against the line's y coordinate). Each track can only be counted once,
     ever, via a `counted` flag.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from models import Detection


@dataclass
class Track:
    track_id: int
    class_name: str
    centroid: Tuple[int, int]
    prev_centroid: Tuple[int, int] = None
    disappeared: int = 0
    counted: bool = False

    def update_position(self, new_centroid: Tuple[int, int]):
        self.prev_centroid = self.centroid
        self.centroid = new_centroid
        self.disappeared = 0


class CentroidTracker:
    def __init__(
        self,
        line_y: int,
        max_distance: float = 80.0,
        max_disappeared: int = 15,
    ):
        """
        line_y: the y-coordinate (pixels) of the horizontal counting line.
        max_distance: max pixel distance to consider two centroids the same object.
        max_disappeared: frames a track can go unmatched before being dropped.
        """
        self.line_y = line_y
        self.max_distance = max_distance
        self.max_disappeared = max_disappeared

        self._next_id = 1
        self.tracks: Dict[int, Track] = {}
        self.counts: Dict[str, int] = {}
        self.total_counted = 0

    def _register(self, detection: Detection) -> None:
        track = Track(
            track_id=self._next_id,
            class_name=detection.class_name,
            centroid=detection.centroid,
        )
        self.tracks[self._next_id] = track
        self._next_id += 1

    def _deregister(self, track_id: int) -> None:
        del self.tracks[track_id]

    def _crossed_line(self, track: Track) -> bool:
        if track.prev_centroid is None:
            return False
        prev_y = track.prev_centroid[1]
        curr_y = track.centroid[1]
        # Crossed if the line sits strictly between the previous and current y.
        return (prev_y < self.line_y <= curr_y) or (curr_y <= self.line_y < prev_y)

    def update(self, detections: List[Detection]) -> List[Track]:
        """
        Feed in this frame's detections. Returns the current list of live
        tracks (after matching/registering/deregistering and counting).
        """
        if not self.tracks:
            for detection in detections:
                self._register(detection)
            return list(self.tracks.values())

        if not detections:
            for track in list(self.tracks.values()):
                track.disappeared += 1
                if track.disappeared > self.max_disappeared:
                    self._deregister(track.track_id)
            return list(self.tracks.values())

        # Build all (track_id, detection_idx, distance) triples.
        candidate_pairs = []
        for track_id, track in self.tracks.items():
            tx, ty = track.centroid
            for idx, detection in enumerate(detections):
                dx, dy = detection.centroid
                distance = ((tx - dx) ** 2 + (ty - dy) ** 2) ** 0.5
                if distance <= self.max_distance:
                    candidate_pairs.append((distance, track_id, idx))

        candidate_pairs.sort(key=lambda p: p[0])

        matched_tracks = set()
        matched_detections = set()

        for distance, track_id, idx in candidate_pairs:
            if track_id in matched_tracks or idx in matched_detections:
                continue
            self.tracks[track_id].update_position(detections[idx].centroid)
            matched_tracks.add(track_id)
            matched_detections.add(idx)

        # Unmatched existing tracks: mark disappeared, drop if too stale.
        for track_id in list(self.tracks.keys()):
            if track_id not in matched_tracks:
                self.tracks[track_id].disappeared += 1
                if self.tracks[track_id].disappeared > self.max_disappeared:
                    self._deregister(track_id)

        # Unmatched detections: brand new vehicles entering the frame.
        for idx, detection in enumerate(detections):
            if idx not in matched_detections:
                self._register(detection)

        # Counting pass: any track that just crossed the line and hasn't
        # been counted yet gets counted exactly once.
        for track in self.tracks.values():
            if not track.counted and self._crossed_line(track):
                track.counted = True
                self.total_counted += 1
                self.counts[track.class_name] = self.counts.get(track.class_name, 0) + 1

        return list(self.tracks.values())
