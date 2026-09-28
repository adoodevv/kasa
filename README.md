# Kasa

Stationary 5-DOF desk companion. Twi: *to speak*.

Mikrobot Physical AI Lab. Not a walker, not a lamp-pet, not a MicroDuck clone. The SO-101 arm is parked in a separate repo until this neck is boring and reliable.

Repo lives on a personal account for now. It will move to an organization later.

## v0 body (frozen)

- Weighted base, short neck, camera in the head, two ears/antennas.
- No legs, wheels, or arm on v0.
- Joints:
  - `base_yaw` ±90° — STS3215
  - `neck_pitch` −20° to +45° — STS3215
  - `head_pitch` −25° to +25° — STS3215
  - `ear_l` / `ear_r` 0–60° — metal 9g or STS3032
- Brain later: Raspberry Pi 5 + wide USB camera + mic/speaker.
- Motion work starts from a laptop + Feetech bus linker.
- Print PETG at Mind2Matter. Target under ~1.2 kg. Kit cost target later ~$180–250 parts.

Full write-up: [`docs/v0_spec.md`](docs/v0_spec.md). Parts: [`docs/bom.md`](docs/bom.md).

## 14-day definition of done

Printed grey neck that:

1. looks at a face
2. startles on camera motion
3. sleeps on a keypress
4. does not jitter

Out of scope for that window: LLM, LeRobot, ROS 2, X announcement, mini-arm.

## Near-term sequence

1. Cardboard mock + photos
2. Onshape: base / yaw horn / neck link / head shell / camera clamp
3. `firmware/wiggle.py` — torque on, ±30° yaw sweep
4. Face track with P-only + deadband
5. Sleep + startle
6. 1 hour unattended
7. 20s silent film

## Status (2026-09-28)

- Spec frozen. This repo created.
- Camera on the bench: **Innomaker U20CAM-1080P** (pack of 2). UVC, 32×32 mm, M12, ~103° H / 130° D, MJPEG 1080p30.
- Laptop vision loop exists as `vision/see.py` (Haar face + motion energy + sleep key). No servos wired yet.
- No cardboard photos yet. No Onshape yet. No Feetech script yet.
- SO-101 stays in https://github.com/adoodevv/so101_ros2 — do not work that repo from here.

## Setup

```bash
git clone https://github.com/adoodevv/kasa.git
cd kasa
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Plug the U20CAM into USB. Confirm it enumerates:

```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
```

Run the camera bench (MJPEG, 1280×720):

```bash
python vision/see.py
```

Keys: `q` quit, `s` sleep, `w` wake. Tune `MOTION_THRESH` in the file to your room.

Always open this module as MJPEG. YUY2 at 1080p is ~5 fps.

## Layout

```
docs/           frozen spec + BOM
vision/         laptop camera bench (no ROS)
firmware/       Feetech wiggle / track (empty until a bus linker is on the desk)
```
