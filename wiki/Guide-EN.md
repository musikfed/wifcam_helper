# English · Complete Guide

This independent lab explores the SD-booting T23N camera as a standalone IP camera and as the head of Hombo3. Choose camera settings from real measurements. Both the native microphone and native speaker MUST work physically. Cloud services are optional.

## 1. Setup and tests

Inspect processes rvd/rsd/rad/rac and the speaker/microphone/play tools over SSH. Probe existing RTSP ch0/ch1 streams with ffprobe; compare TCP and UDP. The short microphone test needs consent, and the quiet speaker test must be heard by an operator near the camera. Software availability is not acoustic proof.


### CLI (Ubuntu 24.04 / Python 3.12 / uv)

```bash
sudo apt-get install -y ffmpeg openssh-client
cd /1tbdisk/PegineLab/projects/wifcam_helper
bash scripts/verify-host.sh
uv run --no-project python3 -m wifcam_helper web
# Open http://127.0.0.1:8765 on CORE, or SSH forward from laptop.
python3 -m wifcam_helper inventory --host CAMERA_IP
python3 -m wifcam_helper probe --rtsp-url rtsp://CAMERA_IP:554/ch0
python3 -m wifcam_helper video --rtsp-url rtsp://CAMERA_IP:554/ch0 --transport tcp
python3 -m wifcam_helper microphone --rtsp-url rtsp://CAMERA_IP:554/ch0 --mic-consent
python3 -m wifcam_helper speaker --host CAMERA_IP --speaker-consent
python3 -m wifcam_helper export-preset
```

Use only a verified camera IP and real ch0/ch1 RTSP URL. The microphone test holds PCM in RAM only; the speaker test emits a quiet 0.2-second tone with explicit consent. Never publish Wi-Fi passwords, SSH keys or TLS private keys in Git. Neither test flashes SD, modifies the kernel nor restarts Raptor.


## 2. Video latency and local vision

RTSP startup time and decoder FPS do NOT equal glass-to-glass video latency. Measure with a real LED or clock and a second camera. Compare moving scenes, low light, resolution, bitrate, packet loss and Wi-Fi stability. Run optional YOLO, local STT and TTS on CORE RTX 3060, not on T23N.

## 3. Local dashboard, Wiki and security

Open `http://127.0.0.1:8765` or use `ssh -L 8765:127.0.0.1:8765 user@192.168.0.100`. Create the first GitHub Wiki Home page in the website, review all translations, then explicitly run `WIFCAM_PUBLISH_WIKI=YES bash scripts/publish-wiki.sh`. Never commit `~/crt-cert/privkey.pem`.

## 4. Project boundaries

- [WifCam Helper](https://github.com/musikfed/wifcam_helper): measurements, reports, presets
- [WIFICAM](https://github.com/musikfed/wificam_T23N/tree/mymarrchWFcam): firmware, kernel, drivers
- [YadroKreator](https://github.com/musikfed/YadroKreator): compilation on CORE
- [Hombo3](https://github.com/musikfed/Hombo3_3.0.0): robot vision and STT/LLM/TTS

**Hardware acceptance is still pending. GitHub CI is not an acoustic test.**
