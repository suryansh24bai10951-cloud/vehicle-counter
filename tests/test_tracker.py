"""
Unit tests for CentroidTracker.

These tests build synthetic Detection objects (no real video or model needed)
to verify: new-track registration, frame-to-frame matching, stale-track
removal, and single-count-per-vehicle line-crossing logic.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from models import Detection
from tracker import CentroidTracker


def make_detection(x, y, class_name="car"):
    # 20x20 bbox centered at (x, y)
    return Detection(bbox=(x - 10, y - 10, x + 10, y + 10), class_name=class_name, confidence=0.9)


def test_first_frame_registers_new_tracks():
    tracker = CentroidTracker(line_y=100)
    tracks = tracker.update([make_detection(50, 50), make_detection(150, 50)])
    assert len(tracks) == 2
    assert {t.track_id for t in tracks} == {1, 2}


def test_same_object_keeps_same_id_across_frames():
    tracker = CentroidTracker(line_y=100)
    tracker.update([make_detection(50, 50)])
    tracks = tracker.update([make_detection(55, 52)])  # moved slightly
    assert len(tracks) == 1
    assert tracks[0].track_id == 1


def test_track_dropped_after_max_disappeared():
    tracker = CentroidTracker(line_y=100, max_disappeared=2)
    tracker.update([make_detection(50, 50)])
    tracker.update([])  # miss 1
    tracker.update([])  # miss 2
    tracks = tracker.update([])  # miss 3 -> should be dropped
    assert len(tracks) == 0


def test_vehicle_counted_once_when_crossing_line():
    tracker = CentroidTracker(line_y=100)
    tracker.update([make_detection(50, 80)])   # above the line
    tracker.update([make_detection(50, 90)])   # still above
    tracker.update([make_detection(50, 110)])  # crosses the line
    assert tracker.total_counted == 1
    assert tracker.counts.get("car") == 1

    # further movement past the line must not double-count
    tracker.update([make_detection(50, 130)])
    assert tracker.total_counted == 1


def test_different_classes_counted_separately():
    tracker = CentroidTracker(line_y=100)
    tracker.update([make_detection(50, 80, "car"), make_detection(200, 80, "truck")])
    tracker.update([make_detection(50, 110, "car"), make_detection(200, 110, "truck")])
    assert tracker.total_counted == 2
    assert tracker.counts == {"car": 1, "truck": 1}


def test_new_detection_far_from_existing_tracks_gets_new_id():
    tracker = CentroidTracker(line_y=100, max_distance=30)
    tracker.update([make_detection(50, 50)])
    # second detection is far away -> should not match, gets new id, first track ages
    tracks = tracker.update([make_detection(500, 500)])
    assert len(tracks) == 2
