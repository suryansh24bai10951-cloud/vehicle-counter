# vehical-counter

[README.md](https://github.com/user-attachments/files/32385495/README.md)
# Vehicle Traffic Counter

A command-line computer vision tool that detects, tracks, and counts vehicles
in a traffic video. Vehicles are detected with a pretrained YOLOv8n model and
tracked frame-to-frame with a custom centroid tracker, which counts each
vehicle exactly once as it crosses a virtual line in the video.

## Overview

Given any traffic video (dashcam, CCTV, drone footage, etc.), this tool:

1. Detects cars, motorcycles, buses, and trucks in each frame (YOLOv8n).
2. Tracks each vehicle across frames, assigning it a persistent ID.
3. Counts each unique vehicle once when it crosses a configurable virtual
   line, broken down by vehicle class.
4. Outputs an annotated video, a per-frame CSV log, and a JSON summary
   report — all from the terminal, no GUI required.

## Features

- Vehicle detection (car / motorcycle / bus / truck) via pretrained YOLOv8n
- Custom greedy centroid tracking algorithm with disappearance handling
- Line-crossing counting logic that guarantees each vehicle is counted once
- Annotated output video with live bounding boxes, IDs, and running counts
- CSV log (per-frame counts) and JSON summary report for further analysis
- Fully configurable via command-line flags (confidence, line position,
  frame-skip for speed, model path)
- Unit-tested tracking and reporting logic (no video/model required to test)

## Technologies / Tools Used

- Python 3.9+
- [ultralytics](https://github.com/ultralytics/ultralytics) (YOLOv8n, pretrained on COCO)
- OpenCV (`opencv-python`) for video I/O and drawing
- Custom centroid-tracking algorithm (no external tracking library)

## Project Structure

```
vehicle-counter/
├── README.md
├── statement.md
├── requirements.txt
├── src/
│   ├── models.py      # shared Detection data structure
│   ├── detector.py     # Module 1: YOLOv8n vehicle detection
│   ├── tracker.py       # Module 2: centroid tracking + line-crossing counter
│   ├── reporter.py      # Module 3: video annotation + CSV/JSON reports
│   └── main.py           # CLI entry point
├── tests/
│   ├── test_tracker.py
│   └── test_reporter.py
├── data/sample/         # put a sample input video here
└── docs/
    └── diagrams.md      # architecture, UML, workflow diagrams
```

## Setup & Installation

**Requirements:** Python 3.9 or later, pip.

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/vehicle-counter.git
   cd vehicle-counter
   ```

2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # on Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   The first run will automatically download the `yolov8n.pt` pretrained
   weights (~6 MB) via the `ultralytics` package — no manual download needed,
   but you do need an internet connection the first time.

4. Add a sample traffic video (any `.mp4`/`.avi`) to `data/sample/`, or point
   `--input` at any video file on your machine. Short public-domain traffic
   clips work well for testing (e.g. search "traffic footage" on Pexels or
   Pixabay for a royalty-free sample).

## Running the Project

From the repository root:

```bash
python src/main.py --input data/sample/traffic.mp4 --output-dir results
```

This writes to `results/`:
- `annotated_output.mp4` — the video with boxes, IDs, and running counts drawn on it
- `frame_log.csv` — per-frame counts over time
- `summary.json` — final totals by vehicle class

### CLI Options

| Flag | Default | Description |
|---|---|---|
| `--input` | *(required)* | Path to the input video file |
| `--output-dir` | `results` | Directory for output video/CSV/JSON |
| `--line-position` | `0.6` | Counting line's vertical position (0–1, fraction of frame height) |
| `--confidence` | `0.4` | Minimum detection confidence (0–1) |
| `--model` | `yolov8n.pt` | Path/name of YOLO weights |
| `--skip-frames` | `1` | Run detection every Nth frame (higher = faster, less accurate) |
| `--no-video-output` | off | Skip writing the annotated video (CSV/JSON still written) |

Run `python src/main.py --help` to see this from the terminal.

## Testing

The tracking and reporting logic is unit-tested with synthetic data, so
tests run instantly without needing a video file or the YOLO model:

```bash
pip install pytest
python -m pytest tests/ -v
```

All 8 tests should pass in well under a second.

## Non-Functional Notes

- **Performance:** `--skip-frames` lets you trade detection frequency for
  processing speed on CPU-only machines.
- **Reliability:** invalid input paths, unreadable videos, and out-of-range
  CLI arguments are validated with clear error messages before processing starts.
- **Usability:** every option has a sensible default; `--help` documents all flags.
- **Scalability:** the tracker's cost per frame scales with the number of
  currently visible vehicles, not the length of the video, so long videos
  process at a steady rate.

## Screenshots

*(Add a screenshot of `annotated_output.mp4` here after running the tool on
your own sample video.)*
