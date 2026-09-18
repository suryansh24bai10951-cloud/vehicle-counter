# Problem Statement

Manual vehicle counting for traffic analysis (e.g. estimating congestion,
planning signal timing, or measuring road usage) is slow, error-prone, and
does not scale to long durations of footage. Traffic authorities and
researchers need an automated, repeatable way to count vehicles passing a
point in a video, broken down by vehicle type, without expensive dedicated
hardware.

## Scope of the Project

This project builds a command-line tool that takes any traffic video as
input and produces:
- A count of vehicles (cars, motorcycles, buses, trucks) that crossed a
  configurable virtual line in the video
- A per-frame CSV log of running counts over time
- A JSON summary report of totals by vehicle class
- An annotated version of the input video for visual verification

The scope is limited to counting from a **fixed-camera or roughly stable**
video (e.g. a mounted CCTV or dashcam viewpoint); it does not attempt
multi-camera fusion, speed estimation, or license-plate recognition.

## Target Users

- Traffic/transport researchers who need a lightweight, scriptable vehicle
  counting tool for short video clips
- Students or hobbyists who want a working example of combining a pretrained
  object detector with a custom tracking algorithm
- Anyone who wants a quick, offline-after-setup way to get vehicle counts
  from a video without a full traffic-analytics platform

## High-Level Features

1. **Detection** — identify cars, motorcycles, buses, and trucks in each
   video frame using a pretrained YOLOv8n model.
2. **Tracking & Counting** — assign a persistent ID to each vehicle across
   frames using a custom centroid-tracking algorithm, and count each vehicle
   exactly once as it crosses a virtual counting line.
3. **Reporting** — produce an annotated output video, a per-frame CSV log,
   and a final JSON summary, all generated from a single terminal command.
