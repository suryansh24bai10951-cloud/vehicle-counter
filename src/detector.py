"""
detector.py
Module 1: Detection

Wraps a pretrained YOLOv8n model (via the `ultralytics` package) and exposes
a simple interface for getting vehicle detections from a single video frame.

Only COCO classes that correspond to road vehicles are kept: car, motorcycle,
bus, truck. Everything else (people, animals, etc.) is filtered out here so
downstream modules never have to think about non-vehicle classes.
"""

from typing import List

from ultralytics import YOLO

from models import Detection

# COCO class ids -> names for the vehicle classes we care about.
# (Full COCO class list is fixed by the pretrained model; these ids are stable.)
VEHICLE_CLASS_IDS = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class VehicleDetector:
    """
    Thin wrapper around a YOLOv8n model that returns only vehicle detections
    above a confidence threshold.
    """

    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.4):
        if not (0.0 < confidence < 1.0):
            raise ValueError("confidence must be between 0 and 1")
        self.confidence = confidence
        self._model = YOLO(model_path)

    def detect(self, frame) -> List[Detection]:
        """
        Run detection on a single BGR frame (as returned by cv2.VideoCapture)
        and return a list of Detection objects for vehicles only.
        """
        results = self._model.predict(
            frame, conf=self.confidence, verbose=False
        )

        detections: List[Detection] = []
        if not results:
            return detections

        result = results[0]
        if result.boxes is None:
            return detections

        for box in result.boxes:
            class_id = int(box.cls.item())
            if class_id not in VEHICLE_CLASS_IDS:
                continue

            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            confidence = float(box.conf.item())

            detections.append(
                Detection(
                    bbox=(x1, y1, x2, y2),
                    class_name=VEHICLE_CLASS_IDS[class_id],
                    confidence=confidence,
                )
            )

        return detections
