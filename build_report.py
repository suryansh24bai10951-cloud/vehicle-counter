"""
Builds the project report PDF (report.pdf) from the project content.
Run once from the repo root: python build_report.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, ListFlowable, ListItem
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontSize=26, leading=32, alignment=TA_CENTER, spaceAfter=20, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="CoverSub", fontSize=14, leading=20, alignment=TA_CENTER, spaceAfter=8, textColor=colors.HexColor("#444444")))
styles.add(ParagraphStyle(name="H1", fontSize=17, leading=22, spaceBefore=18, spaceAfter=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#1a1a1a")))
styles.add(ParagraphStyle(name="H2", fontSize=13, leading=18, spaceBefore=10, spaceAfter=6, fontName="Helvetica-Bold"))
styles.add(ParagraphStyle(name="Body", fontSize=10.5, leading=15, spaceAfter=8))
styles.add(ParagraphStyle(name="Caption", fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=14))
styles.add(ParagraphStyle(name="CodeBlock", fontSize=9, leading=12, fontName="Courier", backColor=colors.HexColor("#f5f5f5"), spaceAfter=8, leftIndent=6, rightIndent=6, spaceBefore=4))

story = []

def h1(text):
    story.append(Paragraph(text, styles["H1"]))

def h2(text):
    story.append(Paragraph(text, styles["H2"]))

def body(text):
    story.append(Paragraph(text, styles["Body"]))

def bullets(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(i, styles["Body"]), leftIndent=10) for i in items],
        bulletType="bullet", start="•"
    ))
    story.append(Spacer(1, 6))

def diagram(path, caption, width=6.2 * inch, max_height=8.5 * inch):
    img = Image(path)
    ratio = img.imageHeight / float(img.imageWidth)
    draw_width = width
    draw_height = width * ratio
    if draw_height > max_height:
        draw_height = max_height
        draw_width = max_height / ratio
    img.drawWidth = draw_width
    img.drawHeight = draw_height
    story.append(img)
    story.append(Paragraph(caption, styles["Caption"]))

# ---------------- Cover Page ----------------
story.append(Spacer(1, 2.2 * inch))
story.append(Paragraph("Vehicle Traffic Counter", styles["CoverTitle"]))
story.append(Paragraph("A Computer Vision Project — Detection, Tracking & Counting", styles["CoverSub"]))
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph("Flipped Course Evaluation — Build Your Own Project", styles["CoverSub"]))
story.append(Paragraph("Course Domain: Computer Vision", styles["CoverSub"]))
story.append(Spacer(1, 1.5 * inch))
story.append(Paragraph("Submitted as: GitHub Repository + Project Report (PDF)", styles["CoverSub"]))
story.append(PageBreak())

# ---------------- Introduction ----------------
h1("1. Introduction")
body(
    "This project implements a command-line computer vision system that detects, tracks, and "
    "counts vehicles in traffic video footage. It combines a pretrained deep-learning object "
    "detector (YOLOv8n) with a custom-built tracking algorithm to solve a problem detection "
    "alone cannot: knowing that the car seen in frame 40 is the same car seen in frame 55, so "
    "it is counted once rather than once per frame it appears in."
)
body(
    "The system is designed as three independent, testable modules — detection, tracking/"
    "counting, and reporting — wired together by a single CLI entry point. It requires no GUI "
    "and no manual dataset labeling; the pretrained model handles recognition, while the "
    "original contribution of this project is the identity-tracking and line-crossing counting "
    "logic, plus the reporting pipeline built around it."
)

# ---------------- Problem Statement ----------------
h1("2. Problem Statement")
body(
    "Manual vehicle counting for traffic analysis is slow, error-prone, and does not scale to "
    "long durations of footage. Traffic authorities, researchers, and students need an automated, "
    "repeatable way to count vehicles passing a point in a video, broken down by vehicle type, "
    "without expensive dedicated hardware or a full traffic-analytics platform."
)
h2("Scope")
body(
    "The project counts vehicles from a fixed-camera or roughly stable viewpoint (CCTV, dashcam, "
    "drone hover footage). It deliberately excludes multi-camera fusion, vehicle speed estimation, "
    "and license-plate recognition, keeping the system focused and achievable."
)
h2("Target Users")
bullets([
    "Traffic/transport researchers needing a lightweight, scriptable vehicle counting tool",
    "Students learning how to combine a pretrained detector with a custom tracking algorithm",
    "Anyone wanting quick, offline-after-setup vehicle counts from a video clip",
])

# ---------------- Functional Requirements ----------------
h1("3. Functional Requirements")
bullets([
    "<b>FR1 — Detection:</b> Detect vehicles (car, motorcycle, bus, truck) in each video frame "
    "using a pretrained YOLOv8n model, filtering out all non-vehicle classes.",
    "<b>FR2 — Tracking &amp; Counting:</b> Assign a persistent ID to each vehicle across frames "
    "using a custom centroid-tracking algorithm, and count each unique vehicle exactly once when "
    "it crosses a configurable virtual line.",
    "<b>FR3 — Reporting:</b> Produce an annotated output video (boxes, IDs, running counts), a "
    "per-frame CSV log, and a final JSON summary broken down by vehicle class.",
    "<b>FR4 — CLI configurability:</b> Allow the user to configure the input video, output "
    "directory, counting-line position, detection confidence threshold, model path, and frame-skip "
    "rate via command-line flags.",
])
h2("Input / Output Structure")
body(
    "<b>Input:</b> a single video file path (any format OpenCV can decode, e.g. .mp4, .avi) plus "
    "optional CLI flags. <b>Output:</b> an annotated video file, a CSV file logging counts over "
    "time, and a JSON file with final totals — all written to a user-specified output directory."
)
h2("User Workflow")
body(
    "1) User runs <font face='Courier'>python src/main.py --input video.mp4</font> from the "
    "terminal &nbsp;→&nbsp; 2) the tool validates the input and loads the model &nbsp;→&nbsp; "
    "3) it processes the video frame-by-frame, printing progress &nbsp;→&nbsp; 4) on completion "
    "it prints a summary to the terminal and writes the three report files."
)

# ---------------- Non-Functional Requirements ----------------
h1("4. Non-Functional Requirements")
nfr_data = [
    ["Requirement", "How it is addressed"],
    ["Performance", "The --skip-frames flag lets detection run on every Nth frame, trading "
                     "accuracy for throughput on CPU-only machines; the tracker's per-frame cost "
                     "scales only with the number of currently visible vehicles."],
    ["Reliability", "Input path, video-open success, and CLI argument ranges (e.g. "
                     "--line-position, --confidence) are validated up front with clear error "
                     "messages and non-zero exit codes, instead of failing mid-run."],
    ["Usability", "Every CLI flag has a sensible default and is documented via --help; the "
                   "annotated output video gives immediate visual feedback that counts are correct."],
    ["Maintainability", "The codebase is split into four single-responsibility modules "
                         "(models, detector, tracker, reporter) connected only through a small, "
                         "well-typed Detection/Track data model, so any module can be modified or "
                         "swapped independently."],
    ["Scalability", "Because tracking cost depends on the number of on-screen vehicles rather "
                     "than total video length, the tool processes long videos at a steady "
                     "per-frame rate rather than slowing down over time."],
    ["Error Handling", "Missing files, unreadable videos, and out-of-range arguments raise clear, "
                        "user-facing errors before any processing begins, rather than throwing raw "
                        "stack traces."],
]
t = Table(nfr_data, colWidths=[1.4 * inch, 4.9 * inch])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 10))

# ---------------- System Architecture ----------------
story.append(PageBreak())
h1("5. System Architecture")
body(
    "The system follows a linear pipeline architecture: each module consumes the previous "
    "module's output and has no knowledge of any module beyond its immediate neighbor. This "
    "keeps each piece independently testable and replaceable (e.g. a different detector model "
    "can be swapped in without touching the tracker or reporter)."
)
diagram("docs/images/diagram1.png", "Figure 1 — System Architecture: data flow from input video to output reports.")

# ---------------- Design Diagrams ----------------
h1("6. Design Diagrams")
h2("6.1 Process / Workflow Diagram")
body("Shows the full control flow of a single run, from CLI argument parsing through per-frame processing to final report writing.")
diagram("docs/images/diagram2.png", "Figure 2 — Workflow of a full program run.", width=4.2 * inch, max_height=7.5 * inch)

h2("6.2 Use Case Diagram")
diagram("docs/images/diagram3.png", "Figure 3 — Use cases available to the user/evaluator via the CLI.")

h2("6.3 Class / Component Diagram")
body("Reflects the actual module structure of the codebase (src/models.py, detector.py, tracker.py, reporter.py).")
diagram("docs/images/diagram4.png", "Figure 4 — Class relationships across the four core modules.")

h2("6.4 Sequence Diagram")
body("Illustrates the calls made once per video frame during processing.")
diagram("docs/images/diagram5.png", "Figure 5 — Sequence of calls for processing a single frame.")

h2("6.5 Database / Storage Design")
body(
    "This project intentionally uses file-based storage (CSV and JSON) rather than a database, "
    "since a single video-processing run produces a self-contained report with no need for "
    "persistent querying or multi-user access. No ER diagram applies. The CSV schema is: "
    "<font face='Courier'>frame, timestamp_sec, total_count, &lt;count per vehicle class&gt;</font>, "
    "one row per processed frame."
)

# ---------------- Design Decisions ----------------
story.append(PageBreak())
h1("7. Design Decisions & Rationale")
bullets([
    "<b>Pretrained detector, custom tracker:</b> Training a detector from scratch would need a "
    "labeled vehicle dataset and GPU time disproportionate to this project's scope. YOLOv8n is "
    "pretrained on COCO and already recognizes car/truck/bus/motorcycle well, so effort was spent "
    "on the tracking and counting algorithm instead — the part that is genuinely specific to this "
    "problem and not available off-the-shelf.",
    "<b>Greedy centroid tracking over a heavier tracker (e.g. DeepSORT):</b> Centroid tracking is "
    "simple to reason about, fast enough for CPU-only use, easy to unit test with synthetic data, "
    "and sufficiently accurate for a single fixed-camera counting line, which is this project's "
    "actual requirement.",
    "<b>Line-crossing counting instead of counting all detections:</b> Counting raw detections per "
    "frame would wildly over-count (the same vehicle appears in dozens of frames). Counting only "
    "on line-crossing, combined with a per-track 'counted' flag, guarantees each vehicle is "
    "counted exactly once regardless of how long it stays on screen.",
    "<b>Separate models.py module:</b> The Detection data class was pulled out of detector.py into "
    "its own dependency-free module specifically so the tracker (and its unit tests) never need "
    "the ultralytics/YOLO dependency — a deliberate decoupling decision made after the initial "
    "design, to keep the core algorithm testable in isolation.",
    "<b>CLI-only, no GUI:</b> Matches the submission requirement that the project be fully "
    "executable from the command line, and keeps the tool scriptable for batch processing.",
])

# ---------------- Implementation Details ----------------
h1("8. Implementation Details")
h2("8.1 Detection Module (src/detector.py)")
body(
    "Wraps ultralytics' YOLO class. On each call to <font face='Courier'>detect(frame)</font>, "
    "it runs inference at a configurable confidence threshold and filters results down to the "
    "four COCO class IDs that correspond to road vehicles (2=car, 3=motorcycle, 5=bus, 7=truck), "
    "returning a list of lightweight <font face='Courier'>Detection</font> objects."
)
h2("8.2 Tracking & Counting Module (src/tracker.py)")
body(
    "Implements <font face='Courier'>CentroidTracker</font>, a greedy nearest-centroid matching "
    "algorithm: on every frame it computes Euclidean distances between all existing track "
    "centroids and all new detection centroids, matches the closest pairs first (below a max "
    "distance threshold), ages out unmatched tracks after N consecutive misses, and registers "
    "unmatched detections as brand-new tracks. A separate line-crossing check compares each "
    "track's previous and current y-coordinate against the counting line, incrementing the count "
    "exactly once per track via a boolean 'counted' flag."
)
h2("8.3 Reporting Module (src/reporter.py)")
body(
    "<font face='Courier'>ReportWriter</font> buffers one row per frame (frame number, timestamp, "
    "running counts) and writes it to CSV at the end of the run, plus a final JSON summary with "
    "totals by class and run metadata. A separate <font face='Courier'>annotate_frame()</font> "
    "function draws the counting line, live track markers with ID/class labels, and a running "
    "count overlay directly onto each video frame using OpenCV drawing primitives."
)
h2("8.4 CLI Entry Point (src/main.py)")
body(
    "Uses <font face='Courier'>argparse</font> to expose all configuration as flags, validates "
    "the input path and argument ranges before doing any expensive work, then drives the main "
    "per-frame loop: read frame → detect (respecting --skip-frames) → update tracker → log to "
    "report → annotate and write to output video."
)

# ---------------- Screenshots / Results ----------------
story.append(PageBreak())
h1("9. Screenshots / Results")
body(
    "The full pipeline (tracker + reporter + annotation) was validated end-to-end using a "
    "synthetic test video generated with OpenCV, simulating two vehicles (one 'car', one 'truck') "
    "moving through the frame and crossing the counting line. This validates the tracking, "
    "counting-once, and reporting logic independently of the YOLO model download step, which "
    "requires network access on first run. The frames below are taken directly from the "
    "annotated output video produced by the tool."
)
diagram("demo/screenshot_frame30.png", "Figure 6 — Frame 30: two vehicles approaching the counting line, not yet counted.", width=4.5*inch)
diagram("demo/screenshot_frame60.png", "Figure 7 — Frame 60: the car has crossed the line and been counted once (Total: 1).", width=4.5*inch)
diagram("demo/screenshot_frame90.png", "Figure 8 — Frame 90: both vehicles have crossed and are counted correctly (Total: 2, car: 1, truck: 1).", width=4.5*inch)

h2("Sample summary.json output")
story.append(Paragraph(
    "{<br/>&nbsp;&nbsp;\"video_source\": \"synthetic_demo\",<br/>"
    "&nbsp;&nbsp;\"frames_processed\": 90,<br/>"
    "&nbsp;&nbsp;\"video_duration_sec\": 4.5,<br/>"
    "&nbsp;&nbsp;\"total_vehicles_counted\": 2,<br/>"
    "&nbsp;&nbsp;\"counts_by_class\": { \"car\": 1, \"truck\": 1 }<br/>}",
    styles["CodeBlock"]
))
body(
    "On a real traffic video, the same pipeline runs unchanged — only the detections come from "
    "YOLOv8n instead of synthetic rectangles. Users can generate this by running "
    "<font face='Courier'>python src/main.py --input &lt;video&gt;</font> as described in the README."
)

# ---------------- Testing Approach ----------------
h1("10. Testing Approach")
body(
    "Testing focuses on the tracker and reporter — the two modules with genuine algorithmic logic "
    "— using synthetic data so tests run instantly without a video file or the ML model."
)
bullets([
    "<b>Tracker tests (6 cases):</b> new-track registration, ID persistence across frames for a "
    "slowly moving object, stale-track removal after max_disappeared misses, single-count-only "
    "line-crossing (including no double-count after further movement), per-class count separation, "
    "and correct handling of a detection too far away to match an existing track.",
    "<b>Reporter tests (2 cases):</b> CSV rows match logged frame data exactly; JSON summary "
    "contains the correct totals and metadata fields.",
    "<b>End-to-end validation:</b> a synthetic video run (Section 9) exercises the full pipeline "
    "— detection-shaped input, tracking, counting, CSV/JSON writing, and video annotation — "
    "together in one run, confirming the modules integrate correctly.",
])
body("All 8 unit tests pass. Run with: <font face='Courier'>python -m pytest tests/ -v</font>")

# ---------------- Challenges Faced ----------------
h1("11. Challenges Faced")
bullets([
    "<b>Avoiding double-counting:</b> An early version counted a vehicle every frame its centroid "
    "was past the line, wildly over-counting. Solved by adding a one-time 'counted' flag per "
    "track, so crossing is a discrete event, not a per-frame state.",
    "<b>Matching detections to tracks stably:</b> Nearest-neighbor matching alone could "
    "occasionally swap IDs when two vehicles passed close together. A max-distance cap on valid "
    "matches (so a detection can only match a track within a plausible movement radius) reduced "
    "this significantly.",
    "<b>Testing without the ML model:</b> The tracker and reporter needed to be testable without "
    "requiring ultralytics/YOLO to be installed (a heavy, network-dependent dependency). This "
    "drove the decision to extract the Detection data class into its own dependency-free "
    "models.py module.",
])

# ---------------- Learnings ----------------
h1("12. Learnings & Key Takeaways")
bullets([
    "Detection and tracking are genuinely separate problems — a strong detector alone does not "
    "give you identity or counts across time; that requires its own algorithm.",
    "Designing for testability up front (isolating the tracker from the ML dependency) made it "
    "possible to verify correctness quickly and repeatedly, rather than only being able to check "
    "results by eye on a video.",
    "Small algorithmic decisions (e.g. exactly when to mark something 'counted') have an outsized "
    "effect on real-world correctness compared to the detector's accuracy.",
])

# ---------------- Future Enhancements ----------------
h1("13. Future Enhancements")
bullets([
    "Multi-line counting to support directional flow (e.g. entering vs. exiting a junction).",
    "Speed estimation using frame-to-frame pixel displacement and a camera calibration step.",
    "Swap the greedy centroid tracker for an IoU- or appearance-based tracker (e.g. DeepSORT) for "
    "more robust identity preservation in dense traffic.",
    "A lightweight web dashboard to visualize the CSV/JSON output over time (optional, since the "
    "core tool is intentionally CLI-first).",
])

# ---------------- References ----------------
h1("14. References")
bullets([
    "Ultralytics YOLOv8 documentation — https://docs.ultralytics.com/",
    "OpenCV Python documentation — https://docs.opencv.org/",
    "COCO dataset class list — https://cocodataset.org/",
    "Centroid tracking algorithm concept — a common, well-documented approach for lightweight "
    "multi-object tracking without a deep re-identification model.",
])

doc = SimpleDocTemplate(
    "report.pdf", pagesize=letter,
    topMargin=0.7*inch, bottomMargin=0.7*inch, leftMargin=0.8*inch, rightMargin=0.8*inch,
    title="Vehicle Traffic Counter - Project Report"
)
doc.build(story)
print("report.pdf built")
