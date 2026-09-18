"""
models.py
Shared data structures used across detector, tracker, and reporter modules.
Kept dependency-free (no OpenCV/YOLO imports) so the tracking algorithm can
be unit-tested without needing the ML model installed.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Detection:
    """A single detected vehicle in one frame."""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2 (pixel coords)
    class_name: str
    confidence: float

    @property
    def centroid(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return (x1 + x2) // 2, (y1 + y2) // 2
