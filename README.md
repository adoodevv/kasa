# Kasa

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Stationary 5-DOF desk companion. Twi: *to speak*.

A weighted base, a short neck, a camera in the head, two ears. It looks, tilts, startles, and sleeps. Print it, plug the bus, write a pose.

## Quick look

```python
from kasa import Kasa

with Kasa() as bot:
    bot.look_at_face()
    bot.goto("curious", t=0.4)
    bot.sleep()
```

Face error from the camera drives the neck. Poses drive roll and ears.

- `ex` moves `base_yaw` (look around the desk)
- `ey` moves `neck_pitch` (nod, startle, sleep)
- roll moves `head_roll` (tilt, curiosity)
- ears move `ear_l` and `ear_r` (expression)

## Hardware overview

Five joints. One motor SKU. One bus.

| Joint | Range | Servo | Role |
| --- | --- | --- | --- |
| `base_yaw` | ±90° | STS3215 7.4 V | Look around. Face `ex`. |
| `neck_pitch` | −20° to +45° | STS3215 7.4 V | Nod, startle up, chin-down sleep. Face `ey`. |
| `head_roll` | ±25° | STS3215 7.4 V | Tilt. Animation, not tracking. |
| `ear_l` | 0–60° | STS3215 7.4 V | Expression. Current-limited in firmware. |
| `ear_r` | 0–60° | STS3215 7.4 V | Expression. Current-limited in firmware. |

Camera in the head: Innomaker U20CAM-1080P, UVC, 32×32 mm, M12, ~103° H / 130° D. Open it as MJPEG.

Print PETG. Target under ~1.2 kg with base ballast.

## Power

5 V wall adapter into a Waveshare bus servo adapter, then five STS3215 7.4 V on one TTL daisy-chain.

Do not power the bus from the host USB port alone. Use the adapter's DC input. Share ground with the host. Ear IDs run a low max-torque / max-current cap so a 19 kg.cm motor does not rip a printed ear.

Laptop: camera on USB, adapter on USB for data, 5 V wall on the adapter barrel. A later Pi 5 can sit on 5 V as well; motor current stays on the adapter.

## Build and start your own robot

1. Cardboard the base, yaw horn, neck, head, and camera clamp. Measure the U20CAM hole pitch.
2. Print PETG. Leave the M12 barrel free to focus. Strain-relieve the USB pigtail in the head shell.
3. Set servo IDs 1-5: `base_yaw`, `neck_pitch`, `head_roll`, `ear_l`, `ear_r`.
4. Plug the Waveshare adapter and the 5 V wall. Sweep yaw ±30° before closing any loop.
5. Face track: `ex` on yaw, `ey` on pitch, 40 px deadband.
6. Poses: `sleep`, `startle`, `curious`, `listen`.
7. One hour unattended.

Done when the printed neck looks at a face, startles on motion, sleeps on a key, and does not jitter.

## Getting started with the Kasa SDK

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

```python
from kasa import Kasa

with Kasa() as bot:
    bot.look_at_face()
    bot.goto("curious", t=0.4)
    bot.ears.alert()
    bot.sleep()
```

Apps and examples are Python. The bus is Feetech TTL on the Waveshare adapter.

## Community and contributing

Fork it. Change a pose. Change an ear mesh. Send a patch.

Issues and pull requests on this repo. Pose files and printed parts are the customization surface.

## License

Apache License 2.0. See [LICENSE](LICENSE).
