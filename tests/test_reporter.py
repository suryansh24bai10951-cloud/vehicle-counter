"""
Unit tests for ReportWriter. Verifies CSV and JSON output structure without
needing a real video file or model.
"""

import csv
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from reporter import ReportWriter


def test_csv_written_with_expected_rows(tmp_path=None):
    tmp_path = tmp_path or Path(tempfile.mkdtemp())
    csv_path = tmp_path / "log.csv"
    json_path = tmp_path / "summary.json"

    report = ReportWriter(str(csv_path), str(json_path))
    report.log_frame(1, fps=30.0, counts={"car": 1}, total=1)
    report.log_frame(2, fps=30.0, counts={"car": 1, "truck": 1}, total=2)
    report.write_csv()

    assert csv_path.exists()
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["frame"] == "1"
    assert rows[1]["total_count"] == "2"


def test_summary_json_written_with_expected_fields(tmp_path=None):
    tmp_path = tmp_path or Path(tempfile.mkdtemp())
    csv_path = tmp_path / "log.csv"
    json_path = tmp_path / "summary.json"

    report = ReportWriter(str(csv_path), str(json_path))
    report.write_summary_json(
        total_counted=5,
        counts_by_class={"car": 3, "truck": 2},
        video_path="sample.mp4",
        frames_processed=300,
        duration_sec=10.0,
    )

    assert json_path.exists()
    with open(json_path) as f:
        summary = json.load(f)

    assert summary["total_vehicles_counted"] == 5
    assert summary["counts_by_class"] == {"car": 3, "truck": 2}
    assert summary["frames_processed"] == 300


if __name__ == "__main__":
    test_csv_written_with_expected_rows()
    test_summary_json_written_with_expected_fields()
    print("All reporter tests passed.")
