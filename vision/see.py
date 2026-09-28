#!/usr/bin/env python3
"""Kasa v0 vision bench: face + motion. No servos, no ROS, no LLM.

q quit | s sleep | w wake

Looks-at-face = largest face center vs frame center (print only).
Startle = motion energy above threshold while awake.
"""
from __future__ import annotations

import argparse
import sys

import cv2
import numpy as np

DEADBAND_PX = 40
MOTION_THRESH = 2.2e6


def require_haar() -> None:
    if not hasattr(cv2, "CascadeClassifier"):
        ver = getattr(cv2, "__version__", "unknown")
        loc = getattr(cv2, "__file__", "unknown")
        raise SystemExit(
            f"this cv2 ({ver} at {loc}) has no CascadeClassifier.\n"
            "OpenCV 5 dropped Haar from core. Pin 4.x:\n"
            "  pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python cv2\n"
            "  pip install 'opencv-python>=4.8,<5'\n"
        )


def open_cam(index: int, width: int, height: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap


def main() -> None:
    require_haar()
    parser = argparse.ArgumentParser(description="Kasa laptop camera bench")
    parser.add_argument("--cam", type=int, default=0)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    args = parser.parse_args()

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        raise SystemExit(f"missing Haar cascade: {cascade_path}")

    cap = open_cam(args.cam, args.width, args.height)
    ok, prev = cap.read()
    if not ok:
        raise SystemExit("no frame — check device index and that the UVC camera is plugged in")

    height, width = prev.shape[:2]
    prev_gray = cv2.GaussianBlur(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    awake = True
    print(f"cv2 {cv2.__version__}  {width}x{height}  s=sleep  w=wake  q=quit", file=sys.stderr)

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (21, 21), 0)

        delta = cv2.absdiff(prev_gray, blur)
        motion = float(np.sum(delta))
        prev_gray = blur
        startled = awake and motion > MOTION_THRESH

        err_x = err_y = 0
        faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            cx, cy = x + w // 2, y + h // 2
            err_x = cx - width // 2
            err_y = cy - height // 2
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
            look = abs(err_x) > DEADBAND_PX or abs(err_y) > DEADBAND_PX
        else:
            look = False

        if not awake:
            status = "SLEEP"
        elif startled:
            status = "STARTLE"
        elif look:
            status = "LOOK"
        else:
            status = "IDLE"

        cv2.putText(
            frame,
            f"{status}  mot={motion / 1e6:.1f}e6  ex={err_x} ey={err_y}",
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        cv2.circle(frame, (width // 2, height // 2), DEADBAND_PX, (80, 80, 80), 1)
        cv2.imshow("kasa-see", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            awake = False
            print("sleep")
        if key == ord("w"):
            awake = True
            print("wake")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
