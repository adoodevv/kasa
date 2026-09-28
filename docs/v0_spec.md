# Kasa v0 spec

Frozen 2026-09. Change only with an explicit decision, not while building.

## What it is

A stationary desk companion. Weighted base, short neck, camera in the head, two ears. It looks, startles, and sleeps. It does not walk. It does not have an arm on v0.

Name: Kasa (Twi, to speak).
Lab: Mikrobot Physical AI Lab / Kasa Lab.

## What it is not

- Not Hugging Face MicroDuck or any walking biped.
- Not an Autonomous Lamp closed pet.
- Not a clone of the SO-101 stack. That arm is parked.

## Joints

| Joint | Range | Servo |
| --- | --- | --- |
| `base_yaw` | ±90° | STS3215 |
| `neck_pitch` | −20° to +45° | STS3215 |
| `head_pitch` | −25° to +25° | STS3215 |
| `ear_l` | 0–60° | metal 9g or STS3032 |
| `ear_r` | 0–60° | metal 9g or STS3032 |

Control for v0 face-track: P-only on yaw / neck / head with a pixel deadband. Ears are expression only.

## Compute and sensing (v0)

- Motion development: laptop + Feetech bus linker.
- Eventual brain: Raspberry Pi 5.
- Camera: Innomaker U20CAM-1080P USB2.0 UVC, 130° D / ~103° H, 32×32 mm PCB, M12 lens, 4× M2 holes. MJPEG 1920×1080@30. Two units on hand (one in head, one spare/bench).
- Mic / speaker: later. Not in the 14-day window.

## Mechanical targets

- Print: PETG at Mind2Matter.
- Mass: under ~1.2 kg including base ballast.
- Parts kit target (later): ~$180–250.
- Camera clamp must leave the M12 barrel free to focus and strain-relieve the USB pigtail off the connector.

## 14-day definition of done

Printed grey neck that looks at a face, startles on camera motion, sleeps on a keypress, and does not jitter.

Explicitly excluded: LLM, LeRobot plugin, ROS 2, public announcement, mini-arm.

## Sequence

cardboard mock + photos → Onshape (base, yaw horn, neck link, head shell, camera clamp) → `firmware/wiggle.py` torque + ±30° yaw sweep → face track P-only + deadband → sleep + startle → 1 hour unattended → 20s silent film.

## After v0

Once the neck is reliable, SO-101 returns as the data machine (LeRobotDataset of Ghana tasks). Kasa stays the face of the same lab stack. That work does not start from this repo until asked.
