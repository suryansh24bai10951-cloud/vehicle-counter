# Design Diagrams

These diagrams render natively on GitHub. They are also included as images
in the PDF project report.

## 1. System Architecture

```mermaid
flowchart LR
    A[Input Video File] --> B[Detector Module\nYOLOv8n]
    B -->|per-frame detections| C[Tracker Module\nCentroid Tracking + Line Counter]
    C -->|live tracks + counts| D[Reporter Module]
    D --> E[Annotated Output Video]
    D --> F[frame_log.csv]
    D --> G[summary.json]
```

## 2. Process / Workflow Diagram

```mermaid
flowchart TD
    Start([Start]) --> ReadArgs[Parse CLI arguments]
    ReadArgs --> Validate{Input video\nvalid?}
    Validate -- No --> Error[Print error, exit 1]
    Validate -- Yes --> LoadModel[Load YOLOv8n model]
    LoadModel --> ReadFrame[Read next frame]
    ReadFrame --> HasFrame{Frame\nread OK?}
    HasFrame -- No --> Finalize[Write CSV + JSON summary,\nrelease video writer]
    HasFrame -- Yes --> Detect[Run detection on frame]
    Detect --> Track[Update tracker with detections]
    Track --> CheckLine{Any track just\ncrossed the line\nand not yet counted?}
    CheckLine -- Yes --> IncrementCount[Increment count for\nthat vehicle class]
    CheckLine -- No --> LogFrame
    IncrementCount --> LogFrame[Log frame to CSV buffer]
    LogFrame --> Annotate[Draw boxes/IDs/counts,\nwrite to output video]
    Annotate --> ReadFrame
    Finalize --> End([End])
```

## 3. Use Case Diagram

```mermaid
flowchart LR
    User((User / Evaluator))
    User --> UC1[Run vehicle count\non a video via CLI]
    User --> UC2[Configure counting line\nand confidence threshold]
    User --> UC3[Review annotated\noutput video]
    User --> UC4[Review CSV / JSON\nreports]
```

## 4. Class / Component Diagram

```mermaid
classDiagram
    class Detection {
        +tuple bbox
        +str class_name
        +float confidence
        +centroid() tuple
    }

    class VehicleDetector {
        -YOLO _model
        -float confidence
        +detect(frame) list~Detection~
    }

    class Track {
        +int track_id
        +str class_name
        +tuple centroid
        +tuple prev_centroid
        +int disappeared
        +bool counted
        +update_position(centroid)
    }

    class CentroidTracker {
        -int line_y
        -float max_distance
        -int max_disappeared
        -dict tracks
        -dict counts
        -int total_counted
        +update(detections) list~Track~
    }

    class ReportWriter {
        -Path csv_path
        -Path json_path
        +log_frame(frame_number, fps, counts, total)
        +write_csv()
        +write_summary_json(...)
    }

    VehicleDetector --> Detection : creates
    CentroidTracker --> Detection : consumes
    CentroidTracker --> Track : manages
    ReportWriter --> Track : reads from
```

## 5. Sequence Diagram (single frame)

```mermaid
sequenceDiagram
    participant Main as main.py
    participant Det as VehicleDetector
    participant Trk as CentroidTracker
    participant Rep as ReportWriter

    Main->>Det: detect(frame)
    Det-->>Main: list[Detection]
    Main->>Trk: update(detections)
    Trk-->>Main: list[Track]
    Main->>Rep: log_frame(frame_number, fps, counts, total)
    Main->>Main: annotate_frame(frame, tracks, ...)
    Main->>Main: video_writer.write(annotated_frame)
```
