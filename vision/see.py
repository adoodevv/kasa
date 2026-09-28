#!/usr/bin/env python3
"""
Kasa v0 vision bench. No servos, no ROS, no LLM.
"""
from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

import cv2
import numpy as np

# Innomaker is video4 on this laptop (video5 is the metadata node).
CAM = 4
WIDTH = 1280
HEIGHT = 720
DEADBAND_PX = 40
MOTION_THRESH = 2.2e6
SCORE_TH = 0.7

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE / "models"
YUNET_FILES = (
    (
        "face_detection_yunet_2026may.onnx",
        "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2026may.onnx",
    ),
    (
        "face_detection_yunet_2023mar.onnx",
        "https://huggingface.co/opencv/face_detection_yunet/resolve/main/face_detection_yunet_2023mar.onnx",
    ),
)


def print_devices() -> None:
    root = Path("/sys/class/video4linux")
    if not root.is_dir():
        print("no /sys/class/video4linux nodes")
        return
    print(f"{'idx':<5} {'dev':<14} name")
    for node in sorted(root.glob("video*")):
        idx = int(node.name.replace("video", ""))
        name_path = node / "name"
        name = name_path.read_text().strip() if name_path.exists() else "?"
        print(f"{idx:<5} /dev/video{idx:<4} {name}")


def ensure_yunet() -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    last_err: Exception | None = None
    for filename, url in YUNET_FILES:
        dest = MODEL_DIR / filename
        if dest.exists() and dest.stat().st_size > 10_000:
            return dest
        try:
            print(f"downloading {filename} …", file=sys.stderr)
            urllib.request.urlretrieve(url, dest)
            if dest.stat().st_size > 10_000:
                return dest
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            if dest.exists():
                dest.unlink()
    raise SystemExit(f"could not fetch YuNet ONNX: {last_err}")


def make_face_detector(width: int, height: int):
    model = ensure_yunet()
    if hasattr(cv2, "FaceDetectorYN_create"):
        return "yunet", cv2.FaceDetectorYN_create(
            str(model), "", (width, height), SCORE_TH, 0.3, 5000
        )
    if hasattr(cv2, "FaceDetectorYN"):
        return "yunet", cv2.FaceDetectorYN.create(
            str(model), "", (width, height), SCORE_TH, 0.3, 5000
        )
    if hasattr(cv2, "CascadeClassifier"):
        path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        det = cv2.CascadeClassifier(path)
        if det.empty():
            raise SystemExit(f"Haar xml missing: {path}")
        return "haar", det
    raise SystemExit(
        f"cv2 {getattr(cv2, '__version__', '?')} has no face detector"
    )


def detect_faces(kind, det, frame, gray):
    h, w = frame.shape[:2]
    if kind == "yunet":
        det.setInputSize((w, h))
        _, faces = det.detect(frame)
        if faces is None:
            return []
        return [(int(f[0]), int(f[1]), int(f[2]), int(f[3])) for f in faces]
    faces = det.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
    return [(int(x), int(y), int(bw), int(bh)) for x, y, bw, bh in faces]


def open_cam(index: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--list", action="store_true")
    args, _ = parser.parse_known_args()
    if args.list:
        print_devices()
        return

    cap = open_cam(CAM)
    ok, prev = cap.read()
    if not ok:
        print_devices()
        raise SystemExit(f"no frame from /dev/video{CAM} — run with --list and change CAM")

    height, width = prev.shape[:2]
    kind, detector = make_face_detector(width, height)
    prev_gray = cv2.GaussianBlur(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    awake = True
    print(
        f"cv2 {cv2.__version__}  detector={kind}  {width}x{height}  "
        f"/dev/video{CAM}  s=sleep w=wake q=quit",
        file=sys.stderr,
    )

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (21, 21), 0)
        motion = float(np.sum(cv2.absdiff(prev_gray, blur)))
        prev_gray = blur
        startled = awake and motion > MOTION_THRESH

        err_x = err_y = 0
        boxes = detect_faces(kind, detector, frame, gray)
        if boxes:
            x, y, bw, bh = max(boxes, key=lambda b: b[2] * b[3])
            cx, cy = x + bw // 2, y + bh // 2
            err_x = cx - width // 2
            err_y = cy - height // 2
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
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